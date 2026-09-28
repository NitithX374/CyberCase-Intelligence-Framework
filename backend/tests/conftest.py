import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def no_shadow_gate(monkeypatch):
    monkeypatch.setattr(settings, "mitre_gate_shadow", "off")
