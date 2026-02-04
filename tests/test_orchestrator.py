import os
import pytest
from orchestrator_agent import OrchestratorAgent


def test_build_sections_minimal():
    orch = OrchestratorAgent()
    # minimal synthetic proposal
    proposal = {
        "client": "Test Co",
        "summary": "A short summary.",
        "requirements": [{"id": "REQ-1", "text": "Migrate X to cloud."}],
        "technical_mapping": [{"requirement_id": "REQ-1", "services": ["Cloud Migration"], "approach": "Lift-and-shift", "compliance_score": 90}],
        "pricing": {"total_hours": 80, "scenarios": {"baseline": 9600, "competitive": 8640, "premium": 11520}},
    }
    sections = orch.build_sections(proposal)
    assert len(sections) == 7
    titles = [s['title'] for s in sections]
    assert 'I. Executive Summary' in titles
    assert 'V. Timeline and Pricing' in titles


if __name__ == '__main__':
    pytest.main([os.path.dirname(__file__)])
