extends SceneTree

## Test helper for FR-EL-002
## Usage: godot --headless --script scripts/test_helper_wiring.gd <test_name>

func _initialize():
	var args = OS.get_cmdline_args()
	var test_name = args[args.size() - 1] if args.size() > 0 else ""

	match test_name:
		"test_load":
			_test_load()
		"test_nodes":
			_test_nodes()
		_:
			print("FAIL: Unknown test: ", test_name)
			quit()

func _test_load():
	var scene = load("res://scenes/wiring_scene.tscn")
	if scene == null:
		print("FAIL: Could not load wiring_scene.tscn")
		quit()
		return

	var instance = scene.instantiate()
	root.add_child(instance)

	# Wait a few frames for _ready
	for i in range(5):
		await create_timer(0.01).timeout

	if instance.has_method("_ready"):
		print("PASS: Wiring Scene initialized and_ready called")
	else:
		print("FAIL: _ready not found")

	quit()

func _test_nodes():
	var scene = load("res://scenes/wiring_scene.tscn")
	var instance = scene.instantiate()
	root.add_child(instance)

	var required_nodes = ["R", "W", "Y", "G", "C", "O"]
	var found = 0
	var wire_nodes = instance.get_node("WireNodes")

	for n in required_nodes:
		if wire_nodes.has_node(n):
			found += 1
		else:
			print("MISSING: ", n)

	if found == required_nodes.size():
		print("PASS: All wire nodes found (", found, "/", required_nodes.size(), ")")
	else:
		print("FAIL: Only ", found, "/", required_nodes.size(), " nodes found")

	quit()
