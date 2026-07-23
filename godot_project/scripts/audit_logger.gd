class_name AuditLogger
extends Node
## Glass-box audit trail with deterministic verification.
## FR-SV-007: Scene hashes and viewport signatures allow any outside AI
## to verify Godot state without screenshots.

var log_file: FileAccess
var log_path: String
var seq: int = 0

func _init():
	var dir = DirAccess.open("user://")
	if dir:
		dir.make_dir_recursive("oe_audit")
	log_path = "user://oe_audit/audit_%s.jsonl" % Time.get_datetime_string_from_system(false).replace(":", "-")
	log_file = FileAccess.open(log_path, FileAccess.WRITE)
	if log_file:
		print("[AuditLogger] audit trail: ", log_path)
	else:
		push_error("[AuditLogger] Cannot open: ", log_path)

func log_event(type: String, data: Dictionary) -> void:
	if not log_file:
		return
	seq += 1
	var entry = {
		"seq": seq,
		"timestamp": Time.get_datetime_string_from_system(true),
		"type": type,
		"data": data
	}
	log_file.store_line(JSON.stringify(entry))
	log_file.flush()

# ── Scene hash — deterministic fingerprint of entire scene tree ──────────────

func log_scene_hash(root: Node) -> void:
	var h = _hash_node_recursive(root)
	log_event("scene_hash", {"hash": h, "node_count": _count_nodes(root)})

func _hash_node_recursive(node: Node) -> String:
	var s = "%s:%s" % [node.name, node.transform]
	for child in node.get_children():
		s += _hash_node_recursive(child)
	return s.md5_text()

func _count_nodes(node: Node) -> int:
	var n = 1
	for child in node.get_children():
		n += _count_nodes(child)
	return n

# ── Viewport perceptual hash — compact fingerprint of rendered output ────────

func log_viewport_signature(vp: Viewport) -> void:
	var tex = vp.get_texture()
	if not tex:
		log_event("viewport_sig", {"phash": "0000000000000000", "error": "no texture"})
		return
	var img = tex.get_image()
	if not img:
		log_event("viewport_sig", {"phash": "0000000000000000", "error": "no image"})
		return
	var ph = _phash_image(img)
	log_event("viewport_sig", {
		"phash": ph,
		"size": [img.get_width(), img.get_height()]
	})

func _phash_image(img: Image) -> String:
	# Perceptual hash: resize to 8×8 grayscale, threshold at mean, pack bits
	var small = img.duplicate()
	small.resize(8, 8, Image.INTERPOLATE_LANCZOS)
	var total: float = 0.0
	for x in range(8):
		for y in range(8):
			total += small.get_pixel(x, y).get_luminance()
	var avg := total / 64.0
	var bits: int = 0
	var idx: int = 0
	for x in range(8):
		for y in range(8):
			if small.get_pixel(x, y).get_luminance() > avg:
				bits |= (1 << idx)
			idx += 1
	return "%016x" % bits

# ── Semantic log helpers ─────────────────────────────────────────────────────

func log_human_input(instruction: String) -> void:
	log_event("human_input", {"instruction": instruction})

func log_ai_thought(thought: String) -> void:
	log_event("ai_thought", {"thought": thought})

func log_mutation(tag: String, params: Dictionary) -> void:
	log_event("mutation", {"tag": tag, "params": params})

func log_covenant_check(rule: String, passed: bool, detail: String) -> void:
	log_event("covenant_check", {"rule": rule, "passed": passed, "detail": detail})

func log_viewport(png_path: String, scene_tree: Dictionary) -> void:
	log_event("viewport_capture", {"png_path": png_path, "scene_tree": scene_tree})

func get_entry_count() -> int:
	return seq

func get_log_path() -> String:
	return log_path
