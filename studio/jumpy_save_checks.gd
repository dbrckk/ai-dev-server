extends SceneTree

var failures: Array[String] = []
var profile
var original: Dictionary

func _initialize() -> void:
	call_deferred("run_checks")

func check(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
		push_error(label)

func load_text(text: String) -> void:
	profile.data = original.duplicate(true)
	var file = FileAccess.open("user://jumpy_save.json", FileAccess.WRITE)
	file.store_string(text)
	file.close()
	profile.load_data()

func run_checks() -> void:
	profile = root.get_node("Profile")
	original = profile.data.duplicate(true)
	original.coins = 0
	original.best_score = 0
	original.sound = true
	load_text(JSON.stringify({"coins": -10, "best_score": "bad", "sound": "false", "unlocked_skins": "bad", "selected_skin": 99, "daily_key": [1]}))
	check(profile.data.coins == 0 and profile.data.best_score == 0 and profile.data.sound == true and profile.data.unlocked_skins == [0] and profile.data.selected_skin == 0 and profile.data.daily_key == "", "Invalid save fields must fall back safely")

	load_text(JSON.stringify({"coins": 12, "sound": false, "unlocked_skins": [0, 2], "selected_skin": 2}))
	check(typeof(profile.data.coins) == TYPE_INT and profile.data.coins == 12 and profile.data.sound == false and profile.data.selected_skin == 2, "Valid JSON numbers must normalize without losing preferences")

	load_text(JSON.stringify({"unlocked_skins": [0, 0, 99, -1, 2.5, "x", 2], "selected_skin": 3}))
	check(profile.data.unlocked_skins == [0, 2] and profile.data.selected_skin == 0, "Skins must be unique valid indices and selected skin unlocked")

	load_text('{"coins":1e100,"runs":2.5,"best_score":true,"daily_key":"2025-02-29","last_play_date":"2024-02-29"}')
	check(profile.data.coins == 0 and profile.data.runs == 0 and profile.data.best_score == 0 and profile.data.daily_key == "" and profile.data.last_play_date == "2024-02-29", "Numeric bounds and calendar dates must be validated")

	load_text('{"coins":')
	check(profile.data.coins == 0, "Truncated JSON must preserve safe defaults")
	load_text('[]')
	check(profile.data.coins == 0, "Non-object JSON must preserve safe defaults")

	profile.data = original.duplicate(true)
	profile.data.coins = 9
	DirAccess.remove_absolute(ProjectSettings.globalize_path("user://jumpy_save.json"))
	profile.load_data()
	check(profile.data.coins == 0, "Missing save must restore defaults")

	profile.data = original.duplicate(true)
	profile.data.coins = 22
	profile.data.sound = false
	profile.save()
	profile.data.coins = 0
	profile.data.sound = true
	profile.load_data()
	check(profile.data.coins == 22 and profile.data.sound == false, "Valid save roundtrip must preserve progress")

	profile.data = original.duplicate(true)
	profile.save()
	var report = FileAccess.open(OS.get_environment("STUDIO_BASELINE_REPORT"), FileAccess.WRITE)
	if report == null:
		quit(1)
		return
	report.store_string(JSON.stringify({"passed": failures.is_empty(), "failures": failures, "checks": 8}))
	report.close()
	print("JUMPY_SAVE_PASS" if failures.is_empty() else "JUMPY_SAVE_FAIL")
	quit(0 if failures.is_empty() else 1)
