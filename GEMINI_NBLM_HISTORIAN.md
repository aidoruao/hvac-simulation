# GEMINI_NBLM_HISTORIAN.md

**Document ID:** HVAC-HIST-001
**Role:** Single Source of Truth for All Campaigns (1a–6a)
**Status:** ACTIVE — Curated by Gemini NBLM (NotebookLM Historian)
**Last Updated:** 2026-07-19

---

## 1. Purpose

This document is the **canonical historical record** of the HVAC Simulation project. It exists to prevent **Agent Amnesia** — the recurring failure mode where LLMs forget project invariants, rediscover known paths, and hallucinate blank-slate environments.

Every AI instance (Kimi, DeepSeek, Gemini, Claude, Grok) must read this file before proposing any mutation to the codebase.

---

## 2. Campaign Archive

### Campaign 1a: Foundation (2026-07-16)
**Scope:** Initial SRS, refrigerant physics, basic scenarios
**Key Deliverables:**
- 14 requirements defined
- CoolProp 8.0.0 integration (Helmholtz EOS)
- First test suite: 64 tests PASS
**Commit:** ca54dc6
**AI:** Kimi

### Campaign 2a: Glass Box & State Inspector (2026-07-16)
**Scope:** Traceability, state inspection, formula citations
**Key Deliverables:**
- FR-SF-002 PASS (glass box enforced)
- `state_inspector.py` — every state inspectable
- FORMULA_CITATIONS.md v1.0
**Commit:** (multiple)
**AI:** Kimi

### Campaign 3a: 3D Mechanical Room (2026-07-17)
**Scope:** Godot 4.7.1 integration, animated compressor/gauge models
**Key Deliverables:**
- FR-3D-001 PASS (3D mechanical room)
- FR-3D-002 PASS (animated models)
- `mechanical_room_bridge.py` — Python ↔ Godot JSON bridge
**Commit:** d4d2581
**AI:** Kimi + Copilot audit

### Campaign 4a: Wiring & SEER (2026-07-17–18)
**Scope:** Thermostat wiring schematic, SEER/COP calculations
**Key Deliverables:**
- FR-EL-001 PASS (wiring schematic)
- FR-EL-002 PASS (Godot wiring scene)
- FR-TD-008 PASS (COP calculator)
- FR-TD-009 PASS (SEER calculator)
**Commit:** (multiple)
**AI:** Kimi

### Campaign 5a: Godot Regression & Heredoc War (2026-07-18)
**Scope:** Automated Godot testing, headless rendering, shell escaping
**Key Deliverables:**
- FR-VA-003 PASS (Godot regression harness)
- **Heredoc War:** 7 consecutive failed attempts to write GDScript via heredoc (`<< EOF`)
- **Resolution:** Base64 Encoding Rule established — `echo <base64> | base64 -d > file`
- D3D12/RTX 4050 headless rendering path confirmed
**Commit:** d4d2581
**AI:** Kimi + Google AI (Muse Spark) audit
**Critical Invariant:** NEVER use heredocs for GDScript. ALWAYS use Base64 or Python intermediate files.

### Campaign 6a: Visual Regression & MOOSE-lite (2026-07-18–19)
**Scope:** Screenshot diff testing, advanced thermodynamics
**Key Deliverables:**
- FR-VA-004 PASS (visual regression, screenshot diff)
- FR-PH-003 PASS (MOOSE-inspired steady-state heat conduction solver)
- 188/188 tests PASS (176 Python + 12 Godot)
**Commits:** f1e5a8d (FR-VA-004), 271a3a3 (FR-PH-003)
**AI:** Kimi + Gemini NBLM (historian/auditor)
**Ground Truth:**
- `venv` path: `~/hvac-simulation/venv`
- Godot binary: `/mnt/c/Users/Aidor/Godot_v4.7.1-stable_win64.exe`
- pytest rootdir: `/home/idor/hvac-simulation`
- Test count invariant: 188/188 PASS

---

## 3. The AI Straightjacket (Canonical Rules)

### 3.1 Environment Invariants (NEVER violate)
| Invariant | Value | Violation Consequence |
|-----------|-------|----------------------|
| Virtual environment | `~/hvac-simulation/venv` | System-wide pip corruption |
| Godot version | 4.7.1-stable | API mismatch, method signature errors |
| Godot binary path | `/mnt/c/Users/Aidor/Godot_v4.7.1-stable_win64.exe` | "Executable not found" |
| pytest rootdir | `/home/idor/hvac-simulation` | WSL2 kernel test discovery, `SystemExit` |
| Test count | 188 (176 Python + 12 Godot) | False confidence in broken state |
| Renderer | Forward Plus (headless D3D12) | Screenshot corruption, visual regression fail |

### 3.2 Shell Escaping Mandate
**Rule:** For any file containing `$`, `\n`, `#`, or GDScript syntax:
- **FORBIDDEN:** `cat << EOF > file.gd` (heredoc)
- **REQUIRED:** `echo <base64> | base64 -d > file.gd`
- **ALTERNATIVE:** Python one-liner with `open().write()`

**Rationale:** Bash interpolates `$` as variable expansion. Heredocs eat GDScript `$Node` references and escape sequences. Seven consecutive failures in Campaign 5a proved this invariant.

### 3.3 The Feedback Loop Protocol
```
1. AI Generates → command or code block
2. Human Pastes → into WSL2 terminal (`idor@Tony:~$`)
3. Human Reports → stdout/stderr back to AI
4. AI Analyzes → waits for evidence before next step
```
**AI must end every turn by explicitly asking for terminal output.**
**AI must never assume a command worked without seeing evidence.**

### 3.4 Path Mapping
WSL2 ↔ Windows bridge for Godot:
```bash
wslpath -w /home/idor/hvac-simulation/godot_project
# Output: \\wsl$\Ubuntu\home\idor\hvac-simulation\godot_project
```

---

## 4. Known Failure Modes (Agent Amnesia Log)

| Instance | Campaign | Failure | Root Cause |
|----------|----------|---------|------------|
| GitHub Content Block | 3a, Turn 4 | Kimi claimed it couldn't read committed docs | Context blindness — fresh instance forgot 1a–2a |
| Fresh Instance Reset | 4a, Turn 5 | Lost track of Godot 3D decision point | Session death at Turn 13, no executive summary |
| GDScript Shell Amnesia | 4a, Turn 30 | Used heredoc despite Heredoc War lessons | Tutorial code reflex over project-specific rules |
| Repeated Heredoc Loop | 5a, Turns 18–24 | 7 consecutive heredoc failures | LLM context blindness — Kierzenka & Shampine BVP solver not applied to shell escaping |
| Environment Ignorance | 6a, Turn 23 | Suggested system-wide `pip install` | Hallucinated blank-slate environment |
| Find the Venv Loop | 6a, Turns 236–237 | Asked to `find ~ -name activate` | Ignored `KIMI_ONBOARDING.md` invariant |

---

## 5. Aerospace/NASA Verification Pattern

### 5.1 Axiom 4: No Authority Without Proof
Every claim must be backed by terminal output. Every test count must be witnessed. Every commit must be hash-anchored.

### 5.2 Axiom 5: No Hidden State
The environment is not unknown territory. It is a Cathedral with a known blueprint. The AI does not discover — it executes within established invariants.

### 5.3 Team Structure
| Role | Entity | Responsibility |
|------|--------|---------------|
| Architect/Historian | Human (idor) | Intentionality, invariants, record curation |
| Developer/Executor | AI (Kimi/DeepSeek/etc.) | Code generation, command orchestration |
| Witness | WSL2 Terminal | Deterministic evidence, ground truth |

---

## 6. Next Phase Targets (Post-6a)

| Priority | Requirement | Description | AI Assignment |
|----------|-------------|-------------|---------------|
| P1 | FR-MA-001 | Mathematical modeling (EOS derivations) | TBD |
| P2 | FR-AN-001 | Aerospace-grade animations (physics-based particles) | TBD |
| P3 | FR-FV-001 | Formal verification strategy (Lean 4 / Coq / TLA+) | TBD |
| P4 | FR-NF-001 | MC/DC coverage ≥ 95% | TBD |

---

## 7. Changelog

| Date | Event | Commit |
|------|-------|--------|
| 2026-07-16 | Campaign 1a: Foundation | ca54dc6 |
| 2026-07-16 | Campaign 2a: Glass Box | — |
| 2026-07-17 | Campaign 3a: 3D Mechanical Room | d4d2581 |
| 2026-07-17–18 | Campaign 4a: Wiring & SEER | — |
| 2026-07-18 | Campaign 5a: Godot Regression & Heredoc War | d4d2581 |
| 2026-07-18–19 | Campaign 6a: Visual Regression & MOOSE-lite | f1e5a8d, 271a3a3 |
| 2026-07-19 | GEMINI_NBLM_HISTORIAN.md created (this document) | — |

---

*This document is the immune system of the project. Read it before every session. Update it after every campaign. No agent amnesia. No hidden state. Glass box.*
