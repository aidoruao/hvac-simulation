"""Extended training scenarios — fault injection expansion.

FR-SC-002: 20+ unique fault injections.
Builds on scenarios.py with additional faults.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from scenarios import Difficulty, Scenario, ScenarioEngine, Assessment


# Extended fault scenarios
EXTENDED_SCENARIOS = [
    Scenario(
        id="SC-006",
        title="The Non-Condensables",
        description="System pressures are erratic. Head pressure swings wildly. What's wrong?",
        difficulty=Difficulty.INTERMEDIATE,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=120,
        liquid_pressure_psig=280,
        suction_temp_c=15,
        liquid_temp_c=45,
        faults=["non_condensables"],
        customer_complaint="It makes a knocking sound and the pressures jump around.",
        hints=[
            "Non-condensable gases (air, nitrogen) raise head pressure.",
            "Look for high liquid pressure with normal suction pressure.",
        ]
    ),
    Scenario(
        id="SC-007",
        title="The Restriction",
        description="Suction pressure is low, superheat is high, but liquid pressure is normal. What's wrong?",
        difficulty=Difficulty.INTERMEDIATE,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=95,
        liquid_pressure_psig=220,
        suction_temp_c=22,
        liquid_temp_c=35,
        faults=["restriction"],
        customer_complaint="The house is warm but the lines feel normal.",
        hints=[
            "Low suction + normal liquid = restriction before evaporator.",
            "High superheat with normal subcooling = starving evaporator.",
        ]
    ),
    Scenario(
        id="SC-008",
        title="The Bad TXV",
        description="Superheat is all over the map. Sometimes flooding, sometimes starving. What's wrong?",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=110,
        liquid_pressure_psig=210,
        suction_temp_c=18,
        liquid_temp_c=38,
        faults=["bad_txv"],
        customer_complaint="It works sometimes, then suddenly doesn't.",
        hints=[
            "TXV (thermostatic expansion valve) controls superheat.",
            "Erratic superheat = TXV hunting or stuck.",
        ]
    ),
    Scenario(
        id="SC-009",
        title="The Dirty Evaporator",
        description="Low suction pressure, low superheat, warm house. What's wrong?",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=100,
        liquid_pressure_psig=200,
        suction_temp_c=8,
        liquid_temp_c=30,
        faults=["dirty_evaporator"],
        customer_complaint="The airflow feels weak and the house won't cool.",
        hints=[
            "Dirty evaporator reduces airflow = lower heat absorption.",
            "Low superheat + low suction = not enough heat in evaporator.",
        ]
    ),
    Scenario(
        id="SC-010",
        title="The Bad Fan Motor",
        description="Head pressure is high on hot days, normal on cool days. What's wrong?",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R410A",
        ambient_temp_c=35,
        suction_pressure_psig=125,
        liquid_pressure_psig=340,
        suction_temp_c=12,
        liquid_temp_c=48,
        faults=["bad_condenser_fan"],
        customer_complaint="It trips on hot afternoons but runs fine in the morning.",
        hints=[
            "Condenser fan moves heat from refrigerant to ambient air.",
            "High head only on hot days = fan not moving enough air.",
        ]
    ),
    Scenario(
        id="SC-011",
        title="The Refrigerant Mix",
        description="Pressures don't match any known refrigerant. What happened?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=115,
        liquid_pressure_psig=215,
        suction_temp_c=14,
        liquid_temp_c=34,
        faults=["refrigerant_mix"],
        customer_complaint="A different tech 'topped it off' last week.",
        hints=[
            "Mixing refrigerants changes the saturation curve.",
            "Pressures between two known refrigerants = contamination.",
        ]
    ),
    Scenario(
        id="SC-012",
        title="The Low Ambient",
        description="Heat pump won't work in cold weather. Pressures are very low. What's wrong?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=-5,
        suction_pressure_psig=45,
        liquid_pressure_psig=140,
        suction_temp_c=-15,
        liquid_temp_c=20,
        faults=["low_ambient_no_kit"],
        customer_complaint="The heat pump works fine above 40°F but stops below freezing.",
        hints=[
            "Low ambient kits maintain head pressure in cold weather.",
            "Without it, head pressure drops too low for proper operation.",
        ]
    ),
    Scenario(
        id="SC-013",
        title="The Overcharge + Non-Condensables",
        description="Multiple issues. High pressures, erratic readings, high power draw. What's wrong?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=150,
        liquid_pressure_psig=320,
        suction_temp_c=5,
        liquid_temp_c=42,
        faults=["overcharge", "non_condensables"],
        customer_complaint="Everything is wrong. Loud, hot, expensive.",
        hints=[
            "Multiple faults compound symptoms.",
            "Start with the most obvious, then look for secondary issues.",
        ]
    ),
    Scenario(
        id="SC-014",
        title="The R32 Retrofit",
        description="System was converted from R410A to R32. Verify with gauges.",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R32",
        ambient_temp_c=25,
        suction_pressure_psig=132,
        liquid_pressure_psig=232,
        suction_temp_c=15,
        liquid_temp_c=35,
        faults=["retrofit_verification"],
        customer_complaint="Just had the retrofit done. Want to verify it's right.",
        hints=[
            "R32 runs at slightly higher pressure than R410A at same temp.",
            "Check label and compare pressures to R32 PT chart.",
        ]
    ),
    Scenario(
        id="SC-015",
        title="The A2L Leak",
        description="R32 system. Smell something sweet? Gauge shows low charge. Safety protocol?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R32",
        ambient_temp_c=25,
        suction_pressure_psig=100,
        liquid_pressure_psig=190,
        suction_temp_c=20,
        liquid_temp_c=40,
        faults=["undercharge", "a2l_leak"],
        customer_complaint="I smell something and the system isn't cooling.",
        hints=[
            "A2L refrigerants are mildly flammable. Safety first.",
            "Evacuate area, ventilate, use leak detector before proceeding.",
        ]
    ),
    Scenario(
        id="SC-016",
        title="The Compressor Valve Failure",
        description="Suction pressure is high, head pressure is low. Compressor sounds different. What's wrong?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=140,
        liquid_pressure_psig=180,
        suction_temp_c=18,
        liquid_temp_c=32,
        faults=["bad_compressor_valves"],
        customer_complaint="It's running but not cooling. Sounds weak.",
        hints=[
            "Compressor valves separate high and low sides.",
            "High suction + low head = compressor not pumping.",
        ]
    ),
    Scenario(
        id="SC-017",
        title="The Reversing Valve Stuck",
        description="Heat pump stuck in heating mode. Pressures look like heat pump in winter. What's wrong?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=220,
        liquid_pressure_psig=125,
        suction_temp_c=35,
        liquid_temp_c=15,
        faults=["reversing_valve_stuck"],
        customer_complaint="It's blowing hot air when I want cold.",
        hints=[
            "Reversing valve swaps suction and liquid lines.",
            "If stuck, indoor coil becomes condenser (heats) instead of evaporator (cools).",
        ]
    ),
    Scenario(
        id="SC-018",
        title="The Liquid Line Restriction",
        description="Normal suction, very low liquid pressure, high subcooling. What's wrong?",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=125,
        liquid_pressure_psig=160,
        suction_temp_c=15,
        liquid_temp_c=20,
        faults=["liquid_line_restriction"],
        customer_complaint="The big line is cold but the small line is warm.",
        hints=[
            "Liquid line restriction backs up refrigerant before the restriction.",
            "High subcooling before restriction = liquid stacking up.",
        ]
    ),
    Scenario(
        id="SC-019",
        title="The Suction Line Insulation",
        description="High superheat, sweating suction line, low efficiency. What's wrong?",
        difficulty=Difficulty.INTERMEDIATE,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=125,
        liquid_pressure_psig=225,
        suction_temp_c=28,
        liquid_temp_c=35,
        faults=["suction_line_uninsulated"],
        customer_complaint="The line outside is sweating and my bill went up.",
        hints=[
            "Uninsulated suction line absorbs heat from ambient air.",
            "Extra heat in suction = compressor works harder = higher bill.",
        ]
    ),
    Scenario(
        id="SC-020",
        title="The Overcharged Heat Pump",
        description="Heat pump in heating mode. Pressures way too high. What's wrong?",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R410A",
        ambient_temp_c=5,
        suction_pressure_psig=180,
        liquid_pressure_psig=280,
        suction_temp_c=10,
        liquid_temp_c=38,
        faults=["overcharge"],
        customer_complaint="It's loud and the pressures are scary high.",
        hints=[
            "Heat pumps move heat from outside to inside.",
            "Overcharge raises pressures in both modes.",
        ]
    ),
    Scenario(
        id="SC-021",
        title="The Capillary Tube Blockage",
        description="System with capillary tube metering. Low suction, high superheat, frost on evaporator. What's wrong?",
        difficulty=Difficulty.ADVANCED,
        refrigerant="R134a",
        ambient_temp_c=25,
        suction_pressure_psig=15,
        liquid_pressure_psig=120,
        suction_temp_c=18,
        liquid_temp_c=30,
        faults=["capillary_blockage"],
        customer_complaint="There's frost on the indoor coil and it's not cooling.",
        hints=[
            "Capillary tube meters refrigerant flow.",
            "Blockage = starving evaporator = frost from low pressure.",
        ]
    ),
    Scenario(
        id="SC-022",
        title="The Head Pressure Control Failure",
        description="Low ambient, head pressure too low, expansion valve starving. What's wrong?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=10,
        suction_pressure_psig=85,
        liquid_pressure_psig=140,
        suction_temp_c=20,
        liquid_temp_c=22,
        faults=["head_pressure_control_failure"],
        customer_complaint="It works fine in summer but not in fall.",
        hints=[
            "TXV needs minimum pressure differential to operate.",
            "Low ambient = low head = TXV can't meter properly.",
        ]
    ),
    Scenario(
        id="SC-023",
        title="The R22 Contamination",
        description="System labeled R410A but pressures look like R22. What's wrong?",
        difficulty=Difficulty.EXPERT,
        refrigerant="R410A",
        ambient_temp_c=25,
        suction_pressure_psig=80,
        liquid_pressure_psig=170,
        suction_temp_c=12,
        liquid_temp_c=30,
        faults=["refrigerant_mix", "r22_contamination"],
        customer_complaint="A cheap tech said he could 'top it off' last year.",
        hints=[
            "R22 runs at lower pressure than R410A at same temperature.",
            "Mixing refrigerants is illegal and destroys the system.",
        ]
    ),
]


class ExtendedScenarioEngine(ScenarioEngine):
    """Scenario engine with extended fault library."""
    
    def __init__(self):
        super().__init__()
        self.SCENARIOS = self.SCENARIOS + EXTENDED_SCENARIOS
    
    def get_fault_count(self) -> int:
        """Count unique faults across all scenarios."""
        unique_faults = set()
        for s in self.SCENARIOS:
            for f in s.faults:
                unique_faults.add(f)
        return len(unique_faults)
    
    def list_faults(self) -> List[str]:
        """List all unique faults."""
        unique_faults = set()
        for s in self.SCENARIOS:
            for f in s.faults:
                unique_faults.add(f)
        return sorted(list(unique_faults))


if __name__ == '__main__':
    print("Extended Training Scenarios — HVAC Simulation")
    print("=" * 60)
    
    engine = ExtendedScenarioEngine()
    print(f"Total scenarios: {len(engine.SCENARIOS)}")
    print(f"Unique faults: {engine.get_fault_count()}")
    print(f"\nFaults: {', '.join(engine.list_faults())}")
    
    print(f"\nBy difficulty:")
    for diff in Difficulty:
        count = len(engine.list_scenarios(diff))
        print(f"  {diff.name}: {count} scenarios")
    
    print(f"\n{'='*60}")
    print("FR-SC-002: Fault injection expansion")
    print(f"Target: 20+ unique faults")
    print(f"Current: {engine.get_fault_count()} unique faults")
    status = "PASS" if engine.get_fault_count() >= 20 else "IN PROGRESS"
    print(f"Status: {status}")
