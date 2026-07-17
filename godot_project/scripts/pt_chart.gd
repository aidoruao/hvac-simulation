extends Control

const PT_DATA_PATH := "res://pt_data.json"
const REFRIGERANT := "R410A"

var pt_data: Dictionary = {}
var points: Array = []

func _ready():
	print("HVAC PT Chart — Loading data...")
	load_pt_data()
	queue_redraw()

func load_pt_data():
	var file = FileAccess.open(PT_DATA_PATH, FileAccess.READ)
	if file:
		var json_text = file.get_as_text()
		file.close()
		
		var json = JSON.new()
		var error = json.parse(json_text)
		if error == OK:
			var all_data = json.data
			pt_data = all_data.get(REFRIGERANT, {})
			points = _zip_points(pt_data.get("temperature_c", []), pt_data.get("pressure_bar", []))
			print("Loaded ", points.size(), " PT points for ", REFRIGERANT)
		else:
			push_error("JSON parse failed")
	else:
		push_error("Could not open pt_data.json")

func _zip_points(temps: Array, pressures: Array) -> Array:
	var result := []
	for i in range(min(temps.size(), pressures.size())):
		result.append(Vector2(temps[i], pressures[i]))
	return result

func _draw():
	if points.is_empty():
		draw_string(ThemeDB.fallback_font, Vector2(100, 100), "No data loaded", HORIZONTAL_ALIGNMENT_LEFT)
		return
	
	var size = get_size()
	var margin = 60.0
	
	var min_t = -40.0
	var max_t = 60.0
	var min_p = 0.0
	var max_p = 30.0
	
	# Background
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.1, 0.1, 0.12))
	
	# Axes
	draw_line(Vector2(margin, size.y - margin), Vector2(size.x - margin, size.y - margin), Color.WHITE, 2)
	draw_line(Vector2(margin, margin), Vector2(margin, size.y - margin), Color.WHITE, 2)
	
	# Title
	draw_string(ThemeDB.fallback_font, Vector2(size.x / 2 - 150, 40), "R410A Pressure-Temperature Chart", HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color.WHITE)
	
	# Axis labels
	draw_string(ThemeDB.fallback_font, Vector2(size.x / 2 - 50, size.y - 15), "Temperature (°C)", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(15, size.y / 2), "Pressure (bar)", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.GRAY, 90)
	
	# PT curve
	for i in range(points.size() - 1):
		var p1 = _data_to_screen(points[i], min_t, max_t, min_p, max_p, size, margin)
		var p2 = _data_to_screen(points[i + 1], min_t, max_t, min_p, max_p, size, margin)
		draw_line(p1, p2, Color(0.18, 0.53, 0.67), 2)
	
	# Reference point at 25°C
	var ref_p = _get_pressure_at_temp(25.0)
	if ref_p > 0:
		var ref_screen = _data_to_screen(Vector2(25.0, ref_p), min_t, max_t, min_p, max_p, size, margin)
		draw_circle(ref_screen, 6, Color(0.29, 0.87, 0.31))
		draw_string(ThemeDB.fallback_font, ref_screen + Vector2(10, -10), "25°C", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.GREEN)

func _data_to_screen(point: Vector2, min_t, max_t, min_p, max_p, size, margin) -> Vector2:
	var x = margin + (point.x - min_t) / (max_t - min_t) * (size.x - 2 * margin)
	var y = size.y - margin - (point.y - min_p) / (max_p - min_p) * (size.y - 2 * margin)
	return Vector2(x, y)

func _get_pressure_at_temp(target_temp: float) -> float:
	var temps = pt_data.get("temperature_c", [])
	var pressures = pt_data.get("pressure_bar", [])
	for i in range(temps.size()):
		if abs(temps[i] - target_temp) < 0.5:
			return pressures[i]
	return 0.0
