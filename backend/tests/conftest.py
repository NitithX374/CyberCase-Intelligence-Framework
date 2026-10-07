import pytest
from fake_case_views import empty_view_reply
from fake_nli import FakeNli

from app.analysis import views
from app.config import settings
from app.trace import nli_model


@pytest.fixture(autouse=True)
def no_shadow_gate(monkeypatch):
    monkeypatch.setattr(settings, "mitre_gate_shadow", "off")


@pytest.fixture(autouse=True)
def no_real_meaning_model(monkeypatch):
    monkeypatch.setattr(settings, "quote_meaning_pointer", "on")
    monkeypatch.setattr(nli_model, "load_nli", lambda: FakeNli())


@pytest.fixture(autouse=True)
def no_real_view_request(monkeypatch):
    monkeypatch.setattr(views, "request_stage", empty_view_reply)
