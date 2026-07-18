"""
FR-ED-004 Integration Test: Spanish localization end-to-end
"""

import subprocess
import sys
import os


def test_scenario_spanish_output():
    """Verify scenarios_localized.py outputs Spanish text when HVAC_LANG=es."""
    env = os.environ.copy()
    env["HVAC_LANG"] = "es"

    result = subprocess.run(
        [sys.executable, "scenarios_localized.py", "SC-001"],
        input="hint\nhint\nR410A\n",
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )

    output = result.stdout + result.stderr

    # Verify Spanish text appears
    assert "Dificultad: BÁSICO" in output, f"Missing Spanish difficulty. Output: {output[:500]}"
    assert "Primer Día" in output, f"Missing Spanish title. Output: {output[:500]}"
    assert "LECTURAS DE MANÓMETROS" in output, f"Missing Spanish gauge label. Output: {output[:500]}"
    assert "PISTAS" in output, f"Missing Spanish hints label. Output: {output[:500]}"


def test_scenario_english_output():
    """Verify scenarios_localized.py outputs English text when HVAC_LANG=en."""
    env = os.environ.copy()
    env["HVAC_LANG"] = "en"

    result = subprocess.run(
        [sys.executable, "scenarios_localized.py", "SC-001"],
        input="hint\nhint\nR410A\n",
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )

    output = result.stdout + result.stderr

    # Verify English text appears
    assert "Difficulty: BASIC" in output, f"Missing English difficulty. Output: {output[:500]}"
    assert "First Day" in output, f"Missing English title. Output: {output[:500]}"
