# HVAC Simulation

**Free, non-proprietary HVAC simulation for trade school alternative.**

No vendor lock-in. Every formula cited with primary sources. Glass box enforced at code level. Multi-language support (English, Spanish). Advanced thermodynamics via MOOSE-inspired numerical methods.

---

## Quick Start

```bash
git clone https://github.com/aidoruao/hvac-simulation.git
cd hvac-simulation
source venv/bin/activate
python3 -m pytest          # 176 Python tests
python3 test_godot_regression.py  # 12 Godot tests
```

**Expected:** 207/207 PASS (195 Python + 12 Godot, 0 xfailed)

---

## What This Is

| Feature | Status |
|---------|--------|
| Multi-refrigerant physics (R22, R134a, R32, R410A, R1234yf) | ✅ |
| 3D mechanical room with real-time gauges (Godot 4.7.1) | ✅ |
| Training scenario engine with 20+ unique faults | ✅ |
| Spanish localization | ✅ |
| Automated visual regression testing (D3D12/RTX 4050) | ✅ |
| MOOSE-inspired steady-state heat conduction solver | ✅ |
| Mathematical modeling (Helmholtz EOS derivations) | ✅ FR-MA-001 complete — R410A vapor/liquid coefficients, c_p, c_v, speed of sound, Jacobian stability |

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
