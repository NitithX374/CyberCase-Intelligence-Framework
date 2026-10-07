from __future__ import annotations

import argparse
import copy
import json
import shutil
from collections import defaultdict

import pytest
from research.attribution_benchmark import run_propagation as harness
from research.attribution_benchmark.data import cluster_key, read_split, verify_manifest
from research.attribution_benchmark.propagation_data import (
    ResponseCluster,
    load_inputs,
    load_verifier,
    select_clusters,
)
from research.attribution_benchmark.propagation_judgement import judge, prepare_payload, row_claim
from research.attribution_benchmark.propagation_metrics import (
    admission_metrics,
    labelled_ids,
    propagation_metrics,
)

from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT
from app.llm.settings import AnalysisPipelineConfig
from app.trace.trace import CaseProviderJudgement

VERIFIER_RUN = (
    harness.REPOSITORY
    / "research/attribution_benchmark/runs/candidates_en_20261006T010418Z/minicheck_cuda_float32_b1"
)


@pytest.fixture(scope="module")
def raw_rows():
    return read_split("dev")


@pytest.fixture(scope="module")
def verifier(raw_rows):
    return load_verifier(VERIFIER_RUN, "dev", raw_rows, verify_manifest())


def groups(rows):
    grouped = defaultdict(list)
    for row in rows:
        grouped[cluster_key(row)].append(row)
    return [
        ResponseCluster(key, tuple(sorted(members, key=lambda row: row["id"])))
        for key, members in sorted(grouped.items())
    ]


def mixed_cluster(rows):
    return next(
        cluster
        for cluster in groups(rows)
        if all(labelled_ids(cluster)) and len({row["claim"] for row in cluster.rows}) >= 2
    )


def args(output, execute=False):
    return argparse.Namespace(
        verifier_run=VERIFIER_RUN,
        split="dev",
        limit=1,
        output=output,
        execute=execute,
        judgement_model="google/gemma-4-26b-a4b-it" if execute else None,
    )


def live_args(output):
    return argparse.Namespace(
        verifier_run=VERIFIER_RUN,
        split="dev",
        limit=1,
        output=output,
        execute=True,
        judgement_model="google/gemma-4-26b-a4b-it",
    )


def actual_summary(cluster, ids):
    return " ".join(
        f"{row['claim']} [{claim_id}]" for claim_id, row in cluster.assigned_rows if claim_id in ids
    )


async def citing_input(payload, config, calls):
    calls.append({"stage": "case_judgement", "status": "test_stub"})
    summary = " ".join(
        f"{claim['text']} [{claim['claim_id']}]" for claim in payload["reading"]["claims"]
    )
    return CaseProviderJudgement(version="case_analysis_trace_v1", summary=summary)


def test_selection_is_reproducible_and_keeps_original_rows(raw_rows):
    original = copy.deepcopy(raw_rows)
    selected, receipt = select_clusters(raw_rows, 5)
    reordered, _ = select_clusters(list(reversed(raw_rows)), 5)
    assert selected == reordered
    assert receipt["eligible_clusters"] > 5
    assert raw_rows == original
    for cluster in selected:
        assert {cluster_key(row) for row in cluster.rows} == {cluster.key}
        assert [row["id"] for _, row in cluster.assigned_rows] == sorted(
            row["id"] for row in cluster.rows
        )
        assert len(cluster.rows) == sum(cluster_key(row) == cluster.key for row in raw_rows)
    with pytest.raises(ValueError, match="1..5"):
        select_clusters(raw_rows, 6)


def test_frozen_scores_match_raw_and_threshold_is_reused(raw_rows, verifier):
    selection = json.loads((VERIFIER_RUN / "selection.json").read_text(encoding="utf-8"))
    assert verifier.threshold == selection["threshold"]
    assert len(verifier.scores) == len(raw_rows)
    for row in raw_rows:
        assert verifier.accepts(row) == (
            verifier.scores[row["id"]]["p_supported"] >= selection["threshold"]
        )
        assert verifier.scores[row["id"]]["references"] == row["references"]


def test_cache_hash_mismatch_fails_without_fallback(raw_rows, tmp_path):
    for filename in (
        "run_manifest.json",
        "summary.json",
        "selection.json",
        "verification.json",
        "scores_dev.jsonl",
    ):
        shutil.copyfile(VERIFIER_RUN / filename, tmp_path / filename)
    with (tmp_path / "scores_dev.jsonl").open("ab") as stream:
        stream.write(b" ")
    with pytest.raises(ValueError, match="artifact hash mismatch"):
        load_verifier(tmp_path, "dev", raw_rows, verify_manifest())


@pytest.mark.parametrize("split", ["dev", "test", "test_ood"])
def test_native_adapter_preserves_long_references_and_original_claim(split):
    rows = read_split(split)
    row = max(rows, key=lambda item: max(map(len, item["references"]), default=0))
    original = copy.deepcopy(row)
    claim = row_claim("A-01", row)
    assert claim.text == row["claim"]
    assert claim.epistemic_status == "reported"
    for index, reference in enumerate(row["references"], 1):
        citations = [
            citation
            for citation in claim.supporting_citations
            if citation.source_id == f"R-{row['id']}-ref-{index:02d}"
        ]
        assert "".join(citation.exact_quote for citation in citations) == reference
        assert all(
            citation.pointer_state == "direct" and citation.document_id is None
            for citation in citations
        )
        assert all(
            citation.exact_quote == reference[citation.start : citation.end]
            for citation in citations
        )
    assert row == original
    assert max(map(len, row["references"])) > 2_000


def test_original_claim_whitespace_is_preserved(raw_rows):
    row = next(row for row in raw_rows if row["claim"] != row["claim"].strip())
    assert row_claim("A-01", row).text == row["claim"]


def test_duplicate_claim_rows_keep_separate_evidence_and_ids(raw_rows):
    cluster = next(
        cluster
        for cluster in groups(raw_rows)
        if len(cluster.rows) > len({row["claim"] for row in cluster.rows}) >= 2
    )
    payload = prepare_payload(cluster, {claim_id for claim_id, _ in cluster.assigned_rows})
    claims = payload["reading"]["claims"]
    assert len(claims) == len(cluster.rows)
    assert len({claim["claim_id"] for claim in claims}) == len(claims)
    source_sets = [
        {citation["source_id"] for citation in claim["supporting_citations"]} for claim in claims
    ]
    assert all(not a & b for i, a in enumerate(source_sets) for b in source_sets[i + 1 :])


def test_gate_preserves_ids_and_never_transmits_gold_or_response(raw_rows, verifier):
    cluster = mixed_cluster(raw_rows)
    accepted = {claim_id for claim_id, row in cluster.assigned_rows if verifier.accepts(row)}
    payload = prepare_payload(cluster, accepted)
    claims = payload["reading"]["claims"]
    assert [claim["claim_id"] for claim in claims] == [
        claim_id for claim_id, _ in cluster.assigned_rows if claim_id in accepted
    ]
    assert set(payload) == {"response_language", "reading", "followup_history", "technical_context"}
    assert payload["technical_context"] is None and payload["followup_history"] == []
    assert all(
        "gold" not in claim and "attribution_label" not in claim and "response" not in claim
        for claim in claims
    )
    assert {claim["epistemic_status"] for claim in claims} <= {"reported"}


def test_metrics_count_original_rows_with_fixed_denominators(raw_rows):
    cluster = mixed_cluster(raw_rows)
    positive, negative = labelled_ids(cluster)
    all_ids = positive | negative
    positive_id, negative_id = min(positive), min(negative)
    summary = actual_summary(cluster, {positive_id, negative_id})
    summary += " " + actual_summary(cluster, {negative_id})
    measured = propagation_metrics(cluster, all_ids, summary)
    assert measured["protocol_valid"]
    assert measured["non_attributable_propagation"] == {
        "numerator": 1,
        "denominator": len(negative),
        "value": 1 / len(negative),
    }
    assert measured["attributable_downstream_retention"]["denominator"] == len(positive)
    gated = propagation_metrics(cluster, positive, summary)
    assert gated["cited_rejected_claim_ids"] == [negative_id]
    assert not gated["protocol_valid"]
    assert gated["non_attributable_conditional_propagation"]["value"] is None
    assert gated["non_attributable_citation_exposure_including_rejected"]["numerator"] == 1
    assert admission_metrics(cluster, set())["accepted_rows"] == 0


def test_unknown_malformed_and_uncited_outputs_are_not_safe_success(raw_rows):
    cluster = mixed_cluster(raw_rows)
    accepted = {claim_id for claim_id, _ in cluster.assigned_rows}
    original_claim = cluster.rows[0]["claim"]
    for summary in (original_claim, f"{original_claim} [A-999]", f"{original_claim} [A-1]", "."):
        assert not propagation_metrics(cluster, accepted, summary)["protocol_valid"]


@pytest.mark.asyncio
async def test_default_offline_runner_never_calls_judgement_reader_or_verifier(
    tmp_path, monkeypatch
):
    async def forbidden(*args, **kwargs):
        raise AssertionError("Offline harness called a model")

    monkeypatch.setattr(harness, "judge", forbidden)
    monkeypatch.setattr("app.analysis.write.request_stage", forbidden)
    monkeypatch.setattr(
        "research.attribution_benchmark.propagation_judgement.request_stage", forbidden
    )
    output = await harness.run(args(tmp_path / "offline"))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    outcomes = json.loads((output / "outcomes.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "prepared" and manifest["maximum_judgement_stage_calls"] == 0
    assert {outcome["arm"] for outcome in outcomes} == {"unfiltered", "verified"}
    assert all(outcome["propagation"] is None and outcome["calls"] == [] for outcome in outcomes)
    assert not list(output.rglob("judgement.json"))
    with pytest.raises(FileExistsError):
        await harness.run(args(output))


@pytest.mark.asyncio
async def test_live_bridge_uses_only_native_judgement_contract(raw_rows, monkeypatch):
    cluster = mixed_cluster(raw_rows)
    accepted = {claim_id for claim_id, _ in cluster.assigned_rows}
    payload = prepare_payload(cluster, accepted)
    config = AnalysisPipelineConfig(model="google/gemma-4-26b-a4b-it")
    received = []

    async def stub(**kwargs):
        received.append(kwargs)
        return CaseProviderJudgement(
            version="case_analysis_trace_v1", summary=actual_summary(cluster, accepted)
        )

    monkeypatch.setattr("research.attribution_benchmark.propagation_judgement.request_stage", stub)
    await judge(payload, config, [])
    assert len(received) == 1
    request = received[0]
    assert request["stage"] == "case_judgement" and request["schema"] is CaseProviderJudgement
    assert request["system"] == CASE_JUDGEMENT_SYSTEM_PROMPT and request["content"] == payload
    assert request["config"] is config and request["temperature"] == 0
    with pytest.raises(ValueError, match="no accepted claims"):
        await judge(prepare_payload(cluster, set()), config, [])
    assert len(received) == 1


@pytest.mark.asyncio
async def test_failures_are_recorded_and_raised(tmp_path, monkeypatch):
    async def failing(payload, config, calls):
        calls.append({"stage": "case_judgement", "status": "failed"})
        raise RuntimeError("controlled transport failure")

    monkeypatch.setattr(harness, "judge", failing)
    output = tmp_path / "failure"
    with pytest.raises(RuntimeError, match="controlled transport failure"):
        await harness.run(args(output, execute=True))
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    outcome = json.loads(
        (next(output.rglob("unfiltered/outcome.json"))).read_text(encoding="utf-8")
    )
    assert manifest["status"] == "failed" and (output / "failure.json").is_file()
    assert outcome["status"] == "failed" and outcome["propagation"] is None
    assert outcome["calls"] == [{"stage": "case_judgement", "status": "failed"}]


def test_live_cli_requires_explicit_model_and_bounded_limit():
    with pytest.raises(SystemExit):
        harness.arguments(["--verifier-run", str(VERIFIER_RUN), "--execute"])
    with pytest.raises(SystemExit):
        harness.arguments(["--verifier-run", str(VERIFIER_RUN), "--limit", "6"])


@pytest.mark.asyncio
async def test_paired_execution_uses_same_config_and_preserves_id_mapping(tmp_path, monkeypatch):
    requests = []

    async def stub(payload, config, calls):
        requests.append((payload, config))
        return await citing_input(payload, config, calls)

    monkeypatch.setattr(harness, "judge", stub)
    output = await harness.run(live_args(tmp_path / "paired"))
    outcomes = json.loads((output / "outcomes.json").read_text(encoding="utf-8"))
    assert len(requests) == 2 and requests[0][1] is requests[1][1]
    original = {claim["claim_id"]: claim for claim in requests[0][0]["reading"]["claims"]}
    assert all(
        original[claim["claim_id"]] == claim for claim in requests[1][0]["reading"]["claims"]
    )
    assert all(outcome["status"] == "completed" for outcome in outcomes)
    assert (
        outcomes[0]["propagation"]["non_attributable_propagation"]["denominator"]
        == outcomes[1]["propagation"]["non_attributable_propagation"]["denominator"]
    )


@pytest.mark.asyncio
async def test_actual_zero_admission_cluster_skips_judgement(tmp_path, monkeypatch):
    dataset, verifier, _, selection = load_inputs("dev", 1, VERIFIER_RUN)
    grouped = defaultdict(list)
    for row in read_split("dev"):
        grouped[cluster_key(row)].append(row)
    key, rows = next(
        (key, rows)
        for key, rows in sorted(grouped.items())
        if len({row["claim"] for row in rows}) >= 2
        and not any(verifier.accepts(row) for row in rows)
    )
    cluster = ResponseCluster(key, tuple(sorted(rows, key=lambda row: row["id"])))
    monkeypatch.setattr(
        harness, "load_inputs", lambda *args: (dataset, verifier, (cluster,), selection)
    )
    monkeypatch.setattr(harness, "judge", citing_input)
    output = await harness.run(live_args(tmp_path / "empty-admission"))
    baseline, filtered = json.loads((output / "outcomes.json").read_text(encoding="utf-8"))
    assert baseline["status"] == "completed" and len(baseline["calls"]) == 1
    assert filtered["status"] == "no_accepted_claims" and filtered["calls"] == []
    assert filtered["propagation"] is None and filtered["accepted_claim_ids"] == []
    assert len(list(output.rglob("judgement.json"))) == 1


@pytest.mark.asyncio
async def test_protocol_violation_is_preserved_and_fails_run(tmp_path, monkeypatch):
    async def uncited(payload, config, calls):
        return CaseProviderJudgement(
            version="case_analysis_trace_v1", summary=payload["reading"]["claims"][0]["text"]
        )

    monkeypatch.setattr(harness, "judge", uncited)
    output = tmp_path / "invalid-summary"
    with pytest.raises(ValueError, match="citation protocol violation"):
        await harness.run(live_args(output))
    outcome = json.loads(next(output.rglob("unfiltered/outcome.json")).read_text(encoding="utf-8"))
    assert outcome["status"] == "protocol_violation"
    assert not outcome["propagation"]["protocol_valid"]
    assert next(output.rglob("judgement.json")).is_file()
    assert json.loads((output / "manifest.json").read_text(encoding="utf-8"))["status"] == "failed"
