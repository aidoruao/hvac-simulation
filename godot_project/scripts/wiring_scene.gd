extends Node3D

## FR-EL-002: Godot Wiring Scene Integration
## Interactive thermostat wiring with Python backend bridge

@onready var wire_nodes = $WireNodes
@onready var system_type = $UI/SystemPanel/VBoxContainer/SystemType
@onready var stages = $UI/SystemPanel/VBoxContainer/Stages
@onready var fault_list = $UI/FaultPanel/VBoxContainer/FaultList
@onready var status_text = $UI/StatusPanel/VBoxContainer/StatusText

const WIRE_COLORS := {
	"R": Color(0.9, 0.1, 0.1),    # Red
	"W": Color(0.95, 0.95, 0.95), # White
	"Y": Color(0.9, 0.9, 0.1),    # Yellow
	"G": Color(0.1, 0.7, 0.1),    # Green
	"C": Color(0.1, 0.3, 0.9),    # Blue
	"O": Color(0.9, 0.5, 0.1)     # Orange
}

const FAULT_TYPES := [
	"open_r",
	"shorted_rc",
	"reversing_stuck",
	"missing_common",
	"fan_always_on",
	"w1_w2_swapped",
	"y1_y2_swapped"
]

var current_system := "conventional"
var current_stages := 1
var current_fault := ""
var wire_states := {}

func _ready():
	print("Wiring Scene initialized (FR-EL-002)")
	_setup_ui()
	_load_wire_states()
	_update_wire_visuals()

func _setup_ui():
	system_type.item_selected.connect(_on_system_changed)
	stages.item_selected.connect(_on_stages_changed)

	fault_list.clear()
	for f in FAULT_TYPES:
		fault_list.add_item(f)
	fault_list.item_selected.connect(_on_fault_selected)

func _on_system_changed(index: int):
	current_system = system_type.get_item_text(index)
	_load_wire_states()
	_update_wire_visuals()

func _on_stages_changed(index: int):
	current_stages = index + 1
	_load_wire_states()
	_update_wire_visuals()

func _on_fault_selected(index: int):
	current_fault = FAULT_TYPES[index]
	_load_wire_states()
	_update_wire_visuals()

func _load_wire_states():
	# Read from Python backend JSON bridge
	var file = FileAccess.open("user://wiring_state.json", FileAccess.READ)
	if file:
		var json = JSON.new()
		var error = json.parse(file.get_as_text())
		file.close()
		if error == OK:
			wire_states = json.get_data()
			return

	# Fallback: build default state
	wire_states = _build_default_state()

func _build_default_state() -> Dictionary:
	var wires := []
	var base := [
		{"label": "R", "color": "RED", "function": "24V power", "connected": true, "voltage_present": true, "fault": null},
		{"label": "W", "color": "WHITE", "function": "Heat call", "connected": true, "voltage_present": false, "fault": null},
		{"label": "Y", "color": "YELLOW", "function": "Cool call", "connected": true, "voltage_present": false, "fault": null},
		{"label": "G", "color": "GREEN", "function": "Fan call", "connected": true, "voltage_present": false, "fault": null},
		{"label": "C", "color": "BLUE", "function": "Common", "connected": true, "voltage_present": false, "fault": null}
	]

	for w in base:
		wires.append(w)

	if current_system == "heat_pump":
		wires.append({"label": "O", "color": "ORANGE", "function": "Reversing valve", "connected": true, "voltage_present": false, "fault": null})

	return {
		"system_type": current_system,
		"stages": current_stages,
		"miswired": false,
		"fault_description": current_fault,
		"wires": wires
	}

func _update_wire_visuals():
	var status_lines := []

	for child in wire_nodes.get_children():
		var label = child.name
		var mesh = child.get_node("Mesh")
		var wire_data = _find_wire_data(label)

		if wire_data:
			var color = WIRE_COLORS.get(label, Color.GRAY)

			if wire_data.get("fault"):
				color = Color(0.9, 0.1, 0.9)  # Magenta for fault
				status_lines.append("%s: FAULT — %s" % [label, wire_data["fault"]])
			elif not wire_data.get("connected", true):
				color = Color(0.3, 0.3, 0.3)  # Gray for disconnected
				status_lines.append("%s: DISCONNECTED" % label)
			elif wire_data.get("voltage_present", false):
				color = Color(0.2, 0.9, 0.2)  # Bright green for active
				status_lines.append("%s: 24V ACTIVE" % label)
			else:
				status_lines.append("%s: OK" % label)

			mesh.material_override = _make_material(color)

	if status_lines.is_empty():
		status_text.text = "All wires OK"
	else:
		status_text.text = "\n".join(status_lines)

func _find_wire_data(label: String) -> Dictionary:
	for w in wire_states.get("wires", []):
		if w.get("label") == label:
			return w
	return {}

func _make_material(color: Color) -> StandardMaterial3D:
	var mat = StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = 0.4
	mat.roughness = 0.3
	return mat

func _write_state():
	var file = FileAccess.open("user://wiring_state.json", FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(wire_states, "\t"))
		file.close()
