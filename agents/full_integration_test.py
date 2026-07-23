#!/usr/bin/env python3
"""
full_integration_test.py — End-to-end: open Godot, talk to native AI,
capture viewport, run all six verification layers.

Requires: xdotool, Godot-OE, DEEPSEEK_API_KEY in environment.
"""
import subprocess
import os
import sys
import time
import json

sys.path.insert(0, "/home/idor/hvac-simulation")

from agents.autonomous_godot_agent import AutonomousGodotAgent
from agents.multi_layer_verify import MultiLayerVerifier


def main() -> bool:
    print("=== Full Integration Test ===")
    print()

    # ── 1. Launch Godot ──────────────────────────────────────────────────
    print("[1/5] Launching Godot...")
    agent = AutonomousGodotAgent()
    if not agent.launch():
        print("FAIL: Godot launch failed")
        return False
    print("OK: Godot running")
    print()

    # ── 2. Type instruction to native AI ──────────────────────────────────
    instruction = "Add a compressor at origin and describe what you see"
    print(f"[2/5] Instructing: {instruction}")
    agent.instruct(instruction)
    print("OK: instruction sent, waiting for AI processing...")
    time.sleep(10)
    print()

    # ── 3. Capture screenshot ────────────────────────────────────────────
    screenshot_dir = "/tmp/godot_verify"
    os.makedirs(screenshot_dir, exist_ok=True)
    screenshot_path = os.path.join(screenshot_dir, "integration_test.png")
    print(f"[3/5] Capturing viewport → {screenshot_path}")
    agent.capture_viewport(screenshot_path)
    print("OK: capture complete")
    print()

    # ── 4. Shutdown ──────────────────────────────────────────────────────
    print("[4/5] Shutting down Godot...")
    agent.shutdown()
    print("OK: Godot stopped")
    print()

    # ── 5. Multi-layer verification ──────────────────────────────────────
    print("[5/5] Running verification...")
    verifier = MultiLayerVerifier()
    result = verifier.run_all(
        instruction=instruction,
        screenshot_path=screenshot_path,
        pdf_section="3.1 Architecture",
    )

    print()
    print(json.dumps(result, indent=2))
    return result.get("all_passed", False)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
