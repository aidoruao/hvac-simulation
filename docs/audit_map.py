#!/usr/bin/env python3
"""
Cathedral Index Auditor — validates that the map contains what it ought to contain.
Run: python3 docs/audit_map.py
"""

import re
import sys
import subprocess
from pathlib import Path

# The Universal Filter — what MUST be in the map
REQUIRED_SECTIONS = [
    ("SRS v1.8", r'id="srs"'),
    ("README", r'id="readme"'),
    ("AI Onboarding", r'id="onboarding"'),
    ("Behavioral Archetypes", r'id="archetypes"'),
    ("Documentation Index", r'id="doc-index"'),
    ("Investigations", r'id="investigations"'),
    ("Formula Citations", r'id="formulas"'),
    ("Reconnaissance", r'id="recon"'),
    ("Contributing", r'id="contributing"'),
    ("Campaign History", r'id="historian"'),
    ("Campaign 9a Findings", r'id="campaign-9a"'),
    ("Math Registry", r'id="math-registry"'),
    ("Auditor QoL", r'id="auditor-qol"'),
    ("Active Warden", r'id="warden"'),
    ("Ecosystem Architecture", r'id="ecosystem"'),
    ("COVENANT.json", r'id="covenant"'),
    ("Horizon Registry", r'id="horizon"'),
    ("Release History", r'id="releases"'),
    ("FR-MA-001 Spec", r'id="ma001-spec"'),
    ("File Inventory", r'id="inventory"'),
    ("External References", r'id="references"'),
]

REQUIRED_INVARIANTS = [
    (r'FR-SV-005', 'Structural Fix Mandate'),
    (r'Almost Failure', 'Almost Failure Invariant'),
    (r'Structural Fix', 'Structural Fix Mandate'),
    (r'Cryptographic Witness', 'Cryptographic Witness Gate'),
    (r'Completion Theater', 'Completion Theater pattern'),
    (r'Heredoc', 'Heredoc ban'),
    (r'INV-9A-001', 'INV-9A-001 investigation'),
]

REQUIRED_MATH = [
    (r'Helmholtz', 'Helmholtz EOS'),
    (r'Maxwell Equal-Area', 'Maxwell Equal-Area Construction'),
    (r'Jacobian', 'Jacobian stability'),
    (r'1e14', 'Jacobian condition number threshold'),
    (r'Landauer', 'Landauer functors'),
    (r'Topos', 'Topos/Category theory'),
    (r'Lean 4', 'Lean 4 formal proofs'),
]

REQUIRED_COMMITS = [
    (r'a7e823b', 'SRS v1.8 baseline'),
    (r'd141846', 'Cathedral Index v3.0'),
]


def check_sections(html_content):
    missing = []
    for name, pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, html_content):
            missing.append(name)
    return missing


def check_invariants(html_content):
    missing = []
    for pattern, name in REQUIRED_INVARIANTS:
        if not re.search(pattern, html_content):
            missing.append(name)
    return missing


def check_math(html_content):
    missing = []
    for pattern, name in REQUIRED_MATH:
        if not re.search(pattern, html_content):
            missing.append(name)
    return missing


def check_commits(html_content):
    missing = []
    for pattern, name in REQUIRED_COMMITS:
        if not re.search(pattern, html_content):
            missing.append(f"{name} ({pattern})")
    return missing


def check_anchor(html_content):
    match = re.search(r'(?:Anchor|Anchored at)[:\s]+([a-f0-9]{7,40})', html_content, re.IGNORECASE)
    if not match:
        return None, "No anchor commit found"
    commit = match.group(1)
    result = subprocess.run(
        ['git', 'cat-file', '-t', commit],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    if result.returncode != 0:
        return commit, f"Commit {commit} not found in repository"
    return commit, f"Valid (git object exists)"


def main():
    html_path = Path(__file__).parent / 'index.html'
    if not html_path.exists():
        print(f"ERROR: {html_path} not found")
        sys.exit(1)

    content = html_path.read_text()

    # Gather results
    missing_sections = check_sections(content)
    missing_invariants = check_invariants(content)
    missing_math = check_math(content)
    missing_commits = check_commits(content)
    commit, anchor_status = check_anchor(content)

    total_checks = (
        len(REQUIRED_SECTIONS)
        + len(REQUIRED_INVARIANTS)
        + len(REQUIRED_MATH)
        + len(REQUIRED_COMMITS)
        + 1  # anchor
    )
    failures = (
        len(missing_sections)
        + len(missing_invariants)
        + len(missing_math)
        + len(missing_commits)
        + (0 if anchor_status.startswith("Valid") else 1)
    )
    passed = total_checks - failures

    print("=" * 66)
    print("  CATHEDRAL INDEX AUDITOR v1.0")
    print("  Map: docs/index.html")
    print("  Standard: Universal Filter (Round 15)")
    print("=" * 66)
    print()

    # 1. Sections
    print(f"[1] SECTIONS ({len(REQUIRED_SECTIONS)} required)")
    if missing_sections:
        print(f"    FAIL — {len(missing_sections)} missing:")
        for m in missing_sections:
            print(f"      - {m}")
    else:
        print(f"    PASS — all {len(REQUIRED_SECTIONS)} present")
    print()

    # 2. Invariants
    print(f"[2] INVARIANTS ({len(REQUIRED_INVARIANTS)} required)")
    if missing_invariants:
        print(f"    FAIL — {len(missing_invariants)} missing:")
        for m in missing_invariants:
            print(f"      - {m}")
    else:
        print(f"    PASS — all {len(REQUIRED_INVARIANTS)} present")
    print()

    # 3. Math
    print(f"[3] MATH ({len(REQUIRED_MATH)} required)")
    if missing_math:
        print(f"    FAIL — {len(missing_math)} missing:")
        for m in missing_math:
            print(f"      - {m}")
    else:
        print(f"    PASS — all {len(REQUIRED_MATH)} present")
    print()

    # 4. Commits
    print(f"[4] COMMIT ANCHORS ({len(REQUIRED_COMMITS)} required)")
    if missing_commits:
        print(f"    FAIL — {len(missing_commits)} missing:")
        for m in missing_commits:
            print(f"      - {m}")
    else:
        print(f"    PASS — all {len(REQUIRED_COMMITS)} present")
    print()

    # 5. Anchor
    print("[5] CRYPTOGRAPHIC ANCHOR")
    if anchor_status.startswith("Valid"):
        print(f"    PASS — anchor commit {commit} verified in git")
    else:
        print(f"    FAIL — {anchor_status}")
    print()

    # Verdict
    print("=" * 66)
    if failures == 0:
        print(f"  VERDICT: PASS — {passed}/{total_checks} checks satisfied")
        print("  The map contains what it ought to contain.")
    else:
        print(f"  VERDICT: FAIL — {failures}/{total_checks} checks failed")
        print("  The map is missing required specifications. Harden the map.")
        print()
        print("  Missing items:")
        for section in missing_sections:
            print(f"    [SECTION] {section}")
        for inv in missing_invariants:
            print(f"    [INVARIANT] {inv}")
        for math in missing_math:
            print(f"    [MATH] {math}")
        for cmt in missing_commits:
            print(f"    [COMMIT] {cmt}")
        if not anchor_status.startswith("Valid"):
            print(f"    [ANCHOR] {anchor_status}")
    print("=" * 66)

    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
