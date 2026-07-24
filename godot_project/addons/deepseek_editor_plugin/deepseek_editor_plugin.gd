@tool
extends EditorPlugin

var client: DeepSeekClient
var chat: DeepSeekChat
var audit: AuditLogger
var poll_timer: Timer
var _last_phash: String = ""
var _frame_count: int = 0

func _enter_tree():
    print("[DeepSeekEditorPlugin] Injecting API key...")
    var env_key = OS.get_environment("DEEPSEEK_API_KEY")
    if env_key.is_empty():
        push_warning("[DeepSeekEditorPlugin] DEEPSEEK_API_KEY not set")
        return
    client = DeepSeekClient.new()
    client.set_api_key(env_key)
    chat = DeepSeekChat.new(env_key)
    audit = AuditLogger.new()
    set_meta("deepseek_client", client)
    set_meta("deepseek_chat", chat)
    set_meta("audit_logger", audit)
    print("[DeepSeekEditorPlugin] API key injected (", env_key.length(), " chars)")

    # Log initial scene state
    var root = get_editor_interface().get_edited_scene_root()
    if root:
        audit.log_scene_hash(root)

    # Start periodic audit polling — captures viewport and scene state
    # every 2 seconds while editor is running
    poll_timer = Timer.new()
    poll_timer.wait_time = 2.0
    poll_timer.timeout.connect(_poll_dock)
    add_child(poll_timer)
    poll_timer.start()
    print("[DeepSeekEditorPlugin] Audit poll timer started (2s interval)")

func _poll_dock() -> void:
    _frame_count += 1
    # Only log every 30 frames (~60s) to avoid flooding
    if _frame_count % 30 != 0:
        return

    # Capture viewport from the actual editor 3D viewport
    var vp = get_editor_interface().get_editor_viewport_3d(0)
    if not vp:
        return

    audit.log_viewport_signature(vp)

    # Also log scene hash if a scene is open
    var root = get_editor_interface().get_edited_scene_root()
    if root:
        audit.log_scene_hash(root)
        print("[DeepSeekEditorPlugin] Poll: node_count=", root.get_child_count(true),
              " audit_seq=", audit.get_entry_count())

func _exit_tree():
    if poll_timer:
        poll_timer.stop()
        poll_timer.queue_free()
    if client: client.free(); client = null
    if chat: chat.free(); chat = null
    if audit: audit.free(); audit = null
