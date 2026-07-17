extends Node3D

## Mechanical Room — 3D visualization of HVAC system state
## FR-3D-001: 3D mechanical room with real-time gauge updates
## Connects to Python backend via JSON bridge (same as PT chart)

@onready var pressure_needle = $Gauges/PressureGauge/CSGCylinder3D2
@onready var temp_needle = $Gauges/TempGauge/CSGCylinder3D2
@onready var sight_glass = $Gauges/SightGlass/CSGCylinder3D

@onready var refrigerant_label = $UI/StatePanel/VBoxContainer/Refrigerant
@onready var pressure_label = $UI/StatePanel/VBoxContainer/Pressure
@onready var temperature_label = $UI/StatePanel/VBoxContainer/Temperature
@onready var superheat_label = $UI/StatePanel/VBoxContainer/Superheat
@onready var subcooling_label = $UI/StatePanel/VBoxContainer/Subcooling
@onready var phase_label = $UI/StatePanel/VBoxContainer/Phase
@onready var scenario_label = $UI/StatePanel/VBoxContainer/Scenario
@onready var faults_label = $UI/StatePanel/VBoxContainer/Faults

var current_state = {}
var target_pressure_angle = 0.0
var target_temp_angle = 0.0

func _ready():
	print("Mechanical Room initialized")
	# Initial data fetch
	_fetch_state()

func _process(delta):
	# Smooth needle animation
	pressure_needle.rotation.z = lerp(pressure_needle.rotation.z, target_pressure_angle, delta * 5)
	temp_needle.rotation.z = lerp(temp_needle.rotation.z, target_temp_angle, delta * 5)

func _on_timer_timeout():
	_fetch_state()

func _fetch_state():
	# Read state from JSON bridge (same mechanism as PT chart)
	var file = FileAccess.open("user://hvac_state.json", FileAccess.READ)
	if file:
		var json = JSON.new()
		var error = json.parse(file.get_as_text())
		file.close()
		
		if error == OK:
			current_state = json.get_data()
			_update_gauges()
			_update_ui()
		else:
			push_error("Failed to parse HVAC state JSON")

func _update_gauges():
	# Pressure gauge: 0-500 PSI mapped to -135 to +135 degrees
	var pressure_psi = current_state.get("pressure_psi", 0.0)
	target_pressure_angle = clamp(deg_to_rad((pressure_psi / 500.0) * 270.0 - 135.0), deg_to_rad(-135), deg_to_rad(135))
	
	# Temperature gauge: 0-150°F mapped to -135 to +135 degrees
	var temp_f = current_state.get("temperature_f", 0.0)
	target_temp_angle = clamp(deg_to_rad((temp_f / 150.0) * 270.0 - 135.0), deg_to_rad(-135), deg_to_rad(135))
	
	# Sight glass color based on phase
	var phase = current_state.get("phase", "unknown")
	match phase:
		"subcooled":
			sight_glass.material_override = _make_color_material(Color(0.2, 0.2, 0.8))  # Blue liquid
		"superheated":
			sight_glass.material_override = _make_color_material(Color(0.9, 0.9, 0.9))  # Clear gas
		"two-phase":
			sight_glass.material_override = _make_color_material(Color(0.5, 0.5, 0.9))  # Bubbly
		_:
			sight_glass.material_override = _make_color_material(Color(0.3, 0.3, 0.3))  # Dark

func _update_ui():
	refrigerant_label.text = "Refrigerant: %s" % current_state.get("refrigerant", "—")
	pressure_label.text = "Pressure: %.1f PSI" % current_state.get("pressure_psi", 0.0)
	temperature_label.text = "Temperature: %.1f °F" % current_state.get("temperature_f", 0.0)
	superheat_label.text = "Superheat: %.1f °F" % current_state.get("superheat_f", 0.0)
	subcooling_label.text = "Subcooling: %.1f °F" % current_state.get("subcooling_f", 0.0)
	phase_label.text = "Phase: %s" % current_state.get("phase", "—")
	scenario_label.text = "Scenario: %s" % current_state.get("scenario_id", "—")
	faults_label.text = "Faults: %s" % ", ".join(current_state.get("faults", []))

func _make_color_material(color: Color) -> StandardMaterial3D:
	var mat = StandardMaterial3D.new()
	mat.albedo_color = color
	mat.metallic = 0.3
	mat.roughness = 0.4
	return mat
