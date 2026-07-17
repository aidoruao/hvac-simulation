"""Tests for mechanical room bridge.

Verifies JSON state bridge between Python backend and Godot 3D scene.
Maps to FR-3D-001 in HVAC_SRS.md.
"""

import pytest
import json
import tempfile
from pathlib import Path

from mechanical_room_bridge import MechanicalRoomBridge, MechanicalRoomState
from refrigerants import Refrigerant


class TestMechanicalRoomState:
    """Unit tests for MechanicalRoomState dataclass."""

    def test_default_state(self):
        state = MechanicalRoomState()
        assert state.refrigerant == "R410A"
        assert state.pressure_psi == 0.0
        assert state.faults == []

    def test_to_dict(self):
        state = MechanicalRoomState(refrigerant="R32", pressure_psi=150.0)
        data = state.to_dict()
        assert data["refrigerant"] == "R32"
        assert data["pressure_psi"] == 150.0

    def test_to_json(self):
        state = MechanicalRoomState(refrigerant="R410A", phase="two-phase")
        json_str = state.to_json()
        data = json.loads(json_str)
        assert data["refrigerant"] == "R410A"
        assert data["phase"] == "two-phase"


class TestMechanicalRoomBridge:
    """Integration tests for MechanicalRoomBridge."""

    def test_bridge_initializes_no_file_yet(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            assert bridge.state_file.exists() is False

    def test_update_from_refrigerant(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            r = Refrigerant("R410A")
            
            state = bridge.update_from_refrigerant(r, 25, 16.52)
            
            assert state.refrigerant == "R410A"
            assert state.pressure_psi == pytest.approx(239.60, rel=0.01)
            assert state.temperature_f == 77.0
            assert state.phase == "two-phase"

    def test_state_written_to_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            r = Refrigerant("R410A")
            bridge.update_from_refrigerant(r, 25, 16.52)
            
            assert bridge.state_file.exists()
            data = bridge.read_state()
            assert data["refrigerant"] == "R410A"

    def test_update_from_scenario(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            
            class MockScenario:
                id = "SC-002"
                difficulty = type('obj', (object,), {'name': 'ADVANCED'})()
                faults = ["undercharge", "dirty_condenser"]
                hints_used = 2
            
            state = bridge.update_from_scenario(MockScenario())
            
            assert state.scenario_id == "SC-002"
            assert state.difficulty == "ADVANCED"
            assert state.faults == ["undercharge", "dirty_condenser"]
            assert state.hints_used == 2

    def test_update_full_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            
            state = bridge.update_full_state(
                refrigerant="R32",
                pressure_psi=180.0,
                temperature_f=85.0,
                phase="superheated"
            )
            
            assert state.refrigerant == "R32"
            assert state.pressure_psi == 180.0
            assert state.phase == "superheated"

    def test_bar_to_psi_conversion(self):
        psi = MechanicalRoomBridge._bar_to_psi(1.0)
        assert psi == pytest.approx(14.5038, rel=0.0001)

    def test_c_to_f_conversion(self):
        f = MechanicalRoomBridge._c_to_f(0)
        assert f == 32.0
        f = MechanicalRoomBridge._c_to_f(100)
        assert f == 212.0

    def test_k_to_f_conversion(self):
        f = MechanicalRoomBridge._k_to_f(5.0)
        assert f == 9.0

    def test_read_empty_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.json"
            path.write_text("")
            bridge = MechanicalRoomBridge(state_file=str(path))
            data = bridge.read_state()
            assert data == {}

    def test_read_missing_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            data = bridge.read_state()
            assert data == {}

    def test_timestamp_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            bridge = MechanicalRoomBridge(state_file=str(path))
            bridge.update_full_state(refrigerant="R410A")
            
            data = bridge.read_state()
            assert "timestamp" in data
            assert len(data["timestamp"]) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
