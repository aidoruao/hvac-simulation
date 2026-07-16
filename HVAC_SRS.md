# HVAC Simulation — Software Requirements Specification v0.1

## 1. Purpose
Physics-accurate, real-time 3D HVAC training simulator. Free forever. Glass box.
Replaces trade school with verifiable, inspectable, open-source training.

## 2. Definitions
- **Saturation pressure (P_sat):** Pressure at which liquid and vapor coexist at equilibrium
- **Superheat:** Temperature above saturation temperature at a given pressure
- **Subcooling:** Temperature below saturation temperature at a given pressure
- **Glass box:** Every state variable inspectable and traceable to source
- **Falsifies if:** Conditions under which a claim or test is proven wrong

## 3. Functional Requirements

### 3.1 Thermodynamics (FR-TD)
| ID | Requirement | Verification | Falsifies If |
|---|---|---|---|
| FR-TD-001 | Calculate R410A P_sat within ±0.5% of CoolProp 8.0.0 | test_r410a_saturation_pressure | Result differs >0.5% |
| FR-TD-002 | Calculate R410A critical point within ±0.5% | test_r410a_critical_point | Result differs >0.5% |
| FR-TD-003 | Calculate latent heat of vaporization | test_r410a_latent_heat | h_fg < 150 kJ/kg |
| FR-TD-004 | Calculate liquid/vapor density | test_r410a_density | rho_liq < rho_vap |
| FR-TD-005 | Calculate superheat/subcooling | test_superheat_calculation | T_sat calculation error >1K |
| FR-TD-006 | Support R22, R134a, R32, R410A, R454B | Future: test_refrigerants.py | Any refrigerant fails ±0.5% |
| FR-TD-007 | Display PT chart interactively | Future: Godot UI | Chart deviates from CoolProp |
| FR-TD-008 | Calculate COP (Coefficient of Performance) | Future: test_cop.py | COP error >2% |

### 3.2 Fluid Dynamics (FR-FD)
| ID | Requirement | Verification | Falsifies If |
|---|---|---|---|
| FR-FD-001 | Model airflow through ductwork | Future: OpenFOAM integration | Pressure drop error >10% |
| FR-FD-002 | Calculate CFM from fan curve | Future: test_fan.py | CFM error >5% |

### 3.3 Electrical (FR-EL)
| ID | Requirement | Verification | Falsifies If |
|---|---|---|---|
| FR-EL-001 | Simulate thermostat wiring | Future: Godot schematic | Short circuit not detected |
| FR-EL-002 | Calculate amp draw from compressor | Future: test_amps.py | Amp error >5% |

### 3.4 Welding/Brazing (FR-WB)
| ID | Requirement | Verification | Falsifies If |
|---|---|---|---|
| FR-WB-001 | Model heat distribution during brazing | Future: MOOSE integration | Temp curve deviates >10% |
| FR-WB-002 | Detect overheating | Future: test_overheat.py | Overheat not flagged |

### 3.5 Scenarios (FR-SC)
| ID | Requirement | Verification | Falsifies If |
|---|---|---|---|
| FR-SC-001 | "First day as a tech" walkthrough | Future: playtest | User cannot complete in 30 min |
| FR-SC-002 | 20+ unique fault injections | Future: fault_matrix.md | <20 faults implemented |
| FR-SC-003 | Customer interaction simulation | Future: dialogue_tree.py | Customer response nonsensical |

### 3.6 Performance (FR-PF)
| ID | Requirement | Target | Falsifies If |
|---|---|---|---|
| FR-PF-001 | Physics calculation latency | <1 ms per call | >5 ms average |
| FR-PF-002 | Godot frame rate | ≥60 FPS | <30 FPS sustained |
| FR-PF-003 | Memory footprint | <2 GB | >4 GB |

### 3.7 Safety (FR-SF)
| ID | Requirement | Rationale | Falsifies If |
|---|---|---|---|
| FR-SF-001 | Warn if simulation diverges >5% from NIST REFPROP | Prevent false confidence | Divergence >5% not flagged |
| FR-SF-002 | All states inspectable | Glass box principle | Any state hidden |
| FR-SF-003 | Every formula cited | No hidden assumptions | Formula without source |

### 3.8 Educational (FR-ED)
| ID | Requirement | Target | Falsifies If |
|---|---|---|---|
| FR-ED-001 | Progressive difficulty | 5 levels: basic → expert | Level 1 requires expert knowledge |
| FR-ED-002 | Pass/fail with reasoning | Explain why answer is wrong | Wrong answer accepted |
| FR-ED-003 | Time-tracked sessions | Log time per scenario | Time not recorded |

## 4. Traceability Matrix
| Requirement | Test | Status | Commit |
|---|---|---|---|
| FR-TD-001 | test_r410a_saturation_pressure | ✅ PASS | 7ef3477 |
| FR-TD-002 | test_r410a_critical_point | ✅ PASS | 7ef3477 |
| FR-TD-003 | test_r410a_latent_heat | ✅ PASS | 7ef3477 |
| FR-TD-004 | test_r410a_density | ✅ PASS | 7ef3477 |
| FR-TD-005 | test_superheat_calculation | ✅ PASS | 7ef3477 |
| FR-TD-006 | test_refrigerants.py | ⏳ TODO | — |
| FR-TD-007 | Godot PT chart UI | ⏳ TODO | — |
| FR-TD-008 | test_cop.py | ⏳ TODO | — |
| FR-FD-001 | OpenFOAM duct model | ⏳ TODO | — |
| FR-EL-001 | Godot wiring schematic | ⏳ TODO | — |
| FR-WB-001 | MOOSE heat model | ⏳ TODO | — |
| FR-SC-001 | Playtest report | ⏳ TODO | — |
| FR-SC-002 | fault_matrix.md | ⏳ TODO | — |
| FR-PF-001 | benchmark_latency.py | ⏳ TODO | — |

## 5. Architecture
┌─────────────────────────────────────────┐
│  LAYER 4: UI/UX (Godot 4.x)            │
│  ├── 3D mechanical room                │
│  ├── Interactive PT chart              │
│  ├── Wiring schematic                  │
│  └── Assessment dashboard              │
├─────────────────────────────────────────┤
│  LAYER 3: Integration (Python)         │
│  ├── CoolProp wrapper                  │
│  ├── OpenFOAM bridge                   │
│  ├── MOOSE bridge                      │
│  └── Scenario runner                   │
├─────────────────────────────────────────┤
│  LAYER 2: Physics Engines              │
│  ├── CoolProp (thermodynamics)         │
│  ├── OpenFOAM (CFD)                    │
│  └── MOOSE (multiphysics)              │
├─────────────────────────────────────────┤
│  LAYER 1: Platform                     │
│  ├── Python 3.12                       │
│  ├── Godot 4.3                         │
│  └── CUDA (RTX 4050)                   │
└─────────────────────────────────────────┘
plain

## 6. Changelog
| Version | Date | Changes |
|---|---|---|
| v0.1 | 2026-07-16 | Initial SRS. 5/5 FR-TD requirements verified. |

## 7. Next Steps
1. FR-TD-006: Add R22, R134a, R32, R454B support
2. FR-PF-001: Benchmark calculation latency
3. Reconnaissance: Catalogue existing open-source HVAC simulators
