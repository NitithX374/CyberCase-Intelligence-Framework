from __future__ import annotations

import json

import httpx
import pytest
from research.attribution_benchmark import evaluate_mt_th, translate_th
from research.attribution_benchmark.paired_statistics import (
    confusion,
    mcnemar,
    paired_cluster_delta,
    wilson,
)
from research.attribution_benchmark.run_propagation import digest
from research.attribution_benchmark.summarize_propagation import summarize


def test_exact_paired_test_and_cluster_bootstrap():
    result = mcnemar([True] * 6 + [False] * 2, [False] * 8)
    assert result["baseline_only"] == 6
    assert result["gate_only"] == 0
    assert result["exact_two_sided_p"] == 0.03125
    assert mcnemar([True], [True])["exact_two_sided_p"] == 1
    assert paired_cluster_delta([1, 1], [0, 0], [1, 1]) == [-1.0, -1.0]
    assert wilson(0, 0) is None
    assert wilson(0, 10)[1] > 0


def test_classifier_rates_use_gold_class_denominators():
    result = confusion([1, 1, 0, 0], [True, False, True, False])
    assert result["false_acceptance_rate"] == 0.5
    assert result["false_rejection_rate"] == 0.5
    assert result["precision"] == result["recall"] == result["f1"] == 0.5


def cache_row(source="Jane transferred money."):
    return {
        "key": digest(source),
        "source": source,
        "translation": "เจนโอนเงิน",
        "endpoint": translate_th.ENDPOINT,
        "model": "nmt",
        "source_language": "en",
        "target_language": "th",
    }


@pytest.mark.parametrize(
    "change",
    [{"source": "changed"}, {"target_language": "fr"}, {"translation": " "}, {"model": "other"}],
)
def test_translation_cache_refuses_changed_identity_or_empty_output(tmp_path, change):
    path = tmp_path / "cache.jsonl"
    path.write_text(json.dumps({**cache_row(), **change}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError):
        translate_th.read_cache(path)


def test_translation_cache_refuses_duplicates(tmp_path):
    path = tmp_path / "cache.jsonl"
    path.write_text((json.dumps(cache_row()) + "\n") * 2, encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate"):
        translate_th.read_cache(path)


def test_official_translation_response_order_and_key_not_in_error():
    seen = []

    def respond(request):
        seen.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={"data": {"translations": [{"translatedText": "หนึ่ง"}, {"translatedText": "สอง"}]}},
        )

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        assert translate_th.translate(client, "private-key", [("a", "one"), ("b", "two")]) == [
            "หนึ่ง",
            "สอง",
        ]
    assert seen == [
        {"q": ["one", "two"], "source": "en", "target": "th", "format": "text", "model": "nmt"}
    ]
    with (
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    403,
                    json={
                        "error": {
                            "message": "private-key",
                            "errors": [{"reason": "userRateLimitExceeded"}],
                        }
                    },
                )
            )
        ) as client,
        pytest.raises(translate_th.TranslationUnavailable) as error,
    ):
        translate_th.translate(client, "private-key", [("a", "one")])
    assert "private-key" not in str(error.value)


def test_incomplete_mt_cache_never_runs_inference(tmp_path, monkeypatch):
    monkeypatch.setattr(evaluate_mt_th, "plan", lambda: ([{"id": "one"}], {"missing": "one"}))
    monkeypatch.setattr(
        evaluate_mt_th, "load_runtime", lambda _: pytest.fail("Incomplete cache reached inference")
    )
    with pytest.raises(ValueError, match="Complete official MT cache"):
        evaluate_mt_th.run(tmp_path, tmp_path / "result")


def test_translation_gateway_error_is_visible_and_safe_to_resume():
    with (
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(502, text="upstream error")
            )
        ) as client,
        pytest.raises(translate_th.TranslationUnavailable, match="502: non-JSON"),
    ):
        translate_th.translate(client, "private-key", [("a", "one")])


@pytest.mark.parametrize(("status", "expected_calls"), [(503, 2), (403, 1)])
def test_explicit_transient_retries_preserve_inputs_and_never_retry_quota(
    status, expected_calls, monkeypatch
):
    payloads, events = [], []
    monkeypatch.setattr(translate_th, "sleep", lambda seconds: None)

    def respond(request):
        payloads.append(json.loads(request.content))
        if len(payloads) == 1:
            return httpx.Response(status, json={"error": {"errors": [{"reason": "test"}]}})
        return httpx.Response(200, json={"data": {"translations": [{"translatedText": "หนึ่ง"}]}})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        if status == 403:
            with pytest.raises(translate_th.TranslationUnavailable):
                translate_th.translate_with_attempts(
                    client, "private-key", [("a", "one")], 3, events.append
                )
        else:
            assert translate_th.translate_with_attempts(
                client, "private-key", [("a", "one")], 3, events.append
            ) == ["หนึ่ง"]
    assert len(payloads) == expected_calls
    assert all(payload == payloads[0] for payload in payloads)
    assert len(events) == 1


def test_transfer_cluster_bootstrap_keeps_paired_error_direction():
    from research.attribution_benchmark.summarize_mt_th import transfer_bootstrap

    rows = [
        {
            "id": f"row{i}",
            "src_dataset": "fixture",
            "question": str(i),
            "response": str(i),
            "attribution_label": "attributable" if i % 2 else "not attributable",
        }
        for i in range(8)
    ]
    scores = {
        row["id"]: {
            "en_supported": row["attribution_label"] == "attributable",
            "th_supported": row["attribution_label"] != "attributable",
        }
        for row in rows
    }
    result = transfer_bootstrap(rows, scores)
    assert result["en95"]["accuracy"] == [1.0, 1.0]
    assert result["th95"]["accuracy"] == [0.0, 0.0]
    assert result["th_minus_en95"]["accuracy"] == [-1.0, -1.0]


def outcome(status, accepted, negative=1, positive=1, cited_negative=0):
    return {
        "status": status,
        "calls": [],
        "raw_responses": [],
        "admission": {
            "original_rows": negative + positive,
            "accepted_rows": accepted,
            "non_attributable_admission": {
                "numerator": max(0, accepted - positive),
                "denominator": negative,
            },
            "attributable_admission_retention": {
                "numerator": min(positive, accepted),
                "denominator": positive,
            },
        },
        "propagation": None
        if status in ("failed", "no_accepted_claims")
        else {
            "non_attributable_citation_exposure_including_rejected": {
                "numerator": cited_negative,
                "denominator": negative,
            },
            "attributable_downstream_retention": {
                "numerator": min(1, accepted),
                "denominator": positive,
            },
        },
    }


def record(key, baseline, gate):
    return {
        "key": key,
        "split": "test",
        "mapping": [1, 2],
        "arms": {"unfiltered": baseline, "verified": gate},
    }


def test_generation_failure_is_unknown_and_abstention_is_explicit():
    result = summarize(
        [
            record(
                "valid", outcome("completed", 2, cited_negative=1), outcome("no_accepted_claims", 0)
            ),
            record("failed", outcome("completed", 2, cited_negative=1), outcome("failed", 1)),
        ]
    )
    assert result["observable_pairs"] == 1
    assert result["verified"]["status_counts"] == {"no_accepted_claims": 1, "failed": 1}
    assert result["unfiltered"]["paired_unsupported_citation_utilization"]["value"] == 1
    assert result["verified"]["paired_unsupported_citation_utilization"]["value"] == 0
    assert result["excluded_pairs"][0]["cluster"] == "failed"
    assert result["verified"]["supported_retention"]["denominator"] == 2


def test_protocol_violations_are_observed_raw_exposure_not_safe_outputs():
    result = summarize(
        [
            record(
                "raw",
                outcome("completed", 2, cited_negative=1),
                outcome("protocol_violation", 1, cited_negative=1),
            )
        ]
    )
    assert result["verified"]["paired_unsupported_citation_utilization"]["value"] == 1
    assert result["verified"]["status_counts"] == {"protocol_violation": 1}
