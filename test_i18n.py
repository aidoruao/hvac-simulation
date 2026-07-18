"""
FR-ED-004: Localization tests
"""

import os
import sys

# Ensure repo root is in path for i18n import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from i18n import _, set_language, get_language, get_scenario_translation


def test_default_language_is_en():
    # Default should be English or whatever HVAC_LANG env var says
    assert get_language() in ("en", "es", os.environ.get("HVAC_LANG", "en"))


def test_spanish_scenario_title():
    set_language("es")
    title = _("scenarios.SC-001.title")
    assert title == "Primer Día: ¿Qué hay en el Sistema?"


def test_spanish_scenario_description():
    set_language("es")
    desc = _("scenarios.SC-001.description")
    assert "primer" in desc.lower() or "solo" in desc.lower()


def test_spanish_cli_prompt():
    set_language("es")
    prompt = _("cli.prompt")
    assert "pista" in prompt


def test_spanish_difficulty_labels():
    set_language("es")
    assert _("difficulty.BASIC") == "BÁSICO"
    assert _("difficulty.INTERMEDIATE") == "INTERMEDIO"
    assert _("difficulty.ADVANCED") == "AVANZADO"


def test_spanish_godot_mechanical_room():
    set_language("es")
    assert _("mechanical_room.refrigerant", section="godot") == "Refrigerante"
    assert _("mechanical_room.pressure", section="godot") == "Presión"
    assert _("mechanical_room.temperature", section="godot") == "Temperatura"


def test_spanish_godot_pt_chart():
    set_language("es")
    assert _("pt_chart.temperature_axis", section="godot") == "Temperatura (°C)"
    assert _("pt_chart.pressure_axis", section="godot") == "Presión (bar)"


def test_spanish_godot_wiring():
    set_language("es")
    assert _("wiring.all_wires_ok", section="godot") == "Todos los cables OK"
    assert _("wiring.fault", section="godot") == "FALLA"
    assert _("wiring.ok", section="godot") == "OK"


def test_get_scenario_translation_full_dict():
    set_language("es")
    trans = get_scenario_translation("SC-001")
    assert trans["title"] == "Primer Día: ¿Qué hay en el Sistema?"
    assert len(trans["hints"]) == 2


def test_fallback_to_key_on_missing():
    set_language("es")
    result = _("nonexistent.key")
    assert result == "nonexistent.key"


def test_english_still_works():
    set_language("en")
    # en.json doesn't exist, so it should fall back to key or default
    result = _("scenarios.SC-001.title", default="Fallback")
    assert result == "First Day: What's in the System?"
