import pytest
from fake_case_views import empty_view_reply
from fake_nli import FakeNli, entailing

from app.analysis import views
from app.config import settings
from app.trace import claim_validation, nli_model


@pytest.fixture(autouse=True)
def no_shadow_gate(monkeypatch):
    monkeypatch.setattr(settings, "mitre_gate_shadow", "off")


@pytest.fixture(autouse=True)
def no_model_warmup(monkeypatch):
    monkeypatch.setattr(settings, "warmup_models", False)


@pytest.fixture(autouse=True)
def no_real_meaning_model(monkeypatch):
    monkeypatch.setattr(nli_model, "load_nli", lambda: FakeNli())


@pytest.fixture(autouse=True)
def no_real_claim_verifier(monkeypatch):
    monkeypatch.setattr(claim_validation, "load_scorer", lambda: entailing("", probability=0.99))


@pytest.fixture(autouse=True)
def no_real_view_request(monkeypatch):
    monkeypatch.setattr(views, "request_stage", empty_view_reply)
