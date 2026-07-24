#!/usr/bin/env python3
"""
programmatic_agent.py — Autonomous loop without xdotool GUI clicking.
Uses DeepSeekChat GDScript wrapper via Godot --script execution.
The GDScript uses process_frame for async HTTP (OS.delay_msec blocks main loop).
"""
import subprocess
import os
import time
import json
import glob
import tempfile
import sys
from pathlib import Path

GODOT_BIN = "/home/idor/godot-OE/bin/godot.linuxbsd.editor.x86_64"
PROJECT_DIR = "/home/idor/hvac-simulation/godot_project"
AUDIT_DIR = os.path.expanduser(
    "~/.local/share/godot/app_userdata/HVAC Simulation/oe_audit"
)


def _get_api_key() -> str:
    env_path = Path("/home/idor/cathedral/.env")
    for line in env_path.read_text().splitlines():
        if line.startswith("DEEPSEEK_API_KEY="):
            return line.split("=", 1)[1].strip()
    return ""


def run_gdscript(gd_code: str, timeout: int = 60):
    """Execute GDScript via Godot --script, return (stdout, stderr, returncode)."""
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


def chat_with_ai(instruction: str) -> str:
    """
    Send instruction to DeepSeek API via GDScript DeepSeekChat wrapper.
    Uses process_frame for async HTTP — OS.delay_msec blocks the main loop.
    """
    gd = '''extends SceneTree

var _chat: RefCounted
var _done: bool = false
var _response: String = ""

func _initialize():
    var key = OS.get_environment("DEEPSEEK_API_KEY")
    var ChatClass = load("res://scripts/deepseek_chat.gd")
    _chat = ChatClass.new(key)
    _chat.chat("''' + instruction.replace('"', '\\"') + '''", _on_response)
    process_frame.connect(_poll)

func _on_response(resp: String):
    _response = resp
    _done = true
    print("AI_RESPONSE:" + _response)

func _poll():
    if _done:
        quit()
'''
    stdout, stderr, rc = run_gdscript(gd, timeout=45)
    for line in stdout.split("\n"):
        if line.startswith("AI_RESPONSE:"):
            return line[len("AI_RESPONSE:"):].strip()
    if stderr:
        return "ERROR: " + stderr[:200]
    return "TIMEOUT"


def capture_editor_viewport() -> str | None:
    """Return path to latest editor capture, or None."""
    captures = glob.glob(
        os.path.expanduser(
            "~/.local/share/godot/app_userdata/HVAC Simulation/"
            "editor_capture_*.png"
        )
    )
    return max(captures, key=os.path.getmtime) if captures else None


def main() -> bool:
    print("=== Programmatic Agent ===")

    # 1. Log human instruction
    instruction = "Say exactly pong and nothing else"
    print(f"HUMAN_INPUT: {instruction}")

    # 2. Send to AI via programmatic API
    print("Sending to DeepSeek API...")
    response = chat_with_ai(instruction)
    print(f"AI_RESPONSE: {response}")

    # 3. Capture editor viewport (if editor is running)
    screenshot = capture_editor_viewport()
    print(f"SCREENSHOT: {screenshot}")

    # 4. Verify
    if screenshot:
        try:
            from PIL import Image
            img = Image.open(screenshot)
            w, h = img.size
            non_black = sum(
                1 for x in range(0, w, 10) for y in range(0, h, 10)
                if img.getpixel((x, y))[0] > 20
                or img.getpixel((x, y))[1] > 20
                or img.getpixel((x, y))[2] > 20
            )
            print(f"VERDICT: Screenshot {w}x{h}, non-black={non_black}")
        except ImportError:
            print("VERDICT: PIL not installed")

    success = "pong" in response.lower()
    print(f"FINAL: {'PASS' if success else 'FAIL'}")
    return success


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
