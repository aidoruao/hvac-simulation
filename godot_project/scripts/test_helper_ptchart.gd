extends SceneTree

## Test helper for FR-VI-001 / FR-VI-002
## Usage: godot --headless --script scripts/test_helper_ptchart.gd <test_name>

func _initialize():
	var args = OS.get_cmdline_args()
	var test_name = args[args.size() - 1] if args.size() > 0 else ""

	match test_name:
		"test_load":
			_test_load()
		"test_dropdown":
			_test_dropdown()
		"test_switch":
			_test_switch()
		"test_reference":
			_test_reference()
		_:
			print("FAIL: Unknown test: ", test_name)
			quit()

func _test_load():
	var scene = load("res://scenes/pt_chart.tscn")
	if scene == null:
		print("FAIL: Could not load pt_chart.tscn")
		quit()
		return

	var instance = scene.instantiate()
	root.add_child(instance)

	for i in range(5):
		await create_timer(0.01).timeout

	if instance.pt_data.is_empty():
		print("FAIL: pt_data not loaded")
	else:
		print("PASS: pt_chart loaded, ", instance.pt_data.size(), " refrigerants")
	quit()

func _test_dropdown():
	var scene = load("res://scenes/pt_chart.tscn")
	var instance = scene.instantiate()
	root.add_child(instance)

	for i in range(5):
		await create_timer(0.01).timeout

	var dropdown = instance.dropdown
	if dropdown == null:
		print("FAIL: Dropdown not found")
		quit()
		return

	if dropdown.item_count > 0:
		print("PASS: Dropdown populated with ", dropdown.item_count, " items")
	else:
		print("FAIL: Dropdown empty")
	quit()

func _test_switch():
	var scene = load("res://scenes/pt_chart.tscn")
	var instance = scene.instantiate()
	root.add_child(instance)

	for i in range(5):
		await create_timer(0.01).timeout

	instance.switch_refrigerant("R134a")
	for i in range(3):
		await create_timer(0.01).timeout

	if instance.current_refrigerant == "R134a" and not instance.points.is_empty():
		print("PASS: Switched to R134a, ", instance.points.size(), " points")
	else:
		print("FAIL: Switch failed, refrigerant=", instance.current_refrigerant, " points=", instance.points.size())
	quit()

func _test_reference():
	var scene = load("res://scenes/pt_chart.tscn")
	var instance = scene.instantiate()
	root.add_child(instance)

	for i in range(5):
		await create_timer(0.01).timeout

	instance.switch_refrigerant("R410A")
	for i in range(3):
		await create_timer(0.01).timeout

	var ref_p = instance._get_pressure_at_temp(25.0)
	if ref_p > 0:
		print("PASS: Reference pressure at 25C = ", snapped(ref_p, 0.01), " bar")
	else:
		print("FAIL: Reference pressure not found")
	quit()
