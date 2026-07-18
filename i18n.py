"""
FR-ED-004: Localization module
Loads translated strings from locales/<lang>.json
Usage: from i18n import _
"""

import json
import os
from typing import Optional

_DEFAULT_LANG = "en"
_CURRENT_LANG = os.environ.get("HVAC_LANG", _DEFAULT_LANG)

# Cache loaded locales
_LOCALE_CACHE = {}

def _load_locale(lang: str) -> dict:
    if lang in _LOCALE_CACHE:
        return _LOCALE_CACHE[lang]

    path = os.path.join(os.path.dirname(__file__), "locales", f"{lang}.json")
    if not os.path.exists(path):
        if lang != _DEFAULT_LANG:
            return _load_locale(_DEFAULT_LANG)
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    _LOCALE_CACHE[lang] = data
    return data

def _(key: str, section: str = "python", default: Optional[str] = None, **kwargs) -> str:
    """
    Get translated string.
    key: dot-separated path, e.g. "scenarios.SC-001.title" or "cli.prompt"
    section: "python" or "godot"
    """
    locale = _load_locale(_CURRENT_LANG)
    data = locale.get(section, {})

    for part in key.split("."):
        if isinstance(data, dict) and part in data:
            data = data[part]
        else:
            return default if default is not None else key

    if isinstance(data, str):
        return data.format(**kwargs) if kwargs else data
    return default if default is not None else key

def get_scenario_translation(scenario_id: str) -> dict:
    """Get full translation dict for a scenario."""
    locale = _load_locale(_CURRENT_LANG)
    return locale.get("python", {}).get("scenarios", {}).get(scenario_id, {})

def set_language(lang: str):
    global _CURRENT_LANG
    _CURRENT_LANG = lang

def get_language() -> str:
    return _CURRENT_LANG
