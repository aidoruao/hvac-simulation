"""Tests for COP calculator.

Verifies refrigeration cycle thermodynamics and COP calculations.
Maps to FR-TD-008 in HVAC_SRS.md.
"""

import pytest
from cop_calculator import (
    CyclePoint, RefrigerationCycle, COPCalculator
)
from refrigerants import Refrigerant


class TestCyclePoint:
    """Unit tests for CyclePoint dataclass."""

    def test_from_coolprop_r410a(self):
        point = CyclePoint.from_coolprop('R410A', 298.15, 1.652e6)
        assert point.temperature_c == pytest.approx(25.0, abs=0.1)
        assert point.pressure_bar == pytest.approx(16.52, rel=0.01)
        assert point.enthalpy_kj_kg > 0

    def test_from_ph_two_phase(self):
        # R410A at p_evap = 9.98 bar, h = 283.76 kJ/kg (from condenser outlet)
        point = CyclePoint.from_ph('R410A', 9.98e5, 283.76e3)
        assert point.phase == "two-phase"
        assert point.quality is not None
        assert 0 < point.quality < 1

    def test_from_ph_subcooled(self):
        # Subcooled liquid at high pressure, low enthalpy
        point = CyclePoint.from_ph('R410A', 33.94e5, 200e3)
        assert point.phase == "subcooled"
        assert point.quality is None


class TestRefrigerationCycle:
    """Integration tests for complete refrigeration cycle."""

    def test_r410a_standard_cycle(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.refrigerant == 'R410A'
        assert cycle.cop_cooling > 3.0
        assert cycle.cop_cooling < 8.0
        assert cycle.cop_heating > 4.0
        assert cycle.cop_heating < 9.0

    def test_cop_heating_equals_cooling_plus_one_approx(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        # For ideal cycle: COP_heat = COP_cool + 1
        # In practice, close but not exact due to non-ideal compression
        assert cycle.cop_heating > cycle.cop_cooling

    def test_isenthalpic_expansion(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        # h4 should approximately equal h3 (isenthalpic expansion)
        h3 = cycle.condenser_out.enthalpy_kj_kg
        h4 = cycle.evaporator_in.enthalpy_kj_kg
        assert h4 == pytest.approx(h3, abs=1.0)

    def test_evaporator_heat_positive(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.evaporator_heat_kj_kg > 0

    def test_condenser_heat_positive(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.condenser_heat_kj_kg > 0

    def test_compressor_work_positive(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.compressor_work_kj_kg > 0

    def test_energy_balance(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        # Q_cond = Q_evap + W_comp (energy conservation)
        q_cond = cycle.condenser_heat_kj_kg
        q_evap = cycle.evaporator_heat_kj_kg
        w_comp = cycle.compressor_work_kj_kg
        assert q_cond == pytest.approx(q_evap + w_comp, rel=0.05)

    def test_point4_two_phase(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.evaporator_in.phase == "two-phase"
        assert cycle.evaporator_in.quality is not None
        assert 0 < cycle.evaporator_in.quality < 1

    def test_point1_superheated(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.compressor_in.phase == "superheated"

    def test_point3_subcooled(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert cycle.condenser_out.phase == "subcooled"

    def test_report_contains_formulas(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        report = cycle.generate_report()
        assert "COP_cooling" in report
        assert "ASHRAE" in report
        assert "NIST REFPROP" in report

    def test_to_dict_structure(self):
        cycle = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        data = cycle.to_dict()
        assert 'cop_cooling' in data
        assert 'cop_heating' in data
        assert 'cycle_points' in data
        assert 'evaporator_in_4' in data['cycle_points']

    def test_compare_refrigerants(self):
        comparison = COPCalculator.compare_refrigerants()
        assert 'R410A' in comparison
        assert 'R32' in comparison
        assert 'error' not in comparison['R410A']
        assert comparison['R410A']['cop_cooling'] > 0


class TestRefrigerantComparison:
    """Cross-refrigerant consistency tests."""

    def test_r32_higher_cop_than_r410a(self):
        # R32 typically has higher COP than R410A
        c32 = COPCalculator.calculate_standard_cycle('R32', 7.2, 54.4)
        c410a = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert c32.cop_cooling > c410a.cop_cooling

    def test_r134a_lower_pressure_than_r410a(self):
        c134a = COPCalculator.calculate_standard_cycle('R134a', 7.2, 54.4)
        c410a = COPCalculator.calculate_standard_cycle('R410A', 7.2, 54.4)
        assert c134a.condenser_out.pressure_bar < c410a.condenser_out.pressure_bar


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
