extends SceneTree

## FR-PF-002: Frame Rate Benchmark
## Measures FPS for PT chart and mechanical room scenes
## Run headless: godot --headless --script scripts/frame_rate_benchmark.gd

const BENCHMARK_DURATION_SEC := 5.0
const TARGET_FPS := 60.0
const RESULTS_PATH := "user://benchmark_results.json"

var scene_paths := [
	"res://scenes/pt_chart.tscn",
	"res://scenes/mechanical_room/mechanical_room.tscn"
]

var bench_results := []
var current_scene_index := 0
var loaded_scene: Node
var fps_samples: Array = []
var timer: float = 0.0

func _initialize():
	print("FR-PF-002: Frame Rate Benchmark starting...")
	print("Target FPS: ", TARGET_FPS)
	print("Duration per scene: ", BENCHMARK_DURATION_SEC, "s")
	print("---")
	_load_next_scene()

func _load_next_scene():
	if current_scene_index >= scene_paths.size():
		_write_results()
		quit()
		return

	var path = scene_paths[current_scene_index]
	print("Loading scene: ", path)

	var packed = load(path)
	if packed == null:
		push_error("Failed to load scene: " + path)
		bench_results.append({
			"scene": path,
			"error": "Failed to load scene",
			"pass": false
		})
		current_scene_index += 1
		_load_next_scene()
		return

	loaded_scene = packed.instantiate()
	root.add_child(loaded_scene)
	fps_samples.clear()
	timer = 0.0
	print("Scene loaded. Benchmarking...")

func _process(delta):
	timer += delta
	var fps = Engine.get_frames_per_second()
	fps_samples.append(fps)
	if timer >= BENCHMARK_DURATION_SEC:
		_finish_current_scene()

func _finish_current_scene():
	var path = scene_paths[current_scene_index]
	var avg_fps = _average(fps_samples)
	var min_fps = fps_samples.min() if fps_samples.size() > 0 else 0.0
	var max_fps = fps_samples.max() if fps_samples.size() > 0 else 0.0
	var passed: bool = avg_fps >= TARGET_FPS

	bench_results.append({
		"scene": path,
		"avg_fps": snapped(avg_fps, 0.01),
		"min_fps": snapped(min_fps, 0.01),
		"max_fps": snapped(max_fps, 0.01),
		"samples": fps_samples.size(),
		"target_fps": TARGET_FPS,
		"pass": passed
	})

	print("  Avg FPS: ", snapped(avg_fps, 0.01))
	print("  Min FPS: ", snapped(min_fps, 0.01))
	print("  Max FPS: ", snapped(max_fps, 0.01))
	print("  Samples: ", fps_samples.size())
	print("  PASS: ", passed)
	print("---")

	if loaded_scene:
		loaded_scene.queue_free()
		loaded_scene = null

	current_scene_index += 1
	_load_next_scene()

func _average(arr: Array) -> float:
	if arr.is_empty():
		return 0.0
	var sum := 0.0
	for v in arr:
		sum += v
	return sum / arr.size()

func _write_results():
	var output := {
		"benchmark": "FR-PF-002",
		"godot_version": Engine.get_version_info()["string"],
		"date": Time.get_datetime_string_from_system(),
		"target_fps": TARGET_FPS,
		"duration_per_scene": BENCHMARK_DURATION_SEC,
		"overall_pass": bench_results.all(func(r): return r.get("pass", false)),
		"results": bench_results
	}

	var file = FileAccess.open(RESULTS_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(output, "	"))
		file.close()
		print("Results written to: ", RESULTS_PATH)
	else:
		push_error("Failed to write results")

	print("=== BENCHMARK COMPLETE ===")
	for r in bench_results:
		var status := "PASS" if r.get("pass", false) else "FAIL"
		print(status, " | ", r["scene"], " | Avg: ", r["avg_fps"], " FPS")
