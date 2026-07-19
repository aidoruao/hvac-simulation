import subprocess
import os
import sys
from pathlib import Path
from PIL import Image, ImageChops

PROJECT_DIR = Path('/home/idor/hvac-simulation/godot_project')
GODOT_BIN = '/mnt/c/Users/Aidor/Godot_v4.7.1-stable_win64.exe'
CAPTURES_DIR = Path(__file__).parent / 'captures'
BASELINES_DIR = Path(__file__).parent / 'baselines'
DIFFS_DIR = Path(__file__).parent / 'diffs'
THRESHOLD = 0.01
VIEWPORT_SIZE = (1920, 1080)

def to_windows_path(linux_path: Path) -> str:
    result = subprocess.run(['wslpath', '-w', str(linux_path)], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f'Failed to convert path: {result.stderr}')
    return result.stdout.strip()

def run_godot_screenshot(scene_path: str, output_name: str) -> Path:
    output_linux = CAPTURES_DIR / f'{output_name}.png'
    output_win = to_windows_path(output_linux)
    cmd = [
        GODOT_BIN,
        '--headless',
        '--path', str(PROJECT_DIR),
        '--display-driver', 'windows',
        '--rendering-driver', 'd3d12',
        'scenes/screenshot_capture.tscn',
        f'--scene={scene_path}',
        f'--output={output_win}',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f'Godot stdout: {result.stdout}')
    print(f'Godot stderr: {result.stderr}')
    if result.returncode != 0:
        raise RuntimeError(f'Screenshot failed for {scene_path}: {result.returncode}')
    return output_linux

def compare_images(baseline_path: Path, capture_path: Path) -> tuple[bool, float]:
    baseline = Image.open(baseline_path).convert('L')
    capture = Image.open(capture_path).convert('L')
    if baseline.size != capture.size:
        raise ValueError(f'Size mismatch: {baseline.size} vs {capture.size}')
    diff = ImageChops.difference(baseline, capture)
    diffs_path = DIFFS_DIR / f'{baseline_path.stem}_diff.png'
    diff.save(diffs_path)
    stats = diff.getextrema()
    diff_count = stats[1] - stats[0]
    total_pixels = baseline.size[0] * baseline.size[1]
    diff_ratio = diff_count / total_pixels
    return diff_ratio < THRESHOLD, diff_ratio

if __name__ == '__main__':
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)
    DIFFS_DIR.mkdir(parents=True, exist_ok=True)
    print('FR-VA-004 infrastructure ready.')
    print(f'Captures: {CAPTURES_DIR}')
    print(f'Baselines: {BASELINES_DIR}')
    print(f'Diffs: {DIFFS_DIR}')

import pytest
import shutil

SCENES = [
    "scenes/mechanical_room/mechanical_room.tscn",
    "scenes/pt_chart.tscn",
    "scenes/wiring_scene.tscn",
]

def generate_baseline(scene_path: str):
    name = Path(scene_path).stem
    capture = run_godot_screenshot(scene_path, name)
    baseline = BASELINES_DIR / f'{name}.png'
    shutil.copy(str(capture), str(baseline))
    print(f"Baseline generated: {baseline}")
    return baseline

@pytest.mark.parametrize("scene_path", SCENES)
def test_visual_regression(scene_path: str):
    name = Path(scene_path).stem
    baseline = BASELINES_DIR / f'{name}.png'
    if not baseline.exists():
        baseline = generate_baseline(scene_path)
    capture = run_godot_screenshot(scene_path, name)
    passed, diff_ratio = compare_images(baseline, capture)
    assert passed, f"Visual regression failed for {scene_path}: {diff_ratio:.4f} difference"

import pytest
import shutil

SCENES = [
    "scenes/mechanical_room/mechanical_room.tscn",
    "scenes/pt_chart.tscn",
    "scenes/wiring_scene.tscn",
]

def generate_baseline(scene_path: str):
    name = Path(scene_path).stem
    capture = run_godot_screenshot(scene_path, name)
    baseline = BASELINES_DIR / f'{name}.png'
    shutil.copy(str(capture), str(baseline))
    print(f"Baseline generated: {baseline}")
    return baseline

@pytest.mark.parametrize("scene_path", SCENES)
def test_visual_regression(scene_path: str):
    name = Path(scene_path).stem
    baseline = BASELINES_DIR / f'{name}.png'
    if not baseline.exists():
        baseline = generate_baseline(scene_path)
    capture = run_godot_screenshot(scene_path, name)
    passed, diff_ratio = compare_images(baseline, capture)
    assert passed, f"Visual regression failed for {scene_path}: {diff_ratio:.4f} difference"
