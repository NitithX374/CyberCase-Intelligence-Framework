from __future__ import annotations

import asyncio

import pytest

from app.analysis.technical_context.gate import chosen_gate, mitre_gate, never_applicable
from app.analysis.technical_context.gate_llm import evaluate_mitre_applicability
from app.config import settings
from app.sources.bundle import CaseSourceItem

CYBER = "ตรวจพบ PowerShell.exe เชื่อมต่อออกไปยังไอพี 198.51.100.23 เมื่อเวลา 03.00 น."
PLAIN = "พนักงานสอบสวนได้ยึดโทรศัพท์มือถือของผู้ต้องหาไว้เป็นของกลาง"


@pytest.fixture
def sources():
    return [CaseSourceItem(source_id="S1", source_kind="narrative", text=f"{PLAIN}\n{CYBER}")]


@pytest.fixture
def mode(monkeypatch):
    def set_to(value):
        monkeypatch.setattr(settings, "mitre_gate_mode", value)

    return set_to


def test_the_mode_setting_picks_the_gate(mode):
    mode("llm")
    assert chosen_gate() is evaluate_mitre_applicability
    mode("never")
    assert chosen_gate() is never_applicable


def test_never_skips_without_asking_anything(mode, sources):
    mode("never")
    record = asyncio.run(mitre_gate(case_sources=sources))

    assert record.decision == "SKIP"
    assert record.failure_code is None
    assert record.trigger_text == []
