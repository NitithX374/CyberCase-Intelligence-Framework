"""Which gate runs, and what the encoder gate makes of what it is given.

The encoder itself is measured in research/mitre_gate, not here. What these
check is the part the rest of the system depends on: that the mode setting
picks the gate, and that whatever the classifier says, the record it produces
is grounded in the material -- every trigger an exact piece of a cited source.
"""

from __future__ import annotations

import asyncio

import pytest

from app.config import settings
from app.services.analysis.mitre_gate import chosen_gate, mitre_gate, never_applicable
from app.services.analysis.mitre_gate.llm import (
    evaluate_mitre_applicability,
    validate_mitre_applicability,
)
from app.services.sources import CaseSourceItem

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


def test_the_encoder_gate_quotes_the_sentence_it_fired_on(mode, monkeypatch, sources):
    """The classifier's answer is a sentence, so the trigger is that sentence."""

    from app.services.analysis.mitre_gate import encoder

    mode("encoder")
    monkeypatch.setattr(
        encoder, "loaded_gate", lambda: encoder.Loaded(None, None, None, 1, 0.5, 96)
    )
    monkeypatch.setattr(
        encoder, "scores", lambda texts: [0.9 if CYBER in t else 0.1 for t in texts]
    )

    record = asyncio.run(mitre_gate(case_sources=sources))

    assert record.decision == "RETRIEVE"
    assert record.source_message_ids == ["S1"]
    assert record.trigger_text == [CYBER]
    assert PLAIN not in record.trigger_text


def test_what_the_encoder_returns_passes_the_grounding_check(mode, monkeypatch, sources):
    """The same check the LLM gate's output has to pass."""

    from app.services.analysis.mitre_gate import encoder

    mode("encoder")
    monkeypatch.setattr(
        encoder, "loaded_gate", lambda: encoder.Loaded(None, None, None, 1, 0.5, 96)
    )
    monkeypatch.setattr(encoder, "scores", lambda texts: [0.9] * len(texts))

    record = asyncio.run(mitre_gate(case_sources=sources))
    regrounded = validate_mitre_applicability(
        {
            "decision": record.decision,
            "source_message_ids": record.source_message_ids,
            "trigger_text": record.trigger_text,
        },
        sources,
    )

    assert regrounded.decision == "RETRIEVE"
    assert regrounded.failure_code is None


def test_nothing_above_the_threshold_is_a_skip(mode, monkeypatch, sources):
    from app.services.analysis.mitre_gate import encoder

    mode("encoder")
    monkeypatch.setattr(
        encoder, "loaded_gate", lambda: encoder.Loaded(None, None, None, 1, 0.5, 96)
    )
    monkeypatch.setattr(encoder, "scores", lambda texts: [0.2] * len(texts))

    assert asyncio.run(mitre_gate(case_sources=sources)).decision == "SKIP"


def test_a_case_with_no_readable_text_is_a_skip(mode):
    """Nothing to split, so nothing to load the model for."""

    mode("encoder")
    blank = [CaseSourceItem(source_id="S1", source_kind="narrative", text="   ")]
    assert asyncio.run(mitre_gate(case_sources=blank)).decision == "SKIP"


def test_only_the_sources_actually_quoted_are_cited(mode, monkeypatch):
    """A source whose sentences all scored low is not named as a trigger."""

    from app.services.analysis.mitre_gate import encoder

    mode("encoder")
    sources = [
        CaseSourceItem(source_id="S1", source_kind="narrative", text=PLAIN),
        CaseSourceItem(source_id="S2", source_kind="narrative", text=CYBER),
    ]
    monkeypatch.setattr(
        encoder, "loaded_gate", lambda: encoder.Loaded(None, None, None, 1, 0.5, 96)
    )
    monkeypatch.setattr(
        encoder, "scores", lambda texts: [0.9 if CYBER in t else 0.1 for t in texts]
    )

    record = asyncio.run(mitre_gate(case_sources=sources))

    assert record.source_message_ids == ["S2"]
