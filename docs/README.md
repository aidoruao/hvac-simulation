# HVAC Simulation

**Free, non-proprietary HVAC simulation for trade school alternative.**

No vendor lock-in. Every formula cited with primary sources. Glass box enforced at code level. Multi-language support (English, Spanish). Advanced thermodynamics via MOOSE-inspired numerical methods.

---

## Quick Start

```bash
git clone https://github.com/aidoruao/hvac-simulation.git
cd hvac-simulation
source venv/bin/activate
PYTHONPATH=. ./venv/bin/pytest  # 267 Python tests
python3 test_godot_regression.py  # 12 Godot tests
```

**Expected:** 279/279 PASS (267 Python + 12 Godot, 0 xfailed)

---

## What This Is

| Feature | Status |
|---------|--------|
| Multi-refrigerant physics (R410A, R32, R134a, R1234yf, R22) | ✅ 5 fluids |
| First-principles Helmholtz EOS (c_v, c_p, w, H, S, P_sat) | ✅ FR-MA-001–009 |
| 3D mechanical room with real-time gauges (Godot 4.7.1) | ✅ FR-3D-001/002 |
| Aerospace-grade particle flow visualization | ✅ FR-AN-001 |
| HelmholtzEOS-driven PT chart with dynamic switching | ✅ FR-3D-003–005 |
| Training scenario engine with 23 unique faults | ✅ 23 scenarios |
| Real-time cycle simulation with fault injection + scoring | ✅ FR-ED-005 |
| Spanish localization | ✅ FR-ED-004 |
| Property-based testing (50,000 random cases) | ✅ FR-FV-001 L1 |
| TLA+ formal specification | ✅ FR-FV-001 L2 |
| 60 FPS with all systems active | ✅ FR-PE-001 |

---

## Development Workflow

- **Canonical environment:** WSL2 on Ubuntu 24.04
- **Virtual environment:** `~/hvac-simulation/venv`
- **Preferred AI agents:** Kimi CLI or Codewhale for direct WSL2 filesystem access
- **Web-based AI agents** (Kimi Web, DeepSeek Web) should use Base64 encoding for file transmission; heredocs are banned due to terminal corruption

### Base64 Encoding Rule

Web agents must encode multi-line content to Base64, then decode:
```bash
echo '<base64>' | base64 -d > target_file
```

### Heredoc Ban

`<< EOF` blocks are banned for multi-line files because Bash interpolates `$`, `\n`, and `#` before file write, and long blocks corrupt mid-sentence. See [KIMI_ONBOARDING.md](docs/KIMI_ONBOARDING.md) for the full history (7 consecutive failures in Campaign 5a).

### Hardware-Accelerated Headless Rendering

For visual regression on RTX 4050:
```bash
--rendering-driver d3d12
```

### Path Mapping

Use `wslpath -w` when the Windows Godot executable writes to the WSL2 filesystem.

---

## Documentation

All documentation lives in [`docs/`](docs/INDEX.md):

- [Requirements (SRS v1.6)](docs/HVAC_SRS.md)
- [Formula Citations](docs/FORMULA_CITATIONS.md)
- [AI Onboarding](docs/KIMI_ONBOARDING.md)
- [Campaign History](docs/GEMINI_NBLM_HISTORIAN.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

---

## License

See [LICENSE](LICENSE)

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*
