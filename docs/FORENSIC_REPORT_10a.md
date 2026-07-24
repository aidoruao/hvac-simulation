# Campaign 10a Forensic Report: Frontend/Backend Divergence

> Generated 2026-07-23 from full git history analysis.
> 122 commits analyzed across 7 days (July 16-23, 2026).

---

## Executive Summary

The Godot frontend contains basic CSG shapes (boxes, cylinders) while the Python backend has 23 training scenarios, Helmholtz equation of state, CoolProp verification, and a full scoring engine. This report traces the exact commit where the project shifted from "build Godot scene" to "document Godot scene."

**The divergence occurred on July 17, 2026.** Between July 16 (Godot scene commits) and July 17 (documentation surge), the project pivoted from building to documenting.

---

## Commit Category Analysis

| Category | Count | Description |
|---|---|---|
| **Docs-only** | 46 | Commits that ONLY changed .md, .html, docs/ files |
| **Code-only** | 33 | Commits that ONLY changed .py, .cpp, .gd, agents/ files |
| **Scene-only** | **0** | Not a single commit was purely scene-focused |
| **Mixed** | 42 | Commits with both docs + code changes |
| **Empty** | 1 | Commit with no file changes |
| **Total** | **122** | |

### Key Ratios

- **Docs-to-scene ratio: 53:1** — For every scene-related change, there are 53 documentation changes
- **Docs-only vs scene-only: 46:0** — 46 commits added documentation without changing a single scene file
- **Today (July 23): 20 commits** — 6 docs-only, 9 code-only, 5 mixed

---

## Divergence Timeline

### Phase 1: Building (July 16, 2026)
```
f358922 feat(godot): interactive PT chart with refrigerant switching     [godot]
1e5ee02 feat(godot): PT chart scene with Python bridge                   [godot]
a052fd5 feat(3d): mechanical room — FR-3D-001 gauge visualization        [godot]
8f601d2 feat(3d): FR-3D-002 animated compressor and condenser fan        [godot]
```
**Last Godot scene commits.** After July 16, no new Godot scene files were created or meaningfully modified.

### Phase 2: Documenting (July 17-23, 2026)
```
d336854 docs: SRS v0.5 — FR-3D-001 PASS, 90/90 tests                    [docs]
9f2e7f7 feat(electrical): thermostat wiring — FR-EL-001                  [empty]
21e7931 feat(thermodynamics): COP calculator — FR-TD-008                  [empty]
296c6e5 docs: SRS v0.6 — 132/132 tests                                    [docs]
7ae1629 docs: add campaign document 3a 7-16-26                            [docs]
7660b92 docs: SRS v0.7 — 139/139 tests                                    [docs]
```
Documentation surge. SRS versions incremented from v0.1 to v0.7. Test counts growing (90→132→139). Campaign files 1a through 9a created. **Zero Godot scene changes.**

### Phase 3: Godot OE Resurgence (July 23, 2026 — today)
```
989d368 fix: compressor mesh generator, material library                  [code+scene]
8a5e0bb feat: AI-Agent-As-Human protocol                                  [code+docs]
365650a feat: DeepSeekChat GDScript wrapper                               [code]
a555b49 fix: editor plugin, audit logging                                 [code]
...
0ad261d feat: programmatic AI-to-AI loop                                  [code]
```
Today's session added: compressor mesh generator (302 lines), DeepSeekChat wrapper, AI dock audit logging (C++), editor viewport capture, multi-layer verification framework. **14 code/agent commits today vs 6 docs-only.**

---

## The Divergence Root Cause

### What the backend has (all built July 16-17)
- 23 training scenarios with 20 unique faults
- Helmholtz equation of state via CoolProp
- Multi-refrigerant support (R410A, R32, R454B, R290, R744)
- COP calculator, cycle analysis
- Session tracking, audit logging, scoring engine
- Validation layer with divergence detection
- State inspector with real-time observability
- SRS v0.7 with 139/139 tests passing
- Formula citations with primary sources

### What the Godot frontend has (minimal scenes from July 16)
- CSG-based compressor (boxes, cylinders — 8 child nodes)
- CSG gauges (torus + needle)
- CSG sight glass, condenser fan
- PT chart scene (one working 2D visualization)
- Wiring scene (template, not functional)
- **Total Godot scene files: 3** (mechanical_room.tscn, pt_chart.tscn, wiring_scene.tscn)
- **Procedural compressor mesh (July 23)** — generated in code, never instantiated in scene

### The structural failure

1. **SRS auditor passed on documentation alone**: The Cathedral Index auditor checks 38 internal consistency rules. It verifies the map describes itself correctly — not that the territory (Godot scenes) matches the map.

2. **Campaign files documented promises, not deliveries**: Each campaign file (1a-9a) recorded what was discussed, not what was built. The absence of scene verification allowed the gap to grow.

3. **No frontend verification pipeline**: Until today (July 23), there was no mechanism to capture and verify Godot viewport content. The EditorCapture plugin and multi-layer verifier were only added in the last 5 hours.

4. **Python backend does not require a Godot frontend**: All 139 SRS tests pass on the Python backend alone. The Godot frontend is referenced in the SRS but never actually tested.

---

## When Did the Auditor Start Passing on Documentation Alone?

The Cathedral Index auditor (`docs/audit_map.py`) checks 38 rules:
- 21 required sections present
- 7 invariants present
- 7 math items present
- 2 commit anchors present
- 1 cryptographic anchor verified

**None of these rules check whether Godot scenes render correctly.** The auditor was designed to verify map consistency, not territory accuracy. It has always passed on documentation alone — this is a design choice, not a bug that appeared at a specific commit.

---

## The Gap in Numbers

| Metric | Backend (Python) | Frontend (Godot) |
|---|---|---|
| Lines of code | ~5,000+ (physics, scenarios, scoring) | ~300 lines (CSG scene definition) |
| Test coverage | 139/139 passing | 0 automated tests |
| Visualization | Matplotlib PT charts | CSG primitives |
| Interactive | CLI/Web API | Static 3D viewport |
| Production readiness | Verified physics | Proof-of-concept CSG |
| Documentation | SRS v0.7, 9 campaign files | SCENE_INVENTORY.md |

---

## Recommendations

1. **Wire the procedural compressor into the scene** — 3-line GDScript change: `gen.new().generate()`
2. **Add automated viewport verification** — EditorCapture plugin already captures on boot; compare pHash baseline
3. **Gate SRS test passes on viewport evidence** — No "PASS" for 3D requirements without screenshot proof
4. **Enforce docs:scene ratio ≤ 2:1** — For every 2 documentation commits, at least 1 must touch scene files
5. **Auditor v2** — Add territory checks: does `mechanical_room.tscn` have >5 child nodes? Does viewport produce >50% non-black pixels?

---

*Investigation complete. 122 commits, 46 docs-only, 0 scene-only, 53:1 docs-to-scene ratio. Divergence began July 17, 2026 when documentation replaced building.*
