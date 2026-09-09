extends Node

const SAVE_PATH: String = "user://jumpy_save.json"
const SAVE_VERSION: int = 1

const DEFAULT_DATA: Dictionary = {
	"version": SAVE_VERSION,
	"best_score": 0,
	"coins": 0,
	"runs": 0,
	"perfect_landings": 0,
	"total_score": 0,
	"selected_skin": 0,
	"unlocked_skins": [0],
	"daily_best": 0,
	"daily_key": "",
	"streak_days": 0,
	"last_play_date": "",
	"sound": true,
	"haptics": true,
	"reduced_motion": false,
	"high_contrast": false
}

var data: Dictionary = DEFAULT_DATA.duplicate(true)

func _save_integer(value: Variant, fallback: int = 0, maximum: int = 2147483647) -> int:
	if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
		return fallback
	var number: float = float(value)
	if not is_finite(number) or number < 0.0 or number > maximum or number != floor(number):
		return fallback
	return int(number)

func _save_date(value: Variant) -> String:
	if not value is String or value.length() != 10:
		return ""
	var parts: PackedStringArray = value.split("-")
	if parts.size() != 3 or parts[0].length() != 4 or parts[1].length() != 2 or parts[2].length() != 2:
		return ""
	for part in parts:
		if not part.is_valid_int() or part.begins_with("+") or part.begins_with("-"):
			return ""
	var year: int = int(parts[0])
	var month: int = int(parts[1])
	var day: int = int(parts[2])
	if year < 1 or month < 1 or month > 12:
		return ""
	var days: Array[int] = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
		days[1] = 29
	return value if day >= 1 and day <= days[month - 1] else ""

func _validated_save(parsed: Dictionary) -> Dictionary:
	var clean: Dictionary = DEFAULT_DATA.duplicate(true)
	for key in ["best_score", "coins", "runs", "perfect_landings", "total_score", "daily_best", "streak_days"]:
		clean[key] = _save_integer(parsed.get(key, 0))
	for key in ["sound", "haptics", "reduced_motion", "high_contrast"]:
		if typeof(parsed.get(key)) == TYPE_BOOL:
			clean[key] = parsed[key]
	for key in ["daily_key", "last_play_date"]:
		clean[key] = _save_date(parsed.get(key))
	var unlocks: Array = [0]
	var saved_unlocks: Variant = parsed.get("unlocked_skins")
	if saved_unlocks is Array:
		for item in saved_unlocks:
			var index: int = _save_integer(item, -1, 5)
			if index >= 0 and not index in unlocks:
				unlocks.append(index)
	clean.unlocked_skins = unlocks
	var selected: int = _save_integer(parsed.get("selected_skin", 0), 0, 5)
	clean.selected_skin = selected if selected in unlocks else 0
	return clean

func _ready() -> void:
	load_data()
	_refresh_daily()

func load_data() -> void:
	data = DEFAULT_DATA.duplicate(true)
	if not FileAccess.file_exists(SAVE_PATH):
		return
	var file: FileAccess = FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		push_warning("Jumpy: unable to open save file; defaults preserved.")
		return
	if file.get_length() > 262144:
		push_warning("Jumpy: save file too large; defaults preserved.")
		return
	var parser: JSON = JSON.new()
	if parser.parse(file.get_as_text()) != OK or not parser.data is Dictionary:
		push_warning("Jumpy: save file is invalid; defaults preserved.")
		return
	data = _validated_save(parser.data)

func save() -> void:
	var file: FileAccess = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_warning("Jumpy: unable to open save file for writing. Error %s" % FileAccess.get_open_error())
		return
	file.store_string(JSON.stringify(data))
	file.flush()
	var error: Error = file.get_error()
	if error != OK:
		push_warning("Jumpy: save write failed with error %s" % error)

func set_preference(key: String, value: bool) -> void:
	if key not in ["sound", "haptics", "reduced_motion", "high_contrast"]:
		push_warning("Jumpy: unknown preference %s" % key)
		return
	data[key] = value
	save()

func record_run(score: int, run_coins: int, perfects: int, daily: bool) -> Dictionary:
	data.runs = int(data.runs) + 1
	data.coins = int(data.coins) + run_coins
	data.total_score = int(data.total_score) + score
	data.perfect_landings = int(data.perfect_landings) + perfects
	data.best_score = maxi(int(data.best_score), score)
	if daily:
		data.daily_best = maxi(int(data.daily_best), score)
	_update_streak()
	_unlock_earned_skins()
	save()
	return get_mission_progress()

func spend_coins(amount: int) -> bool:
	if amount <= 0 or int(data.coins) < amount:
		return false
	data.coins = int(data.coins) - amount
	save()
	return true

func select_skin(index: int) -> void:
	if index in data.unlocked_skins:
		data.selected_skin = index
		save()

func get_mission_progress() -> Dictionary:
	return {
		"runs": mini(int(data.runs), 10),
		"runs_goal": 10,
		"perfects": mini(int(data.perfect_landings), 50),
		"perfects_goal": 50,
		"score": mini(int(data.total_score), 5000),
		"score_goal": 5000
	}

func daily_seed() -> int:
	_refresh_daily()
	return absi(hash(str(data.daily_key)))

func _refresh_daily() -> void:
	var date: Dictionary = Time.get_date_dict_from_system()
	var key: String = "%04d-%02d-%02d" % [date.year, date.month, date.day]
	if str(data.daily_key) != key:
		data.daily_key = key
		data.daily_best = 0
		save()

func _update_streak() -> void:
	var date: Dictionary = Time.get_date_dict_from_system()
	var today: String = "%04d-%02d-%02d" % [date.year, date.month, date.day]
	if str(data.last_play_date) == today:
		return
	if str(data.last_play_date).is_empty():
		data.streak_days = 1
	else:
		var now_unix: int = int(Time.get_unix_time_from_system())
		var last_unix: int = int(Time.get_unix_time_from_datetime_string(str(data.last_play_date) + "T00:00:00"))
		var days: int = int((now_unix - last_unix) / 86400.0)
		data.streak_days = int(data.streak_days) + 1 if days <= 1 else 1
	data.last_play_date = today

func _unlock_earned_skins() -> void:
	var unlocks: Array = data.unlocked_skins
	var milestones: Array[int] = [0, 250, 900, 2200, 5000, 10000]
	for i: int in range(milestones.size()):
		if int(data.total_score) >= milestones[i] and not i in unlocks:
			unlocks.append(i)
	data.unlocked_skins = unlocks
