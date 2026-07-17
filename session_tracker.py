"""Session tracking and audit logging.

FR-ED-003: Time-tracked sessions. Log time per scenario.
Also satisfies aerospace audit trail requirements.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
import uuid


@dataclass
class ScenarioAttempt:
    """A single attempt at a scenario."""
    scenario_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    user_refrigerant: Optional[str] = None
    user_diagnosis: Optional[str] = None
    user_superheat: Optional[float] = None
    user_subcooling: Optional[float] = None
    passed: bool = False
    hints_used: int = 0
    retries: int = 0
    reasoning: Optional[str] = None


@dataclass
class Session:
    """A complete training session."""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    scenarios_attempted: List[ScenarioAttempt] = field(default_factory=list)
    total_hints: int = 0
    total_passes: int = 0
    total_failures: int = 0
    
    def add_attempt(self, attempt: ScenarioAttempt):
        """Add a scenario attempt to this session."""
        self.scenarios_attempted.append(attempt)
        self.total_hints += attempt.hints_used
        if attempt.passed:
            self.total_passes += 1
        else:
            self.total_failures += 1
    
    def finalize(self):
        """Calculate session totals and end time."""
        self.end_time = datetime.now().isoformat()
        
        if self.scenarios_attempted:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_seconds = (end - start).total_seconds()


class SessionTracker:
    """Tracks all training sessions with persistent storage."""
    
    LOG_DIR = "session_logs"
    
    def __init__(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        self.current_session: Optional[Session] = None
    
    def start_session(self) -> Session:
        """Start a new training session."""
        session = Session(
            session_id=str(uuid.uuid4())[:8],
            start_time=datetime.now().isoformat()
        )
        self.current_session = session
        return session
    
    def start_attempt(self, scenario_id: str) -> ScenarioAttempt:
        """Start a new scenario attempt within current session."""
        if not self.current_session:
            self.start_session()
        
        attempt = ScenarioAttempt(
            scenario_id=scenario_id,
            start_time=datetime.now().isoformat()
        )
        return attempt
    
    def end_attempt(self, attempt: ScenarioAttempt, passed: bool, 
                    refrigerant: Optional[str] = None,
                    diagnosis: Optional[str] = None,
                    superheat: Optional[float] = None,
                    subcooling: Optional[float] = None,
                    hints_used: int = 0,
                    reasoning: Optional[str] = None):
        """End a scenario attempt and record results."""
        attempt.end_time = datetime.now().isoformat()
        attempt.passed = passed
        attempt.user_refrigerant = refrigerant
        attempt.user_diagnosis = diagnosis
        attempt.user_superheat = superheat
        attempt.user_subcooling = subcooling
        attempt.hints_used = hints_used
        attempt.reasoning = reasoning
        
        # Calculate duration
        start = datetime.fromisoformat(attempt.start_time)
        end = datetime.fromisoformat(attempt.end_time)
        attempt.duration_seconds = (end - start).total_seconds()
        
        self.current_session.add_attempt(attempt)
    
    def end_session(self) -> Session:
        """End current session and save to disk."""
        if not self.current_session:
            raise ValueError("No active session")
        
        self.current_session.finalize()
        self._save_session(self.current_session)
        session = self.current_session
        self.current_session = None
        return session
    
    def _save_session(self, session: Session):
        """Save session to JSON file."""
        filename = f"{self.LOG_DIR}/session_{session.session_id}_{session.start_time[:10]}.json"
        
        data = {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "duration_seconds": session.duration_seconds,
            "total_scenarios": len(session.scenarios_attempted),
            "total_passes": session.total_passes,
            "total_failures": session.total_failures,
            "total_hints": session.total_hints,
            "scenarios": [asdict(a) for a in session.scenarios_attempted]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Session saved: {filename}")
    
    def load_session(self, filename: str) -> Dict:
        """Load a session from disk."""
        with open(filename, 'r') as f:
            return json.load(f)
    
    def list_sessions(self) -> List[str]:
        """List all session log files."""
        if not os.path.exists(self.LOG_DIR):
            return []
        return sorted([f for f in os.listdir(self.LOG_DIR) if f.endswith('.json')])
    
    def get_stats(self) -> Dict:
        """Get aggregate statistics across all sessions."""
        sessions = []
        for filename in self.list_sessions():
            sessions.append(self.load_session(os.path.join(self.LOG_DIR, filename)))
        
        if not sessions:
            return {"message": "No sessions recorded"}
        
        total_time = sum(s.get('duration_seconds', 0) or 0 for s in sessions)
        total_attempts = sum(s.get('total_scenarios', 0) for s in sessions)
        total_passes = sum(s.get('total_passes', 0) for s in sessions)
        total_failures = sum(s.get('total_failures', 0) for s in sessions)
        
        return {
            "total_sessions": len(sessions),
            "total_time_seconds": total_time,
            "total_scenarios_attempted": total_attempts,
            "total_passes": total_passes,
            "total_failures": total_failures,
            "pass_rate": total_passes / total_attempts if total_attempts > 0 else 0,
            "avg_time_per_scenario": total_time / total_attempts if total_attempts > 0 else 0,
        }


if __name__ == '__main__':
    print("HVAC Simulation — Session Tracker")
    print("FR-ED-003: Time-tracked sessions")
    print("=" * 50)
    
    tracker = SessionTracker()
    
    # Demo: simulate a session
    session = tracker.start_session()
    print(f"Session started: {session.session_id}")
    
    # Simulate SC-001 attempt
    attempt1 = tracker.start_attempt("SC-001")
    import time
    time.sleep(0.5)  # Simulate thinking time
    
    tracker.end_attempt(
        attempt1, passed=True,
        refrigerant="R410A", diagnosis="none",
        superheat=9.0, subcooling=-10.0,
        hints_used=1,
        reasoning="Correct refrigerant identification"
    )
    print(f"  SC-001: PASS ({attempt1.duration_seconds:.2f}s)")
    
    # Simulate SC-003 attempt
    attempt2 = tracker.start_attempt("SC-003")
    time.sleep(0.3)
    
    tracker.end_attempt(
        attempt2, passed=False,
        refrigerant="R410A", diagnosis="undercharge",  # Wrong
        superheat=2.0, subcooling=3.0,
        hints_used=2,
        reasoning="Wrong diagnosis — should be overcharge"
    )
    print(f"  SC-003: FAIL ({attempt2.duration_seconds:.2f}s)")
    
    # End session
    session = tracker.end_session()
    print(f"\nSession ended: {session.duration_seconds:.2f}s total")
    print(f"  Passes: {session.total_passes}, Failures: {session.total_failures}")
    print(f"  Hints used: {session.total_hints}")
    
    # Stats
    print(f"\n{'='*50}")
    print("All-time stats:")
    stats = tracker.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
