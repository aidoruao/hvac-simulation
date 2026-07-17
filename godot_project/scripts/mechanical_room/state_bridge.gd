extends Node

## State Bridge — writes HVAC state to JSON for Godot consumption
## Runs in Python backend, same pattern as PT chart bridge

const STATE_FILE = "user://hvac_state.json"

func write_state(state_data: Dictionary):
	var file = FileAccess.open(STATE_FILE, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(state_data))
		file.close()
	else:
		push_error("Failed to write HVAC state file")

func read_state() -> Dictionary:
	var file = FileAccess.open(STATE_FILE, FileAccess.READ)
	if file:
		var json = JSON.new()
		var error = json.parse(file.get_as_text())
		file.close()
		if error == OK:
			return json.get_data()
	return {}
