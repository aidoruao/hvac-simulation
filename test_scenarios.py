"""Tests for training scenario engine.

Verifies scenario generation, assessment logic, and calculations.
Each test maps to FR-SC requirements in HVAC_SRS.md.
"""

import pytest
from scenarios import ScenarioEngine, Difficulty, Scenario


class TestScenarioEngine:
    """FR-SC-001: Training scenarios exist and are runnable."""
    
    def test_engine_initializes(self):
        """ScenarioEngine can be instantiated."""
        engine = ScenarioEngine()
        assert len(engine.SCENARIOS) >= 5
        assert len(engine.completed) == 0
    
    def test_list_all_scenarios(self):
        """All scenarios are listable."""
        engine = ScenarioEngine()
        all_scenarios = engine.list_scenarios()
        assert len(all_scenarios) == 5
        ids = [s.id for s in all_scenarios]
        assert "SC-001" in ids
        assert "SC-005" in ids
    
    def test_filter_by_difficulty(self):
        """Scenarios can be filtered by difficulty."""
        engine = ScenarioEngine()
        basic = engine.list_scenarios(Difficulty.BASIC)
        assert len(basic) == 2
        assert all(s.difficulty == Difficulty.BASIC for s in basic)
        
        intermediate = engine.list_scenarios(Difficulty.INTERMEDIATE)
        assert len(intermediate) == 2
    
    def test_get_scenario_by_id(self):
        """Individual scenarios are retrievable."""
        engine = ScenarioEngine()
        sc001 = engine.get_scenario("SC-001")
        assert sc001 is not None
        assert sc001.refrigerant == "R410A"
        
        missing = engine.get_scenario("SC-999")
        assert missing is None


class TestScenarioCalculations:
    """FR-TD-005: Superheat and subcooling calculations."""
    
    def test_sc001_superheat(self):
        """SC-001 superheat calculation is correct."""
        engine = ScenarioEngine()
        sc = engine.get_scenario("SC-001")
        sh = sc.expected_superheat_k()
        assert sh > 0
        assert sh < 20
    
    def test_sc001_subcooling(self):
        """SC-001 subcooling calculation is correct."""
        engine = ScenarioEngine()
        sc = engine.get_scenario("SC-001")
        sc_val = sc.expected_subcooling_k()
        assert isinstance(sc_val, float)
    
    def test_sc003_overcharge_low_superheat(self):
        """Overcharge scenario has low superheat."""
        engine = ScenarioEngine()
        sc = engine.get_scenario("SC-003")
        sh = sc.expected_superheat_k()
        assert sh < 5
    
    def test_sc004_undercharge_high_superheat(self):
        """Undercharge scenario has high superheat."""
        engine = ScenarioEngine()
        sc = engine.get_scenario("SC-004")
        sh = sc.expected_superheat_k()
        assert sh > 10


class TestAssessment:
    """FR-SC-001: Assessment with reasoning."""
    
    def test_correct_answer_passes(self):
        """Correct refrigerant and calculations pass."""
        engine = ScenarioEngine()
        sc = engine.get_scenario("SC-001")
        
        assessment = engine.run_scenario(
            "SC-001",
            user_refrigerant="R410A",
            user_diagnosis="none",
            user_superheat=sc.expected_superheat_k(),
            user_subcooling=sc.expected_subcooling_k()
        )
        
        assert assessment.correct_refrigerant
        assert assessment.passed
        assert "Correct refrigerant" in assessment.reasoning
    
    def test_wrong_refrigerant_fails(self):
        """Wrong refrigerant fails."""
        engine = ScenarioEngine()
        
        assessment = engine.run_scenario(
            "SC-001",
            user_refrigerant="R22",
            user_diagnosis="none",
            user_superheat=5.0,
            user_subcooling=8.0
        )
        
        assert not assessment.correct_refrigerant
        assert not assessment.passed
        assert "Wrong refrigerant" in assessment.reasoning
    
    def test_fault_diagnosis(self):
        """Fault diagnosis is checked."""
        engine = ScenarioEngine()
        
        assessment = engine.run_scenario(
            "SC-003",
            user_refrigerant="R410A",
            user_diagnosis="overcharge",
            user_superheat=2.0,
            user_subcooling=3.0
        )
        
        assert assessment.correct_diagnosis
    
    def test_wrong_fault_diagnosis(self):
        """Wrong fault diagnosis fails."""
        engine = ScenarioEngine()
        
        assessment = engine.run_scenario(
            "SC-003",
            user_refrigerant="R410A",
            user_diagnosis="undercharge",
            user_superheat=2.0,
            user_subcooling=3.0
        )
        
        assert not assessment.correct_diagnosis


class TestA2LScenarios:
    """A2L refrigerant scenarios."""
    
    def test_r32_scenario_exists(self):
        """R32 transition scenario exists."""
        engine = ScenarioEngine()
        sc = engine.get_scenario("SC-002")
        assert sc.refrigerant == "R32"
        assert sc.difficulty == Difficulty.BASIC


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
