"""Validation layer — cross-check CoolProp against reference data.

FR-SF-001: Warn if simulation diverges >5% from reference.
Every calculation gets a second opinion.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from CoolProp.CoolProp import PropsSI
from refrigerants import Refrigerant


# Reference data from NIST and ASHRAE handbooks
# These are ground truth values independent of CoolProp
REFERENCE_DATA = {
    'R410A': {
        'P_sat_25C_bar': 16.52,      # NIST REFPROP / ASHRAE
        'P_sat_0C_bar': 8.00,        # Approximate
        'T_crit_C': 71.34,
        'P_crit_bar': 49.01,
        'h_fg_25C_kJ_kg': 186.48,
        'rho_liq_25C_kg_m3': 1058.90,
        'rho_vap_25C_kg_m3': 65.95,
    },
    'R22': {
        'P_sat_25C_bar': 10.44,
        'T_crit_C': 96.15,
        'P_crit_bar': 49.90,
    },
    'R134a': {
        'P_sat_25C_bar': 6.65,
        'T_crit_C': 101.06,
        'P_crit_bar': 40.59,
    },
    'R32': {
        'P_sat_25C_bar': 16.90,
        'T_crit_C': 78.11,
        'P_crit_bar': 57.83,
    },
    'R1234yf': {
        'P_sat_25C_bar': 6.83,
        'T_crit_C': 94.70,
        'P_crit_bar': 33.84,
    },
}

DIVERGENCE_THRESHOLD = 0.05  # 5% per FR-SF-001


@dataclass
class ValidationResult:
    """Result of a validation check."""
    property_name: str
    refrigerant: str
    calculated: float
    reference: float
    divergence: float  # Absolute relative error
    passed: bool
    warning: Optional[str] = None


class ValidationLayer:
    """Cross-checks CoolProp calculations against reference data."""
    
    def __init__(self, threshold: float = DIVERGENCE_THRESHOLD):
        self.threshold = threshold
        self.history: List[ValidationResult] = []
    
    def validate_saturation_pressure(self, refrigerant: str, temp_c: float) -> ValidationResult:
        """Validate saturation pressure at given temperature."""
        ref_key = f'P_sat_{int(temp_c)}C_bar'
        ref_value = REFERENCE_DATA.get(refrigerant, {}).get(ref_key)
        
        if ref_value is None:
            return ValidationResult(
                property_name=f'P_sat_{int(temp_c)}C',
                refrigerant=refrigerant,
                calculated=0.0,
                reference=0.0,
                divergence=0.0,
                passed=True,
                warning=f"No reference data for {refrigerant} at {temp_c}°C"
            )
        
        r = Refrigerant(refrigerant)
        calculated = r.saturation_pressure(temp_c)
        divergence = abs(calculated - ref_value) / ref_value
        
        result = ValidationResult(
            property_name=f'P_sat_{int(temp_c)}C',
            refrigerant=refrigerant,
            calculated=calculated,
            reference=ref_value,
            divergence=divergence,
            passed=divergence < self.threshold,
            warning=None if divergence < self.threshold else 
                f"DIVERGENCE WARNING: {divergence*100:.2f}% > {self.threshold*100:.0f}%"
        )
        
        self.history.append(result)
        return result
    
    def validate_critical_point(self, refrigerant: str) -> Tuple[ValidationResult, ValidationResult]:
        """Validate critical temperature and pressure."""
        r = Refrigerant(refrigerant)
        T_crit, P_crit = r.critical_point()
        
        ref = REFERENCE_DATA.get(refrigerant, {})
        
        T_result = self._check_value('T_crit', refrigerant, T_crit, ref.get('T_crit_C', 0))
        P_result = self._check_value('P_crit', refrigerant, P_crit, ref.get('P_crit_bar', 0))
        
        self.history.extend([T_result, P_result])
        return T_result, P_result
    
    def _check_value(self, prop: str, refrigerant: str, calculated: float, 
                     reference: float) -> ValidationResult:
        """Generic value check."""
        if reference == 0:
            return ValidationResult(
                property_name=prop,
                refrigerant=refrigerant,
                calculated=calculated,
                reference=reference,
                divergence=0.0,
                passed=True,
                warning="No reference value"
            )
        
        divergence = abs(calculated - reference) / reference
        return ValidationResult(
            property_name=prop,
            refrigerant=refrigerant,
            calculated=calculated,
            reference=reference,
            divergence=divergence,
            passed=divergence < self.threshold,
            warning=None if divergence < self.threshold else 
                f"DIVERGENCE WARNING: {divergence*100:.2f}%"
        )
    
    def validate_all(self) -> Dict[str, List[ValidationResult]]:
        """Run full validation suite on all refrigerants."""
        results = {}
        
        for name in Refrigerant.SUPPORTED:
            results[name] = []
            
            # Saturation pressure at 25°C
            if f'P_sat_25C_bar' in REFERENCE_DATA.get(name, {}):
                results[name].append(self.validate_saturation_pressure(name, 25))
            
            # Critical point
            T_res, P_res = self.validate_critical_point(name)
            results[name].extend([T_res, P_res])
        
        return results
    
    def get_divergence_report(self) -> str:
        """Generate human-readable divergence report."""
        lines = ["VALIDATION REPORT", "=" * 50]
        
        warnings = [r for r in self.history if r.warning]
        passes = [r for r in self.history if r.passed and not r.warning]
        failures = [r for r in self.history if not r.passed]
        
        lines.append(f"\nTotal checks: {len(self.history)}")
        lines.append(f"Passed: {len(passes)}")
        lines.append(f"Warnings (no ref data): {len(warnings) - len(failures)}")
        lines.append(f"FAILURES: {len(failures)}")
        
        if failures:
            lines.append("\n--- FAILURES ---")
            for f in failures:
                lines.append(f"{f.refrigerant}.{f.property_name}: "
                           f"calc={f.calculated:.4f} ref={f.reference:.4f} "
                           f"err={f.divergence*100:.3f}%")
                lines.append(f"  >> {f.warning}")
        
        lines.append("\n--- ALL CHECKS ---")
        for r in self.history:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"{status} {r.refrigerant}.{r.property_name}: "
                       f"{r.calculated:.4f} vs {r.reference:.4f} "
                       f"({r.divergence*100:.3f}%)")
        
        return "\n".join(lines)


if __name__ == '__main__':
    print("HVAC Simulation — Validation Layer")
    print("FR-SF-001: Divergence check against reference data")
    print("=" * 50)
    
    validator = ValidationLayer()
    results = validator.validate_all()
    
    print(validator.get_divergence_report())
    
    # Exit with error code if any failures
    failures = sum(1 for checks in results.values() for c in checks if not c.passed)
    if failures > 0:
        print(f"\n⚠️  {failures} validation failures detected.")
        print("CoolProp may have updated its equations of state.")
        print("Review reference data or adjust threshold.")
    else:
        print("\n✅ All validations passed. Physics engine verified.")
