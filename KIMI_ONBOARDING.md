# KIMI ONBOARDING — HVAC Simulation

**Last Updated:** 2026-07-18 (Campaign 5a)
**Status:** LOCKED

## Headless Mode
- Godot runs without a display window: `godot --headless --script <script.gd> <arg>`
- Used because WSL2 has no X11 server
- Output captured via Python `subprocess.run()`, stdout/stderr combined
- `quit()` terminates the process; `print("PASS"/"FAIL")` is the test signal

## Shell Escaping Rule
- **NEVER** use heredoc for GDScript. Shell eats `$`, `\n`, `"`, `##`.
- **ALWAYS** use Python intermediate file:
  ```bash
  cat > /tmp/write_file.py << 'PYEOF'
  content = r"""...[raw string]..."""
  with open("target/file.gd", "w") as f:
      f.write(content)
  PYEOF
  python3 /tmp/write_file.py
  ```

## Godot Version Mismatch
- Repo binary: `~/hvac-simulation/godot` (4.3.stable, Linux, not tracked)
- Test runner may invoke Windows binary (4.7.1) from `~/Downloads`
- GDScript parser strictness differs between versions
- Fix: Match signatures to the binary being invoked, or pin to one version

## Current State (Campaign 5a)
- Pytest: 158/158 PASS ✅
- Godot regression: 10/10 PASS ✅ (FR-VA-003 complete)
- SRS: v1.2, 168/168 total tests verified
- Next: FR-ED-004 (Spanish localization) or FR-VA-004 (visual regression)

## What Headless CAN Test
- Scene loading, node existence, state variables, method calls

## What Headless CANNOT Test
- Visual rendering, animation smoothness, pixel-perfect output (future FR-VA-004)
