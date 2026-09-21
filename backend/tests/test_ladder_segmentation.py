from __future__ import annotations

import pytest
import torch
from backend.experiments.ladder_relevance.segmentation import (
    aggregate_top_segment_margins,
    build_segment_inputs,
    pad_segment_inputs,
)


class FakeTokenizer:
    def num_special_tokens_to_add(self, pair: bool = False) -> int:
        assert pair is False
        return 2

    def encode(self, text: str, add_special_tokens: bool, truncation: bool) -> list[int]:
        assert add_special_tokens is False
        assert truncation is False
        return list(range(1, len(text) + 1))

    def build_inputs_with_special_tokens(self, token_ids: list[int]) -> list[int]:
        return [0, *token_ids, 2]


def test_build_segment_inputs_preserves_fixed_input_size() -> None:
    segments = build_segment_inputs(FakeTokenizer(), "abcdefghij", max_tokens=6)

    assert segments == [[0, 1, 2, 3, 4, 2], [0, 5, 6, 7, 8, 2], [0, 9, 10, 2]]


def test_pad_segment_inputs_returns_attention_mask() -> None:
    input_ids, attention_mask = pad_segment_inputs([[0, 1, 2], [0, 3, 4, 2]], 1)

    assert torch.equal(input_ids, torch.tensor([[0, 1, 2, 1], [0, 3, 4, 2]]))
    assert torch.equal(attention_mask, torch.tensor([[1, 1, 1, 0], [1, 1, 1, 1]]))


def test_aggregate_top_three_segment_margins() -> None:
    score, margin, selected = aggregate_top_segment_margins(torch.tensor([0.2, 1.5, 0.8, -0.2]))

    assert selected == [1, 2, 0]
    assert margin == pytest.approx(0.8333333)
    assert score == pytest.approx(0.6970593)


def test_aggregate_uses_all_segments_when_document_is_short() -> None:
    score, margin, selected = aggregate_top_segment_margins(torch.tensor([0.5, -0.5]), top_k=3)

    assert selected == [0, 1]
    assert margin == pytest.approx(0.0)
    assert score == pytest.approx(0.5)
