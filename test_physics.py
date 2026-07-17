"""Tests for HVAC physics engine.

Verifies refrigerant properties using CoolProp 8.0.0 Helmholtz EOS.
Maps to FR-PH-001 and FR-PH-002 in HVAC_SRS.md.
"""

import pytest
from refrigerants import Refrigerant


class TestR410AProperties:
    """Verify R410A saturation properties against NIST data."""

    def test_r410a_saturation_pressure(self):
        """R410A saturation pressure at 25°C ≈ 16.52 bar (CoolProp 8.0.0)."""
        r = Refrigerant('R410A')
        p_sat = r.saturation_pressure(25)
        assert p_sat == pytest.approx(16.52, rel=0.01)

    def test_r410a_critical_point(self):
        """R410A critical point: Tc = 71.3°C, Pc = 49.0 bar."""
        r = Refrigerant('R410A')
        tc, pc = r.critical_point()
        assert tc == pytest.approx(71.34, abs=0.5)
        assert pc == pytest.approx(49.01, rel=0.02)

    def test_r410a_latent_heat(self):
        """R410A latent heat of vaporization at 25°C ≈ 186 kJ/kg."""
        r = Refrigerant('R410A')
        h_latent = r.latent_heat(25)
        assert h_latent == pytest.approx(186, rel=0.1)

    def test_r410a_saturation_temperature(self):
        """R410A saturation temperature at 16.52 bar ≈ 25°C."""
        r = Refrigerant('R410A')
        t_sat = r.saturation_temperature(16.52)
        assert t_sat == pytest.approx(25.0, abs=0.5)

    def test_state_phase_at_saturation(self):
        """At saturation pressure and temperature, phase is two-phase."""
        r = Refrigerant('R410A')
        state = r.get_state(25, 16.52)
        assert state.phase == 'two-phase'
        assert state.refrigerant == 'R410A'
        assert state.temperature_c == 25
        assert state.pressure_bar == pytest.approx(16.52, rel=0.01)


class TestMultiRefrigerant:
    """FR-PH-001: All supported refrigerants load without error."""

    def test_r22_loads(self):
        r = Refrigerant('R22')
        assert r.name == 'R22'

    def test_r134a_loads(self):
        r = Refrigerant('R134a')
        assert r.name == 'R134a'

    def test_r32_loads(self):
        r = Refrigerant('R32')
        assert r.name == 'R32'

    def test_r1234yf_loads(self):
        r = Refrigerant('R1234yf')
        assert r.name == 'R1234yf'


class TestA2LSafety:
    """FR-PH-002: A2L safety classification display."""

    def test_r32_is_a2l(self):
        r = Refrigerant('R32')
        assert r.info['class'] == 'A2L'

    def test_r1234yf_is_a2l(self):
        r = Refrigerant('R1234yf')
        assert r.info['class'] == 'A2L'

    def test_r410a_is_not_a2l(self):
        r = Refrigerant('R410A')
        assert r.info['class'] != 'A2L'
        assert r.info['class'] == 'A1'

    def test_r134a_is_not_a2l(self):
        r = Refrigerant('R134a')
        assert r.info['class'] == 'A1'


class TestRefrigerantState:
    """Verify RefrigerantState dataclass behavior."""

    def test_state_attributes(self):
        r = Refrigerant('R410A')
        state = r.get_state(25, 16.52)
        assert hasattr(state, 'density_kg_m3')
        assert hasattr(state, 'enthalpy_kj_kg')
        assert hasattr(state, 'entropy_kj_kg_k')
        assert hasattr(state, 'quality')
        assert hasattr(state, 'phase')

    def test_state_methods(self):
        r = Refrigerant('R410A')
        state = r.get_state(25, 16.52)
        assert state.is_two_phase() is True
        assert state.is_subcooled() is False
        assert state.is_superheated() is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
