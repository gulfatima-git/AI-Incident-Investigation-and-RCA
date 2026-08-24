from __future__ import annotations

from datetime import datetime

from src.correlation.incident_builder import Incident
from src.reporting import report_generator


def test_prompt_contains_required_fields(monkeypatch) -> None:
    incident = Incident(
        incident_id="test-1",
        source_ip="tcp|http|SF",
        start_time=datetime(2024, 1, 1, 0, 0, 0),
        end_time=datetime(2024, 1, 1, 0, 5, 0),
        event_count=2,
        attack_categories=["Probe"],
        severity="Medium",
        events=[{"event_time": datetime(2024, 1, 1, 0, 0, 0), "service": "http", "flag": "SF", "predicted_attack_category": "Probe"}],
    )

    captured = {}

    class StubClient:
        def generate(self, prompt: str) -> str:
            captured["prompt"] = prompt
            return "ok"

    monkeypatch.setattr(report_generator, "get_llm_client", lambda: StubClient())
    text = report_generator.generate_report(incident)
    assert "Incident ID: test-1" in captured["prompt"]
    assert "Source: tcp|http|SF" in captured["prompt"]
    assert text == "ok"
