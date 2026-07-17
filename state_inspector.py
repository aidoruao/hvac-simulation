"""State inspector — real-time observability of all system states.

FR-SF-002: All states inspectable. Glass box enforcement.
Every variable, every calculation, every decision — visible.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import inspect


@dataclass
class StateSnapshot:
    """A snapshot of the complete system state at a point in time."""
    timestamp: str
    refrigerant: Optional[str] = None
    temperature_c: Optional[float] = None
    pressure_bar: Optional[float] = None
    superheat_k: Optional[float] = None
    subcooling_k: Optional[float] = None
    phase: Optional[str] = None
    scenario_id: Optional[str] = None
    difficulty: Optional[str] = None
    faults: List[str] = field(default_factory=list)
    hints_used: int = 0
    session_id: Optional[str] = None
    attempts_total: int = 0
    attempts_passed: int = 0
    attempts_failed: int = 0
    validation_status: Optional[str] = None
    divergence_percent: Optional[float] = None
    source_formula: Optional[str] = None
    source_citation: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


class StateInspector:
    """Real-time state inspector for the HVAC simulation.
    
    Every state variable is exposed. Nothing is hidden.
    """
    
    def __init__(self):
        self.history: List[StateSnapshot] = []
        self.current: Optional[StateSnapshot] = None
        self._observers: List[callable] = []
    
    def snapshot(self, **kwargs) -> StateSnapshot:
        """Create a state snapshot from current system state."""
        # Separate known fields from extra data
        known_fields = {f.name for f in StateSnapshot.__dataclass_fields__.values()}
        known_fields.remove('extra_data')
        
        snap_kwargs = {'timestamp': datetime.now().isoformat()}
        extra = {}
        
        for key, value in kwargs.items():
            if key in known_fields:
                snap_kwargs[key] = value
            else:
                extra[key] = value
        
        snap_kwargs['extra_data'] = extra
        snap = StateSnapshot(**snap_kwargs)
        
        self.current = snap
        self.history.append(snap)
        self._notify_observers(snap)
        return snap
    
    def observe(self, refrigerant=None, scenario=None, session=None,
                validation=None, **extra) -> StateSnapshot:
        """Observe and snapshot the complete system state."""
        snap_kwargs = {}
        
        if refrigerant:
            snap_kwargs['refrigerant'] = refrigerant.name if hasattr(refrigerant, 'name') else str(refrigerant)
            snap_kwargs['temperature_c'] = getattr(refrigerant, 'temperature_c', None)
            snap_kwargs['pressure_bar'] = getattr(refrigerant, 'pressure_bar', None)
        
        if scenario:
            snap_kwargs['scenario_id'] = scenario.id if hasattr(scenario, 'id') else None
            snap_kwargs['difficulty'] = scenario.difficulty.name if hasattr(scenario.difficulty, 'name') else str(scenario.difficulty)
            snap_kwargs['faults'] = scenario.faults if hasattr(scenario, 'faults') else []
        
        if session:
            snap_kwargs['session_id'] = session.session_id if hasattr(session, 'session_id') else None
            snap_kwargs['attempts_total'] = len(session.scenarios_attempted) if hasattr(session, 'scenarios_attempted') else 0
            snap_kwargs['attempts_passed'] = session.total_passes if hasattr(session, 'total_passes') else 0
            snap_kwargs['attempts_failed'] = session.total_failures if hasattr(session, 'total_failures') else 0
        
        if validation:
            snap_kwargs['validation_status'] = 'PASS' if getattr(validation, 'passed', False) else 'FAIL'
            snap_kwargs['divergence_percent'] = validation.divergence * 100 if hasattr(validation, 'divergence') else None
        
        snap_kwargs.update(extra)
        return self.snapshot(**snap_kwargs)
    
    def get_current(self) -> Optional[StateSnapshot]:
        """Get the most recent state snapshot."""
        return self.current
    
    def get_history(self, limit: int = 100) -> List[StateSnapshot]:
        """Get recent state history."""
        return self.history[-limit:]
    
    def register_observer(self, callback: callable):
        """Register a callback to be called on every state change."""
        self._observers.append(callback)
    
    def _notify_observers(self, snap: StateSnapshot):
        """Notify all observers of state change."""
        for cb in self._observers:
            try:
                cb(snap)
            except Exception as e:
                print(f"Observer error: {e}")
    
    def generate_report(self) -> str:
        """Generate human-readable state report."""
        if not self.current:
            return "No state recorded."
        
        s = self.current
        lines = [
            "STATE INSPECTOR REPORT",
            "=" * 50,
            f"Timestamp: {s.timestamp}",
            "",
            "THERMODYNAMIC STATE",
            f"  Refrigerant: {s.refrigerant or 'N/A'}",
            f"  Temperature: {s.temperature_c:.2f}°C" if s.temperature_c else "  Temperature: N/A",
            f"  Pressure: {s.pressure_bar:.4f} bar" if s.pressure_bar else "  Pressure: N/A",
            f"  Superheat: {s.superheat_k:.2f}K" if s.superheat_k else "  Superheat: N/A",
            f"  Subcooling: {s.subcooling_k:.2f}K" if s.subcooling_k else "  Subcooling: N/A",
            f"  Phase: {s.phase or 'N/A'}",
            "",
            "SCENARIO STATE",
            f"  ID: {s.scenario_id or 'N/A'}",
            f"  Difficulty: {s.difficulty or 'N/A'}",
            f"  Faults: {', '.join(s.faults) if s.faults else 'N/A'}",
            f"  Hints used: {s.hints_used}",
            "",
            "SESSION STATE",
            f"  Session ID: {s.session_id or 'N/A'}",
            f"  Attempts: {s.attempts_total} (Pass: {s.attempts_passed}, Fail: {s.attempts_failed})",
            "",
            "VALIDATION STATE",
            f"  Status: {s.validation_status or 'N/A'}",
            f"  Divergence: {s.divergence_percent:.4f}%" if s.divergence_percent else "  Divergence: N/A",
            "",
            "TRACEABILITY",
            f"  Formula: {s.source_formula or 'N/A'}",
            f"  Citation: {s.source_citation or 'N/A'}",
        ]
        
        if s.extra_data:
            lines.extend([
                "",
                "EXTRA DATA",
            ])
            for key, value in s.extra_data.items():
                lines.append(f"  {key}: {value}")
        
        lines.extend([
            "",
            "HISTORY",
            f"  Total snapshots: {len(self.history)}",
        ])
        
        return "\n".join(lines)


class GlassBox:
    """Glass box decorator — wraps any function to expose its state."""
    
    def __init__(self, inspector: StateInspector, formula: str = None, citation: str = None):
        self.inspector = inspector
        self.formula = formula
        self.citation = citation
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            self.inspector.snapshot(
                source_formula=self.formula or func.__name__,
                source_citation=self.citation or "See FORMULA_CITATIONS.md",
                extra_data={'function_args': kwargs, 'function_result': result}
            )
            
            return result
        return wrapper


if __name__ == '__main__':
    print("HVAC Simulation — State Inspector")
    print("FR-SF-002: All states inspectable")
    print("=" * 50)
    
    from refrigerants import Refrigerant
    
    inspector = StateInspector()
    
    r = Refrigerant('R410A')
    state = r.get_state(25, 16.52)
    
    inspector.observe(
        refrigerant=r,
        temperature_c=25,
        pressure_bar=16.52,
        superheat_k=9.0,
        subcooling_k=-10.0,
        phase=state.phase,
        source_formula="PropsSI('P', 'T', T_k, 'Q', 1, 'R410A')",
        source_citation="CoolProp 8.0.0 Helmholtz EOS, Lemmon et al. 2018"
    )
    
    print(inspector.generate_report())
    print(f"\n{'='*50}")
    print("JSON export:")
    print(inspector.current.to_json())
