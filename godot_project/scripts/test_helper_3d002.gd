extends SceneTree

## Test helper for FR-3D-002
## Usage: godot --headless --script scripts/test_helper_3d002.gd <test_name>

var test_name := ""
var test_instance: Node = null

func _initialize() -> void:
	var args = OS.get_cmdline_args()
	test_name = args[args.size() - 1] if args.size() > 0 else ""

	match test_name:
		"has_compressor":
			_test_has_compressor()
		"has_fan":
			_test_has_fan()
		"animation_on":
			_test_animation_on()
		"animation_off":
			_test_animation_off()
		_:
			print("FAIL: Unknown test: ", test_name)
			print("Args: ", args)
			quit()
	return

func _test_has_compressor() -> void:
	var scene = load("res://scenes/mechanical_room/mechanical_room.tscn")
	if scene == null:
		print("FAIL: Could not load scene")
		quit()
		return

	var instance = scene.instantiate()
	var compressor = instance.find_child("Compressor", true, false)
	if compressor:
		print("PASS: Compressor node found")
	else:
		print("FAIL: Compressor node not found")
	quit()
	return

func _test_has_fan() -> void:
	var scene = load("res://scenes/mechanical_room/mechanical_room.tscn")
	if scene == null:
		print("FAIL: Could not load scene")
		quit()
		return

	var instance = scene.instantiate()
	var fan = instance.find_child("CondenserFan", true, false)
	if fan:
		print("PASS: CondenserFan node found")
	else:
		print("FAIL: CondenserFan node not found")
	quit()
	return

func _test_animation_on() -> void:
	_write_state({
		"refrigerant": "R410A",
		"pressure_psi": 250.0,
		"temperature_f": 85.0,
		"superheat_f": 10.0,
		"subcooling_f": 5.0,
		"phase": "two-phase",
		"scenario_id": "TEST_001",
		"faults": [],
		"compressor_running": true,
		"load_percent": 75.0
	})

	var scene = load("res://scenes/mechanical_room/mechanical_room.tscn")
	test_instance = scene.instantiate()
	root.add_child(test_instance)

	# Wait for _ready and state fetch
	for i in range(5):
		await create_timer(0.01).timeout

	_check_animation()
	quit()
	return

func _test_animation_off() -> void:
	_write_state({
		"refrigerant": "R410A",
		"pressure_psi": 150.0,
		"temperature_f": 75.0,
		"superheat_f": 0.0,
		"subcooling_f": 0.0,
		"phase": "subcooled",
		"scenario_id": "TEST_002",
		"faults": ["compressor_off"],
		"compressor_running": false,
		"load_percent": 0.0
	})

	var scene = load("res://scenes/mechanical_room/mechanical_room.tscn")
	test_instance = scene.instantiate()
	root.add_child(test_instance)

	# Wait for _ready and state fetch
	for i in range(5):
		await create_timer(0.01).timeout

	_check_animation()
	quit()
	return

func _write_state(state: Dictionary) -> void:
	var f = FileAccess.open("user://hvac_state.json", FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(state))
		f.close()
	return

func _check_animation() -> void:
	if test_name == "animation_on":
		if test_instance.compressor_rpm > 0 and test_instance.fan_rpm > 0:
			print("PASS: Animation RPM set - compressor=", test_instance.compressor_rpm, " fan=", test_instance.fan_rpm)
		else:
			print("FAIL: Animation RPM not set - compressor=", test_instance.compressor_rpm, " fan=", test_instance.fan_rpm)
	elif test_name == "animation_off":
		if test_instance.compressor_rpm == 0 and test_instance.fan_rpm == 0:
			print("PASS: Animation stopped - compressor=", test_instance.compressor_rpm, " fan=", test_instance.fan_rpm)
		else:
			print("FAIL: Animation still running - compressor=", test_instance.compressor_rpm, " fan=", test_instance.fan_rpm)
	return
