# HVAC Simulation — Software Requirements Specification v0.3

## 1. Purpose
Physics-accurate, real-time 3D HVAC training simulator. Free forever. Glass box.
Replaces trade school with verifiable, inspectable, open-source training.

## 2. Definitions
- **Saturation pressure (P_sat):** Pressure at which liquid and vapor coexist at equilibrium
- **Superheat:** Temperature above saturation temperature at a given pressure
- **Subcooling:** Temperature below saturation temperature at a given pressure
- **Glass box:** Every state variable inspectable and traceable to source
- **Falsifies if:** Conditions under which a claim or test is proven wrong
- **Divergence:** Difference between calculated value and independent reference

## 3. Functional Requirements

### 3.1 Thermodynamics (FR-TD)
| ID | Requirement | Verification | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-TD-001 | Calculate R410A P_sat within ±0.5% of CoolProp 8.0.0 | test_r410a_saturation_pressure | Result differs >0.5% | ✅ PASS | 7ef3477 |
| FR-TD-002 | Calculate R410A critical point within ±0.5% | test_r410a_critical_point | Result differs >0.5% | ✅ PASS | 7ef3477 |
| FR-TD-003 | Calculate latent heat of vaporization | test_r410a_latent_heat | h_fg < refrigerant-specific min | ✅ PASS | 7ef3477 |
| FR-TD-004 | Calculate liquid/vapor density | test_r410a_density | rho_liq < rho_vap | ✅ PASS | 7ef3477 |
| FR-TD-005 | Calculate superheat/subcooling | test_superheat_calculation | T_sat error >1K | ✅ PASS | 7ef3477 |
| FR-TD-006 | Support R22, R134a, R32, R410A, R1234yf | test_refrigerants.py | Any refrigerant fails ±0.5% | ✅ PASS | 0c84134 |
| FR-TD-007 | Display PT chart interactively | Godot PT chart + pt_charts.py | Chart deviates from CoolProp | ✅ PASS | 7f912dd |
| FR-TD-008 | Calculate COP (Coefficient of Performance) | Future: test_cop.py | COP error >2% | ⏳ TODO | — |

### 3.2 Fluid Dynamics (FR-FD)
| ID | Requirement | Verification | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-FD-001 | Model airflow through ductwork | Future: OpenFOAM integration | Pressure drop error >10% | ⏳ TODO | — |
| FR-FD-002 | Calculate CFM from fan curve | Future: test_fan.py | CFM error >5% | ⏳ TODO | — |

### 3.3 Electrical (FR-EL)
| ID | Requirement | Verification | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-EL-001 | Simulate thermostat wiring | Future: Godot schematic | Short circuit not detected | ⏳ TODO | — |
| FR-EL-002 | Calculate amp draw from compressor | Future: test_amps.py | Amp error >5% | ⏳ TODO | — |

### 3.4 Welding/Brazing (FR-WB)
| ID | Requirement | Verification | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-WB-001 | Model heat distribution during brazing | Future: MOOSE integration | Temp curve deviates >10% | ⏳ TODO | — |
| FR-WB-002 | Detect overheating | Future: test_overheat.py | Overheat not flagged | ⏳ TODO | — |

### 3.5 Scenarios (FR-SC)
| ID | Requirement | Verification | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-SC-001 | "First day as a tech" walkthrough | scenarios.py + test_scenarios.py | User cannot complete in 30 min | ✅ PASS | 834afff |
| FR-SC-002 | 20+ unique fault injections | scenarios_extended.py + test | <20 faults | ✅ PASS | 4272b88 |
| FR-SC-003 | Customer interaction simulation | scenarios.py dialogue | Customer response nonsensical | ⚠️ PARTIAL | 834afff |
| FR-SC-004 | Progressive difficulty (5 levels) | test_scenarios.py + extended | Level 1 requires expert knowledge | ✅ PASS | 834afff |

### 3.6 Performance (FR-PF)
| ID | Requirement | Target | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-PF-001 | Physics calculation latency | <1 ms per call | >5 ms average | ✅ PASS | benchmark_latency.py |
| FR-PF-002 | Godot frame rate | ≥60 FPS | <30 FPS sustained | ⏳ TODO | — |
| FR-PF-003 | Memory footprint | <2 GB | >4 GB | ⏳ TODO | — |

### 3.7 Safety (FR-SF)
| ID | Requirement | Rationale | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-SF-001 | Warn if simulation diverges >5% from NIST REFPROP | Prevent false confidence | Divergence >5% not flagged | ✅ PASS | d8a866c |
| FR-SF-002 | All states inspectable | Glass box principle | Any state hidden | ⚠️ PARTIAL | 7f912dd |
| FR-SF-003 | Every formula cited | No hidden assumptions | Formula without source | ✅ PASS | 6e90ccc |
| FR-SF-004 | A2L safety training | Charge limits, ventilation | A2L hazard not flagged | ⚠️ PARTIAL | 0c84134 |

### 3.8 Educational (FR-ED)
| ID | Requirement | Target | Falsifies If | Status | Commit |
|---|---|---|---|---|---|
| FR-ED-001 | Progressive difficulty | 5 levels: basic → expert | Level 1 requires expert knowledge | ✅ PASS | 834afff |
| FR-ED-002 | Pass/fail with reasoning | Explain why answer is wrong | Wrong answer accepted | ✅ PASS | 834afff |
| FR-ED-003 | Time-tracked sessions | Log time per scenario | Time not recorded | ✅ PASS | 6d710f2 |

## 4. Architecture
┌─────────────────────────────────────────┐
│  LAYER 4: UI/UX (Godot 4.x)            │
│  ├── 2D PT chart (interactive)         │ ✅
│  ├── 3D mechanical room (planned)      │ ⏳
│  ├── Interactive wiring schematic      │ ⏳
│  └── Assessment dashboard              │ ⏳
├─────────────────────────────────────────┤
│  LAYER 3: Integration (Python)         │
│  ├── CoolProp wrapper                  │ ✅
│  ├── Validation layer                  │ ✅
│  ├── Scenario engine                   │ ✅
│  ├── Session tracker                   │ ✅
│  ├── OpenFOAM bridge                   │ ⏳
│  └── MOOSE bridge                      │ ⏳
├─────────────────────────────────────────┤
│  LAYER 2: Physics Engines              │
│  ├── CoolProp (thermodynamics)         │ ✅ Verified
│  ├── OpenFOAM (CFD)                    │ ⏳
│  └── MOOSE (multiphysics)              │ ⏳
├─────────────────────────────────────────┤
│  LAYER 1: Platform                     │
│  ├── Python 3.12 + venv                │ ✅
│  ├── Godot 4.3/4.7                     │ ✅
│  └── CUDA (RTX 4050)                   │ ✅
└─────────────────────────────────────────┘
plain

## 5. Test Summary
| Suite | Tests | Passing | Commit |
|---|---|---|---|
| test_physics.py | 5 | 5 | 7ef3477 |
| test_refrigerants.py | 14 | 14 | 0c84134 |
| test_scenarios.py | 13 | 13 | 834afff |
| test_validation.py | 9 | 9 | d8a866c |
| test_session_tracker.py | 11 | 11 | 6d710f2 |
| test_scenarios_extended.py | 12 | 12 | 4272b88 |
| **Total** | **64** | **64** | — |

## 6. Changelog
| Version | Date | Changes |
|---|---|---|
| v0.1 | 2026-07-16 | Initial SRS. 5/5 FR-TD verified. |
| v0.2 | 2026-07-16 | Added validation layer, interactive PT chart, scenario engine. 41/41 tests. |
| v0.3 | 2026-07-16 | Added session tracking, 20+ faults, formula citations. 64/64 tests. FR-SC-002, FR-ED-003, FR-SF-003 PASS. |

## 7. Next Steps (Prioritized)
1. **FR-SF-002:** Full state inspectability — integrate session tracker with scenarios
2. **3D mechanical room:** Godot 3D scene with gauge models
3. **FR-EL-001:** Thermostat wiring schematic
4. **FR-TD-008:** COP calculation
5. **FR-PF-002:** Frame rate benchmark in Godot

