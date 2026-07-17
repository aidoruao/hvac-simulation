"""Tests for extended scenario engine.

Verifies 20+ unique faults and extended scenario library.
Maps to FR-SC-002 in HVAC_SRS.md.
"""

import pytest
from scenarios_extended import ExtendedScenarioEngine, EXTENDED_SCENARIOS
from scenarios import Difficulty


class TestExtendedScenarios:
    """FR-SC-002: 20+ unique fault injections."""
    
    def test_engine_has_23_scenarios(self):
        """Total scenario count is 23."""
        engine = ExtendedScenarioEngine()
        assert len(engine.SCENARIOS) == 23
    
    def test_20_unique_faults(self):
        """At least 20 unique faults exist."""
        engine = ExtendedScenarioEngine()
        assert engine.get_fault_count() >= 20
    
    def test_all_difficulties_present(self):
        """All difficulty levels have scenarios."""
        engine = ExtendedScenarioEngine()
        for diff in Difficulty:
            count = len(engine.list_scenarios(diff))
            assert count > 0, f"No scenarios for {diff.name}"
    
    def test_expert_scenarios_exist(self):
        """Expert-level scenarios exist."""
        engine = ExtendedScenarioEngine()
        expert = engine.list_scenarios(Difficulty.EXPERT)
        assert len(expert) >= 3
    
    def test_a2l_safety_scenario(self):
        """A2L leak scenario exists."""
        engine = ExtendedScenarioEngine()
        faults = engine.list_faults()
        assert "a2l_leak" in faults
    
    def test_r32_scenarios(self):
        """R32 refrigerant scenarios exist."""
        engine = ExtendedScenarioEngine()
        r32_scenarios = [s for s in engine.SCENARIOS if s.refrigerant == "R32"]
        assert len(r32_scenarios) >= 2
    
    def test_multiple_fault_scenario(self):
        """At least one scenario has multiple faults."""
        engine = ExtendedScenarioEngine()
        multi_fault = [s for s in engine.SCENARIOS if len(s.faults) > 1]
        assert len(multi_fault) >= 1
    
    def test_all_scenarios_have_customer_complaint(self):
        """All scenarios beyond BASIC have customer complaints."""
        engine = ExtendedScenarioEngine()
        for s in engine.SCENARIOS:
            if s.difficulty != Difficulty.BASIC:
                assert s.customer_complaint is not None
                assert len(s.customer_complaint) > 0
    
    def test_all_scenarios_have_hints(self):
        """All scenarios have at least one hint."""
        engine = ExtendedScenarioEngine()
        for s in engine.SCENARIOS:
            assert len(s.hints) >= 1
    
    def test_fault_list_is_sorted(self):
        """Fault list is alphabetically sorted."""
        engine = ExtendedScenarioEngine()
        faults = engine.list_faults()
        assert faults == sorted(faults)
    
    def test_scenario_ids_unique(self):
        """All scenario IDs are unique."""
        engine = ExtendedScenarioEngine()
        ids = [s.id for s in engine.SCENARIOS]
        assert len(ids) == len(set(ids))
    
    def test_scenario_ids_sequential(self):
        """Scenario IDs follow SC-XXX pattern."""
        engine = ExtendedScenarioEngine()
        for s in engine.SCENARIOS:
            assert s.id.startswith("SC-")
            num = int(s.id.split("-")[1])
            assert 1 <= num <= 999


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
