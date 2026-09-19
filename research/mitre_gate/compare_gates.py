"""The two gates on the same sentences, so one number can be read against the other.

The encoder is measured per sentence because that is the unit it works in. To
compare, the LLM gate is asked the same way -- one sentence at a time -- which
is not how it runs in production, where it reads the whole case at once. What
this measures is the two gates answering the same question about the same text,
not the production path.

One thing has to be said about the LLM gate's score before reading it. Its
prompt carries ten worked examples, and this eval set was written from the same
traps, so some sentences are near-copies of examples the gate has been shown
the answers to. Those are found here by trigram containment -- the same measure
the analysis uses to tell a clumsy quotation from an invented one -- and
reported separately. The uncontaminated number is the one that means anything.

    python compare_gates.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(BACKEND.parent / ".env")

from app.config import settings  # noqa: E402
from app.services.case_analysis.mitre_applicability_gate import (  # noqa: E402
    MITRE_APPLICABILITY_SYSTEM_PROMPT,
    evaluate_mitre_applicability,
)
from app.services.case_analysis.source_quote_resolver import (  # noqa: E402
    looks_like_a_paraphrase,
)
from app.services.sources import CaseSourceItem  # noqa: E402

CONCURRENCY = 6


def read(path: str) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def prompt_examples() -> list[str]:
    """The worked examples the LLM gate is shown, as written in its prompt."""

    return re.findall(r'S1:\s*"([^"]+)"', MITRE_APPLICABILITY_SYSTEM_PROMPT)


def shown_already(text: str, examples: list[str]) -> bool:
    return any(looks_like_a_paraphrase(text, example) for example in examples)


async def llm_decisions(rows: list[dict]) -> list[str]:
    limit = asyncio.Semaphore(CONCURRENCY)

    async def one(index, row):
        async with limit:
            source = CaseSourceItem(source_id="S1", source_kind="narrative", text=row["text"])
            record = await evaluate_mitre_applicability(case_sources=[source])
            print(f"\r  {index + 1}/{len(rows)}", end="", file=sys.stderr)
            return record.decision

    decisions = await asyncio.gather(*(one(i, row) for i, row in enumerate(rows)))
    print(file=sys.stderr)
    return list(decisions)


def encoder_decisions(rows: list[dict], model_path: str) -> list[str]:
    # The setting is relative to the backend, which is not the cwd here.
    settings.mitre_gate_model_path = str(BACKEND / model_path)
    from app.services.case_analysis.mitre_gate_encoder import loaded_gate, scores

    threshold = loaded_gate().threshold
    return [
        "RETRIEVE" if score >= threshold else "SKIP"
        for score in scores([row["text"] for row in rows])
    ]


def measure(rows, decisions):
    tp = sum(d == "RETRIEVE" and r["label"] == 1 for r, d in zip(rows, decisions))
    fp = sum(d == "RETRIEVE" and r["label"] == 0 for r, d in zip(rows, decisions))
    fn = sum(d == "SKIP" and r["label"] == 1 for r, d in zip(rows, decisions))
    tn = sum(d == "SKIP" and r["label"] == 0 for r, d in zip(rows, decisions))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "n": len(rows),
        "accuracy": (tp + tn) / len(rows) if rows else 0.0,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "fp": fp, "fn": fn,
    }


def show(name, result):
    print(
        f"  {name:26} n={result['n']:3}  acc={result['accuracy']:6.1%}  "
        f"P={result['precision']:6.1%}  R={result['recall']:6.1%}  "
        f"F1={result['f1']:6.1%}   fp={result['fp']} fn={result['fn']}"
    )


def table(label, rows, decisions, clean_index):
    print(f"\n{label}")
    show("all", measure(rows, decisions))
    clean_rows = [rows[i] for i in clean_index]
    show("not shown in the prompt", measure(clean_rows, [decisions[i] for i in clean_index]))
    for language in sorted({row["lang"] for row in clean_rows}):
        pairs = [(i, rows[i]) for i in clean_index if rows[i]["lang"] == language]
        show(f"  {language}", measure([r for _, r in pairs], [decisions[i] for i, _ in pairs]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval", default="eval_sentences.jsonl")
    parser.add_argument("--model", default="xlmr_ladder_best/xlmr_ladder_best")
    args = parser.parse_args()

    rows = read(args.eval)
    examples = prompt_examples()
    contaminated = [i for i, row in enumerate(rows) if shown_already(row["text"], examples)]
    clean_index = [i for i in range(len(rows)) if i not in contaminated]

    print(f"{len(rows)} sentences, {len(examples)} worked examples in the LLM gate's prompt")
    print(f"{len(contaminated)} of them are near-copies of an example the gate has been shown:")
    for i in contaminated:
        print(f"    y={rows[i]['label']}  {rows[i]['text'][:72]}")

    print("\nasking the LLM gate, one sentence at a time")
    llm = asyncio.run(llm_decisions(rows))
    encoder = encoder_decisions(rows, args.model)

    table("LLM gate (prompt, openai/gpt-5.6-luna)", rows, llm, clean_index)
    table("encoder gate (XLM-R, LADDER checkpoint)", rows, encoder, clean_index)

    print("\nwhere they disagree, on the sentences neither was shown")
    for i in clean_index:
        if llm[i] != encoder[i]:
            truth = "RETRIEVE" if rows[i]["label"] == 1 else "SKIP"
            right = "LLM" if llm[i] == truth else "encoder"
            print(
                f"  truth={truth:8} llm={llm[i]:8} enc={encoder[i]:8} "
                f"({right} right)  {rows[i]['text'][:52]}"
            )

    Path("comparison.json").write_text(
        json.dumps(
            {
                "contaminated": [rows[i]["text"] for i in contaminated],
                "llm": {
                    "all": measure(rows, llm),
                    "clean": measure([rows[i] for i in clean_index], [llm[i] for i in clean_index]),
                },
                "encoder": {
                    "all": measure(rows, encoder),
                    "clean": measure([rows[i] for i in clean_index], [encoder[i] for i in clean_index]),
                },
            },
            indent=1,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print("\nwrote comparison.json")


if __name__ == "__main__":
    main()
