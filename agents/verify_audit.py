#!/usr/bin/env python3
"""
verify_audit.py — Prove Godot state changes without screenshots.

Agent equalizer: parse JSONL audit log, verify scene hashes, viewport
perceptual signatures, and mutation causality chains.  Any outside AI
can prove what happened inside Godot by reading the log alone.

Yeshua Standard: no hidden state, no authority without proof.
"""
import json
import sys
import glob
import os
from typing import List, Dict, Optional

LOG_DIR = os.path.expanduser(
    "~/.local/share/godot/app_userdata/HVAC Simulation/oe_audit"
)


def load_latest_log() -> Optional[str]:
    """Return path to the most recent audit log, or None."""
    logs = glob.glob(f"{LOG_DIR}/audit_*.jsonl")
    if not logs:
        return None
    return max(logs, key=os.path.getmtime)


def load_entries(path: str) -> List[Dict]:
    """Parse a JSONL file into a list of entry dicts."""
    entries: List[Dict] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def verify_chain(entries: List[Dict]) -> int:
    """Run all verification checks.  Returns 0 on success, 1 on failure."""
    failures = 0
    path = entries[0].get("_path", "unknown") if entries else "empty"

    print(f"=== Audit Verification: {path} ===")
    print(f"Total entries: {len(entries)}")

    # ── G1: Sequence continuity ──────────────────────────────────────────
    for i, e in enumerate(entries):
        expected = i + 1
        actual = e.get("seq")
        if actual != expected:
            print(f"FAIL: Sequence break at index {i}: "
                  f"expected seq={expected}, got seq={actual}")
            failures += 1

    # ── G2: Mutation causality ───────────────────────────────────────────
    # Every mutation must be preceded by a human_input or ai_thought
    for i, e in enumerate(entries):
        if e.get("type") != "mutation":
            continue
        # Check up to 5 prior entries for a cause
        prior_types = {
            p.get("type")
            for p in entries[max(0, i - 5): i]
        }
        if not ("human_input" in prior_types or "ai_thought" in prior_types):
            print(f"FAIL: Orphan mutation at seq {e['seq']}: "
                  f"no prior instruction or thought. "
                  f"Prior types: {prior_types}")
            failures += 1

    # ── G3: Scene hash delta ─────────────────────────────────────────────
    hashes = [
        (e["seq"], e["data"]["hash"])
        for e in entries
        if e.get("type") == "scene_hash" and "hash" in e.get("data", {})
    ]
    if len(hashes) >= 2:
        if hashes[-1][1] == hashes[0][1]:
            print(f"FAIL: Scene hash unchanged across {len(hashes)} samples "
                  f"— mutation may have produced no effect")
            failures += 1
        else:
            print(f"OK: Scene hash delta: "
                  f"{hashes[0][1][:16]}... -> {hashes[-1][1][:16]}... "
                  f"({len(hashes)} samples)")

    # ── G4: Viewport signatures non-blank ────────────────────────────────
    sigs = [e for e in entries if e.get("type") == "viewport_sig"]
    for s in sigs:
        phash = s.get("data", {}).get("phash", "")
        if phash == "0000000000000000":
            print(f"FAIL: Blank viewport at seq {s['seq']} "
                  f"— render produced no visual output")
            failures += 1

    if sigs:
        print(f"OK: {len(sigs)} viewport signature(s) with valid pHash")

    # ── G5: Covenant check presence ──────────────────────────────────────
    covenants = [e for e in entries if e.get("type") == "covenant_check"]
    if not covenants:
        print("WARN: No covenant_check entries found — "
              "invariant enforcement not recorded")

    # ── Summary ──────────────────────────────────────────────────────────
    print()
    if failures == 0:
        print("VERIFIED: All invariants hold. No screenshots required.")
        return 0
    else:
        print(f"FAILED: {failures} invariant violation(s) detected.")
        return 1


def main() -> int:
    log = load_latest_log()
    if not log:
        print("NO_AUDIT_LOG")
        return 2

    entries = load_entries(log)
    if not entries:
        # Try previous non-empty logs
        logs = sorted(
            glob.glob(f"{LOG_DIR}/audit_*.jsonl"),
            key=os.path.getmtime,
            reverse=True,
        )
        for alt in logs:
            alt_entries = load_entries(alt)
            if alt_entries:
                entries = alt_entries
                log = alt
                print(f"NOTE: latest log empty, using {os.path.basename(alt)}")
                break

    if not entries:
        print("EMPTY_LOG (all logs empty)")
        return 2

    # Annotate with source path for diagnostics
    entries[0]["_path"] = os.path.basename(log)

    return verify_chain(entries)


if __name__ == "__main__":
    sys.exit(main())
