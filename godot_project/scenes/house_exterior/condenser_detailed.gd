extends Node3D
## FR-3D-003: Production-grade condenser with animated fan and PBR materials.

var fan: MeshInstance3D
var fan_speed: float = 1.0

func _ready():
	# ── Body: steel shell with metallic material ──────────────────────
	var body = MeshInstance3D.new()
	body.name = "Body"
	body.mesh = BoxMesh.new()
	body.mesh.size = Vector3(0.8, 0.8, 0.6)
	var steel = StandardMaterial3D.new()
	steel.albedo_color = Color(0.85, 0.85, 0.9)
	steel.metallic = 0.3
	steel.roughness = 0.4
	body.material_override = steel
	add_child(body)

	# ── Coil fins: thin horizontal slats ──────────────────────────────
	for i in range(4):
		var fin = MeshInstance3D.new()
		fin.name = "Fin_%d" % i
		fin.mesh = BoxMesh.new()
		fin.mesh.size = Vector3(0.75, 0.02, 0.55)
		var alum = StandardMaterial3D.new()
		alum.albedo_color = Color(0.75, 0.78, 0.82)
		alum.metallic = 0.7
		alum.roughness = 0.3
		fin.material_override = alum
		fin.position = Vector3(0, -0.3 + i * 0.2, 0.05)
		add_child(fin)

	# ── Fan: spinning grill with noise texture ────────────────────────
	fan = MeshInstance3D.new()
	fan.name = "Fan"
	fan.mesh = CylinderMesh.new()
	fan.mesh.top_radius = 0.35
	fan.mesh.bottom_radius = 0.35
	fan.mesh.height = 0.05
	var fan_mat = StandardMaterial3D.new()
	var tex = load("res://assets/textures/fan_grill_noise.png")
	if tex:
		fan_mat.albedo_texture = tex
	fan_mat.albedo_color = Color(0.2, 0.2, 0.22)
	fan_mat.metallic = 0.5
	fan_mat.roughness = 0.6
	fan.material_override = fan_mat
	fan.position = Vector3(0, 0.42, 0)
	add_child(fan)

	# ── Fan guard: wireframe grille ───────────────────────────────────
	var guard = MeshInstance3D.new()
	guard.name = "FanGuard"
	guard.mesh = CylinderMesh.new()
	guard.mesh.top_radius = 0.38
	guard.mesh.bottom_radius = 0.38
	guard.mesh.height = 0.02
	var guard_mat = StandardMaterial3D.new()
	guard_mat.albedo_color = Color(0.15, 0.15, 0.18)
	guard_mat.metallic = 0.8
	guard_mat.roughness = 0.2
	guard.material_override = guard_mat
	guard.position = Vector3(0, 0.45, 0)
	add_child(guard)

	# ── Labels ────────────────────────────────────────────────────────
	var label = Label3D.new()
	label.name = "BrandLabel"
	label.text = "HVAC-SIM"
	label.position = Vector3(0, 0, 0.35)
	label.modulate = Color(0.3, 0.3, 0.3)
	label.font_size = 32
	add_child(label)

	# ── Animate fan ───────────────────────────────────────────────────
	var tween = create_tween().set_loops()
	tween.tween_property(fan, "rotation:y", TAU, 1.0 / fan_speed)

	print("[CondenserDetailed] Body + 4 fins + animated fan + guard + label")
