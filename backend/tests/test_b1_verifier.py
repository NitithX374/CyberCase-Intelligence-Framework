from types import SimpleNamespace

import pytest

from app.trace.b1_verifier import B1Verifier, selected_indices, supported_probability
from app.trace.nli_model import NliProbabilities


@pytest.mark.parametrize(
    ("scores", "indices"),
    [([0.1, 0.2, 0.8, 0.19], (1, 2)), ([0.1, 0.1], (0,)), ([-0.1, 0.15], (1,)), ([], ())],
)
def test_frozen_selector_threshold_order_and_first_maximum(scores, indices):
    assert selected_indices(scores) == indices


def test_classifier_uses_all_three_probabilities_not_entailment_argmax():
    assert supported_probability([0.45, 0.5, 0.05]) >= 0.5
    assert supported_probability([0.01, 0.98, 0.01]) < 0.5
    assert supported_probability([0.01, 0.01, 0.98]) < 0.5


@pytest.mark.parametrize("vector", [[float("nan"), 0, 1], [1, 1, 0], [1, 0], [-1, 1, 1]])
def test_invalid_nli_features_fail(vector):
    with pytest.raises(ValueError):
        supported_probability(vector)


def test_retained_units_remain_original_text_in_original_order():
    seen = []
    selector = SimpleNamespace(similarities=lambda claim, units: [0.3, 0.1, 0.5])

    def predict(premise, claim):
        seen.append((premise, claim))
        return NliProbabilities(0.9, 0.08, 0.02, 600, True)

    verifier = B1Verifier(selector, SimpleNamespace(predict=predict))
    result = verifier.verify("Jane lost 25,000 baht.", ["<tr>Jane</tr>", "weather", "25,000 baht."])
    assert seen == [("<tr>Jane</tr>\n25,000 baht.", "Jane lost 25,000 baht.")]
    assert result.indices == (0, 2)
    assert result.nli.truncated is True
    assert result.p_supported > 0.5


def test_selector_missing_scores_and_empty_units_fail():
    verifier = B1Verifier(SimpleNamespace(similarities=lambda claim, units: []), None)
    with pytest.raises(ValueError, match="every Source unit"):
        verifier.verify("claim", ["source"])
    with pytest.raises(ValueError, match="resolved Source"):
        verifier.verify("claim", [])
