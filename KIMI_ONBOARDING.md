# KIMI ONBOARDING — HVAC Simulation

**Last Updated:** 2026-07-18 (Campaign 5a, Entry 24)
**Status:** LOCKED
**Current Commit:** 8b1d706

## Headless Mode
- Godot runs without a display window: `godot --headless --script <script.gd> <arg>`
- Used because WSL2 has no X11 server
- Output captured via Python subprocess, stdout/stderr combined
- `quit()` terminates the process; `print("PASS"/"FAIL")` is the test signal

## Shell Escaping Rule
- **NEVER** use heredoc for GDScript. Shell eats special characters.
- **ALWAYS** use Python intermediate file approach (see 5a campaign entry 24)

## Godot Version Mismatch
- Repo binary: ~/hvac-simulation/godot (4.3.stable, Linux)
- Test runner may use different version
- GDScript parser differs between versions
- Fix: Match signatures or pin version

## Current State (Campaign 5a)
- Pytest: 158/158 PASS
- Godot regression (FR-VA-003): In progress
  - test_helper_3d002.gd — DONE
  - test_helper_wiring.gd — DONE
  - test_helper_ptchart.gd — DONE (entry 24)
  - Python harness (test_godot_regression.py) — NEXT
- SRS: v1.2 target
- Next: Complete Python harness, run all Godot tests

## What Headless CAN/CANNOT Test
- CAN: Scene loading, node existence, state variables, method calls
- CANNOT: Visual rendering, animation timing, pixel-perfect output


## New Rules (Campaign 6a, Entry 126)

### 1. Base64 Encoding Rule
- The "Heredoc War" is not over. Shell interpretation of `$`` and `n\` in heredocs corrupts multi-line GDScript and nested Python.
- **SOLUTION**: Write complex multi-line files (scripts, configs, nested code) via base64-decoded strings.
- **PROCEDURE**:
  1. Encode the file content as base64 in a separate step (or pre-calculated).
  2. Use `echo <base64_string> | base64 -d > /tmp/write.py && python3 /tmp/write.py`.
- **EXAMPLE**: See Campaign 6a turns 20-109 for screenshot_capture.gd and test_screenshot_diff.py.

### 2. Cross-Platform Path Mapping
- The Windows Godot exe (4.7.1) cannot write directly to WSL2 Linux paths (`/home/idor/...`).
- **SOLUTION**: Use `wslpath -w <linux_path>` to convert to `f\\wsl.localhost\\Ubuntu-24.04\...` format.
- **POST-CAPTURE**: Copy back to Windows temp if needed, but `wsl.localhost` is the canonical bridge.

### 3. Hardware-Accelerated Headless Rendering
- Visual regression requires actual pixel data. The headless "dummy" renderer cannot capture textures.
- **SOLUTION**: Force `--display-driver windows --rendering-driver d3d12` to use RTX 4050 for headless screenshot capture.
- **REQUIREMENT**: GSU (real GPU or hybrid dGPU) must be available in WSL2 environment.

### Current State (Campaign 6a)
- Pytest: 174/174 PASS (+3 visual regression)
- Godot regression (FR-VA-003): 12/12 PASS
- Visual regression (FR-VA-004): 3/3 PASS
- Total: 186/186 PASS
- SRS: v1.4
- Latest Commit: f1e5a8d