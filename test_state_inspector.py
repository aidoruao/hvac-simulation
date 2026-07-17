"""Tests for state inspector.

Verifies real-time observability of all system states.
Maps to FR-SF-002 in HVAC_SRS.md.
"""

import pytest
import json
from state_inspector import StateInspector, StateSnapshot, GlassBox
from refrigerants import Refrigerant


class TestStateInspector:
    """FR-SF-002: All states inspectable."""

    def test_inspector_initializes(self):
        inspector = StateInspector()
        assert inspector.current is None
        assert inspector.history == []
        assert inspector._observers == []

    def test_snapshot_creates_state(self):
        inspector = StateInspector()
        snap = inspector.snapshot(refrigerant="R410A", temperature_c=25)
        assert snap.refrigerant == "R410A"
        assert snap.temperature_c == 25
        assert snap.timestamp is not None

    def test_snapshot_stores_history(self):
        inspector = StateInspector()
        inspector.snapshot(refrigerant="R410A")
        inspector.snapshot(refrigerant="R32")
        assert len(inspector.history) == 2
        assert inspector.history[0].refrigerant == "R410A"
        assert inspector.history[1].refrigerant == "R32"

    def test_current_returns_latest(self):
        inspector = StateInspector()
        inspector.snapshot(refrigerant="R410A")
        inspector.snapshot(refrigerant="R32")
        assert inspector.get_current().refrigerant == "R32"

    def test_observe_with_refrigerant(self):
        inspector = StateInspector()
        r = Refrigerant("R410A")
        snap = inspector.observe(refrigerant=r, temperature_c=25, pressure_bar=16.52)
        assert snap.refrigerant == "R410A"
        assert snap.temperature_c == 25
        assert snap.pressure_bar == 16.52

    def test_json_export(self):
        inspector = StateInspector()
        snap = inspector.snapshot(refrigerant="R410A", temperature_c=25)
        json_str = snap.to_json()
        data = json.loads(json_str)
        assert data["refrigerant"] == "R410A"
        assert data["temperature_c"] == 25
        assert "timestamp" in data

    def test_report_generation(self):
        inspector = StateInspector()
        inspector.snapshot(
            refrigerant="R410A",
            temperature_c=25,
            pressure_bar=16.52,
            superheat_k=9.0,
            source_formula="PropsSI('P','T',298.15,'Q',1,'R410A')",
            source_citation="CoolProp 8.0.0"
        )
        report = inspector.generate_report()
        assert "STATE INSPECTOR REPORT" in report
        assert "R410A" in report
        assert "16.52" in report
        assert "CoolProp 8.0.0" in report

    def test_observer_pattern(self):
        inspector = StateInspector()
        observed = []
        def callback(snap):
            observed.append(snap.refrigerant)
        inspector.register_observer(callback)
        inspector.snapshot(refrigerant="R410A")
        assert len(observed) == 1
        assert observed[0] == "R410A"

    def test_glass_box_decorator(self):
        inspector = StateInspector()
        @GlassBox(inspector, formula="test_formula", citation="test_citation")
        def test_func(x):
            return x * 2
        result = test_func(x=5)
        assert result == 10
        assert len(inspector.history) == 1
        assert inspector.history[0].source_formula == "test_formula"

    def test_history_limit(self):
        inspector = StateInspector()
        for i in range(150):
            inspector.snapshot(temperature_c=float(i))
        recent = inspector.get_history(limit=10)
        assert len(recent) == 10
        assert recent[-1].temperature_c == 149.0

    def test_empty_report(self):
        inspector = StateInspector()
        report = inspector.generate_report()
        assert "No state recorded" in report

    def test_all_fields_present_in_json(self):
        inspector = StateInspector()
        snap = inspector.snapshot(
            refrigerant="R410A",
            temperature_c=25,
            pressure_bar=16.52,
            superheat_k=9.0,
            subcooling_k=-10.0,
            phase="two-phase",
            scenario_id="SC-001",
            difficulty="BASIC",
            faults=["overcharge"],
            hints_used=1,
            session_id="abc123",
            attempts_total=5,
            attempts_passed=3,
            attempts_failed=2,
            validation_status="PASS",
            divergence_percent=0.008,
            source_formula="PropsSI",
            source_citation="CoolProp"
        )
        data = json.loads(snap.to_json())
        assert data["refrigerant"] == "R410A"
        assert data["scenario_id"] == "SC-001"
        assert data["faults"] == ["overcharge"]
        assert data["validation_status"] == "PASS"
        assert data["divergence_percent"] == 0.008


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
