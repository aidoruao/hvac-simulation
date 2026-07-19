# Changelog — HVAC Simulation

**Canonical version history across all project documents.**

---

## 2026-07-19 — docs/ Folder Created, v1.5 Locked

### Added
- `docs/` folder with unified documentation structure
- `docs/INDEX.md` — master navigation with commit hash registry
- `docs/README.md` — minimal project overview
- `docs/CONTRIBUTING.md` — contribution guidelines
- `docs/CHANGELOG.md` — this file

### Changed
- `HVAC_SRS.md` → `docs/HVAC_SRS.md` (v1.5, FR-PH-003 PASS, 188/188 tests)
- `FORMULA_CITATIONS.md` → `docs/FORMULA_CITATIONS.md` (MOOSE-lite citations added)
- `KIMI_ONBOARDING.md` → `docs/KIMI_ONBOARDING.md` (updated to 188/188, Campaign 6a)
- `RECONNAISSANCE.md` → `docs/RECONNAISSANCE.md` (Campaign 6a discoveries added)
- `GEMINI_NBLM_HISTORIAN.md` → `docs/GEMINI_NBLM_HISTORIAN.md` (moved into docs/)

### Ground Truth
- Commit: `9cb3c3b`
- Tests: 188/188 PASS
- SRS: v1.5

---

## 2026-07-18 — Campaign 6a Complete

### Added
- FR-PH-003: MOOSE-inspired steady-state heat conduction solver (2/2 PASS)
- FR-VA-004: Visual regression testing with screenshot diff (3/3 PASS)
- `tests/moose_lite/` directory
- `tests/visual_regression/` directory

### Ground Truth
- Commit: `271a3a3` (FR-PH-003), `f1e5a8d` (FR-VA-004)
- Tests: 186/186 → 188/188 PASS

---

## 2026-07-18 — SRS v1.4

### Added
- FR-ED-004: Spanish localization (13/13 PASS)
- `i18n.py`, `locales/es.json`, `locale_es.gd`

### Ground Truth
- Commit: `c370d25`
- Tests: 183/183 PASS

---

## 2026-07-17 — Campaign 3a–5a

### Added
- FR-3D-001/002: 3D mechanical room with animated compressor/fan
- FR-EL-001/002: Thermostat wiring schematic + Godot integration
- FR-TD-008/009: COP and SEER calculations
- FR-PF-002: Frame rate benchmark (≥60 FPS)
- FR-VI-001/002: Interactive PT chart
- FR-VA-001/002/003: Divergence detection, NIST cross-check, Godot regression harness

### Ground Truth
- Commit: `d4d2581`
- Tests: 147 → 168 PASS

---

## 2026-07-16 — Campaign 1a–2a

### Added
- Foundation: 14 requirements
- CoolProp 8.0.0 integration
- Glass box: `state_inspector.py`
- Formula citations: primary sources only
- Session tracking and audit logging

### Ground Truth
- Commit: `ca54dc6`
- Tests: 64/64 PASS

---

*Every entry links to a commit. Every commit links to a test count. No hidden history.*
