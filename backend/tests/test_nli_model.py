from __future__ import annotations

import json
import logging
import sys
import threading
import time
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.config import settings
from app.trace import nli_model
from app.trace.nli_model import (
    LABEL_ORDER,
    MAX_TOKENS,
    WEIGHTS_SHA256,
    MdebertaNli,
    NliUnavailable,
)

WEIGHTS = Path(__file__).resolve().parents[1] / "nli_mdeberta"
HAS_WEIGHTS = (WEIGHTS / "model.safetensors").is_file()


REAL_LOAD = nli_model.load_nli


@pytest.fixture(autouse=True)
def fresh_state(monkeypatch):
    monkeypatch.setattr(nli_model, "load_nli", REAL_LOAD)
    nli_model.forget()
    yield
    nli_model.forget()


def folder(tmp_path: Path, *, labels=None) -> Path:
    (tmp_path / "model.safetensors").write_bytes(b"not the weights")
    order = labels or {"0": "entailment", "1": "neutral", "2": "contradiction"}
    (tmp_path / "config.json").write_text(json.dumps({"id2label": order}), encoding="utf-8")
    return tmp_path


def stub_libraries(monkeypatch, *, tokenizer=None, model=None):
    torch = SimpleNamespace(
        no_grad=nullcontext,
        softmax=lambda logits, dim: [[0.7, 0.2, 0.1]],
    )
    transformers = SimpleNamespace(
        AutoTokenizer=SimpleNamespace(from_pretrained=tokenizer or (lambda path: object())),
        AutoModelForSequenceClassification=SimpleNamespace(
            from_pretrained=model or (lambda path: SimpleNamespace(eval=lambda: object()))
        ),
    )
    monkeypatch.setitem(sys.modules, "torch", torch)
    monkeypatch.setitem(sys.modules, "transformers", transformers)


def at(monkeypatch, path: Path) -> None:
    monkeypatch.setattr(settings, "claim_nli_path", str(path))


def reason_of() -> str:
    with pytest.raises(NliUnavailable) as raised:
        nli_model.build()
    return raised.value.reason


def test_a_missing_folder_or_missing_weights_is_unavailable(tmp_path, monkeypatch):
    at(monkeypatch, tmp_path / "nowhere")
    assert reason_of() == "weights_missing"

    at(monkeypatch, tmp_path)
    assert reason_of() == "weights_missing"

    (tmp_path / "model.safetensors").write_bytes(b"x")
    assert reason_of() == "weights_missing"


def test_missing_libraries_are_unavailable(tmp_path, monkeypatch):
    at(monkeypatch, folder(tmp_path))
    monkeypatch.setitem(sys.modules, "torch", None)

    assert reason_of() == "libraries_missing"


def test_weights_that_are_not_the_pinned_checkpoint_are_unavailable(tmp_path, monkeypatch):
    at(monkeypatch, folder(tmp_path))
    stub_libraries(monkeypatch)

    assert reason_of() == "weights_hash_mismatch"


def test_a_label_order_that_is_not_the_expected_one_is_unavailable(tmp_path, monkeypatch):
    at(
        monkeypatch,
        folder(tmp_path, labels={"0": "neutral", "1": "entailment", "2": "contradiction"}),
    )
    stub_libraries(monkeypatch)
    monkeypatch.setattr(nli_model, "file_sha256", lambda path: WEIGHTS_SHA256)

    assert reason_of() == "label_mapping_mismatch"


def test_labels_are_read_whatever_their_case(tmp_path, monkeypatch):
    at(
        monkeypatch,
        folder(tmp_path, labels={"0": "ENTAILMENT", "1": "Neutral", "2": "contradiction"}),
    )
    stub_libraries(monkeypatch)
    monkeypatch.setattr(nli_model, "file_sha256", lambda path: WEIGHTS_SHA256)

    assert nli_model.build().order == LABEL_ORDER


def test_a_checkpoint_that_fails_to_load_is_unavailable_with_the_kind_of_failure(
    tmp_path, monkeypatch
):
    at(monkeypatch, folder(tmp_path))

    def broken(path):
        raise OSError("corrupt")

    stub_libraries(monkeypatch, tokenizer=broken)
    monkeypatch.setattr(nli_model, "file_sha256", lambda path: WEIGHTS_SHA256)

    assert reason_of() == "load_failed:OSError"


def test_the_model_is_loaded_once_and_a_failure_is_remembered_and_warned_once(
    tmp_path, monkeypatch, caplog
):
    at(monkeypatch, tmp_path / "nowhere")

    with caplog.at_level(logging.WARNING, logger="app.trace.nli_model"):
        for _ in range(3):
            with pytest.raises(NliUnavailable):
                nli_model.load_nli()

    warnings = [r for r in caplog.records if "Claim support NLI unavailable" in r.getMessage()]
    assert len(warnings) == 1
    assert "weights_missing" in warnings[0].getMessage()


def test_threads_asking_together_load_the_model_once(monkeypatch):
    built: list[int] = []

    def slow_build():
        built.append(1)
        time.sleep(0.05)
        return MdebertaNli(None, None, None, LABEL_ORDER)

    monkeypatch.setattr(nli_model, "build", slow_build)
    results: list[object] = []
    threads = [
        threading.Thread(target=lambda: results.append(nli_model.load_nli())) for _ in range(8)
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(built) == 1
    assert len({id(item) for item in results}) == 1


class Encoded(dict):
    def __init__(self, length: int) -> None:
        super().__init__(input_ids=SimpleNamespace(shape=(1, length)))


def scorer(length: int = 10, probabilities=(0.7, 0.2, 0.1), seen=None):
    def tokenizer(premise, hypothesis, truncation, return_tensors, verbose):
        assert truncation is False
        return Encoded(length)

    def model(**batch):
        if seen is not None:
            seen.append(batch)
        return SimpleNamespace(logits=None)

    torch = SimpleNamespace(
        no_grad=nullcontext,
        softmax=lambda logits, dim: [SimpleNamespace(tolist=lambda: list(probabilities))],
    )
    return MdebertaNli(torch, tokenizer, model, LABEL_ORDER)


def test_a_pair_fits_up_to_the_models_limit_and_is_never_cut():
    assert scorer(MAX_TOKENS).fits("premise", "hypothesis")
    assert not scorer(MAX_TOKENS + 1).fits("premise", "hypothesis")


def test_the_label_is_the_argmax_and_the_entailment_is_its_own_probability():
    entailed = scorer(probabilities=(0.7, 0.2, 0.1)).judge("p", "h")
    neutral = scorer(probabilities=(0.45, 0.5, 0.05)).judge("p", "h")
    contradicted = scorer(probabilities=(0.1, 0.2, 0.7)).judge("p", "h")

    assert (entailed.label, entailed.entailment) == ("entailment", 0.7)
    assert (neutral.label, neutral.entailment) == ("neutral", 0.45)
    assert (contradicted.label, contradicted.entailment) == ("contradiction", 0.1)


def test_inference_is_one_at_a_time():
    running = {"now": 0, "most": 0}
    guard = threading.Lock()

    def tokenizer(premise, hypothesis, truncation, return_tensors, verbose):
        return Encoded(10)

    def model(**batch):
        with guard:
            running["now"] += 1
            running["most"] = max(running["most"], running["now"])
        time.sleep(0.02)
        with guard:
            running["now"] -= 1
        return SimpleNamespace(logits=None)

    torch = SimpleNamespace(
        no_grad=nullcontext,
        softmax=lambda logits, dim: [SimpleNamespace(tolist=lambda: [0.7, 0.2, 0.1])],
    )
    nli = MdebertaNli(torch, tokenizer, model, LABEL_ORDER)
    threads = [threading.Thread(target=lambda: nli.judge("p", "h")) for _ in range(6)]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert running["most"] == 1


SOURCE = (
    "The outage began on Monday morning in the main office. "
    "The attackers encrypted the file server on Monday night. "
    "Staff were sent home early on Tuesday as a precaution. "
    "A ransom note appeared on every desktop in the building."
)
UNRELATED_QUOTE = "Quantum widgets shimmer under violet moonlight beyond the horizon."


needs_weights = pytest.mark.skipif(not HAS_WEIGHTS, reason="the NLI weights are not in the folder")


@needs_weights
def test_the_real_model_points_at_the_sentence_that_says_what_the_claim_says(monkeypatch):
    at(monkeypatch, WEIGHTS)
    nli = nli_model.load_nli()
    premise = "The attackers encrypted the file server on Monday night."
    hypothesis = "The file server was encrypted on Monday night."
    judgment = nli.judge(premise, hypothesis)

    assert judgment.label == "entailment"
    assert judgment.entailment >= 0.5


@needs_weights
@pytest.mark.parametrize(
    ("claim_text", "premise"),
    [
        pytest.param(
            "The hospital paid 55,000 dollars to the attackers.",
            "The weather in Bangkok was hot and humid on Monday afternoon. Traffic on the ring road was slow.",
            id="an unrelated sentence",
        ),
        pytest.param(
            "The hospital paid 5,000 dollars to the attackers.",
            "The hospital paid a ransom of 55,000 dollars to the attackers. The board met on Friday morning.",
            id="a wrong amount",
        ),
        pytest.param(
            "The hospital paid a ransom to the attackers.",
            "The hospital did not pay any ransom to the attackers. The board met on Friday morning.",
            id="a negation",
        ),
        pytest.param(
            "The accountant paid the money to the vendor on Monday.",
            "Prosecutors allege that the accountant paid the money to the vendor on Monday. The court sat late.",
            id="an allegation",
        ),
    ],
)
def test_the_real_model_gives_no_passage_when_the_source_does_not_say_it(
    claim_text, premise, monkeypatch
):
    at(monkeypatch, WEIGHTS)
    nli = nli_model.load_nli()
    judgment = nli.judge(premise, claim_text)

    assert judgment.label != "entailment" or judgment.entailment < 0.5


@needs_weights
def test_the_real_model_reads_thai(monkeypatch):
    at(monkeypatch, WEIGHTS)
    nli = nli_model.load_nli()
    premise = "ผู้เสียหายโอนเงินจำนวน 85,000 บาทไปยังบัญชีของคนร้ายเมื่อวันที่ 5 มีนาคม"
    hypothesis = "ผู้เสียหายโอนเงิน 85,000 บาทให้คนร้าย"
    judgment = nli.judge(premise, hypothesis)

    assert judgment.label == "entailment"
    assert judgment.entailment >= 0.5


@needs_weights
def test_the_real_weights_match_the_pinned_checkpoint():
    assert nli_model.file_sha256(WEIGHTS / "model.safetensors") == WEIGHTS_SHA256
