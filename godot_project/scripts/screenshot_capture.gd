extends Node

var target_scene_path: String = ""
var output_path: String = ""
var viewport_size: Vector2i = Vector2i(1920, 1080)

func _ready():
    for arg in OS.get_cmdline_args():
        if arg.begins_with("--scene="):
            target_scene_path = arg.split("=", false, 1)[1]
        elif arg.begins_with("--output="):
            output_path = arg.split("=", false, 1)[1]

    if target_scene_path.is_empty() or output_path.is_empty():
        print("ERROR: --scene= <path> and --output= <path> are required")
        get_tree().quit(1)
        return

    var viewport = SubViewport.new()
    viewport.size = viewport_size
    add_child(viewport)

    var scene = load(target_scene_path).instantiate()
    viewport.add_child(scene)

    await get_tree().create_timer(0.1).timeout
    await get_tree().create_timer(0.1).timeout

    var viewport_texture = viewport.get_texture()

    if viewport_texture == null:
        print("ERROR: Could not capture viewport texture")
        get_tree().quit(1)
        return

    var image = viewport_texture.get_image()

    if image == null:
        print("ERROR: Image data is null")
        get_tree().quit(1)
        return

    var error = image.save_png(output_path)
    if error != OK:
        print("ERROR: Failed to save screenshot: " + str(error))
        get_tree().quit(1)
        return

    print("OK: Screenshot saved to " + output_path)
    get_tree().quit(0)
