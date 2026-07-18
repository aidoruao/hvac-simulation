extends SceneTree

## Test helper for FR-ED-004 locale loading
## Usage: godot --headless --script scripts/test_helper_locale.gd <test_name>

func _initialize() -> void:
	var args = OS.get_cmdline_args()
	var test_name = args[args.size() - 1] if args.size() > 0 else ""

	match test_name:
		"test_load_es":
			_test_load_es()
		"test_label_es":
			_test_label_es()
		_:
			print("FAIL: Unknown test: ", test_name)
			quit()
	return

func _test_load_es() -> void:
	var locale = load("res://scripts/locale_es.gd")
	if locale == null:
		print("FAIL: Could not load locale_es.gd")
		quit()
		return
	print("PASS: locale_es.gd loaded")
	quit()
	return

func _test_label_es() -> void:
	var locale = load("res://scripts/locale_es.gd")
	if locale == null:
		print("FAIL: Could not load locale_es.gd")
		quit()
		return

	# Check a specific Spanish label exists
	var es_data = locale.LOCALE_ES
	if es_data.has("mechanical_room"):
		var mr = es_data["mechanical_room"]
		if mr.has("refrigerant") and mr["refrigerant"] == "Refrigerante":
			print("PASS: Spanish label 'Refrigerante' found")
		else:
			print("FAIL: Spanish label not found")
	else:
		print("FAIL: mechanical_room section not found")
	quit()
	return
