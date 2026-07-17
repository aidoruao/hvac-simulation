"""Tests for validation layer.

Verifies divergence detection and reference data integrity.
Maps to FR-SF-001 in HVAC_SRS.md.
"""

import pytest
from validation import ValidationLayer, ValidationResult, REFERENCE_DATA, DIVERGENCE_THRESHOLD
from refrigerants import Refrigerant


class TestValidationLayer:
    """FR-SF-001: Divergence warning system."""
    
    def test_layer_initializes(self):
        """ValidationLayer can be instantiated."""
        v = ValidationLayer()
        assert v.threshold == DIVERGENCE_THRESHOLD
        assert len(v.history) == 0
    
    def test_saturation_pressure_validation_passes(self):
        """R410A saturation pressure at 25°C validates within threshold."""
        v = ValidationLayer()
        result = v.validate_saturation_pressure('R410A', 25)
        
        assert result.passed
        assert result.divergence < DIVERGENCE_THRESHOLD
        assert result.warning is None
    
    def test_critical_point_validation(self):
        """Critical point validation for all refrigerants."""
        v = ValidationLayer()
        
        for name in Refrigerant.SUPPORTED:
            T_res, P_res = v.validate_critical_point(name)
            assert T_res.passed, f"{name} T_crit failed: {T_res.divergence*100:.3f}%"
            assert P_res.passed, f"{name} P_crit failed: {P_res.divergence*100:.3f}%"
    
    def test_full_validation_suite(self):
        """Full validation suite runs without failures."""
        v = ValidationLayer()
        results = v.validate_all()
        
        total_checks = sum(len(checks) for checks in results.values())
        assert total_checks > 0
        
        failures = sum(1 for checks in results.values() for c in checks if not c.passed)
        assert failures == 0, f"{failures} validation failures detected"
    
    def test_history_tracks_all_checks(self):
        """All validation calls are tracked in history."""
        v = ValidationLayer()
        v.validate_saturation_pressure('R410A', 25)
        v.validate_critical_point('R410A')
        
        assert len(v.history) == 3
    
    def test_report_generation(self):
        """Divergence report is human-readable."""
        v = ValidationLayer()
        v.validate_all()
        
        report = v.get_divergence_report()
        assert "VALIDATION REPORT" in report
        assert "PASS" in report
        assert "Total checks:" in report


class TestReferenceData:
    """Reference data integrity."""
    
    def test_all_refrigerants_have_reference_data(self):
        """Every supported refrigerant has reference data."""
        for name in Refrigerant.SUPPORTED:
            assert name in REFERENCE_DATA, f"No reference data for {name}"
    
    def test_reference_values_are_positive(self):
        """All reference values are physically reasonable."""
        for name, data in REFERENCE_DATA.items():
            for key, value in data.items():
                assert value > 0, f"{name}.{key} = {value} (must be positive)"
    
    def test_r410a_reference_matches_test_physics(self):
        """R410A reference data matches test_physics.py ground truth."""
        ref = REFERENCE_DATA['R410A']
        assert abs(ref['P_sat_25C_bar'] - 16.52) < 0.01
        assert abs(ref['T_crit_C'] - 71.34) < 0.01
        assert abs(ref['P_crit_bar'] - 49.01) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
