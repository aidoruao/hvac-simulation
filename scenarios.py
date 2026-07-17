"""Training scenario engine for HVAC simulation.

Progressive difficulty. Fault injection. Assessment with reasoning.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
import random
from refrigerants import Refrigerant


class Difficulty(Enum):
    BASIC = 1      # Identify refrigerant from gauge readings
    INTERMEDIATE = 2  # Diagnose overcharge/undercharge
    ADVANCED = 3   # Multiple faults, customer interaction
    EXPERT = 4     # Full system diagnosis with time pressure


@dataclass
class Scenario:
    """A single training scenario."""
    id: str
    title: str
    description: str
    difficulty: Difficulty
    refrigerant: str
    ambient_temp_c: float
    suction_pressure_psig: float
    liquid_pressure_psig: float
    suction_temp_c: float
    liquid_temp_c: float
    faults: List[str] = field(default_factory=list)
    customer_complaint: Optional[str] = None
    hints: List[str] = field(default_factory=list)
    
    def expected_superheat_k(self) -> float:
        """Calculate expected superheat for this scenario."""
        r = Refrigerant(self.refrigerant)
        P_sat_suction_bar = (self.suction_pressure_psig / 14.5038) + 1.01325
        T_sat_suction_c = r.saturation_temperature(P_sat_suction_bar)
        return self.suction_temp_c - T_sat_suction_c
    
    def expected_subcooling_k(self) -> float:
        """Calculate expected subcooling for this scenario."""
        r = Refrigerant(self.refrigerant)
        P_sat_liquid_bar = (self.liquid_pressure_psig / 14.5038) + 1.01325
        T_sat_liquid_c = r.saturation_temperature(P_sat_liquid_bar)
        return T_sat_liquid_c - self.liquid_temp_c


@dataclass
class Assessment:
    """Result of a scenario attempt."""
    scenario_id: str
    correct_refrigerant: bool
    correct_diagnosis: bool
    superheat_calculated: Optional[float]
    subcooling_calculated: Optional[float]
    reasoning: str
    passed: bool


class ScenarioEngine:
    """Generates and runs training scenarios."""
    
    SCENARIOS = [
        # Level 1: Basic refrigerant identification
        Scenario(
            id="SC-001",
            title="First Day: What's in the System?",
            description="You're on your first solo call. The homeowner says the AC isn't cooling. You hook up your gauges. What refrigerant is this?",
            difficulty=Difficulty.BASIC,
            refrigerant="R410A",
            ambient_temp_c=25,
            suction_pressure_psig=125,
            liquid_pressure_psig=225,
            suction_temp_c=15,
            liquid_temp_c=35,
            hints=[
                "Look at the liquid pressure. R410A runs higher pressure than R22.",
                "R410A saturation pressure at 25°C is about 225 psig.",
            ]
        ),
        Scenario(
            id="SC-002",
            title="The R32 Transition",
            description="New equipment install. The label says R32. Verify with gauges.",
            difficulty=Difficulty.BASIC,
            refrigerant="R32",
            ambient_temp_c=25,
            suction_pressure_psig=130,
            liquid_pressure_psig=230,
            suction_temp_c=15,
            liquid_temp_c=35,
            hints=[
                "R32 pressures are slightly higher than R410A at the same temperature.",
                "Check the critical point: R32 has higher P_crit than R410A.",
            ]
        ),
        # Level 2: Overcharge/undercharge
        Scenario(
            id="SC-003",
            title="The Overcharge",
            description="System running but high power bills. Gauges look high on both sides. What's wrong?",
            difficulty=Difficulty.INTERMEDIATE,
            refrigerant="R410A",
            ambient_temp_c=25,
            suction_pressure_psig=145,  # High suction
            liquid_pressure_psig=245,  # High liquid
            suction_temp_c=10,  # Low superheat
            liquid_temp_c=30,  # Low subcooling
            faults=["overcharge"],
            customer_complaint="My electric bill doubled this month.",
            hints=[
                "Both pressures are high. That's not a restriction.",
                "Calculate superheat. If it's low, liquid is flooding back.",
            ]
        ),
        Scenario(
            id="SC-004",
            title="The Undercharge",
            description="System runs constantly but can't keep up. Suction pressure is low. What's wrong?",
            difficulty=Difficulty.INTERMEDIATE,
            refrigerant="R410A",
            ambient_temp_c=25,
            suction_pressure_psig=105,  # Low suction
            liquid_pressure_psig=205,  # Low liquid
            suction_temp_c=20,  # High superheat
            liquid_temp_c=40,  # High subcooling
            faults=["undercharge"],
            customer_complaint="It never shuts off and the house is still warm.",
            hints=[
                "Low pressures on both sides usually means low charge or restriction.",
                "High superheat + low subcooling = undercharge.",
            ]
        ),
        # Level 3: Multiple faults
        Scenario(
            id="SC-005",
            title="The Dirty Condenser",
            description="System trips on high pressure. Reset it, check gauges. Multiple issues?",
            difficulty=Difficulty.ADVANCED,
            refrigerant="R410A",
            ambient_temp_c=35,  # Hot day
            suction_pressure_psig=120,
            liquid_pressure_psig=350,  # Very high liquid
            suction_temp_c=12,
            liquid_temp_c=50,  # Very high liquid temp
            faults=["dirty_condenser", "overcharge_possible"],
            customer_complaint="It keeps shutting off and making a loud noise.",
            hints=[
                "Liquid pressure over 300 psig on R410A is dangerous.",
                "Check ambient. 35°C ambient + dirty condenser = high head pressure.",
            ]
        ),
    ]
    
    def __init__(self):
        self.completed: List[Assessment] = []
    
    def list_scenarios(self, difficulty: Optional[Difficulty] = None) -> List[Scenario]:
        """List available scenarios, optionally filtered by difficulty."""
        if difficulty:
            return [s for s in self.SCENARIOS if s.difficulty == difficulty]
        return self.SCENARIOS
    
    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get a specific scenario by ID."""
        for s in self.SCENARIOS:
            if s.id == scenario_id:
                return s
        return None
    
    def run_scenario(self, scenario_id: str, 
                     user_refrigerant: str,
                     user_diagnosis: str,
                     user_superheat: Optional[float] = None,
                     user_subcooling: Optional[float] = None) -> Assessment:
        """Run a scenario and assess the user's answers."""
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")
        
        # Check refrigerant
        correct_refrigerant = user_refrigerant.upper() == scenario.refrigerant.upper()
        
        # Check diagnosis (simple string match for now)
        correct_diagnosis = any(fault in user_diagnosis.lower() for fault in scenario.faults) \
            if scenario.faults else True
        
        # Calculate actual values
        actual_sh = scenario.expected_superheat_k()
        actual_sc = scenario.expected_subcooling_k()
        
        # Check calculations (within 2K tolerance)
        sh_correct = user_superheat is not None and abs(user_superheat - actual_sh) < 2
        sc_correct = user_subcooling is not None and abs(user_subcooling - actual_sc) < 2
        
        # Pass criteria
        passed = correct_refrigerant and correct_diagnosis and sh_correct and sc_correct
        
        # Build reasoning
        parts = []
        if correct_refrigerant:
            parts.append(f"✅ Correct refrigerant: {scenario.refrigerant}")
        else:
            parts.append(f"❌ Wrong refrigerant. Expected {scenario.refrigerant}, got {user_refrigerant}")
        
        if scenario.faults:
            if correct_diagnosis:
                parts.append(f"✅ Correct diagnosis: {', '.join(scenario.faults)}")
            else:
                parts.append(f"❌ Wrong diagnosis. Faults: {', '.join(scenario.faults)}")
        
        parts.append(f"Actual superheat: {actual_sh:.1f}K, subcooling: {actual_sc:.1f}K")
        
        reasoning = "\n".join(parts)
        
        assessment = Assessment(
            scenario_id=scenario_id,
            correct_refrigerant=correct_refrigerant,
            correct_diagnosis=correct_diagnosis,
            superheat_calculated=user_superheat,
            subcooling_calculated=user_subcooling,
            reasoning=reasoning,
            passed=passed
        )
        
        self.completed.append(assessment)
        return assessment


def interactive_scenario(scenario_id: str = "SC-001"):
    """Run a scenario interactively in the terminal."""
    engine = ScenarioEngine()
    scenario = engine.get_scenario(scenario_id)
    
    if not scenario:
        print(f"Scenario {scenario_id} not found.")
        return
    
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario.title}")
    print(f"Difficulty: {scenario.difficulty.name}")
    print(f"{'='*60}")
    print(f"\n{scenario.description}")
    
    if scenario.customer_complaint:
        print(f"\n🗣️  Customer says: \"{scenario.customer_complaint}\"")
    
    print(f"\n📊 GAUGE READINGS:")
    print(f"   Ambient: {scenario.ambient_temp_c}°C")
    print(f"   Suction: {scenario.suction_pressure_psig} psig, {scenario.suction_temp_c}°C")
    print(f"   Liquid:  {scenario.liquid_pressure_psig} psig, {scenario.liquid_temp_c}°C")
    
    print(f"\n💡 HINTS (type 'hint' for next hint):")
    
    hint_idx = 0
    while True:
        print(f"\n{'-'*40}")
        user_input = input("Your answer (refrigerant,diagnosis,superheat,subcooling) or 'hint': ").strip()
        
        if user_input.lower() == 'hint':
            if hint_idx < len(scenario.hints):
                print(f"   Hint {hint_idx+1}: {scenario.hints[hint_idx]}")
                hint_idx += 1
            else:
                print("   No more hints.")
            continue
        
        # Parse input: refrigerant,diagnosis,superheat,subcooling
        parts = [p.strip() for p in user_input.split(',')]
        
        if len(parts) < 2:
            print("Format: REFRIGERANT,DIAGNOSIS,SUPERHEAT,SUBCOOLING")
            print("Example: R410A,overcharge,5,8")
            continue
        
        refrigerant = parts[0]
        diagnosis = parts[1] if len(parts) > 1 else ""
        
        try:
            superheat = float(parts[2]) if len(parts) > 2 else None
            subcooling = float(parts[3]) if len(parts) > 3 else None
        except ValueError:
            print("Superheat and subcooling must be numbers.")
            continue
        
        assessment = engine.run_scenario(
            scenario_id, refrigerant, diagnosis, superheat, subcooling
        )
        
        print(f"\n{'='*60}")
        print(assessment.reasoning)
        print(f"\n{'PASSED' if assessment.passed else 'FAILED'}")
        print(f"{'='*60}")
        
        if not assessment.passed:
            retry = input("Try again? (y/n): ").strip().lower()
            if retry == 'y':
                continue
        
        break
    
    return assessment


if __name__ == '__main__':
    print("HVAC Training Scenarios")
    print("=" * 60)
    print("\nAvailable scenarios:")
    
    engine = ScenarioEngine()
    for s in engine.list_scenarios():
        status = "✅" if any(a.scenario_id == s.id and a.passed for a in engine.completed) else "⏳"
        print(f"  {status} {s.id}: {s.title} ({s.difficulty.name})")
    
    print("\nRun: python3 scenarios.py SC-001")
    print("Or import and use ScenarioEngine programmatically.")
    
    import sys
    if len(sys.argv) > 1:
        interactive_scenario(sys.argv[1])
    else:
        interactive_scenario("SC-001")
