# HVAC Simulation v1.7 — Release Notes

**Date:** 2026-07-20
**SRS:** v1.7
**Requirements:** 48/48 PASS
**Tests:** 267 Python + 12 Godot = 279 total (0 xfailed)
**Performance:** ≥60 FPS desktop, ≥30 FPS mobile

---

## Feature Summary

### Educational Features (FR-ED-005 through FR-ED-008)
- **Real-time cycle simulation**: 4-point vapor compression cycle with live pressure/temperature gauges
- **23 fault types**: full mapping to all training scenarios — low refrigerant, overcharge, non-condensables, restriction, TXV failure, compressor failure, mixed refrigerants, and more
- **Interactive instructor panel**: 23 fault buttons with descriptions, one-click injection
- **Student diagnosis panel**: 4 multiple-choice options, submit with immediate feedback
- **Timed scoring**: 30-second countdown, 100 pts max, -20 per hint, 0 if wrong
- **Mobile optimized**: adaptive particles (50 mobile / 250 desktop), simplified gauges, platform detection

### Mathematical Modeling (carried from v1.6)
- **First-principles Helmholtz EOS** for R410A, R32, R134a, R1234yf, R22
- **Full derivative stack + derived properties** (c_v, c_p, w, H, S, P_sat)
- **Aly-Lee ideal-gas** correlation with CoolProp calibration
- **Property-based testing**: 50,000 Hypothesis random cases
- **TLA+ formal specification**

### Visual & Performance
- **Aerospace-grade particle flow**: GPUParticles3D per cycle component
- **HelmholtzEOS-driven PT chart**: dynamic refrigerant switching
- **60 FPS desktop, 30 FPS mobile** with all systems active

---

## What's New in v1.7 (from v1.6)

| Feature | v1.6 | v1.7 |
|:---|:---|:---|
| Fault types | 4 | **23** |
| Instructor UI | Text readout | **Interactive 23-button panel** |
| Student diagnosis | None | **4-choice + timer + scoring** |
| Mobile support | None | **Particle LOD, simplified gauges** |
| Requirements | 45 | **48** |

---

## Known Limitations

1. **Multiplayer/remote instruction**: not yet implemented (planned v1.8)
2. **Non-R410A regression edge cases**: max pressure errors up to 6.5% at extreme random states
3. **Integration constants C, D = 0**: enthalpy/entropy baselines approximate
4. **Two-phase SPEED_OF_SOUND**: CoolProp incompatibility handled by fallback

---

## Performance

| Scene | Desktop (RTX 4050) | Mobile (simulated) | Target |
|:---|---:|---:|:---|
| PT Chart | 116 FPS | — | 60 |
| Mechanical Room | 145 FPS | ≥30 FPS | 60/30 |

---

## Next Version (v1.8 Preview)

| Priority | Feature |
|:---|:---|
| P1 | Multiplayer/remote instruction (WebRTC) |
| P2 | R454B and R513A refrigerant support (CoolProp 8.1) |
| P3 | Lean 4 formal verification (derivative correctness) |
| P4 | CI/CD pipeline with GitHub Actions |

---

## Commit History (v1.7)

```
6948d8b feat(godot): FR-ED-008 mobile optimization
3c3393f feat(godot): FR-ED-007 interactive fault UI + diagnosis
e839997 feat(edu): FR-ED-006 full 23-scenario fault mapping
547be68 feat(edu): FR-ED-005 real-time cycle + fault injection + scoring
143ff93 feat(godot): FR-ED-005 Godot frontend
50923bf docs: v1.6 stability audit, v1.7 roadmap
51402ab docs: v1.6 release — RELEASE_NOTES, final CHANGELOG, tag v1.6
```

---

*Glass box enforced. Every state inspectable. No hidden assumptions.*
*Every formula cited with primary source. No black-box thermodynamics.*
*23 faults, 30 seconds, one correct answer. Train like you troubleshoot.*
