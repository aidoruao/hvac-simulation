"""
FR-TD-009: SEER Calculator Test
"""

import pytest
from seer_calculator import SEERCalculator, PartLoadCondition

def test_seer_calculator_initializes():
    seer = SEERCalculator("R410A")
    assert seer.refrigerant == "R410A"
    assert len(seer.conditions) == 4
    assert seer.seer > 0

def test_seer_standard_r410a():
    seer = SEERCalculator("R410A")
    assert seer.seer == pytest.approx(22.40, abs=0.1)
    assert seer.weighted_cop == pytest.approx(6.56, abs=0.1)
    assert seer.total_cooling_btu > 0
    assert seer.total_energy_wh > 0

def test_seer_above_doe_minimum():
    seer = SEERCalculator("R410A")
    assert seer.seer >= 14.0, "SEER below DOE 2023 minimum of 14.0"

def test_seer_above_energy_star():
    seer = SEERCalculator("R410A")
    assert seer.seer >= 15.0, "SEER below ENERGY STAR 2023 minimum of 15.0"

def test_part_load_conditions_sum_to_one():
    seer = SEERCalculator("R410A")
    total_frac = sum(c.fractional_hours for c in seer.conditions)
    assert total_frac == pytest.approx(1.0, abs=0.001)

def test_eer_conversion():
    seer = SEERCalculator("R410A")
    expected_eer = seer.weighted_cop * 3.41214
    assert seer.eer_from_cop == pytest.approx(expected_eer, abs=0.01)

def test_json_export():
    seer = SEERCalculator("R410A")
    data = seer.to_dict()
    assert "seer" in data
    assert "weighted_cop" in data
    assert "conditions" in data
    assert len(data["conditions"]) == 4
    assert data["seer"] > 0

def test_formula_citations_present():
    seer = SEERCalculator("R410A")
    assert "AHRI" in seer.SOURCE
    assert "ASHRAE" in seer.VALIDATION
    assert "SEER" in seer.SEER_FORMULA
    assert "COP" in seer.COP_TO_EER

def test_report_generation():
    seer = SEERCalculator("R410A")
    report = seer.generate_report()
    assert "SEER ANALYSIS REPORT" in report
    assert "R410A" in report
    assert "22.40" in report or str(round(seer.seer, 2)) in report
    assert "DOE Minimum" in report
    assert "ENERGY STAR" in report
