# Design Specifications — Verification Architecture

## DeepSeek-VL: Viewport Verification Design Spec
**File:** DeepSeek-VL-Viewport-Verification-Design.pdf

**Why this paper is load-bearing:**
Outside AI (Codewhale, Kimi, IDE) sends instructions to Godot-native AI.
But how does the outside AI verify the Godot-native AI actually executed correctly?
Screenshots are too heavy (3.6 MB). Human eyes are not available.
This paper provides the architecture for structured visual verification.

**Key design decisions from paper:**

| Section | Decision | Application in Godot-OE |
|---|---|---|
| §3.1 Hybrid Vision Encoder | Process 1024×1024 efficiently | Viewport captured at 1280×720, downsampled to 1024×1024 for analysis |
| §3.2 Competitive Dynamics | Balance vision vs language modalities | Godot-native AI must not lose language reasoning when analyzing images |
| §4.1 Real-World Scenarios | Web screenshots, PDFs, OCR, charts | Viewport = web screenshot; scene tree = chart; material specs = PDF |
| §4.2 Instruction Tuning | Fine-tune on real user scenarios | Train on "add compressor → verify compressor visible → measure dimensions" |

**Verification loop architecture:**

```
Outside AI (Codewhale)
    ↓ instruction: "Add compressor at origin"
Godot-native AI (DeepSeek in dock)
    ↓ executes: DeepSeekMutation.add_node("Compressor", ...)
    ↓ captures: ViewportCapture.get_image()
    ↓ analyzes: "I see a cylindrical mesh at (0,0,0), diameter ~254px"
    ↓ reports: JSON {"verified": true, "observed": "compressor", "position": [0,0,0]}
Outside AI
    ↓ reads audit log, confirms scene hash changed
    ↓ confirms viewport signature non-blank
    ↓ confirms Godot-native AI self-report matches expected
```

**Without this spec:**
- Outside AI sends instructions blindly
- No structured verification possible
- Agent equalizer fails (FR-SV-007 violated)

**With this spec:**
- Every instruction has a verification path
- Godot-native AI can self-verify via viewport analysis
- Outside AI can audit via JSONL without screenshots
- Yeshua Standard: no authority without proof
