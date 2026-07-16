"""Tests for unified refrigerant interface.

Verifies all supported refrigerants against CoolProp 8.0.0.
Each test has FALSIFIES_IF conditions per HVAC_SRS.md.
"""

import pytest
from refrigerants import Refrigerant, RefrigerantState


class TestRefrigerantDatabase:
    """FR-TD-006: Multi-refrigerant support."""
    
    def test_all_refrigerants_instantiable(self):
        """Every supported refrigerant can be instantiated."""
        for name in Refrigerant.SUPPORTED:
            r = Refrigerant(name)
            assert r.name == name
            assert r.info['class'] in ['A1', 'A2L']
    
    def test_planned_refrigerants_raise_error(self):
        """Planned refrigerants raise informative errors."""
        for name in ['R454B', 'R452B', 'R1234ze']:
            with pytest.raises(ValueError) as exc_info:
                Refrigerant(name)
            assert "planned" in str(exc_info.value).lower()
    
    def test_invalid_refrigerant_raises(self):
        """Invalid refrigerant names raise ValueError."""
        with pytest.raises(ValueError):
            Refrigerant('R9999')


class TestCriticalPoints:
    """FR-TD-002: Critical point accuracy."""
    
    # Reference values from CoolProp 8.0.0
    CRITICAL_POINTS = {
        'R22':    {'T_crit': 96.15, 'P_crit': 49.90},
        'R410A':  {'T_crit': 71.34, 'P_crit': 49.01},
        'R134a':  {'T_crit': 101.06, 'P_crit': 40.59},
        'R32':    {'T_crit': 78.11, 'P_crit': 57.83},
        'R1234yf': {'T_crit': 94.70, 'P_crit': 33.84},
    }
    
    def test_critical_points(self):
        """Critical points match CoolProp within ±0.5%."""
        for name, expected in self.CRITICAL_POINTS.items():
            r = Refrigerant(name)
            T_crit, P_crit = r.critical_point()
            
            # FALSIFIES IF: deviation > 0.5%
            T_error = abs(T_crit - expected['T_crit']) / expected['T_crit']
            P_error = abs(P_crit - expected['P_crit']) / expected['P_crit']
            
            assert T_error < 0.005, f"{name} T_crit error: {T_error*100:.2f}%"
            assert P_error < 0.005, f"{name} P_crit error: {P_error*100:.2f}%"


class TestSaturationPressure:
    """FR-TD-001: Saturation pressure accuracy."""
    
    def test_r410a_at_25c(self):
        """R410A saturation pressure at 25°C."""
        r = Refrigerant('R410A')
        P = r.saturation_pressure(25)
        expected = 16.52  # bar, verified by CoolProp 8.0.0
        
        # FALSIFIES IF: deviation > 0.5%
        error = abs(P - expected) / expected
        assert error < 0.005, f"R410A P_sat error: {error*100:.2f}%"
    
    def test_r32_at_25c(self):
        """R32 saturation pressure at 25°C."""
        r = Refrigerant('R32')
        P = r.saturation_pressure(25)
        expected = 16.90  # bar, verified by CoolProp 8.0.0
        
        error = abs(P - expected) / expected
        assert error < 0.005, f"R32 P_sat error: {error*100:.2f}%"
    
    def test_r1234yf_at_25c(self):
        """R1234yf saturation pressure at 25°C."""
        r = Refrigerant('R1234yf')
        P = r.saturation_pressure(25)
        expected = 6.83  # bar, verified by CoolProp 8.0.0
        
        error = abs(P - expected) / expected
        assert error < 0.005, f"R1234yf P_sat error: {error*100:.2f}%"


class TestLatentHeat:
    """FR-TD-003: Latent heat of vaporization."""
    
    # Refrigerant-specific minimum latent heat values (kJ/kg at 25°C)
    # HFOs have lower latent heat than traditional refrigerants — this is physical reality
    MIN_LATENT_HEAT = {
        'R22': 180,
        'R410A': 180,
        'R134a': 170,
        'R32': 230,
        'R1234yf': 140,  # HFO — lower latent heat is correct
    }
    
    def test_latent_heat_positive(self):
        """Latent heat is positive and above refrigerant-specific minimum."""
        for name in Refrigerant.SUPPORTED:
            r = Refrigerant(name)
            h_fg = r.latent_heat(25)
            minimum = self.MIN_LATENT_HEAT[name]
            
            # FALSIFIES IF: h_fg < refrigerant-specific minimum
            assert h_fg > minimum, \
                f"{name} h_fg = {h_fg:.2f} kJ/kg (below minimum {minimum})"
    
    def test_r410a_latent_heat(self):
        """R410A latent heat at 25°C matches known value."""
        r = Refrigerant('R410A')
        h_fg = r.latent_heat(25)
        expected = 186.48  # kJ/kg, from test_physics.py
        
        error = abs(h_fg - expected) / expected
        assert error < 0.01, f"R410A h_fg error: {error*100:.2f}%"


class TestStateDetermination:
    """FR-TD-005: Phase state determination."""
    
    def test_superheated_state(self):
        """State above saturation is superheated."""
        r = Refrigerant('R410A')
        # At 25°C, P_sat = 16.52 bar. At 10 bar, should be superheated.
        state = r.get_state(25, 10)
        assert state.phase == 'superheated'
        assert state.is_superheated()
    
    def test_subcooled_state(self):
        """State below saturation is subcooled."""
        r = Refrigerant('R410A')
        # At 25°C, P_sat = 16.52 bar. At 20 bar, should be subcooled.
        state = r.get_state(25, 20)
        assert state.phase == 'subcooled'
        assert state.is_subcooled()


class TestA2LSafety:
    """A2L refrigerant safety properties."""
    
    def test_r32_is_a2l(self):
        """R32 is classified as A2L."""
        r = Refrigerant('R32')
        assert r.info['class'] == 'A2L'
    
    def test_r32_gwp_lower_than_r410a(self):
        """R32 GWP is significantly lower than R410A."""
        r32 = Refrigerant('R32')
        r410a = Refrigerant('R410A')
        
        assert r32.info['gwp'] < r410a.info['gwp'] / 2, \
            "R32 GWP should be < 50% of R410A"


class TestPTChartData:
    """FR-TD-007: PT chart data generation."""
    
    def test_pt_chart_structure(self):
        """PT chart data has correct structure."""
        r = Refrigerant('R410A')
        data = r.pt_chart_data(t_min_c=-40, t_max_c=60, points=100)
        
        assert 'temperature_c' in data
        assert 'pressure_bar' in data
        assert len(data['temperature_c']) == 100
        assert len(data['pressure_bar']) == 100
        
        # Pressures should increase with temperature
        for i in range(1, len(data['pressure_bar'])):
            assert data['pressure_bar'][i] > data['pressure_bar'][i-1], \
                "PT curve should be monotonically increasing"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
