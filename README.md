
## Current State — Honest Assessment

What works:
- Godot editor launches with OpenGL3/WSLg rendering (100% non-black viewport)
- DeepSeek AI Assistant dock initializes with API key auto-injection
- Programmatic AI-to-AI chat: `chat_with_ai("instruction")` → "pong" confirmed
- Editor viewport auto-capture: 1213×821 PNG every 60s
- Multi-layer verification: 6 gates with fallback chains
- C++ audit logging: every `_log()` call writes JSONL
- Compressor procedural mesh generator: 8 child nodes (Shell, Ports, Feet, Label)

What doesn't work yet:
- xdotool GUI clicking: WSLg BadWindow errors after repeated mouse interactions
- The default open scene is `pt_chart.tscn` (pressure-temperature chart), not mechanical room
- To see the compressor: open `scenes/mechanical_room/mechanical_room.tscn` manually
- No grass/houses — this is HVAC simulation, not landscape

How to see the compressor:
1. Launch Godot editor
2. File → Open Scene → `res://scenes/mechanical_room/mechanical_room.tscn`
3. Or: set `run/main_scene` in `project.godot` to the mechanical room path
