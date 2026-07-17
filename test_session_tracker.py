"""Tests for session tracking and audit logging.

Maps to FR-ED-003 in HVAC_SRS.md.
"""

import pytest
import os
import json
import time
import shutil
from session_tracker import SessionTracker, Session, ScenarioAttempt


@pytest.fixture(autouse=True)
def clean_logs():
    """Remove session_logs before each test."""
    if os.path.exists("session_logs"):
        shutil.rmtree("session_logs")
    yield
    # Cleanup after test
    if os.path.exists("session_logs"):
        shutil.rmtree("session_logs")


class TestSessionTracker:
    """FR-ED-003: Time-tracked sessions."""
    
    def test_tracker_initializes(self):
        tracker = SessionTracker()
        assert os.path.exists(SessionTracker.LOG_DIR)
    
    def test_start_session(self):
        tracker = SessionTracker()
        session = tracker.start_session()
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.start_time is not None
        assert session.scenarios_attempted == []
    
    def test_start_attempt(self):
        tracker = SessionTracker()
        tracker.start_session()
        attempt = tracker.start_attempt("SC-001")
        assert attempt.scenario_id == "SC-001"
        assert attempt.start_time is not None
        assert attempt.end_time is None
    
    def test_end_attempt_records_duration(self):
        tracker = SessionTracker()
        tracker.start_session()
        attempt = tracker.start_attempt("SC-001")
        time.sleep(0.1)
        tracker.end_attempt(attempt, passed=True, refrigerant="R410A")
        assert attempt.end_time is not None
        assert attempt.duration_seconds is not None
        assert attempt.duration_seconds >= 0.1
        assert attempt.passed is True
    
    def test_session_tracks_passes_and_failures(self):
        tracker = SessionTracker()
        tracker.start_session()
        a1 = tracker.start_attempt("SC-001")
        tracker.end_attempt(a1, passed=True)
        a2 = tracker.start_attempt("SC-003")
        tracker.end_attempt(a2, passed=False)
        assert tracker.current_session.total_passes == 1
        assert tracker.current_session.total_failures == 1
    
    def test_session_tracks_hints(self):
        tracker = SessionTracker()
        tracker.start_session()
        attempt = tracker.start_attempt("SC-001")
        tracker.end_attempt(attempt, passed=True, hints_used=2)
        assert tracker.current_session.total_hints == 2
    
    def test_end_session_saves_file(self):
        tracker = SessionTracker()
        tracker.start_session()
        attempt = tracker.start_attempt("SC-001")
        tracker.end_attempt(attempt, passed=True)
        session = tracker.end_session()
        files = tracker.list_sessions()
        assert len(files) == 1
        data = tracker.load_session(os.path.join(tracker.LOG_DIR, files[0]))
        assert data["session_id"] == session.session_id
        assert data["total_passes"] == 1
        assert len(data["scenarios"]) == 1
    
    def test_load_session_structure(self):
        tracker = SessionTracker()
        tracker.start_session()
        attempt = tracker.start_attempt("SC-001")
        tracker.end_attempt(
            attempt, passed=True,
            refrigerant="R410A",
            diagnosis="none",
            superheat=5.0,
            subcooling=8.0,
            hints_used=1,
            reasoning="Correct"
        )
        session = tracker.end_session()
        files = tracker.list_sessions()
        data = tracker.load_session(os.path.join(tracker.LOG_DIR, files[0]))
        assert "session_id" in data
        assert "start_time" in data
        assert "end_time" in data
        assert "duration_seconds" in data
        assert "total_scenarios" in data
        assert "total_passes" in data
        assert "total_failures" in data
        assert "total_hints" in data
        assert "scenarios" in data
        scenario = data["scenarios"][0]
        assert scenario["scenario_id"] == "SC-001"
        assert scenario["passed"] is True
        assert scenario["user_refrigerant"] == "R410A"
        assert scenario["hints_used"] == 1
    
    def test_stats_calculation(self):
        tracker = SessionTracker()
        tracker.start_session()
        a1 = tracker.start_attempt("SC-001")
        tracker.end_attempt(a1, passed=True)
        tracker.end_session()
        tracker.start_session()
        a2 = tracker.start_attempt("SC-003")
        tracker.end_attempt(a2, passed=False)
        tracker.end_session()
        stats = tracker.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["total_passes"] == 1
        assert stats["total_failures"] == 1
        assert stats["pass_rate"] == 0.5
        assert stats["total_scenarios_attempted"] == 2
    
    def test_no_active_session_error(self):
        tracker = SessionTracker()
        with pytest.raises(ValueError):
            tracker.end_session()
    
    def test_empty_stats(self):
        tracker = SessionTracker()
        stats = tracker.get_stats()
        assert "message" in stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
