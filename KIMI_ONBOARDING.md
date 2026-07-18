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

