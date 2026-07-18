"""
FR-ED-004: Localized scenario runner
Wraps scenarios.py with i18n support.
Usage: HVAC_LANG=es python3 scenarios_localized.py SC-001
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scenarios import ScenarioEngine, Difficulty
from i18n import _, set_language, get_scenario_translation


def run_scenario_localized(scenario_id: str):
    """Run a scenario with localized output."""
    engine = ScenarioEngine()
    scenario = engine.get_scenario(scenario_id)

    if not scenario:
        print(_("cli.not_found").format(scenario_id=scenario_id))
        return

    trans = get_scenario_translation(scenario_id)

    title = trans.get("title", scenario.title)
    description = trans.get("description", scenario.description)
    difficulty = _("difficulty." + scenario.difficulty.name, default=scenario.difficulty.name)

    print(f"\n{'='*60}")
    print(_("cli.scenario_header").format(title=title))
    print(_("cli.difficulty_label").format(difficulty=difficulty))
    print(f"{'='*60}")
    print(_("cli.description_label").format(description=description))

    if scenario.customer_complaint:
        complaint = trans.get("customer_complaint", scenario.customer_complaint)
        if complaint:
            print(_("cli.customer_says").format(complaint=complaint))

    print(_("cli.gauge_readings"))
    print(f"   Ambient: {scenario.ambient_temp_c}°C")
    print(f"   Suction: {scenario.suction_pressure_psig} psig, {scenario.suction_temp_c}°C")
    print(f"   Liquid:  {scenario.liquid_pressure_psig} psig, {scenario.liquid_temp_c}°C")

    hints = trans.get("hints", scenario.hints)
    if hints:
        print(_("cli.hint_header"))

    hint_idx = 0
    while True:
        user_input = input(_("cli.prompt")).strip()
        if user_input.lower() == _("cli.hint_command"):
            if hint_idx < len(hints):
                print(_("cli.hint_format").format(idx=hint_idx+1, text=hints[hint_idx]))
                hint_idx += 1
            else:
                print(_("cli.no_more_hints"))
        else:
            break


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: HVAC_LANG=es python3 scenarios_localized.py <scenario_id>")
        sys.exit(1)

    run_scenario_localized(sys.argv[1])
