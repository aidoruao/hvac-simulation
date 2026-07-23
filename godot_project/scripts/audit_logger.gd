extends Node
class_name AuditLogger
## Structured JSON audit trail for AI-human collaboration.
## Output: user://oe_audit/YYYY-MM-DD_HH-MM-SS.jsonl (JSON Lines format)
## FR-SV-005 compliant: no hidden state, every mutation traceable.

var _file: FileAccess
var _path: String
var _entry_count: int = 0

func _init():
    var dir = DirAccess.open("user://")
    if dir:
        dir.make_dir_recursive("oe_audit")
    var ts = Time.get_datetime_string_from_system(false).replace(":", "-")
    _path = "user://oe_audit/audit_" + ts + ".jsonl"
    _file = FileAccess.open(_path, FileAccess.WRITE)
    if _file:
        print("[AuditLogger] audit trail: " + _path)
    else:
        push_error("[AuditLogger] cannot open: " + _path)

func log_event(type: String, data: Dictionary) -> void:
    if not _file:
        return
    _entry_count += 1
    var entry = {
        "seq": _entry_count,
        "timestamp": Time.get_datetime_string_from_system(true),
        "type": type,
        "data": data
    }
    _file.store_line(JSON.stringify(entry))
    _file.flush()

func log_human_input(instruction: String) -> void:
    log_event("human_input", {"instruction": instruction})

func log_ai_thought(thought: String) -> void:
    log_event("ai_thought", {"thought": thought})

func log_mutation(tag: String, params: Dictionary) -> void:
    log_event("mutation", {"tag": tag, "params": params})

func log_viewport(png_path: String, scene_tree: Dictionary) -> void:
    log_event("viewport_capture", {"png_path": png_path, "scene_tree": scene_tree})

func log_covenant_check(rule_id: String, passed: bool, detail: String) -> void:
    log_event("covenant_check", {"rule": rule_id, "passed": passed, "detail": detail})

func get_entry_count() -> int:
    return _entry_count

func get_log_path() -> String:
    return _path
