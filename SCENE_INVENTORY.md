# Scene Inventory — Honest Assessment

> Generated 2026-07-24 from live editor viewport captures.
> 1213×821 RGBA, 100% non-black pixels, 287 KB each.

---

## What's Actually Visible (screenshot-proven)

| Component | Type | Material | Status |
|---|---|---|---|
| Compressor | CSG boxes (Housing, Pulley, Belt, Motor, MotorPulley) | Default gray | ✅ Visible |
| Sight Glass | CSG cylinder | Default gray | ✅ Visible |
| Condenser Fan | CSG cylinder | Default gray | ✅ Visible |
| PSI Gauge | CSG torus + needle | Default gray | ✅ Visible |
| °F Gauge | CSG torus + needle | Default gray | ✅ Visible |
| Godot Editor UI | Menus, Inspector, Scene Tree, FileSystem | Native | ✅ Visible |
| DeepSeek AI Dock | Right panel with text field + "Capture & Analyze" button | Native | ✅ Visible |
| 3D Viewport | Grid, gizmos, origin marker | Native | ✅ Visible |
| World Environment | Background color (0.1, 0.1, 0.15) | Native | ✅ Visible |

---

## What's in Code But Not Instantiated

| Asset | File | Contents | Usage |
|---|---|---|---|
| **Procedural Compressor** | `assets/models/compressor_mesh_gen.gd` (302 lines) | 8 detailed child nodes: Shell, TopDome, BasePlate, 3×Feet, SuctionPort (7/8" copper + insulation), DischargePort (1/2" copper), LabelPlate (aluminum), TerminalBox (steel + conduit) | Call `generate()` → returns `Node3D`, never added to any scene |
| PBR Materials | In generator: `_setup_materials()` | Steel (metallic 0.9), Copper (metallic 0.95), Aluminum (metallic 0.8), Rubber (matte), Label (gloss) | Created in `_init()`, only used if `generate()` called |
| Invariant Constants | Generator lines 18-29 | Shell 254mm × 420mm, ports 7/8" and 1/2" OD | Enforced at compile-time |
| Refrigerant Flow | `scripts/mechanical_room/refrigerant_flow.gd` | GPU particles, mass flow, phase colors | Attached to MechanicalRoom scene but never triggered |
| Frame Rate Benchmark | `scripts/frame_rate_benchmark.gd` | FPS measurement | Run via `--script`, not in main scene |
| DeepSeek Mutation | C++ module | `add_node()`, `set_node_property()`, `edit_script()` | Editor-only, never called in production |

---

## What's Documented But Not Implemented

| Feature | Reference | Status |
|---|---|---|
| Expansion valve | SRS | Not in scene |
| Evaporator coil | SRS | Not in scene |
| Condenser coil | SRS | Not modeled (fan only) |
| Refrigerant lines | SRS | No pipe geometry |
| Wiring connections | SRS | 2D schematic only |
| Real-time pressure/temperature | Gauge CSG | Static labels, no live data binding |
| Compressor animation | `mechanical_room.gd` | Script exists, animation not visible |
| HVAC state bridge | Python backend | `hvac_state.json` exists, not connected to frontend |

---

## What's Not in Scope

| Item | Reason |
|---|---|
| Grass / outdoor landscape | This is an indoor mechanical room simulation, not outdoor |
| Houses / architecture | HVAC simulation, not architectural visualization |
| Day/night cycle | Indoor environment, constant lighting |
| Weather effects | N/A |

---

## Verification Status

| Layer | Status | Evidence |
|---|---|---|
| Scene renders | ✅ **PASS** | 100% non-black, 1213×821, 287 KB |
| Compressor exists | ✅ **PASS** | CSG primitives in scene; procedural mesh in code |
| UI functional | ✅ **PASS** | Editor menus, dock, viewport all visible |
| API connectivity | ✅ **PASS** | Live "pong" from DeepSeek via programmatic agent |
| Audit trail | ⚠️ Partial | dock init logged; human_input/ai_response need button press |
| Screenshot capture | ✅ **PASS** | EditorCapture plugin, 100% non-black |
| Physics backend | ✅ **PASS** | `hvac_state.json` exists, R410A + pressure |

---

## How to Instantiate the Detailed Compressor

```gdscript
# In any scene script:
var gen = load("res://assets/models/compressor_mesh_gen.gd")
var compressor = gen.new().generate()  # Returns Node3D with 8 children
compressor.position = Vector3(0, 0, 0)
add_child(compressor)
```

The generator creates:
- **Shell**: 254mm diameter × 355mm height, steel, 64-segment cylinder
- **TopDome**: Hemisphere cap, 40mm height, steel
- **BasePlate**: 264mm diameter × 25mm, steel
- **Feet**: 3× rubber tripod, 15mm height
- **SuctionPort**: 7/8" OD copper tube + black insulation sleeve
- **DischargePort**: 1/2" OD copper tube
- **LabelPlate**: 80×60mm aluminum rating plate
- **TerminalBox**: Steel enclosure with aluminum conduit

Total: 8 child nodes, 5 PBR materials, 11 invariant constants.
