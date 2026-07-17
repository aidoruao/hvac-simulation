"""Tests for thermostat wiring simulator.

Verifies low-voltage HVAC control circuit logic.
Maps to FR-EL-001 in HVAC_SRS.md.
"""

import pytest
from thermostat_wiring import (
    ThermostatWiring, Wire, WireColor, 
    WiringTroubleshooter
)


class TestThermostatWiring:
    """FR-EL-001: Thermostat wiring schematic."""

    def test_conventional_single_stage(self):
        tw = ThermostatWiring("conventional", 1)
        assert tw.system_type == "conventional"
        assert tw.stages == 1
        assert len(tw.wires) == 5
        labels = [w.label for w in tw.wires]
        assert "R" in labels
        assert "W" in labels
        assert "Y" in labels
        assert "G" in labels
        assert "C" in labels

    def test_heat_pump_has_reversing_valve(self):
        tw = ThermostatWiring("heat_pump", 1)
        labels = [w.label for w in tw.wires]
        assert "O" in labels
        assert tw.system_type == "heat_pump"

    def test_two_stage_has_w2_y2(self):
        tw = ThermostatWiring("conventional", 2)
        labels = [w.label for w in tw.wires]
        assert "W2" in labels
        assert "Y2" in labels

    def test_heat_pump_two_stage(self):
        tw = ThermostatWiring("heat_pump", 2)
        labels = [w.label for w in tw.wires]
        assert "O" in labels
        assert "W2" in labels
        assert "Y2" in labels
        assert len(tw.wires) == 8

    def test_wire_colors_match_standard(self):
        tw = ThermostatWiring("conventional", 1)
        r_wire = tw.get_wire_by_label("R")
        assert r_wire.color == WireColor.RED
        assert r_wire.function == "24V power (hot)"

    def test_apply_fault_open_r(self):
        tw = ThermostatWiring("conventional", 1)
        tw.apply_fault("open_r")
        assert tw.miswired is True
        r_wire = tw.get_wire_by_label("R")
        assert r_wire.connected is False
        assert "Open circuit" in r_wire.fault

    def test_apply_fault_missing_common(self):
        tw = ThermostatWiring("conventional", 1)
        tw.apply_fault("missing_common")
        c_wire = tw.get_wire_by_label("C")
        assert c_wire.connected is False
        assert "missing" in tw.fault_description or "Open circuit" in c_wire.fault

    def test_apply_fault_fan_always_on(self):
        tw = ThermostatWiring("conventional", 1)
        tw.apply_fault("fan_always_on")
        g_wire = tw.get_wire_by_label("G")
        assert "Jumpered" in g_wire.fault

    def test_apply_fault_reversing_stuck(self):
        tw = ThermostatWiring("heat_pump", 1)
        tw.apply_fault("reversing_stuck")
        o_wire = tw.get_wire_by_label("O")
        assert "stuck" in o_wire.fault

    def test_apply_fault_w1_w2_swapped(self):
        tw = ThermostatWiring("conventional", 2)
        tw.apply_fault("w1_w2_swapped")
        w1 = tw.get_wire_by_label("W")
        w2 = tw.get_wire_by_label("W2")
        assert "swapped" in w1.fault
        assert "swapped" in w2.fault

    def test_get_active_calls_no_voltage(self):
        tw = ThermostatWiring("conventional", 1)
        active = tw.get_active_calls()
        assert active == []  # No voltage present yet

    def test_get_active_calls_with_voltage(self):
        tw = ThermostatWiring("conventional", 1)
        for w in tw.wires:
            w.voltage_present = True
        active = tw.get_active_calls()
        assert "R" in active
        assert "W" in active
        assert "Y" in active

    def test_generate_schematic_contains_all_wires(self):
        tw = ThermostatWiring("conventional", 1)
        schematic = tw.generate_schematic()
        assert "R" in schematic
        assert "W" in schematic
        assert "Y" in schematic
        assert "G" in schematic
        assert "C" in schematic

    def test_generate_schematic_shows_fault(self):
        tw = ThermostatWiring("heat_pump", 1)
        tw.apply_fault("reversing_stuck")
        schematic = tw.generate_schematic()
        assert "FAULT INJECTED" in schematic
        assert "reversing_stuck" in schematic

    def test_to_dict_structure(self):
        tw = ThermostatWiring("conventional", 1)
        data = tw.to_dict()
        assert data['system_type'] == "conventional"
        assert data['stages'] == 1
        assert len(data['wires']) == 5
        assert 'color' in data['wires'][0]

    def test_to_json_roundtrip(self):
        tw = ThermostatWiring("conventional", 1)
        json_str = tw.to_json()
        import json
        data = json.loads(json_str)
        assert data['system_type'] == "conventional"


class TestWiringTroubleshooter:
    """FR-EL-001: Troubleshooting guide."""

    def test_diagnose_known_fault(self):
        diag = WiringTroubleshooter.diagnose("open_r")
        assert "symptom" in diag
        assert "cause" in diag
        assert "test" in diag
        assert "fix" in diag

    def test_diagnose_unknown_fault(self):
        diag = WiringTroubleshooter.diagnose("nonexistent")
        assert "error" in diag

    def test_list_faults(self):
        faults = WiringTroubleshooter.list_faults()
        assert "open_r" in faults
        assert "missing_common" in faults
        assert "reversing_stuck" in faults

    def test_reversing_stuck_symptom(self):
        diag = WiringTroubleshooter.diagnose("reversing_stuck")
        assert "cold air" in diag["symptom"].lower() or "hot" in diag["symptom"].lower()

    def test_open_r_symptom(self):
        diag = WiringTroubleshooter.diagnose("open_r")
        assert "dead" in diag["symptom"].lower() or "no display" in diag["symptom"].lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
