"""
FR-PF-002: Frame Rate Benchmark Test
Runs Godot headless benchmark and validates FPS results.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

GODOT_BINARY = "./godot"
PROJECT_PATH = "godot_project"
BENCHMARK_SCRIPT = "scripts/frame_rate_benchmark.gd"
RESULTS_FILE = Path.home() / ".local/share/godot/app_userdata/HVAC Simulation/benchmark_results.json"
TARGET_FPS = 60.0


def run_benchmark() -> dict:
    """Run Godot headless benchmark and return parsed results."""
    cmd = [
        GODOT_BINARY,
        "--headless",
        "--path", PROJECT_PATH,
        "--script", BENCHMARK_SCRIPT
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    print("--- STDOUT ---")
    print(result.stdout)
    if result.stderr:
        print("--- STDERR ---")
        print(result.stderr)
    
    if result.returncode != 0:
        raise RuntimeError(f"Godot benchmark failed with code {result.returncode}")
    
    if not RESULTS_FILE.exists():
        # Fallback: search for results file
        for root, dirs, files in os.walk(Path.home() / ".local/share/godot"):
            for f in files:
                if f == "benchmark_results.json":
                    return json.load(open(Path(root) / f))
        raise FileNotFoundError(f"Results file not found: {RESULTS_FILE}")
    
    with open(RESULTS_FILE) as f:
        return json.load(f)


def test_benchmark_runs():
    """Verify benchmark executes and produces valid output."""
    data = run_benchmark()
    
    assert data["benchmark"] == "FR-PF-002"
    assert "godot_version" in data
    assert "date" in data
    assert "results" in data
    assert len(data["results"]) == 2  # PT chart + mechanical room
    
    for r in data["results"]:
        assert "scene" in r
        assert "avg_fps" in r
        assert "min_fps" in r
        assert "max_fps" in r
        assert "samples" in r
        assert "pass" in r
        assert r["avg_fps"] >= 0
        assert r["min_fps"] >= 0
        assert r["max_fps"] >= 0
        assert r["samples"] > 0


def test_pt_chart_fps():
    """PT chart scene must maintain target FPS."""
    data = run_benchmark()
    pt_result = next(r for r in data["results"] if "pt_chart" in r["scene"])
    
    print(f"PT Chart: avg={pt_result['avg_fps']} min={pt_result['min_fps']} max={pt_result['max_fps']}")
    assert pt_result["avg_fps"] >= TARGET_FPS, \
        f"PT chart avg FPS {pt_result['avg_fps']} below target {TARGET_FPS}"


def test_mechanical_room_fps():
    """Mechanical room scene must maintain target FPS."""
    data = run_benchmark()
    mech_result = next(r for r in data["results"] if "mechanical_room" in r["scene"])
    
    print(f"Mechanical Room: avg={mech_result['avg_fps']} min={mech_result['min_fps']} max={mech_result['max_fps']}")
    assert mech_result["avg_fps"] >= TARGET_FPS, \
        f"Mechanical room avg FPS {mech_result['avg_fps']} below target {TARGET_FPS}"


def test_overall_pass():
    """Both scenes must pass FPS target."""
    data = run_benchmark()
    assert data["overall_pass"] is True, \
        f"Benchmark failed. Results: {json.dumps(data['results'], indent=2)}"


if __name__ == "__main__":
    # Run all tests
    test_benchmark_runs()
    print("test_benchmark_runs: PASS")
    
    test_pt_chart_fps()
    print("test_pt_chart_fps: PASS")
    
    test_mechanical_room_fps()
    print("test_mechanical_room_fps: PASS")
    
    test_overall_pass()
    print("test_overall_pass: PASS")
    
    print("\n=== FR-PF-002 ALL TESTS PASS ===")
