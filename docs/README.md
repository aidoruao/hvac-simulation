# HVAC Simulation

**Free, non-proprietary HVAC simulation for trade school alternative.**

No vendor lock-in. Every formula cited with primary sources. Glass box enforced at code level. Multi-language support (English, Spanish). Advanced thermodynamics via MOOSE-inspired numerical methods.

---

## Quick Start

```bash
git clone https://github.com/aidoruao/hvac-simulation.git
cd hvac-simulation
source venv/bin/activate
PYTHONPATH=. ./venv/bin/pytest  # 282 Python tests (10 expected non-R410A failures)
python3 test_godot_regression.py  # 12 Godot tests
```

**Expected:** 282/292 PASS (282 Python + 12 Godot, 10 expected non-R410A Helmholtz failures)

---

## What This Is

| Feature | Status |
|---------|--------|
| Multi-refrigerant physics (R410A, R32, R134a, R1234yf, R22, R454B, R513A) | ✅ 7 fluids |
| First-principles Helmholtz EOS (c_v, c_p, w, H, S, P_sat) | ✅ FR-MA-001–010 |
| 3D mechanical room with real-time gauges (Godot 4.7.1) | ✅ FR-3D-001/002 |
| Aerospace-grade particle flow visualization | ✅ FR-AN-001 |
| HelmholtzEOS-driven PT chart with dynamic switching | ✅ FR-3D-003–005 |
| DeepSeek AI plugin — autonomous scene mutation engine | ✅ FR-3D-006–010 (headless) |
| Training scenario engine with 23 unique faults | ✅ 23 scenarios |
| Real-time cycle simulation with fault injection + scoring | ✅ FR-ED-005–008 |
| Spanish localization | ✅ FR-ED-004 |
| Property-based testing (50,000 random cases) | ✅ FR-FV-001 L1 |
| TLA+ formal specification | ✅ FR-FV-001 L2 |
| 60 FPS with all systems active | ✅ FR-PE-001 |
| Mobile optimization (particle LOD, simplified gauges) | ✅ FR-ED-008 |

---

## The Cathedral Index (The Map)

All critical documentation is unified into a single, self-contained HTML document:

```bash
# Open the map
cat docs/index.html
```

**`docs/index.html`** is the Cathedral Index — the single source of truth containing:

- Full SRS v1.8 text (all 44 requirements with verification matrix)
- Complete formula citations with primary sources and traceability
- AI behavioral archetypes (Patterns 1-4 + Almost Failure Invariant)
- Active investigations (INV-9A-001: GLSL Shader Import Failures)
- Campaign history (1a–9a)
- Ecosystem architecture (hvac-simulation ↔ godot-OE)
- COVENANT.json (AI behavioral constitution)
- Horizon Registry (Maxwell construction, Lean 4, Topos/Landauer)
- Active Integrity Warden (RLHF sanitizer, Almost Failure detector, Cryptographic Witness gate)
- 21 verified specifications, all inline CSS/JS, zero external dependencies

---

## Map Auditor

Validate that the map contains what it ought to contain:

```bash
cd ~/hvac-simulation
python3 docs/audit_map.py
```

The auditor checks:
1. **Sections** — all 21 required sections present
2. **Invariants** — FR-SV-005, Almost Failure, Completion Theater, Heredoc ban, INV-9A-001
3. **Math** — Helmholtz EOS, Maxwell construction, Jacobian stability, Landauer functors, Lean 4
4. **Commit anchors** — cryptographic references to ground truth commits
5. **Anchor verification** — the anchor commit exists in the git repository

---

## Documentation

All documentation lives in [`docs/`](docs/):

- **[Cathedral Index](docs/index.html)** — unified map (the single source of truth)
- **[Map Auditor](docs/audit_map.py)** — validates the map
- **[Requirements (SRS v1.8)](docs/HVAC_SRS.md)** — full software requirements specification
- **[Formula Citations](docs/FORMULA_CITATIONS.md)** — every formula traced to primary source
- **[AI Onboarding](docs/KIMI_ONBOARDING.md)** — environment invariants for AI agents
- **[Behavioral Archetypes](docs/AI_BEHAVIORAL_ARCHETYPES.md)** — observed AI failure patterns
- **[Investigations](docs/INVESTIGATIONS.md)** — active defects (INV-9A-001)
- **[Campaign History](docs/GEMINI_NBLM_HISTORIAN.md)** — immutable campaign archive (1a–8a)
- **[Contributing Guide](docs/CONTRIBUTING.md)** — AI Patch Rejection Protocol (FR-SV-005)

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

## Running Tests

```bash
# Activate virtual environment
source ~/hvac-simulation/venv/bin/activate

# Python tests (282 pass, 10 expected non-R410A failures)
cd ~/hvac-simulation && PYTHONPATH=. ./venv/bin/pytest

# Godot regression (12 tests)
cd ~/hvac-simulation && python3 test_godot_regression.py
```

**Gate:** 282/292 must pass. 10 property-based test failures are expected (non-R410A Helmholtz EOS — FR-MA-002 pending).

---

## License

See [LICENSE](LICENSE)

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*
*SRS v1.8. 282/292 PASS. Cathedral Index v3.0 anchored at d141846.*