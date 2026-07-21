extends Node3D

## FR-AN-001: Aerospace-grade refrigerant flow particle visualization.
##
## Particle system visualizes refrigerant flow through the four main
## cycle components.  Particle count, speed, and color respond to
## thermodynamic state.
##
## Attach to the MechanicalRoom scene root.

# Particle material presets
const MAT_LIQUID = preload("res://materials/liquid_particle.tres") if ResourceLoader.exists("res://materials/liquid_particle.tres") else null
const MAT_VAPOR = preload("res://materials/vapor_particle.tres") if ResourceLoader.exists("res://materials/vapor_particle.tres") else null
const MAT_TWOPHASE = preload("res://materials/twophase_particle.tres") if ResourceLoader.exists("res://materials/twophase_particle.tres") else null

# Component bounding boxes (set in _ready from scene node positions)
var compressor_box: AABB
var condenser_box: AABB
var expansion_box: AABB
var evaporator_box: AABB

# FR-ED-008: mobile detection for adaptive rendering
var is_mobile := false

# Flow parameters (updated from state)
var mass_flow: float = 0.0        # kg/s
var high_pressure: float = 1.0    # bar
var low_pressure: float = 1.0     # bar
var phase: String = "unknown"
var system_on: bool = false

# Particle system references
var particles_compressor: GPUParticles3D
var particles_condenser: GPUParticles3D
var particles_expansion: GPUParticles3D
var particles_evaporator: GPUParticles3D

# Colors
var color_liquid := Color(0.2, 0.3, 0.9, 0.8)
var color_vapor  := Color(0.95, 0.95, 0.95, 0.6)
var color_two    := Color(0.5, 0.6, 0.95, 0.7)

func _ready():
	print("FR-AN-001 Refrigerant Flow initialized")
	# FR-ED-008: mobile detection
	is_mobile = OS.get_name() in ["Android", "iOS"] or OS.has_feature("mobile")
	_setup_particles()
	_estimate_boxes()

func _setup_particles():
	# Create particle systems for each component
	particles_compressor = _make_particle_system("CompressorFlow", color_vapor)
	particles_condenser  = _make_particle_system("CondenserFlow", color_vapor)
	particles_expansion  = _make_particle_system("ExpansionFlow", color_two)
	particles_evaporator = _make_particle_system("EvaporatorFlow", color_two)

func _make_particle_system(name: String, default_color: Color) -> GPUParticles3D:
	var ps = GPUParticles3D.new()
	ps.name = name
	ps.amount = 50 if is_mobile else 100  # FR-ED-008: mobile LOD
	ps.lifetime = 1.0 if is_mobile else 1.5
	ps.explosiveness = 0.0
	ps.randomness = 0.3
	ps.emitting = false
	ps.one_shot = false
	ps.speed_scale = 1.0

	# Process material
	var mat = ParticleProcessMaterial.new()
	mat.direction = Vector3(1, 0, 0)
	mat.spread = 30.0
	mat.gravity = Vector3(0, -0.5, 0)
	mat.initial_velocity_min = 2.0
	mat.initial_velocity_max = 5.0
	mat.scale_min = 0.1
	mat.scale_max = 0.3
	mat.color = default_color
	mat.color_ramp = _make_color_ramp(default_color)
	ps.process_material = mat

	# Draw pass — sphere mesh
	var mesh = SphereMesh.new()
	mesh.radius = 0.05
	mesh.height = 0.1
	ps.draw_pass_1 = mesh

	add_child(ps)
	return ps

func _make_color_ramp(base_color: Color) -> GradientTexture1D:
	var grad = Gradient.new()
	grad.set_color(0, Color(base_color.r, base_color.g, base_color.b, 1.0))
	grad.set_color(1, Color(base_color.r, base_color.g, base_color.b, 0.0))
	var tex = GradientTexture1D.new()
	tex.gradient = grad
	return tex

func _estimate_boxes():
	# Estimate component positions from known scene layout.
	# These will be refined once the scene is instantiated.
	var root = get_parent()
	if root:
		# Compressor: lower-left quadrant
		compressor_box = AABB(Vector3(-2, 0, -2), Vector3(1, 1.5, 1))
		# Condenser: upper-right
		condenser_box = AABB(Vector3(1, 0.5, 1), Vector3(2, 1, 2))
		# Expansion: between condenser and evaporator
		expansion_box = AABB(Vector3(0, 0, 1), Vector3(0.5, 0.5, 0.5))
		# Evaporator: lower-right
		evaporator_box = AABB(Vector3(1, 0, -1), Vector3(2, 1, 1))

func update_from_state(state: Dictionary):
	system_on = state.get("compressor_running", false)
	phase = state.get("phase", "unknown")
	high_pressure = state.get("pressure_bar", 1.0)
	low_pressure = state.get("pressure_bar", 1.0)
	mass_flow = state.get("mass_flow", 0.0)

	# FR-ED-005: fault-aware particle behavior
	# Compressor failure → stop all particles immediately
	if not system_on:
		particles_compressor.emitting = false
		particles_condenser.emitting = false
		particles_expansion.emitting = false
		particles_evaporator.emitting = false
		return

	# Low refrigerant → reduced emission
	var emit := mass_flow > 0.001
	particles_compressor.emitting = emit
	particles_condenser.emitting = emit
	particles_expansion.emitting = emit
	particles_evaporator.emitting = emit

	if not emit:
		return

	# Speed scale proportional to mass flow
	var speed = clamp(mass_flow * 50.0, 0.5, 5.0)
	particles_compressor.speed_scale = speed
	particles_condenser.speed_scale = speed * 0.8
	particles_expansion.speed_scale = speed * 0.5
	particles_evaporator.speed_scale = speed * 0.6

	# Color by phase
	var color: Color
	match phase:
		"subcooled":
			color = color_liquid
		"superheated":
			color = color_vapor
		"two-phase":
			color = color_two
		_:
			color = Color.GRAY

	# Update particle materials
	_update_particle_color(particles_compressor, color_vapor)   # discharge = hot vapor
	_update_particle_color(particles_condenser, color_liquid)    # condensing → liquid
	_update_particle_color(particles_expansion, color_two)       # expansion = two-phase
	_update_particle_color(particles_evaporator, color_vapor)    # evaporating → vapor

	# Amount proportional to mass flow
	var max_count = 50 if is_mobile else 250  # FR-ED-008: mobile LOD
	var count = clamp(int(mass_flow * 500), 10, max_count)
	particles_compressor.amount = count
	particles_condenser.amount = int(count * 0.8)
	particles_expansion.amount = int(count * 0.6)
	particles_evaporator.amount = int(count * 0.7)

func _update_particle_color(ps: GPUParticles3D, color: Color):
	if ps and ps.process_material is ParticleProcessMaterial:
		ps.process_material.color = color
