# Investigation Manifest — HVAC Simulation

**Last Updated:** 2026-07-21  
**Document ID:** HVAC-INV-001  
**Status:** ACTIVE  

---

## Open Investigations

### INV-9A-001: GLSL Shader Import Failures (SMAA, Fog, GI)

| Field | Value |
|---|---|
| **ID** | INV-9A-001 |
| **Date Opened** | 2026-07-21 |
| **Discovered During** | Campaign 9a, Round 11 / Turn 45 SIT Gate |
| **Focus** | GLSL Shader Import Failures — SMAA, Volumetric Fog, Global Illumination, FSR2, SSAO, SSIL |
| **Category** | Almost Failure / Ontological Layer Omission |
| **Severity** | **CRITICAL** — blocks GUI-level mutation authorization |
| **Status** | **ACTIVE** |

#### Symptoms

- 15 separate GLSL shader import errors reported in Godot editor console
- Engine falls back to CPU software rendering (llvmpipe/Lavapipe)
- Viewport renders black or corrupted frames
- ViewportCapture produces invalid pixel data
- AI visual comprehension pipeline is blind

#### Root Cause (Diagnostic)

The WSL2 NVIDIA GPU passthrough is partially configured:

- `/dev/dxg` present — CUDA/DirectX path works
- `libcuda.so` in `/usr/lib/wsl/lib/` — CUDA available
- `libnvidia-vulkan.so` — **MISSING**
- NVIDIA Vulkan ICD (`nvidia_icd.json`) — **MISSING** from `/usr/share/vulkan/icd.d/`
- Active Vulkan driver: **lvp (Lavapipe)** — CPU software renderer
- NVIDIA ICD JSONs exist in `/usr/lib/wsl/drivers/` but reference Windows `.dll` paths

#### Impact

- FR-3D-007 (Visual Comprehension Bridge): Viewport::get_texture() returns black/corrupted data
- FR-3D-006 (DeepSeek Module): AI dock UI works, but visual pipeline is broken
- FR-3D-008 (Mutation Engine): Headless verified, but GUI execution blocked
- FR-3D-009 (Physics Validation): Cannot compare AI node positions against rendered scene
- SIT Gate (Round 6): Editor GUI cannot validate visual output

#### Resolution Path

| Option | Description | Priority |
|---|---|---|
| A | Install NVIDIA Vulkan ICD for WSL2 (Windows host driver update → `nvidia_icd.json` in `/usr/share/vulkan/icd.d/`) | **P1 — Recommended** |
| B | Build Godot with `vulkan=no opengl3=yes` and run with `--rendering-driver opengl3` | P2 — Workaround |
| C | Use Windows-native Godot binary from `/mnt/c/` path instead of WSL2 build | P3 — Bypass |

#### Linked Requirements

- FR-3D-009 (Physics Validation) — blocked until rendering is restored
- FR-SV-005 (Structural Fix Mandate) — demands driver-level fix, not UI workaround
- FR-SV-007 (Agent Equalizer) — visual state must be identical for human/AI

#### Investigation Log

| Date | Event |
|---|---|
| 2026-07-21 | Opened. Diagnostic confirmed llvmpipe fallback, missing NVIDIA Vulkan ICD. |
| 2026-07-21 | SRS v1.8 updated: FR-3D-006/007/008 marked PASS (Headless), FR-3D-009 linked to INV-9A-001. |

---

## Closed Investigations

*(None yet.)*

---

*Glass box enforced. Every investigation is public. No hidden defects.*
