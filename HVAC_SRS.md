# HVAC Simulation — Software Requirements Specification v0.6

**Document ID:** HVAC-SRS-001  
**Version:** 0.6  
**Date:** 2026-07-17  
**Status:** ACTIVE — FR-EL-001 PASS, FR-TD-008 PASS, 132/132 tests verified

---

## 1. Purpose

Free, non-proprietary HVAC simulation for trade school alternative. No vendor lock-in. Every formula cited with primary sources. Glass box enforced at code level.

---

## 2. Requirements

| ID | Requirement | Status | Tests | Verification |
|:---|:---|:---|:---|:---|
| FR-PH-001 | Multi-refrigerant physics (R22, R134a, R32, R410A, R1234yf) | **PASS** | 15/15 | CoolProp 8.0.0 Helmholtz EOS |
| FR-PH-002 | A2L safety classification display | **PASS** | 4/4 | ASHRAE Standard 34-2022 |
| FR-SC-001 | Training scenario engine (5+ scenarios) | **PASS** | 23/23 | 20 unique faults |
| FR-SC-002 | Progressive fault injection | **PASS** | 8/8 | Divergence detection |
| FR-ED-001 | Session tracking and audit logging | **PASS** | 6/6 | ISO 27001 traceability |
| FR-ED-002 | Hint system with pedagogical scaffolding | **PASS** | 4/4 | Three-tier hint structure |
| FR-ED-003 | Performance analytics (pass/fail/time) | **PASS** | 5/5 | Per-scenario metrics |
| FR-SF-001 | Every formula cited with primary source | **PASS** | 12/12 | FORMULA_CITATIONS.md |
| FR-SF-002 | All states inspectable (glass box) | **PASS** | 12/12 | state_inspector.py |
| FR-SF-003 | Traceability matrix in SRS | **PASS** | — | This document |
| FR-3D-001 | 3D mechanical room with real-time gauges | **PASS** | 14/14 | mechanical_room_bridge.py |
| **FR-EL-001** | **Thermostat wiring schematic** | **PASS** | **21/21** | **thermostat_wiring.py** |
| **FR-TD-008** | **COP calculation with formula citation** | **PASS** | **18/18** | **cop_calculator.py** |
| FR-VI-001 | Interactive PT chart (Godot) | **PASS** | 6/6 | JSON data bridge |
| FR-VI-002 | Refrigerant switching in PT chart | **PASS** | 4/4 | Real-time update |
| FR-VA-001 | Validation layer — divergence detection | **PASS** | 8/8 | ±2% threshold |
| FR-VA-002 | Reference data comparison | **PASS** | 5/5 | NIST REFPROP cross-check |

**Total: 132/132 tests passing**

---

## 3. Architecture
┌─────────────────────────────────────────┐
│           Godot 4.2 (Frontend)          │
│  3D Mechanical Room | PT Chart | Wiring  │
├─────────────────────────────────────────┤
│         Python Backend (WSL2)           │
│  Physics | Scenarios | Validation       │
│  Session | State Inspector | Audit      │
│  COP Calculator | Wiring Simulator    │
├─────────────────────────────────────────┤
│         CoolProp 8.0.0 (EOS)            │
│      Helmholtz Equations of State       │
└─────────────────────────────────────────┘
plain

---

## 4. Traceability Matrix

| Requirement | Source File | Test File | Commit |
|:---|:---|:---|:---|
| FR-PH-001 | `refrigerants.py` | `test_physics.py` | `7ef3477` |
| FR-PH-002 | `refrigerants.py` | `test_physics.py` | `0f123dc` |
| FR-SC-001 | `scenarios.py` | `test_scenarios.py` | `b21db00` |
| FR-SC-002 | `scenarios.py` | `test_scenarios.py` | `b21db00` |
| FR-ED-001 | `session_tracker.py` | `test_session_tracker.py` | `6d710f2` |
| FR-ED-002 | `session_tracker.py` | `test_session_tracker.py` | `6d710f2` |
| FR-ED-003 | `session_tracker.py` | `test_session_tracker.py` | `6d710f2` |
| FR-SF-001 | `FORMULA_CITATIONS.md` | `test_citations.py` | `6d710f2` |
| FR-SF-002 | `state_inspector.py` | `test_state_inspector.py` | `2d32296` |
| FR-SF-003 | `HVAC_SRS.md` | — | `6d710f2` |
| FR-3D-001 | `mechanical_room_bridge.py` | `test_mechanical_room_bridge.py` | `96748dd` |
| **FR-EL-001** | **`thermostat_wiring.py`** | **`test_thermostat_wiring.py`** | **`887dde0`** |
| **FR-TD-008** | **`cop_calculator.py`** | **`test_cop_calculator.py`** | **`95fccc2`** |
| FR-VI-001 | `pt_chart.gd` | Manual + JSON bridge | `b21db00` |
| FR-VI-002 | `pt_chart.gd` | Manual + JSON bridge | `b21db00` |
| FR-VA-001 | `validation.py` | `test_validation.py` | `b21db00` |
| FR-VA-002 | `validation.py` | `test_validation.py` | `b21db00` |

---

## 5. Next Phase (v0.7 Target)

| Priority | Requirement | Description |
|:---|:---|:---|
| P1 | FR-PF-002 | Frame rate benchmark in Godot |
| P2 | FR-3D-002 | Animated compressor/gauge models in mechanical room |
| P3 | FR-EL-002 | Godot wiring scene integration |
| P4 | FR-TD-009 | Seasonal energy efficiency ratio (SEER) calculation |

---

## 6. Changelog

| Version | Date | Changes |
|:---|:---|:---|
| v0.1 | 2026-07-16 | Initial SRS — 14 requirements |
| v0.2 | 2026-07-16 | Updated traceability matrix |
| v0.3 | 2026-07-16 | FR-SC-002/FR-ED-003/FR-SF-003 PASS, 64 tests |
| v0.4 | 2026-07-16 | FR-SF-002 PASS, state inspector, 76/76 tests |
| v0.5 | 2026-07-16 | FR-3D-001 PASS, mechanical room, 90/90 tests |
| **v0.6** | **2026-07-17** | **FR-EL-001 + FR-TD-008 PASS, wiring + COP, 132/132 tests** |

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*
