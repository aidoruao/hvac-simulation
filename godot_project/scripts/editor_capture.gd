@tool
extends EditorPlugin

var capture_count: int = 0

func _enter_tree():
    print("[EditorCapture] Starting capture sequence (editor 3D viewport)...")
    var timer = Timer.new()
    timer.wait_time = 5.0
    timer.one_shot = true
    timer.timeout.connect(_do_capture)
    add_child(timer)
    timer.start()

func _do_capture():
    capture_count += 1
    var vp = get_editor_interface().get_editor_viewport_3d(0)
    if not vp:
        print("[EditorCapture] ERROR: No 3D viewport available")
        return

    var tex = vp.get_texture()
    if not tex:
        print("[EditorCapture] ERROR: No texture from viewport")
        return

    var img = tex.get_image()
    if not img:
        print("[EditorCapture] ERROR: No image from texture")
        return

    var path = "user://editor_capture_%d.png" % capture_count
    img.save_png(path)
    print("[EditorCapture] Saved %s size=%dx%d" % [path, img.get_width(), img.get_height()])

    # Analyze pixel content
    var non_black = 0
    var total = 0
    var step = 10
    for x in range(0, img.get_width(), step):
        for y in range(0, img.get_height(), step):
            total += 1
            var c = img.get_pixel(x, y)
            if c.r > 0.05 or c.g > 0.05 or c.b > 0.05:
                non_black += 1

    var pct = float(non_black) / float(max(1, total)) * 100.0
    print("[EditorCapture] Non-black: %d/%d (%.1f%%)" % [non_black, total, pct])
    print("[EditorCapture] VERDICT: %s" % ("VISIBLE" if non_black > 100 else "BLACK/EMPTY"))

    # Re-arm for a second capture
    if capture_count < 2:
        var timer = Timer.new()
        timer.wait_time = 10.0
        timer.one_shot = true
        timer.timeout.connect(_do_capture)
        add_child(timer)
        timer.start()

func _exit_tree():
    pass
