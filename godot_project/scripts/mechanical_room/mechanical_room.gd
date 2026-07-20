extends Node3D

## Mechanical Room — 3D visualization with animated compressor and fan
## FR-3D-002: Animated compressor/gauge models

@onready var pressure_needle = $Gauges/PressureGauge/Needle
@onready var temp_needle = $Gauges/TempGauge/Needle
@onready var sight_glass = $Gauges/SightGlass/Body

@onready var compressor_pulley = $Compressor/Pulley
@onready var motor_pulley = $Compressor/MotorPulley
@onready var condenser_fan = $CondenserFan

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

# Animation state
var compressor_rpm := 0.0
var fan_rpm := 0.0
var compressor_angle := 0.0
var fan_angle := 0.0

@onready var flow_system = $RefrigerantFlow if has_node("RefrigerantFlow") else null

func _ready():
	print("Mechanical Room initialized (FR-3D-002 + FR-AN-001)")
	if not flow_system:
		# Instantiate flow system dynamically
		var flow_script = load("res://scripts/mechanical_room/refrigerant_flow.gd")
		flow_system = Node3D.new()
		flow_system.name = "RefrigerantFlow"
		flow_system.set_script(flow_script)
		add_child(flow_system)
	_fetch_state()

func _process(delta):
	# Smooth needle animation
	pressure_needle.rotation.z = lerp(pressure_needle.rotation.z, target_pressure_angle, delta * 5)
	temp_needle.rotation.z = lerp(temp_needle.rotation.z, target_temp_angle, delta * 5)

	# Compressor animation (RPM from system state)
	if compressor_rpm > 0:
		compressor_angle += compressor_rpm * delta * 0.1047
		compressor_pulley.rotation.x = compressor_angle
		motor_pulley.rotation.x = compressor_angle * 1.75

	# Condenser fan animation
	if fan_rpm > 0:
		fan_angle += fan_rpm * delta * 0.1047
		condenser_fan.rotation.y = fan_angle

func _on_timer_timeout():
	_fetch_state()

func _fetch_state():
	var file = FileAccess.open("user://hvac_state.json", FileAccess.READ)
	if file:
		var json = JSON.new()
		var error = json.parse(file.get_as_text())
		file.close()

		if error == OK:
			current_state = json.get_data()
			_update_gauges()
			_update_ui()
			_update_animation_state()
		else:
			push_error("Failed to parse HVAC state JSON")

func _update_gauges():
	var pressure_psi = current_state.get("pressure_psi", 0.0)
	target_pressure_angle = clamp(deg_to_rad((pressure_psi / 500.0) * 270.0 - 135.0), deg_to_rad(-135), deg_to_rad(135))

	var temp_f = current_state.get("temperature_f", 0.0)
	target_temp_angle = clamp(deg_to_rad((temp_f / 150.0) * 270.0 - 135.0), deg_to_rad(-135), deg_to_rad(135))

	var phase = current_state.get("phase", "unknown")
	match phase:
		"subcooled":
			sight_glass.material_override = _make_color_material(Color(0.2, 0.2, 0.8))
		"superheated":
			sight_glass.material_override = _make_color_material(Color(0.9, 0.9, 0.9))
		"two-phase":
			sight_glass.material_override = _make_color_material(Color(0.5, 0.5, 0.9))
		_:
			sight_glass.material_override = _make_color_material(Color(0.3, 0.3, 0.3))

func _update_animation_state():
	var system_on = current_state.get("compressor_running", false)
	var load_percent = current_state.get("load_percent", 0.0)

	if system_on:
		compressor_rpm = 1800.0 * (load_percent / 100.0)
		fan_rpm = 1200.0 * (load_percent / 100.0)
	else:
		compressor_rpm = 0.0
		fan_rpm = 0.0

	# FR-AN-001: update refrigerant flow particles
	if flow_system and flow_system.has_method("update_from_state"):
		flow_system.update_from_state(current_state)

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
