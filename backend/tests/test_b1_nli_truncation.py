from contextlib import nullcontext
from types import SimpleNamespace

from app.trace.nli_model import LABEL_ORDER, MAX_TOKENS, MdebertaNli


def test_production_feature_vector_uses_research_longest_first_truncation():
    tokens, calls = [], []

    def tokenizer(premise, hypothesis, **kwargs):
        tokens.append(kwargs)
        size = MAX_TOKENS if kwargs.get("truncation") else MAX_TOKENS + 40
        return {"input_ids": SimpleNamespace(shape=(1, size))}

    def model(**batch):
        calls.append(batch["input_ids"].shape[-1])
        return SimpleNamespace(logits=None)

    torch = SimpleNamespace(
        no_grad=nullcontext,
        softmax=lambda logits, dim: [SimpleNamespace(tolist=lambda: [0.45, 0.5, 0.05])],
    )
    result = MdebertaNli(torch, tokenizer, model, LABEL_ORDER).predict("source", "complete claim")
    assert result.vector == (0.45, 0.5, 0.05)
    assert result.label == "neutral"
    assert result.raw_tokens == MAX_TOKENS + 40
    assert result.truncated is True
    assert calls == [MAX_TOKENS]
    assert tokens[-1]["truncation"] is True
    assert tokens[-1]["max_length"] == MAX_TOKENS
