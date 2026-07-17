"""Thermostat Wiring — low-voltage HVAC control circuit simulator.

FR-EL-001: Thermostat wiring schematic with interactive troubleshooting.
Teaches wire functions, color codes, and common miswiring faults.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum, auto
import json


class WireColor(Enum):
    """Standard thermostat wire colors per NEC and industry convention."""
    RED = "R"      # 24V power
    WHITE = "W"    # Heat call
    YELLOW = "Y"   # Cooling call
    GREEN = "G"    # Fan call
    BLUE = "C"     # Common (neutral)
    ORANGE = "O"   # Reversing valve (heat pump cool)
    BROWN = "B"    # Reversing valve (heat pump heat) or common alternate
    BLACK = "B"    # Alternate for common or reversing valve
    PINK = "P"     # Emergency heat
    GRAY = "Gray"  # Second stage heat/cool
    TAN = "Tan"    # Second stage heat/cool


@dataclass
class Wire:
    """A single low-voltage control wire."""
    color: WireColor
    label: str
    function: str
    voltage_present: bool = False
    connected: bool = True
    fault: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'color': self.color.name,
            'label': self.label,
            'function': self.function,
            'voltage_present': self.voltage_present,
            'connected': self.connected,
            'fault': self.fault
        }


@dataclass 
class ThermostatWiring:
    """Complete thermostat wiring configuration."""
    system_type: str  # "conventional", "heat_pump", "dual_fuel"
    stages: int  # 1 or 2
    wires: List[Wire] = field(default_factory=list)
    miswired: bool = False
    fault_description: Optional[str] = None
    
    def __post_init__(self):
        if not self.wires:
            self._build_standard_wiring()
    
    def _build_standard_wiring(self):
        """Build standard wiring for the configured system."""
        base_wires = [
            Wire(WireColor.RED, "R", "24V power (hot)"),
            Wire(WireColor.WHITE, "W", "Heat call (W1)"),
            Wire(WireColor.YELLOW, "Y", "Cooling call (Y1)"),
            Wire(WireColor.GREEN, "G", "Fan call"),
            Wire(WireColor.BLUE, "C", "Common (neutral)"),
        ]
        
        if self.system_type == "heat_pump":
            base_wires.append(Wire(WireColor.ORANGE, "O", "Reversing valve (cooling mode)"))
        
        if self.stages == 2:
            base_wires.append(Wire(WireColor.GRAY, "W2", "Second stage heat"))
            base_wires.append(Wire(WireColor.TAN, "Y2", "Second stage cool"))
        
        self.wires = base_wires
    
    def apply_fault(self, fault_type: str):
        """Apply a common miswiring fault for training."""
        self.miswired = True
        self.fault_description = fault_type
        
        faults = {
            "open_r": lambda: self._disconnect_wire("R"),
            "shorted_rc": lambda: self._short_wires("R", "C"),
            "reversing_stuck": lambda: self._stuck_reversing_valve(),
            "w1_w2_swapped": lambda: self._swap_wires("W", "W2"),
            "y1_y2_swapped": lambda: self._swap_wires("Y", "Y2"),
            "missing_common": lambda: self._disconnect_wire("C"),
            "fan_always_on": lambda: self._jumper_wire("G", "R"),
        }
        
        if fault_type in faults:
            faults[fault_type]()
    
    def _disconnect_wire(self, label: str):
        for w in self.wires:
            if w.label == label:
                w.connected = False
                w.fault = f"Open circuit: {label} wire disconnected"
    
    def _short_wires(self, label1: str, label2: str):
        for w in self.wires:
            if w.label in (label1, label2):
                w.fault = f"Short circuit: {label1}-{label2} shorted"
    
    def _stuck_reversing_valve(self):
        for w in self.wires:
            if w.label == "O":
                w.fault = "Reversing valve stuck in heating position"
    
    def _swap_wires(self, label1: str, label2: str):
        w1 = next((w for w in self.wires if w.label == label1), None)
        w2 = next((w for w in self.wires if w.label == label2), None)
        if w1 and w2:
            w1.fault = f"Miswired: swapped with {label2}"
            w2.fault = f"Miswired: swapped with {label1}"
    
    def _jumper_wire(self, label1: str, label2: str):
        for w in self.wires:
            if w.label == label1:
                w.fault = f"Jumpered: {label1} connected to {label2} — fan runs continuously"
    
    def get_wire_by_label(self, label: str) -> Optional[Wire]:
        return next((w for w in self.wires if w.label == label), None)
    
    def get_active_calls(self) -> List[str]:
        """Return list of active control signals."""
        active = []
        for w in self.wires:
            if w.connected and w.voltage_present and not w.fault:
                active.append(w.label)
        return active
    
    def to_dict(self) -> dict:
        return {
            'system_type': self.system_type,
            'stages': self.stages,
            'miswired': self.miswired,
            'fault_description': self.fault_description,
            'wires': [w.to_dict() for w in self.wires]
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
    
    def generate_schematic(self) -> str:
        """Generate ASCII schematic of wiring."""
        lines = [
            "THERMOSTAT WIRING SCHEMATIC",
            "=" * 50,
            f"System: {self.system_type.replace('_', ' ').title()}  |  Stages: {self.stages}",
            ""
        ]
        
        if self.miswired:
            lines.append(f"⚠️  FAULT INJECTED: {self.fault_description}")
            lines.append("")
        
        lines.append("Wire    Color      Function                    Status")
        lines.append("-" * 55)
        
        for w in self.wires:
            status = "OK"
            if w.fault:
                status = f"FAULT: {w.fault}"
            elif not w.connected:
                status = "DISCONNECTED"
            elif w.voltage_present:
                status = "24V ACTIVE"
            
            color_name = w.color.name.ljust(8)
            lines.append(f"{w.label.ljust(6)}  {color_name}  {w.function.ljust(26)}  {status}")
        
        lines.extend([
            "",
            "LEGEND:",
            "  R  = Red     (24V power)",
            "  W  = White   (Heat)",
            "  Y  = Yellow  (Cool)",
            "  G  = Green   (Fan)",
            "  C  = Blue    (Common)",
            "  O  = Orange  (Reversing valve — heat pump)",
            "  W2 = Gray    (2nd stage heat)",
            "  Y2 = Tan     (2nd stage cool)",
        ])
        
        return "\n".join(lines)


class WiringTroubleshooter:
    """Interactive troubleshooting guide for wiring faults."""
    
    FAULTS = {
        "open_r": {
            "symptom": "Thermostat completely dead, no display",
            "cause": "R wire (24V power) is open or disconnected",
            "test": "Check voltage between R and C at thermostat — should be ~24VAC",
            "fix": "Reconnect or replace R wire. Check transformer fuse."
        },
        "shorted_rc": {
            "symptom": "Blown low-voltage fuse, transformer hot",
            "cause": "R and C wires shorted together",
            "test": "Ohmmeter between R and C — should be open circuit",
            "fix": "Trace and separate shorted wires. Replace fuse."
        },
        "reversing_stuck": {
            "symptom": "Heat pump blows cold air in heat mode, or hot in cool mode",
            "cause": "Reversing valve (O wire) stuck or miswired",
            "test": "Check 24V at O terminal in cooling mode",
            "fix": "Verify O wire connected. If present, valve may be mechanically stuck."
        },
        "missing_common": {
            "symptom": "Thermostat works on batteries but not on system power",
            "cause": "C wire (common) missing or disconnected",
            "test": "Check for C wire at thermostat and at control board",
            "fix": "Install C wire adapter or run new 18/5 cable."
        },
        "fan_always_on": {
            "symptom": "Blower fan runs continuously, even when system is off",
            "cause": "G wire jumpered to R or fan relay stuck closed",
            "test": "Remove G wire from thermostat — fan should stop",
            "fix": "Remove jumper. If fan still runs, replace fan relay."
        },
        "w1_w2_swapped": {
            "symptom": "Second stage heat comes on immediately, or first stage never activates",
            "cause": "W1 and W2 wires swapped at thermostat or board",
            "test": "Trace wire colors: W1 should be white, W2 should be gray/tan",
            "fix": "Swap wires back to correct terminals."
        }
    }
    
    @classmethod
    def diagnose(cls, fault_type: str) -> dict:
        return cls.FAULTS.get(fault_type, {"error": "Unknown fault type"})
    
    @classmethod
    def list_faults(cls) -> List[str]:
        return list(cls.FAULTS.keys())


if __name__ == '__main__':
    print("Thermostat Wiring Simulator — FR-EL-001")
    print("=" * 60)
    
    # Demo: Conventional single-stage system
    print("\n--- CONVENTIONAL SINGLE-STAGE ---")
    conv = ThermostatWiring("conventional", 1)
    print(conv.generate_schematic())
    
    # Demo: Heat pump with fault
    print("\n--- HEAT PUMP WITH REVERSING VALVE STUCK ---")
    hp = ThermostatWiring("heat_pump", 1)
    hp.apply_fault("reversing_stuck")
    print(hp.generate_schematic())
    
    # Demo: Troubleshooting guide
    print("\n--- TROUBLESHOOTING: REVERSING VALVE ---")
    diag = WiringTroubleshooter.diagnose("reversing_stuck")
    for key, value in diag.items():
        print(f"{key.upper()}: {value}")
