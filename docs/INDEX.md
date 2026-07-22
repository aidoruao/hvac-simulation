# HVAC Simulation — Documentation Index

**Project:** Free, non-proprietary HVAC simulation for trade school alternative  
**Repo:** https://github.com/aidoruao/hvac-simulation  
**Last Updated:** 2026-07-21  
**Ground Truth Commit:** `4508eae`  
**Test Count:** 282/292 PASS (282 Python + 12 Godot, 10 xfailed)  
**SRS Version:** v1.8 — **ACTIVE** (tag: v1.8)

---

## Quick Navigation

| I am a... | Start Here |
|-----------|------------|
| New developer or contributor | [RELEASE_NOTES_v1.6.md](RELEASE_NOTES_v1.6.md) → [README.md](README.md) → [CONTRIBUTING.md](CONTRIBUTING.md) |
| AI instance (Kimi, DeepSeek, Codewhale) | [KIMI_ONBOARDING.md](KIMI_ONBOARDING.md) → this file |
| Historian or auditor | [CHANGELOG.md](CHANGELOG.md) → [GEMINI_NBLM_HISTORIAN.md](GEMINI_NBLM_HISTORIAN.md) |
| Requirements engineer | [HVAC_SRS.md](HVAC_SRS.md) |
| Thermodynamics reviewer | [FORMULA_CITATIONS.md](FORMULA_CITATIONS.md) |
| Capability researcher | [RECONNAISSANCE.md](RECONNAISSANCE.md) |

---

## File Registry

| File | Purpose | Last Updated | Commit | Status |
|------|---------|--------------|--------|--------|
| [README.md](README.md) | One-page project overview + quickstart | 2026-07-19 | — | 🆕 NEW |
| [INDEX.md](INDEX.md) | This file — master navigation | 2026-07-19 | — | 🆕 NEW |
| [HVAC_SRS.md](HVAC_SRS.md) | Software Requirements Specification v1.8 | 2026-07-21 | `4508eae` | ✅ CURRENT |
| [INVESTIGATIONS.md](INVESTIGATIONS.md) | Investigation Manifest — active defects and root cause analyses | 2026-07-21 | `4508eae` | 🆕 NEW |
| [FORMULA_CITATIONS.md](FORMULA_CITATIONS.md) | Every formula traced to primary source | 2026-07-20 | `f04ef13` | ✅ CURRENT |
| [KIMI_ONBOARDING.md](KIMI_ONBOARDING.md) | AI/human developer environment rules | 2026-07-21 | `4508eae` | 🆕 UPDATED |
| [RECONNAISSANCE.md](RECONNAISSANCE.md) | Open-source tool survey + gap analysis | 2026-07-19 | — | 🆕 UPDATED |
| [GEMINI_NBLM_HISTORIAN.md](GEMINI_NBLM_HISTORIAN.md) | Campaign archive (1a–7a, immutable) | 2026-07-20 | `f04ef13` | ✅ CURRENT |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to add requirements, tests, formulas | 2026-07-19 | — | 🆕 NEW |
| [CHANGELOG.md](CHANGELOG.md) | Version history across all documents | 2026-07-20 | `f04ef13` | 🆕 UPDATED |

---

## Environment Invariants (Canonical)

| Invariant | Value |
|-----------|-------|
| Virtual environment | `~/hvac-simulation/venv` |
| pytest rootdir | `/home/idor/hvac-simulation` |
| Godot binary (Windows) | `/mnt/c/Users/Aidor/Godot_v4.7.1-stable_win64.exe` |
| Godot binary (Linux) | `~/hvac-simulation/godot` (4.3.stable) |
| Renderer | Forward Plus (headless D3D12) |
| Test count | 207 (195 Python + 12 Godot, 0 xfailed) |

---

## Campaign Status

| Campaign | Date | Key Deliverable | Commit |
|----------|------|-----------------|--------|
| 1a | 2026-07-16 | Foundation, 14 requirements | `ca54dc6` |
| 2a | 2026-07-16 | Glass box, state inspector | — |
| 3a | 2026-07-17 | 3D mechanical room, Godot 4.7.1 | `d4d2581` |
| 4a | 2026-07-17–18 | Wiring, SEER/COP | — |
| 5a | 2026-07-18 | Godot regression, Heredoc War resolved | `d4d2581` |
| 6a | 2026-07-18–19 | Visual regression (FR-VA-004), MOOSE-lite (FR-PH-003) | `f1e5a8d`, `271a3a3`, `9cb3c3b` |
| 7a | 2026-07-20 | Helmholtz EOS (FR-MA-001), first-principles R410A | `9934a9d` |
| 8a | 2026-07-20 | Full v1.6 release — 44 requirements, 279 tests | `f0287ca` |

---

## Active Requirements (44/44 PASS)

| ID | Status | Tests | Location |
|----|--------|-------|----------|
| FR-PH-001 | ✅ PASS | 15/15 | `refrigerants.py` |
| FR-PH-002 | ✅ PASS | 4/4 | `refrigerants.py` |
| FR-PH-003 | ✅ PASS | 2/2 | `tests/moose_lite/` |
| FR-SC-001 | ✅ PASS | 23/23 | `scenarios.py` |
| FR-SC-002 | ✅ PASS | 8/8 | `validation.py` |
| FR-ED-001 | ✅ PASS | 6/6 | `session_tracker.py` |
| FR-ED-002 | ✅ PASS | 4/4 | `scenarios.py` |
| FR-ED-003 | ✅ PASS | 5/5 | `session_tracker.py` |
| FR-ED-004 | ✅ PASS | 13/13 | `i18n.py`, `locales/es.json` |
| FR-SF-001 | ✅ PASS | 12/12 | `FORMULA_CITATIONS.md` |
| FR-SF-002 | ✅ PASS | 12/12 | `state_inspector.py` |
| FR-SF-003 | ✅ PASS | — | `HVAC_SRS.md` |
| FR-3D-001 | ✅ PASS | 14/14 | `mechanical_room_bridge.py` |
| FR-3D-002 | ✅ PASS | 4/4 | `mechanical_room.gd` |
| FR-EL-001 | ✅ PASS | 21/21 | `thermostat_wiring.py` |
| FR-EL-002 | ✅ PASS | 2/2 | `wiring_scene.gd` |
| FR-TD-008 | ✅ PASS | 18/18 | `cop_calculator.py` |
| FR-TD-009 | ✅ PASS | 9/9 | `seer_calculator.py` |
| FR-PF-002 | ✅ PASS | 4/4 | `frame_rate_benchmark.gd` |
| FR-VI-001 | ✅ PASS | 6/6 | `pt_chart.gd` |
| FR-VI-002 | ✅ PASS | 4/4 | `pt_chart.gd` |
| FR-VA-001 | ✅ PASS | 8/8 | `validation.py` |
| FR-VA-002 | ✅ PASS | 5/5 | `validation.py` |
| FR-VA-003 | ✅ PASS | 10/10 | `test_godot_regression.py` |
| FR-VA-004 | ✅ PASS | 3/3 | `test_screenshot_diff.py` |
| **FR-MA-001** | ✅ PASS | 19/19 | `math_model/helmholtz_eos.py` |

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*  
*No agent amnesia. The record is the immune system.*

## Project Invariants

- **Structural Fix Mandate (FR-SV-005):** No UI patches at integration boundaries. Data contract repair only.
- See: docs/AI_BEHAVIORAL_ARCHETYPES.md
