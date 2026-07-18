#!/usr/bin/env python3
"""
FR-VA-003: Godot Regression Test Runner
Runs all Godot scene tests and reports PASS/FAIL.
Usage: python3 test_godot_regression.py
"""

import subprocess
import sys
import os

GODOT_BIN = "/mnt/c/Users/Aidor/Godot_v4.7.1-stable_win64.exe"
PROJECT_DIR = os.path.expanduser("~/hvac-simulation/godot_project")

TEST_SUITES = {
    "FR-3D-002": {
        "script": "scripts/test_helper_3d002.gd",
        "tests": ["has_compressor", "has_fan", "animation_on", "animation_off"],
    },
    "FR-EL-002": {
        "script": "scripts/test_helper_wiring.gd",
        "tests": ["test_load", "test_nodes"],
    },
    "FR-VI-001/002": {
        "script": "scripts/test_helper_ptchart.gd",
        "tests": ["test_load", "test_dropdown", "test_switch", "test_reference"],
    },
}

def run_test(script: str, test_name: str) -> bool:
    cmd = [
        GODOT_BIN,
        "--headless",
        "--path", PROJECT_DIR,
        "--script", script,
        test_name,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        passed = "PASS:" in output
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")
        if not passed:
            for line in output.splitlines():
                if line.strip():
                    print(f"    {line}")
        return passed
    except subprocess.TimeoutExpired:
        print(f"  [FAIL] {test_name} -- timeout")
        return False
    except Exception as e:
        print(f"  [FAIL] {test_name} -- {e}")
        return False

def main():
    print("=" * 60)
    print("FR-VA-003: Godot Regression Test Runner")
    print(f"Godot binary: {GODOT_BIN}")
    print(f"Project dir:  {PROJECT_DIR}")
    print("=" * 60)

    total = 0
    passed = 0

    for suite_name, suite in TEST_SUITES.items():
        print(f"\n{suite_name} ({suite['script']}):")
        for test_name in suite["tests"]:
            total += 1
            if run_test(suite["script"], test_name):
                passed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")
    if passed == total:
        print("ALL GODOT REGRESSION TESTS PASS")
    else:
        print("SOME TESTS FAILED")
    print("=" * 60)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
