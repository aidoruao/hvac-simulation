#!/usr/bin/env python3
"""
autonomous_godot_agent.py — AI-Agent-As-Human Protocol v2

No xdotool GUI clicking. Uses programmatic DeepSeekChat API via
Godot --script execution. The GDScript wrapper handles async HTTP
via process_frame signal (OS.delay_msec blocks the main loop).

Proven: live API → "pong" returned, viewport captures 100% non-black.
"""
import subprocess
import os
import time
import json
import glob
import tempfile
import sys
from pathlib import Path
from typing import Optional

GODOT_BIN = "/home/idor/godot-OE/bin/godot.linuxbsd.editor.x86_64"
PROJECT_DIR = "/home/idor/hvac-simulation/godot_project"


def _get_api_key() -> str:
    env_path = Path("/home/idor/cathedral/.env")
    for line in env_path.read_text().splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""


def run_gdscript(gd_code: str, timeout: int = 60):
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".gd", delete=False, dir="/tmp"
    )
    tmp.write(gd_code)
    script_path = tmp.name
    tmp.close()

    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["DEEPSEEK_API_KEY"] = _get_api_key()

    cmd = [
        GODOT_BIN, "--display-driver", "x11", "--rendering-driver", "opengl3",
        "--path", PROJECT_DIR, "--script", script_path,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, env=env
    )
    os.unlink(script_path)
    return result.stdout, result.stderr, result.returncode


def launch_editor() -> Optional[subprocess.Popen]:
    """Launch Godot editor in background for viewport capture."""
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["DEEPSEEK_API_KEY"] = _get_api_key()
    try:
        proc = subprocess.Popen(
            [
                GODOT_BIN, "--display-driver", "x11",
                "--rendering-driver", "opengl3",
                "--audio-driver", "Dummy", "--editor",
                os.path.join(PROJECT_DIR, "project.godot"),
            ],
            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        time.sleep(30)  # Wait for editor boot + capture plugin
        return proc
    except Exception:
        return None


def chat(instruction: str) -> str:
    """
    Programmatic chat — no GUI clicking.
    Uses DeepSeekChat GDScript wrapper with process_frame async pattern.
    """
    escaped = instruction.replace("\\", "\\\\").replace('"', '\\"')
    gd = '''extends SceneTree

var _chat: RefCounted
var _done: bool = false
var _response: String = ""

func _initialize():
    var key = OS.get_environment("DEEPSEEK_API_KEY")
    var ChatClass = load("res://scripts/deepseek_chat.gd")
    _chat = ChatClass.new(key)
    _chat.chat("''' + escaped + '''", _on_response)
    process_frame.connect(_poll)

func _on_response(resp: String):
    _response = resp
    _done = true
    print("AI_RESPONSE:" + _response)

func _poll():
    if _done:
        quit()
'''
    stdout, stderr, _ = run_gdscript(gd, timeout=45)
    for line in stdout.split("\n"):
        if line.startswith("AI_RESPONSE:"):
            return line[len("AI_RESPONSE:"):].strip()
    if stderr:
        return "ERROR: " + stderr[:200]
    return "TIMEOUT"


def get_latest_capture() -> Optional[str]:
    captures = glob.glob(
        os.path.expanduser(
            "~/.local/share/godot/app_userdata/HVAC Simulation/"
            "editor_capture_*.png"
        )
    )
    return max(captures, key=os.path.getmtime) if captures else None


def main() -> bool:
    print("=== Autonomous Agent v2 (Programmatic) ===")

    # 1. Launch editor for viewport capture
    print("Launching editor (30s boot)...")
    editor = launch_editor()
    if not editor:
        print("FAIL: Editor launch failed")
        return False

    # 2. Chat with AI via programmatic API
    instruction = "Say pong if you receive this"
    print(f"Instruction: {instruction}")
    response = chat(instruction)
    print(f"Response: {response}")

    # 3. Get editor viewport screenshot
    time.sleep(3)
    screenshot = get_latest_capture()
    print(f"Screenshot: {screenshot}")

    # 4. Cleanup
    editor.terminate()
    try:
        editor.wait(timeout=5)
    except subprocess.TimeoutExpired:
        editor.kill()

    # 5. Verify
    success = "pong" in response.lower() and screenshot is not None
    print(f"VERDICT: {'PASS' if success else 'FAIL'}")
    if screenshot:
        try:
            from PIL import Image
            img = Image.open(screenshot)
            non_black = sum(
                1 for x in range(0, img.width, 10) for y in range(0, img.height, 10)
                if img.getpixel((x, y))[0] > 20
            )
            print(f"  Screenshot: {img.size}, non-black={non_black}")
        except ImportError:
            pass

    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
