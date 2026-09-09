extends SceneTree

var failures: Array[String] = []

func check(condition: bool, label: String) -> void:
	if not condition:
		failures.append(label)
		push_error(label)

func _initialize() -> void:
	call_deferred("run_checks")

func run_checks() -> void:
	var scene = load("res://scenes/Main.tscn")
	if scene == null:
		quit(1)
		return
	var game = scene.instantiate()
	root.add_child(game)
	await process_frame
	game.set_physics_process(false)
	var profile = root.get_node("Profile")
	profile.data.sound = false
	profile.data.haptics = false

	check(game.state == "READY", "Initial state must be READY")
	game.reset_run(true)
	var first = game.platforms.duplicate(true)
	game.reset_run(true)
	check(first == game.platforms, "Daily platforms must reproduce within one day")
	game.start_run()
	check(game.state == "PLAYING" and game.player_vy < 0, "Start must initiate a jump")
	var tap = InputEventAction.new()
	tap.action = "tap"
	tap.pressed = true
	game._unhandled_input(tap)
	check(not game.pulse_available, "First airborne tap must consume the pulse")
	game.player_vy = 100.0
	game._unhandled_input(tap)
	check(game.player_vy == 100.0, "Second airborne tap must not apply another pulse")
	var runs_before = int(profile.data.runs)
	game.die()
	game.die()
	check(int(profile.data.runs) == runs_before + 1, "Death must record a run exactly once")
	check(game.state == "DEAD" and game.ui.retry.visible, "Death must offer retry")
	game.restart_pressed()
	check(game.state == "PLAYING" and game.score == 0, "Retry must reset score and start")

	var count: int = 8
	if "--finance" in OS.get_cmdline_user_args():
		count += 4
		profile.data.coins = 10
		check(not profile.spend_coins(-5) and int(profile.data.coins) == 10, "Negative spending must preserve balance")
		profile.data.coins = 10
		check(not profile.spend_coins(0) and int(profile.data.coins) == 10, "Zero spending must be refused")
		profile.data.coins = 10
		check(not profile.spend_coins(11) and int(profile.data.coins) == 10, "Insufficient funds must preserve balance")
		profile.data.coins = 10
		check(profile.spend_coins(4) and int(profile.data.coins) == 6, "Valid spending must debit exactly once")
	var report_path = OS.get_environment("STUDIO_BASELINE_REPORT")
	if report_path.is_empty():
		report_path = "user://baseline-result.json"
	var report = FileAccess.open(report_path, FileAccess.WRITE)
	if report == null:
		quit(1)
		return
	report.store_string(JSON.stringify({"passed": failures.is_empty(), "failures": failures, "checks": count}))
	report.close()
	print("JUMPY_BASELINE_PASS" if failures.is_empty() else "JUMPY_BASELINE_FAIL")
	quit(0 if failures.is_empty() else 1)
