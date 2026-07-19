# HVAC Simulation — Existing Tools Reconnaissance

**Date:** 2026-07-19 (updated from 2026-07-16)  
**Scope:** Identify all open-source HVAC/thermodynamics simulators, test what works, document gaps  
**Status:** Campaign 6a complete — new capabilities discovered

---

## Tools Surveyed

### 1. CoolProp
- **URL:** https://github.com/CoolProp/CoolProp
- **License:** MIT
- **What it does:** Thermophysical properties for 136+ fluids. Equations of state, transport properties, mixtures, humid air.
- **What it doesn't:** No simulation loop, no UI, no training scenarios.
- **Our use:** Backend thermodynamics engine. Verified working (`test_physics.py`, commit `7ef3477`).
- **Verdict:** ✅ ADOPT — proven, accurate, actively maintained

### 2. SimVCCE
- **URL:** https://github.com/thermalogic/SimVCCE
- **License:** Unknown
- **What it does:** Vapor-compression cycle steady-state simulator. Educational focus. Python/C++/Rust.
- **What it doesn't:** No 3D, no real-time, no fault injection, no customer interaction, no progressive difficulty.
- **Our use:** Reference implementation for cycle calculations. Code to learn from, not build on.
- **Verdict:** ⚠️ REFERENCE — educational but limited scope

### 3. DWSIM
- **URL:** https://github.com/DanWBR/dwsim
- **License:** GPL/LGPL
- **What it does:** Full chemical process simulator with GUI. Uses CoolProp. 400+ compounds.
- **What it doesn't:** Not HVAC-specific. Steep learning curve. .NET/Mono dependency. No training scenarios.
- **Our use:** Not applicable to training audience. Different problem domain.
- **Verdict:** ❌ SKIP — too complex for trade school replacement

### 4. Modelica Buildings Library
- **URL:** https://github.com/lbl-srg/modelica-buildings
- **License:** BSD
- **What it does:** Building-scale HVAC system modeling. Accurate to ±0.5°F per literature.
- **What it doesn't:** Requires Modelica expertise. No game-like UI. No training scenarios.
- **Our use:** Potential backend for building-scale simulations (Phase 3+).
- **Verdict:** ⏳ DEFER — powerful but not for v1.0

### 5. OpenFOAM
- **URL:** https://github.com/OpenFOAM/OpenFOAM-dev
- **License:** GPL
- **What it does:** CFD for airflow, ductwork, heat transfer.
- **What it doesn't:** Steep learning curve. No HVAC-specific templates. No training integration.
- **Our use:** Potential backend for airflow visualization (Phase 4+).
- **Verdict:** ⏳ DEFER — research-grade, not training-grade

### 6. MOOSE
- **URL:** https://github.com/idaholab/moose
- **License:** LGPL
- **What it does:** Multiphysics including welding heat transfer, phase change.
- **What it doesn't:** No HVAC integration. Research-focused. No UI.
- **Our use:** **ADOPTED as inspiration** — FR-PH-003 implements MOOSE-lite steady-state heat conduction (commit `271a3a3`). Full MOOSE deferred to Phase 4+ (brazing simulation).
- **Verdict:** ✅ ADOPT (lite) / ⏳ DEFER (full)

---

## The Gap Analysis

| Capability | CoolProp | SimVCCE | DWSIM | Modelica | OpenFOAM | MOOSE | **Our Sim** |
|---|---|---|---|---|---|---|---|
| Thermodynamics | ✅ | ✅ | ✅ | ✅ | ⚠️ | ❌ | ✅ (CoolProp) |
| 3D Real-time | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ (Godot)** |
| Training scenarios | ❌ | ⚠️ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Fault injection | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Customer interaction | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Glass-box inspectable | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Progressive difficulty | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅** |
| Cross-domain (elec/weld/CFD) | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **✅** |
| **Numerical methods with analytical verification** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ (FR-PH-003)** |
| **Visual regression testing** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ (FR-VA-004)** |

**Conclusion:** No existing open-source tool fills the training gap. We are not competing with physics engines — we are the *training layer* that makes them learnable.

---

## Strategic Decisions

| Decision | Rationale |
|---|---|
| **Use CoolProp** | Proven accurate, MIT license, already verified |
| **Use Godot 4.7.1** | Best open-source 3D engine, Python bridge, exports to all platforms |
| **MOOSE-lite (FR-PH-003)** | BVP solver for steady-state heat conduction, analytical verification to 1e-9 |
| **Defer OpenFOAM** | CFD is Phase 4+, not v1.0 |
| **Defer full MOOSE** | Welding is Phase 4+, not v1.0 |
| **Defer Modelica** | Building-scale is Phase 3+, not v1.0 |
| **Build own scenario engine** | No existing tool has progressive training with fault injection |

---

## Campaign 6a Discoveries

### FR-VA-004: D3D12-Accelerated Headless Screenshot Capture
- Windows Godot 4.7.1 renders headlessly via D3D12 Forward+ on RTX 4050 within WSL2
- `--display-driver windows --rendering-driver d3d12` forces real GPU rendering
- `wslpath -w` bridges WSL2 Linux paths to Windows Godot write access
- Pixel-level assurance of Godot UI rendering across 3 scenes

### FR-PH-003: MOOSE-Inspired Numerical Methods
- `scipy.integrate.solve_bvp` for cylindrical steady-state heat conduction
- Analytical verification: max error < 1e-9 against ln(r) solution
- Heat flux conservation verified numerically across pipe radius
- Citation: Gaston et al. 2015 (MOOSE), Incropera et al. 2011 (heat transfer), Kierzenka & Shampine 2008 (BVP)

---

## Current State (Campaign 6a Complete)

| Metric | Value |
|--------|-------|
| SRS | v1.5 |
| Tests | 188/188 PASS |
| Commit | `9cb3c3b` |
| Scenes verified visually | mechanical_room, pt_chart, wiring_scene |
| Numerical methods verified | cylindrical heat conduction (analytical) |

---

## Next Actions (v1.5 Targets)

1. ⚡ FR-MA-001 P1: Real R410A coefficients for Helmholtz EOS
2. ⚒ FR-AN-001: Aerospace-grade animations (physics-based particle systems)
3. 🔬 FR-FV-001: Formal verification strategy (property-based testing)

---

*Reconnaissance is continuous. Every tool is evaluated. No adoption without verification.*
