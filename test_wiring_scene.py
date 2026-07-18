"""
FR-EL-002: Godot Wiring Scene Integration Test
"""

import subprocess

GODOT_BINARY = "./godot"
PROJECT_PATH = "godot_project"

def _run_godot(script_name, test_name):
    cmd = [
        GODOT_BINARY,
        "--headless",
        "--path", PROJECT_PATH,
        "--script", script_name,
        test_name
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode

def test_wiring_scene_loads():
    stdout, stderr, rc = _run_godot("scripts/test_helper_wiring.gd", "test_load")
    print("STDOUT:", stdout.strip())
    assert "PASS: Wiring Scene initialized" in stdout
    print("test_wiring_scene_loads: PASS")

def test_wiring_scene_has_wire_nodes():
    stdout, stderr, rc = _run_godot("scripts/test_helper_wiring.gd", "test_nodes")
    print("STDOUT:", stdout.strip())
    assert "PASS: All wire nodes found" in stdout
    print("test_wiring_scene_has_wire_nodes: PASS")

if __name__ == "__main__":
    test_wiring_scene_loads()
    test_wiring_scene_has_wire_nodes()
    print("=== FR-EL-002 ALL TESTS PASS ===")
