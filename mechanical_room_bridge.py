"""Mechanical Room Bridge — writes HVAC state to JSON for Godot 3D scene.

FR-3D-001: 3D mechanical room with real-time gauge updates.
Connects Python backend to Godot frontend via JSON file bridge.
Same pattern as PT chart bridge.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

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
    
    def __post_init__(self):
        if self.faults is None:
            self.faults = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class MechanicalRoomBridge:
    """Bridge between Python backend and Godot 3D mechanical room."""
    
    def __init__(self, state_file: str = None):
        if state_file is None:
            self.state_file = Path("/tmp/hvac_state.json")
        else:
            self.state_file = Path(state_file)
        
        self.current_state = MechanicalRoomState()
    
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
