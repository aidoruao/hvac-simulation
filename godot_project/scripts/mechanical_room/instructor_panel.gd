extends Control

## FR-ED-007: Interactive fault injection instructor panel and student diagnosis UI.
## Attached programmatically by mechanical_room.gd.

# Fault definitions (synced with mechanical_room_bridge.py FAULTS dict)
const FAULTS: Array[Dictionary] = [
	{ "id": "low_refrigerant", "name": "Low Refrigerant", "desc": "Charge below spec" },
	{ "id": "overcharge", "name": "Overcharge", "desc": "Excess refrigerant" },
	{ "id": "undercharge", "name": "Undercharge", "desc": "Low charge, high SH" },
	{ "id": "dirty_condenser", "name": "Dirty Condenser", "desc": "High head pressure" },
	{ "id": "bad_condenser_fan", "name": "Condenser Fan Fail", "desc": "Overheating condenser" },
	{ "id": "non_condensables", "name": "Non-Condensables", "desc": "Air in system" },
	{ "id": "restriction", "name": "Restriction", "desc": "Blocked line" },
	{ "id": "bad_txv", "name": "Bad TXV", "desc": "Valve hunting" },
	{ "id": "bad_expansion_valve", "name": "Failed TXV", "desc": "Stuck expansion valve" },
	{ "id": "dirty_evaporator", "name": "Dirty Evaporator", "desc": "Low suction" },
	{ "id": "compressor_failure", "name": "Compressor Failure", "desc": "No flow" },
	{ "id": "bad_compressor_valves", "name": "Bad Valves", "desc": "Low compression" },
	{ "id": "refrigerant_mix", "name": "Mixed Refrigerants", "desc": "Contaminated" },
	{ "id": "r22_contamination", "name": "R22 Contamination", "desc": "Wrong refrigerant" },
	{ "id": "low_ambient_no_kit", "name": "Low Ambient", "desc": "No cold-weather kit" },
	{ "id": "overcharge_and_noncond", "name": "Overcharge + NCG", "desc": "Multiple issues" },
	{ "id": "retrofit_verification", "name": "R32 Retrofit", "desc": "Post-conversion check" },
	{ "id": "a2l_leak", "name": "A2L Leak", "desc": "Flammable leak" },
	{ "id": "capillary_blockage", "name": "Capillary Block", "desc": "Metering device clog" },
	{ "id": "head_pressure_failure", "name": "Head Pressure Fail", "desc": "Control failure" },
	{ "id": "reversing_valve_stuck", "name": "Reversing Valve", "desc": "Stuck mid-cycle" },
	{ "id": "suction_uninsulated", "name": "Bare Suction Line", "desc": "Heat gain" },
	{ "id": "liquid_line_restriction", "name": "Liquid Restriction", "desc": "Low subcooling" },
]

# UI state
var active_fault_id := ""
var score := 0
var hints_used := 0
var time_left := 30
var timer_active := false
var diagnosis_options := ["Low Refrigerant", "Dirty Condenser", "Bad Expansion Valve", "Compressor Failure"]

# Node references
var fault_scroll: ScrollContainer
var fault_grid: GridContainer
var student_panel: Panel
var diagnosis_buttons: Array[Button] = []
var submit_button: Button
var feedback_label: Label
var score_label: Label
var timer_label: Label

func _ready():
	setup_instructor_panel()
	setup_student_panel()
	start_new_round()

func setup_instructor_panel():
	fault_scroll = ScrollContainer.new()
	fault_scroll.name = "FaultScroll"
	fault_scroll.size = Vector2(250, 500)
	fault_scroll.position = Vector2(10, 60)

	fault_grid = GridContainer.new()
	fault_grid.name = "FaultGrid"
	fault_grid.columns = 1
	fault_scroll.add_child(fault_grid)

	for fault in FAULTS:
		var btn = Button.new()
		btn.text = "%s\n%s" % [fault["name"], fault["desc"]]
		btn.custom_minimum_size = Vector2(230, 40)
		btn.pressed.connect(_on_fault_selected.bind(fault["id"]))
		fault_grid.add_child(btn)

	add_child(fault_scroll)

func setup_student_panel():
	student_panel = Panel.new()
	student_panel.name = "StudentPanel"
	student_panel.size = Vector2(300, 250)
	student_panel.position = Vector2(280, 400)

	var vbox = VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_theme_constant_override("separation", 8)
	student_panel.add_child(vbox)

	# Score and timer
	score_label = Label.new()
	score_label.text = "Score: 100"
	vbox.add_child(score_label)

	timer_label = Label.new()
	timer_label.text = "Time: 30s"
	vbox.add_child(timer_label)

	# Diagnosis options
	var diag_label = Label.new()
	diag_label.text = "Diagnosis:"
	vbox.add_child(diag_label)

	for opt in diagnosis_options:
		var btn = Button.new()
		btn.text = opt
		btn.pressed.connect(_on_diagnosis_selected.bind(opt))
		vbox.add_child(btn)

	# Submit
	submit_button = Button.new()
	submit_button.text = "Submit Answer"
	submit_button.pressed.connect(_on_submit)
	vbox.add_child(submit_button)

	# Feedback
	feedback_label = Label.new()
	feedback_label.text = ""
	vbox.add_child(feedback_label)

	add_child(student_panel)

func start_new_round():
	active_fault_id = ""
	score = 100
	hints_used = 0
	time_left = 30
	timer_active = false
	feedback_label.text = "Select a fault to begin"
	score_label.text = "Score: %d" % score
	timer_label.text = "Time: %ds" % time_left

func _on_fault_selected(fault_id: String):
	active_fault_id = fault_id
	time_left = 30
	timer_active = true
	score = 100
	hints_used = 0
	feedback_label.text = "Fault injected: %s" % fault_id
	score_label.text = "Score: %d" % score

	# Signal to mechanical_room to inject fault
	get_parent().inject_fault_from_ui(fault_id)

func _on_diagnosis_selected(answer: String):
	# Deselect other buttons
	for btn in diagnosis_buttons:
		btn.button_pressed = false

func _on_submit():
	if active_fault_id == "":
		return
	timer_active = false

	# Simple scoring: correct fault substring match
	var correct := false
	for btn in diagnosis_buttons:
		if btn.button_pressed:
			if btn.text.to_lower().replace(" ", "_").find(active_fault_id) >= 0 or active_fault_id.find(btn.text.to_lower().replace(" ", "_")) >= 0:
				correct = true
			break

	score = max(0, 100 - hints_used * 20)
	if not correct:
		score = 0

	feedback_label.text = "✓ CORRECT! Score: %d" % score if correct else "✗ Incorrect. Answer: %s" % active_fault_id
	score_label.text = "Score: %d" % score
	get_parent().clear_fault_from_ui()

func _process(delta):
	if timer_active:
		time_left -= delta
		if time_left <= 0:
			time_left = 0
			timer_active = false
			feedback_label.text = "TIME UP!"
		timer_label.text = "Time: %.0fs" % max(0, time_left)
