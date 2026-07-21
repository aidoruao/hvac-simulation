"""Mechanical Room Bridge — writes HVAC state to JSON for Godot 3D scene.

FR-3D-001: 3D mechanical room with real-time gauge updates.
FR-ED-005: Real-time cycle simulation with fault injection and scoring.
Connects Python backend to Godot frontend via JSON file bridge.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
import random

from refrigerants import Refrigerant


@dataclass
class MechanicalRoomState:
    """Complete state for the 3D mechanical room scene."""
    refrigerant: str = "R410A"
    pressure_psi: float = 0.0
    temperature_f: float = 0.0
    superheat_f: float = 0.0
    subcooling_f: float = 0.0
    phase: str = "unknown"
    scenario_id: str = ""
    difficulty: str = ""
    faults: list = None
    hints_used: int = 0
    session_id: str = ""
    attempts_total: int = 0
    attempts_passed: int = 0
    attempts_failed: int = 0
    validation_status: str = ""
    divergence_percent: float = 0.0
    timestamp: str = ""
    # FR-AN-001: flow visualization fields
    compressor_running: bool = False
    load_percent: float = 0.0
    mass_flow: float = 0.0
    pressure_bar: float = 0.0
    
    def __post_init__(self):
        if self.faults is None:
            self.faults = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class CycleState:
    """FR-ED-005: 4-point vapor compression cycle state."""
    refrigerant: str = "R410A"
    suction_p_bar: float = 0.0
    suction_T_C: float = 0.0
    suction_superheat_K: float = 0.0
    discharge_p_bar: float = 0.0
    discharge_T_C: float = 0.0
    condenser_out_p_bar: float = 0.0
    condenser_out_T_C: float = 0.0
    condenser_out_subcooling_K: float = 0.0
    expansion_in_p_bar: float = 0.0
    expansion_in_T_C: float = 0.0
    compressor_running: bool = True
    mass_flow: float = 0.05
    phase: str = "superheated"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FaultInjection:
    """FR-ED-005: Active fault configuration."""
    name: str = ""
    mass_flow_multiplier: float = 1.0
    discharge_pressure_offset_bar: float = 0.0
    superheat_offset_K: float = 0.0
    compressor_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScoringState:
    """FR-ED-005: Student scoring for fault diagnosis."""
    active_fault: str = ""
    time_remaining_s: int = 30
    hints_used: int = 0
    max_score: int = 100
    hint_penalty: int = 20
    selected_answer: str = ""
    correct_answer: str = ""
    score: int = 0

    def use_hint(self):
        self.hints_used += 1

    def submit_answer(self, answer: str):
        self.selected_answer = answer
        self.score = max(0, self.max_score - self.hint_penalty * self.hints_used)
        if answer != self.correct_answer:
            self.score = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MechanicalRoomBridge:
    """Bridge between Python backend and Godot 3D mechanical room."""
    
    def __init__(self, state_file: str = None):
        if state_file is None:
            self.state_file = Path("/tmp/hvac_state.json")
        else:
            self.state_file = Path(state_file)
        
        self.current_state = MechanicalRoomState()
        self.cycle_state = CycleState()
        self.active_fault = FaultInjection()
        self.scoring = ScoringState()
    
    def update_from_refrigerant(self, refrigerant: Refrigerant, 
                                 temperature_c: float,
                                 pressure_bar: float) -> MechanicalRoomState:
        """Update state from refrigerant physics."""
        state = refrigerant.get_state(temperature_c, pressure_bar)
        
        self.current_state.refrigerant = refrigerant.name
        self.current_state.pressure_psi = self._bar_to_psi(pressure_bar)
        self.current_state.temperature_f = self._c_to_f(temperature_c)
        self.current_state.superheat_f = self._k_to_f(state.superheat_k) if hasattr(state, 'superheat_k') else 0.0
        self.current_state.subcooling_f = self._k_to_f(abs(state.subcooling_k)) if hasattr(state, 'subcooling_k') else 0.0
        self.current_state.phase = state.phase
        
        self._write_state()
        return self.current_state
    
    def update_from_scenario(self, scenario) -> MechanicalRoomState:
        """Update state from active scenario."""
        self.current_state.scenario_id = scenario.id if hasattr(scenario, 'id') else ""
        self.current_state.difficulty = scenario.difficulty.name if hasattr(scenario, 'difficulty') else ""
        self.current_state.faults = scenario.faults if hasattr(scenario, 'faults') else []
        self.current_state.hints_used = scenario.hints_used if hasattr(scenario, 'hints_used') else 0
        
        self._write_state()
        return self.current_state
    
    def update_full_state(self, **kwargs) -> MechanicalRoomState:
        """Update any fields directly."""
        for key, value in kwargs.items():
            if hasattr(self.current_state, key):
                setattr(self.current_state, key, value)
        
        self.current_state.timestamp = __import__('datetime').datetime.now().isoformat()
        self._write_state()
        return self.current_state
    
    # ── FR-ED-005: real-time cycle and fault injection ─────────────────

    def update_cycle_from_pressures(self, suction_p: float, discharge_p: float,
                                     suction_T: float = 10.0,
                                     condenser_out_T: float = 35.0,
                                     refrigerant: str = "R410A"):
        """Update 4-point cycle state from pressure and temperature data."""
        self.cycle_state.refrigerant = refrigerant
        self.cycle_state.suction_p_bar = suction_p
        self.cycle_state.suction_T_C = suction_T
        self.cycle_state.discharge_p_bar = discharge_p
        self.cycle_state.condenser_out_p_bar = discharge_p
        self.cycle_state.condenser_out_T_C = condenser_out_T
        self.cycle_state.expansion_in_p_bar = suction_p
        self.cycle_state.expansion_in_T_C = suction_T - 5

        # Apply active fault modifiers
        self.cycle_state.mass_flow = 0.05 * self.active_fault.mass_flow_multiplier
        self.cycle_state.discharge_p_bar += self.active_fault.discharge_pressure_offset_bar
        self.cycle_state.suction_superheat_K = max(0, 5.0 + self.active_fault.superheat_offset_K)
        self.cycle_state.compressor_running = self.active_fault.compressor_enabled

        # Sync to main state
        self.current_state.compressor_running = self.cycle_state.compressor_running
        self.current_state.mass_flow = self.cycle_state.mass_flow
        self.current_state.pressure_bar = discharge_p
        self._write_state()

    FAULTS = {
        "low_refrigerant": {
            "name": "Low Refrigerant Charge",
            "mass_flow_multiplier": 0.4,
            "discharge_pressure_offset_bar": -2.0,
            "superheat_offset_K": 10.0,
            "compressor_enabled": True,
        },
        "dirty_condenser": {
            "name": "Dirty Condenser",
            "mass_flow_multiplier": 1.0,
            "discharge_pressure_offset_bar": 5.0,
            "superheat_offset_K": 0.0,
            "compressor_enabled": True,
        },
        "bad_expansion_valve": {
            "name": "Failed Expansion Valve",
            "mass_flow_multiplier": 0.7,
            "discharge_pressure_offset_bar": 0.0,
            "superheat_offset_K": -4.0,
            "compressor_enabled": True,
        },
        "compressor_failure": {
            "name": "Compressor Failure",
            "mass_flow_multiplier": 0.0,
            "discharge_pressure_offset_bar": -10.0,
            "superheat_offset_K": 0.0,
            "compressor_enabled": False,
        },
    }

    def inject_fault(self, fault_id: str):
        """Inject a fault by ID. Returns fault description."""
        if fault_id not in self.FAULTS:
            raise ValueError(f"Unknown fault: {fault_id}. Available: {list(self.FAULTS)}")
        cfg = self.FAULTS[fault_id]
        self.active_fault = FaultInjection(**cfg)
        self.scoring.active_fault = fault_id
        self.scoring.correct_answer = fault_id
        self.scoring.time_remaining_s = 30
        self.scoring.hints_used = 0
        self.scoring.score = 0
        self.current_state.faults = [cfg["name"]]
        return cfg["name"]

    def clear_fault(self):
        """Clear active fault."""
        self.active_fault = FaultInjection()
        self.scoring = ScoringState()
        self.current_state.faults = []

    def _write_state(self):
        """Write current state to JSON file."""
        self.current_state.timestamp = __import__('datetime').datetime.now().isoformat()
        self.state_file.write_text(self.current_state.to_json())
    
    def read_state(self) -> Dict[str, Any]:
        """Read current state from JSON file. Returns empty dict if file missing or empty."""
        if not self.state_file.exists():
            return {}
        content = self.state_file.read_text().strip()
        if not content:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {}
    
    @staticmethod
    def _bar_to_psi(bar: float) -> float:
        """Convert bar to PSI."""
        return bar * 14.5038
    
    @staticmethod
    def _c_to_f(c: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return c * 9.0 / 5.0 + 32.0
    
    @staticmethod
    def _k_to_f(k: float) -> float:
        """Convert Kelvin delta to Fahrenheit delta."""
        return k * 9.0 / 5.0


if __name__ == '__main__':
    print("Mechanical Room Bridge — FR-3D-001")
    print("=" * 50)
    
    bridge = MechanicalRoomBridge()
    
    r = Refrigerant('R410A')
    state = r.get_state(25, 16.52)
    
    bridge.update_from_refrigerant(r, 25, 16.52)
    bridge.update_full_state(
        scenario_id="SC-001",
        difficulty="BASIC",
        faults=["overcharge"],
        session_id="demo_session_001",
        attempts_total=5,
        attempts_passed=3,
        attempts_failed=2,
        validation_status="PASS",
        divergence_percent=0.008
    )
    
    print("State written to:", bridge.state_file)
    print("\nCurrent state:")
    print(json.dumps(bridge.read_state(), indent=2))
