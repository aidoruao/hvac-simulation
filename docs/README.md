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

**Expected:** 188/188 PASS

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
| Mathematical modeling (Helmholtz EOS derivations) | 🚧 P0 skeleton |

---

## Documentation

All documentation lives in [`docs/`](docs/INDEX.md):

- [Requirements (SRS v1.5)](docs/HVAC_SRS.md)
- [Formula Citations](docs/FORMULA_CITATIONS.md)
- [AI Onboarding](docs/KIMI_ONBOARDING.md)
- [Campaign History](docs/GEMINI_NBLM_HISTORIAN.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

---

## License

See [LICENSE](LICENSE)

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*
