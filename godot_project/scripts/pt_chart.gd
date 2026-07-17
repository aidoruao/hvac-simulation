extends Control

const PT_DATA_PATH := "res://pt_data.json"

var pt_data: Dictionary = {}
var all_refrigerants: Array = []
var current_refrigerant: String = "R410A"
var points: Array = []

# UI references
@onready var dropdown: OptionButton = $RefrigerantDropdown
@onready var readout: Label = $ReadoutLabel

func _ready():
	print("HVAC PT Chart — Loading data...")
	load_all_data()
	setup_dropdown()
	switch_refrigerant("R410A")

func load_all_data():
	var file = FileAccess.open(PT_DATA_PATH, FileAccess.READ)
	if file:
		var json_text = file.get_as_text()
		file.close()
		
		var json = JSON.new()
		var error = json.parse(json_text)
		if error == OK:
			pt_data = json.data
			all_refrigerants = pt_data.keys()
			print("Loaded ", all_refrigerants.size(), " refrigerants: ", all_refrigerants)
		else:
			push_error("JSON parse failed")
	else:
		push_error("Could not open pt_data.json")

func setup_dropdown():
	dropdown.clear()
	for r in all_refrigerants:
		dropdown.add_item(r)
	
	# Set default
	for i in range(dropdown.item_count):
		if dropdown.get_item_text(i) == current_refrigerant:
			dropdown.select(i)
			break
	
	dropdown.item_selected.connect(_on_refrigerant_changed)

func _on_refrigerant_changed(index: int):
	var selected = dropdown.get_item_text(index)
	switch_refrigerant(selected)

func switch_refrigerant(name: String):
	current_refrigerant = name
	var r_data = pt_data.get(name, {})
	points = _zip_points(r_data.get("temperature_c", []), r_data.get("pressure_bar", []))
	readout.text = "Refrigerant: " + name + "\nClick on curve to read values"
	queue_redraw()

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
	var margin = 80.0
	
	var min_t = -40.0
	var max_t = 60.0
	var min_p = 0.0
	var max_p = _get_max_pressure() * 1.1
	
	# Background
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.1, 0.1, 0.12))
	
	# Grid lines
	for t in range(-40, 61, 20):
		var x = _data_to_screen(Vector2(t, 0), min_t, max_t, min_p, max_p, size, margin).x
		draw_line(Vector2(x, margin), Vector2(x, size.y - margin), Color(0.2, 0.2, 0.2), 1)
		draw_string(ThemeDB.fallback_font, Vector2(x - 10, size.y - margin + 20), str(t), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.GRAY)
	
	# Axes
	draw_line(Vector2(margin, size.y - margin), Vector2(size.x - margin, size.y - margin), Color.WHITE, 2)
	draw_line(Vector2(margin, margin), Vector2(margin, size.y - margin), Color.WHITE, 2)
	
	# Axis labels
	draw_string(ThemeDB.fallback_font, Vector2(size.x / 2 - 60, size.y - 10), "Temperature (°C)", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.GRAY)
	draw_string(ThemeDB.fallback_font, Vector2(20, size.y / 2), "Pressure (bar)", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, Color.GRAY, 90)
	
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
		draw_string(ThemeDB.fallback_font, ref_screen + Vector2(10, -10), "25°C: " + str(snapped(ref_p, 0.01)) + " bar", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color.GREEN)

func _data_to_screen(point: Vector2, min_t, max_t, min_p, max_p, size, margin) -> Vector2:
	var x = margin + (point.x - min_t) / (max_t - min_t) * (size.x - 2 * margin)
	var y = size.y - margin - (point.y - min_p) / (max_p - min_p) * (size.y - 2 * margin)
	return Vector2(x, y)

func _screen_to_data(screen_pos: Vector2, min_t, max_t, min_p, max_p, size, margin) -> Vector2:
	var x = min_t + (screen_pos.x - margin) / (size.x - 2 * margin) * (max_t - min_t)
	var y = min_p + (size.y - margin - screen_pos.y) / (size.y - 2 * margin) * (max_p - min_p)
	return Vector2(x, y)

func _get_max_pressure() -> float:
	var max_p = 0.0
	for p in points:
		if p.y > max_p:
			max_p = p.y
	return max_p

func _get_pressure_at_temp(target_temp: float) -> float:
	var temps = pt_data.get(current_refrigerant, {}).get("temperature_c", [])
	var pressures = pt_data.get(current_refrigerant, {}).get("pressure_bar", [])
	for i in range(temps.size()):
		if abs(temps[i] - target_temp) < 0.5:
			return pressures[i]
	return 0.0

func _get_pressure_at_screen_x(screen_x: float) -> float:
	var size = get_size()
	var margin = 80.0
	var min_t = -40.0
	var max_t = 60.0
	var min_p = 0.0
	var max_p = _get_max_pressure() * 1.1
	
	var data_pos = _screen_to_data(Vector2(screen_x, 0), min_t, max_t, min_p, max_p, size, margin)
	var target_temp = data_pos.x
	
	# Find closest point
	var closest_idx = 0
	var closest_dist = 999.0
	var temps = pt_data.get(current_refrigerant, {}).get("temperature_c", [])
	
	for i in range(temps.size()):
		var dist = abs(temps[i] - target_temp)
		if dist < closest_dist:
			closest_dist = dist
			closest_idx = i
	
	var pressures = pt_data.get(current_refrigerant, {}).get("pressure_bar", [])
	return pressures[closest_idx]

func _gui_input(event):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var screen_x = event.position.x
		var size = get_size()
		var margin = 80.0
		
		if screen_x < margin or screen_x > size.x - margin:
			return
		
		var temp = _screen_to_data(Vector2(screen_x, 0), -40, 60, 0, _get_max_pressure() * 1.1, size, margin).x
		var pressure = _get_pressure_at_screen_x(screen_x)
		
		readout.text = "Refrigerant: " + current_refrigerant + "\n"
		readout.text += "Temperature: " + str(snapped(temp, 0.1)) + "°C\n"
		readout.text += "Pressure: " + str(snapped(pressure, 0.01)) + " bar\n"
		readout.text += "Saturation: " + ("YES" if pressure > 0 else "NO")
		
		queue_redraw()
