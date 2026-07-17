"""
FR-3D-002: Animated Compressor and Fan Test
Uses Godot helper script for scene validation.
"""

import subprocess

GODOT_BINARY = "./godot"
PROJECT_PATH = "godot_project"
HELPER_SCRIPT = "scripts/test_helper_3d002.gd"


def _run_test(test_name: str) -> tuple:
    cmd = [
        GODOT_BINARY,
        "--headless",
        "--path", PROJECT_PATH,
        "--script", HELPER_SCRIPT,
        test_name
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result.stdout, result.stderr, result.returncode


def test_scene_has_compressor():
    stdout, stderr, rc = _run_test("has_compressor")
    print("STDOUT:", stdout.strip())
    assert "PASS: Compressor node found" in stdout, f"Failed. stdout={stdout} stderr={stderr}"
    print("test_scene_has_compressor: PASS\n")


def test_scene_has_condenser_fan():
    stdout, stderr, rc = _run_test("has_fan")
    print("STDOUT:", stdout.strip())
    assert "PASS: CondenserFan node found" in stdout, f"Failed. stdout={stdout} stderr={stderr}"
    print("test_scene_has_condenser_fan: PASS\n")


def test_animation_state_on():
    stdout, stderr, rc = _run_test("animation_on")
    print("STDOUT:", stdout.strip())
    assert "PASS: Animation RPM set" in stdout, f"Failed. stdout={stdout} stderr={stderr}"
    print("test_animation_state_on: PASS\n")


def test_animation_state_off():
    stdout, stderr, rc = _run_test("animation_off")
    print("STDOUT:", stdout.strip())
    assert "PASS: Animation stopped" in stdout, f"Failed. stdout={stdout} stderr={stderr}"
    print("test_animation_state_off: PASS\n")


if __name__ == "__main__":
    test_scene_has_compressor()
    test_scene_has_condenser_fan()
    test_animation_state_on()
    test_animation_state_off()
    print("=== FR-3D-002 ALL TESTS PASS ===")
