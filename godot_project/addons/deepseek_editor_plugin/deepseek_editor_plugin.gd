@tool
extends EditorPlugin

var client: DeepSeekClient
var chat: DeepSeekChat

func _enter_tree():
    print("[DeepSeekEditorPlugin] Injecting API key...")
    var env_key = OS.get_environment("DEEPSEEK_API_KEY")
    if env_key.is_empty():
        push_warning("[DeepSeekEditorPlugin] DEEPSEEK_API_KEY not set")
        return
    client = DeepSeekClient.new()
    client.set_api_key(env_key)
    chat = DeepSeekChat.new(env_key)
    set_meta("deepseek_client", client)
    set_meta("deepseek_chat", chat)
    print("[DeepSeekEditorPlugin] API key injected (", env_key.length(), " chars)")

func _exit_tree():
    if client:
        client.free()
        client = null
    if chat:
        chat.free()
        chat = null
