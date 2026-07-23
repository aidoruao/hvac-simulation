extends Node
## DeepSeek API Key Configuration — Autoload
## Reads DEEPSEEK_API_KEY from environment and configures DeepSeekClient.
## FR-3D-006: AI-Native Engine bootstrap.

func _ready():
    var key = OS.get_environment("DEEPSEEK_API_KEY")
    if key and not key.is_empty():
        # Configure the global DeepSeek client
        var client = DeepSeekClient.new()
        client.set_api_key(key)
        add_child(client)
        print("[DeepSeekConfig] API key configured from environment (" + str(key.length()) + " chars)")
    else:
        push_warning("[DeepSeekConfig] DEEPSEEK_API_KEY not set in environment. AI features disabled.")
