#!/usr/bin/env python3
"""
test_godot_opengl3_wslg.py — Verify Godot renders under OpenGL3/WSLg with non-black frames.
FR-3D-006/007/008/010 bypass verification. Cathedral Index v3.1.
INV-9A-001: BYPASSED. Requires: DISPLAY=:0, godot-OE binary.
"""
import subprocess
import os
import tempfile
import sys

GODOT_BIN = "/home/idor/godot-OE/bin/godot.linuxbsd.editor.x86_64"
PROJECT_PATH = "/home/idor/hvac-simulation/godot_project"
MIN_NONBLACK_RATIO = 0.90


def test_opengl3_wslg_renders():
    os.environ.setdefault("DISPLAY", ":0")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        png_path = f.name

    # Godot 4.8 SceneTree._initialize() API
    gd_script = (
        'extends SceneTree\n'
        'func _initialize():\n'
        '    await create_timer(1.0).timeout\n'
        '    var img = root.get_texture().get_image()\n'
        f'    img.save_png("{png_path}")\n'
        '    print("CAPTURED: " + str(img.get_width()) + "x" + str(img.get_height()))\n'
        '    quit()\n'
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".gd", delete=False) as sf:
        sf.write(gd_script)
        script_path = sf.name

    cmd = [
        GODOT_BIN,
        "--display-driver", "x11",
        "--rendering-driver", "opengl3",
        "--path", PROJECT_PATH,
        "--script", script_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    captured = "CAPTURED:" in result.stdout or "CAPTURED:" in result.stderr
    if not captured:
        print("STDOUT:", result.stdout[-500:])
        print("STDERR:", result.stderr[-500:])
        sys.exit(f"Godot exited {result.returncode}. No CAPTURED in output.")

    # Verify PNG is non-black
    from PIL import Image
    img = Image.open(png_path)
    w, h = img.size
    px = img.load()
    nonblack = sum(
        1 for x in range(0, w, 10) for y in range(0, h, 10)
        if px[x, y] != (0, 0, 0, 255)
    )
    total = ((w // 10) + 1) * ((h // 10) + 1)
    ratio = nonblack / total
    print(f"SIZE: {w}x{h}  NONBLACK: {nonblack}/{total}  RATIO: {ratio:.2%}")

    assert ratio >= MIN_NONBLACK_RATIO, (
        f"Non-black ratio {ratio:.2%} below threshold {MIN_NONBLACK_RATIO}"
    )

    os.unlink(png_path)
    os.unlink(script_path)
    print("PASS: OpenGL3/WSLg renders non-black frames")


if __name__ == "__main__":
    test_opengl3_wslg_renders()
