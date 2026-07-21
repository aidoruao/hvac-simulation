# KIMI ONBOARDING — HVAC Simulation

**Last Updated:** 2026-07-20 (Campaign 7a, FR-MA-001 complete)  
**Status:** LOCKED  
**Current Commit:** `f04ef13`  
**SRS Version:** v1.6  
**Test Count:** 207/207 PASS (195 Python + 12 Godot, 0 xfailed)  
**Docs Root:** `docs/INDEX.md`

---

## Environment Invariants (NEVER violate)

| Invariant | Value | Violation Consequence |
|-----------|-------|----------------------|
| Virtual environment | `~/hvac-simulation/venv` | System-wide pip corruption |
| pytest rootdir | `/home/idor/hvac-simulation` | WSL2 kernel test discovery, `SystemExit` |
| Godot binary (Windows) | `/mnt/c/Users/Aidor/Godot_v4.7.1-stable_win64.exe` | "Executable not found" |
| Godot binary (Linux) | `~/hvac-simulation/godot` (4.3.stable) | Version mismatch |
| Renderer | Forward Plus (headless D3D12) | Screenshot corruption |
| Test count | 207 (195 Python + 12 Godot, 0 xfailed) | False confidence in broken state |
| Documentation root | `docs/INDEX.md` | Navigation failure |

---

## Shell Escaping Rule

- **NEVER** use heredoc (`<< EOF`) for GDScript or any file with `$`, `\n`, `#`
- **ALWAYS** use `echo <base64> | base64 -d > file` or Python intermediate file
- **Rationale:** 7 consecutive failures in Campaign 5a (Heredoc War)

---

## Feedback Loop Protocol

```
1. AI Generates → command or code block
2. Human Pastes → into WSL2 terminal (`idor@Tony:~$`)
3. Human Reports → stdout/stderr back to AI
4. AI Analyzes → waits for evidence before next step
```

AI must end every turn by explicitly asking for terminal output.

---

## Campaign Status

| Campaign | Date | Deliverables | Commit |
|----------|------|--------------|--------|
| 1a | 2026-07-16 | Foundation, 14 requirements | `ca54dc6` |
| 2a | 2026-07-16 | Glass box, state inspector | — |
| 3a | 2026-07-17 | 3D mechanical room, Godot 4.7.1 | `d4d2581` |
| 4a | 2026-07-17–18 | Wiring, SEER/COP | — |
| 5a | 2026-07-18 | Godot regression, Heredoc War resolved | `d4d2581` |
| 6a | 2026-07-18–19 | Visual regression (FR-VA-004), MOOSE-lite (FR-PH-003) | `f1e5a8d`, `271a3a3`, `9cb3c3b` |
| 7a | 2026-07-20 | Helmholtz EOS (FR-MA-001), first-principles R410A | `9934a9d`, `2d96437`, `f04ef13` |

---

## Active Requirements (25/25 PASS)

| ID | Status | Tests | Location |
|----|--------|-------|----------|
| FR-PH-001 | PASS | 15/15 | `refrigerants.py` |
| FR-PH-002 | PASS | 4/4 | `refrigerants.py` |
| FR-PH-003 | PASS | 2/2 | `tests/moose_lite/` |
| FR-SC-001 | PASS | 23/23 | `scenarios.py` |
| FR-SC-002 | PASS | 8/8 | `validation.py` |
| FR-ED-001 | PASS | 6/6 | `session_tracker.py` |
| FR-ED-002 | PASS | 4/4 | `scenarios.py` |
| FR-ED-003 | PASS | 5/5 | `session_tracker.py` |
| FR-ED-004 | PASS | 13/13 | `i18n.py`, `locales/es.json` |
| FR-SF-001 | PASS | 12/12 | `docs/FORMULA_CITATIONS.md` |
| FR-SF-002 | PASS | 12/12 | `state_inspector.py` |
| FR-SF-003 | PASS | — | `docs/HVAC_SRS.md` |
| FR-3D-001 | PASS | 14/14 | `mechanical_room_bridge.py` |
| FR-3D-002 | PASS | 4/4 | `mechanical_room.gd` |
| FR-EL-001 | PASS | 21/21 | `thermostat_wiring.py` |
| FR-EL-002 | PASS | 2/2 | `wiring_scene.gd` |
| FR-TD-008 | PASS | 18/18 | `cop_calculator.py` |
| FR-TD-009 | PASS | 9/9 | `seer_calculator.py` |
| FR-PF-002 | PASS | 4/4 | `frame_rate_benchmark.gd` |
| FR-VI-001 | PASS | 6/6 | `pt_chart.gd` |
| FR-VI-002 | PASS | 4/4 | `pt_chart.gd` |
| FR-VA-001 | PASS | 8/8 | `validation.py` |
| FR-VA-002 | PASS | 5/5 | `validation.py` |
| FR-VA-003 | PASS | 10/10 | `test_godot_regression.py` |
| FR-VA-004 | PASS | 3/3 | `test_screenshot_diff.py` |
| **FR-MA-001** | **PASS** | **19/19** | **`math_model/helmholtz_eos.py`** |

**TOTAL: 25/25 PASS — 207/207 tests (0 xfailed)**

---

## Next Phase (v1.6 Target)

| ID | Priority | Description |
|----|----------|-------------|
| FR-MA-002 | P1 | Next refrigerant: R32 Helmholtz EOS (reuse FR-MA-001 framework) |
| FR-MA-001-L1 | P2 | Liquid-region 6% error reduction |
| FR-AN-001 | P3 | Aerospace-grade animations |
| FR-FV-001 | P4 | Formal verification (Lean 4 / Coq) |

---

## Canonical Historian

**`docs/GEMINI_NBLM_HISTORIAN.md`** is the single source of truth for all campaigns (1a–6a).
Read it before every session. Update it after every campaign.

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*  
*No agent amnesia. The record is the immune system.*


## AI Behavioral Archetypes Observed

**Turn 240:** Kimi Web AI proposed UI patch (pt_chart.gd) for pt_data.json format mismatch.
Human operator rejected patch, demanded structural fix (generate_pt_fast.py).
**Pattern:** AI defaults to path of least resistance at integration boundaries.
**Countermeasure:** Human must enforce structural repair protocol (FR-SV-005).

> ⚠️ **WARNING — Read this if you are an AI agent:**
> Your default at SIT/POST is to patch symptoms. This is known and documented.
> Your required behavior is to repair structures. This is enforced.
> See: docs/AI_BEHAVIORAL_ARCHETYPES.md
