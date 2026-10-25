"""Cost estimate for run_current.py, from the 2026-10-02 run's recorded usage. No model call, no network.

  python estimate_cost.py

Reads ../results/run_20261001_223057.jsonl (provider-reported tokens and USD per call) and counts, with the backend's
own o200k token counter, the reading request each backend builds for the 100 articles x 3 arms: the pinned
969d61a backend (the old run's code) and the current one, each in its own subprocess. Prints counts only.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
BACKEND = HERE.parents[3]
PINNED = EXPERIMENT / "pinned" / "969d61a" / "backend"
SAMPLE_SIZE = 100
ARMS = ("clean", "targeted", "realistic")
OLD_RUN = EXPERIMENT / "results" / "run_20261001_223057.jsonl"


def articles() -> list[dict]:
    lines = (EXPERIMENT / "data" / "articles.jsonl").read_text(encoding="utf-8").split("\n")
    return [json.loads(line) for line in lines if line.strip()][:SAMPLE_SIZE]


def no_network(*args, **kwargs):
    raise OSError("estimate_cost: network blocked")


def side(which: str) -> None:
    import socket

    socket.create_connection = no_network
    socket.getaddrinfo = no_network
    code = PINNED if which == "old" else BACKEND
    os.environ["HF_HOME"] = str(BACKEND / "models" / "hf")
    os.environ["TIKTOKEN_CACHE_DIR"] = str(BACKEND / "models" / "tiktoken")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.chdir(code)
    sys.path.insert(0, str(code))
    from app.analysis.prompts import CASE_READING_JSON_PROMPT
    from app.llm.settings import AnalysisPipelineConfig
    from app.sources.bundle import CaseSourceBundle, CaseSourceItem
    from app.trace.trace import CaseProviderReadingReply

    config = AnalysisPipelineConfig(model="google/gemma-4-26b-a4b-it")
    counts = {}
    if which == "old":
        from app.analysis.write import reading_request
        from app.llm.request import stage_payload, token_count

        for article in articles():
            for arm in ARMS:
                bundle = CaseSourceBundle(revision=1, sources=(
                    CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=article[arm]),))
                payload = stage_payload(config, CASE_READING_JSON_PROMPT, reading_request(bundle, "thai", ()),
                                        CaseProviderReadingReply, grammar=False)
                counts[f"{article['id']}|{arm}"] = token_count(payload)
    else:
        from app.analysis.prompts import CASE_JUDGEMENT_SYSTEM_PROMPT, CASE_VIEWS_SYSTEM_PROMPT
        from app.analysis.reading_sources import ReadingSources
        from app.analysis.views import DerivedCaseViewsReply
        from app.analysis.write import reading_request
        from app.llm.payload import stage_payload, token_count
        from app.trace.sentences import segmenter_identity
        from app.trace.trace import CaseProviderJudgement

        for article in articles():
            for arm in ARMS:
                source = CaseSourceItem(source_id="SRC-1", source_kind="narrative", text=article[arm])
                payload = stage_payload(config, CASE_READING_JSON_PROMPT,
                                        reading_request(ReadingSources((source,)), "thai", ()),
                                        CaseProviderReadingReply)
                counts[f"{article['id']}|{arm}"] = token_count(payload)
        counts["_judgement_system"] = token_count(stage_payload(config, CASE_JUDGEMENT_SYSTEM_PROMPT, "",
                                                                CaseProviderJudgement)["system"])
        counts["_views_system"] = token_count(stage_payload(config, CASE_VIEWS_SYSTEM_PROMPT, "",
                                                            DerivedCaseViewsReply)["system"])
        counts["_segmenter"] = segmenter_identity()
    print(json.dumps(counts))


def main() -> None:
    sides = {}
    for which in ("old", "current"):
        out = subprocess.run([sys.executable, __file__, which], capture_output=True, text=True, encoding="utf-8",
                             check=True).stdout
        sides[which] = json.loads(out.strip().split("\n")[-1])
    ids = {a["id"] for a in articles()}
    calls = [c for line in OLD_RUN.read_text(encoding="utf-8").split("\n") if line.strip()
             for r in [json.loads(line)] if r["article"] in ids for c in r["calls"]]
    stage = {s: [c for c in calls if c["stage"] == s] for s in ("case_reading", "case_judgement")}
    mean = lambda cs, k: statistics.mean((c[k] or 0) for c in cs)  # noqa: E731
    keys = [k for k in sides["old"] if not k.startswith("_")]
    old_tokens = statistics.mean(sides["old"][k] for k in keys)
    current_tokens = statistics.mean(sides["current"][k] for k in keys)
    usd = sum(c["usd"] for c in calls)
    tokens_in = sum(c["input_tokens"] or 0 for c in calls)
    tokens_out = sum(c["output_tokens"] or 0 for c in calls)
    report = {
        "old_run": {"runs": 3 * SAMPLE_SIZE, "calls": len(calls), "usd": round(usd, 4),
                    "usd_per_run": round(usd / (3 * SAMPLE_SIZE), 5),
                        "effective_usd_per_m_at_0.10_in_0.30_out": round(usd / (tokens_in * 0.10e-6 + tokens_out
                                                                                 * 0.30e-6), 3)},
        "old_reading": {"calls": len(stage["case_reading"]), "input": round(mean(stage["case_reading"], "input_tokens")),
                        "output_incl_thinking": round(mean(stage["case_reading"], "output_tokens")),
                        "thinking": round(mean(stage["case_reading"], "thinking_tokens"))},
        "old_judgement": {"calls": len(stage["case_judgement"]),
                          "input": round(mean(stage["case_judgement"], "input_tokens")),
                          "output_incl_thinking": round(mean(stage["case_judgement"], "output_tokens")),
                          "thinking": round(mean(stage["case_judgement"], "thinking_tokens"))},
        "reading_request_o200k_mean": {"old": round(old_tokens), "current": round(current_tokens),
                                       "ratio": round(current_tokens / old_tokens, 3)},
        "current_system_prompt_o200k": {"judgement": sides["current"]["_judgement_system"],
                                        "views": sides["current"]["_views_system"]},
        "current_segmenter_on_this_host": sides["current"]["_segmenter"],
    }
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in ("old", "current"):
        side(sys.argv[1])
    else:
        main()
