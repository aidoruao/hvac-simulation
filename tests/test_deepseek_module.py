#!/usr/bin/env python3
"""
test_deepseek_module.py — Verify all 6 DeepSeek module components.
Requires: godot-OE binary with modules/deepseek/ compiled in. Cathedral Index v3.1.
"""
import subprocess
import os
import tempfile
import sys

GODOT_BIN = "/home/idor/godot-OE/bin/godot.linuxbsd.editor.x86_64"
PROJECT_PATH = "/home/idor/hvac-simulation/godot_project"

COMPONENTS = [
    ("DeepSeekClient", "SERVERS"),
    ("DeepSeekCovenant", "SERVERS"),
    ("SceneSerializer", "SERVERS"),
    ("ViewportCapture", "SERVERS"),
    ("DeepSeekMutation", "EDITOR"),
    ("DeepSeekAIAssistant", "EDITOR"),
]


def test_components_in_binary():
    """Verify all 6 component class names appear in the compiled binary."""
    result = subprocess.run(["strings", GODOT_BIN], capture_output=True, text=True)
    out = result.stdout
    missing = []
    for name, level in COMPONENTS:
        if name in out:
            print(f"  FOUND: {name} ({level})")
        else:
            missing.append(name)
            print(f"  MISSING: {name} ({level})")
    assert not missing, f"Components not in binary: {missing}"


def test_viewport_capture_functional():
    """Verify ViewportCapture.capture_screenshot() produces a valid PNG."""
    os.environ.setdefault("DISPLAY", ":0")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        png_path = f.name

    # Godot 4.8 SceneTree._initialize() with ViewportCapture API
    gd_script = (
        'extends SceneTree\n'
        'func _initialize():\n'
        '    await create_timer(1.0).timeout\n'
        '    var vpc = ViewportCapture.new()\n'
        '    var err = vpc.capture_screenshot(root)\n'
        '    print("VP_CAPTURE_ERR=" + str(err))\n'
        '    var img = vpc.get_image()\n'
        f'    img.save_png("{png_path}")\n'
        '    print("VP_CAPTURE: " + str(img.get_width()) + "x" + str(img.get_height()))\n'
        '    quit()\n'
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".gd", delete=False) as sf:
        sf.write(gd_script)
        script_path = sf.name

    cmd = [
        GODOT_BIN, "--display-driver", "x11", "--rendering-driver", "opengl3",
        "--path", PROJECT_PATH, "--script", script_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert "VP_CAPTURE:" in result.stdout, (
        f"ViewportCapture failed. Output: {result.stdout[-400:]}"
    )

    from PIL import Image
    img = Image.open(png_path)
    assert img.size[0] > 0 and img.size[1] > 0, f"Invalid image: {img.size}"
    print(f"  ViewportCapture: {img.size[0]}x{img.size[1]} PNG")

    os.unlink(png_path)
    os.unlink(script_path)


def test_scene_serializer_functional():
    """Verify SceneSerializer.serialize_tree() produces output."""
    os.environ.setdefault("DISPLAY", ":0")

    gd_script = (
        'extends SceneTree\n'
        'func _initialize():\n'
        '    await create_timer(1.0).timeout\n'
        '    var ser = SceneSerializer.new()\n'
        '    ser.serialize_tree(root)\n'
        '    var tree = ser.get_compressed_tree()\n'
        '    var count = ser.get_node_count()\n'
        '    print("SER_NODES=" + str(count) + " SER_LEN=" + str(tree.length()))\n'
        '    quit()\n'
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".gd", delete=False) as sf:
        sf.write(gd_script)
        script_path = sf.name

    cmd = [
        GODOT_BIN, "--display-driver", "x11", "--rendering-driver", "opengl3",
        "--path", PROJECT_PATH, "--script", script_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    assert "SER_NODES=" in result.stdout, (
        f"SceneSerializer failed. Output: {result.stdout[-400:]}"
    )
    print(f"  SceneSerializer: {result.stdout.strip()[-200:]}")

    os.unlink(script_path)


if __name__ == "__main__":
    print("[1/3] Checking binary for 6/6 components...")
    test_components_in_binary()
    print("[2/3] Testing ViewportCapture.capture_screenshot()...")
    test_viewport_capture_functional()
    print("[3/3] Testing SceneSerializer.serialize_tree()...")
    test_scene_serializer_functional()
    print("PASS: All 6 DeepSeek module components verified")
