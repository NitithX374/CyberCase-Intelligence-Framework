from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODEL = "BAAI/bge-m3"
REVISION = "5617a9f61b028005a4858fdac845db406aefb181"
SNAPSHOT = Path.home() / ".cache" / "huggingface" / "hub" / "models--BAAI--bge-m3" / "snapshots" / REVISION
DEV = "English development"
PREMISES = ("quote", "window")
LEVELS = (0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50)
OUT = HERE / "results" / "checker_embedding_scores.json"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"
    sys.path.insert(0, str(HERE))
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer
    from checker_units import checks as load_checks

    torch.set_num_threads(args.threads)
    checks = load_checks(args.backend)
    texts = sorted({t for c in checks for t in (c["claim"], c["quote"], c["window"])}, key=lambda t: (len(t), t))
    model = SentenceTransformer(str(SNAPSHOT), device="cpu")
    model.max_seq_length = 2048
    lengths = [len(model.tokenizer(t)["input_ids"]) for t in texts]
    print(f"{len(checks)} checks, {len(texts)} texts, longest {max(lengths)} tokens", flush=True)
    started = time.monotonic()
    parts = []
    for start in range(0, len(texts), 256):
        parts.append(model.encode(texts[start:start + 256], batch_size=16, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False))
        print(f"{start + len(parts[-1])}/{len(texts)} {time.monotonic() - started:.0f}s", flush=True)
    seconds = time.monotonic() - started
    vectors = np.concatenate(parts)
    at = {t: i for i, t in enumerate(texts)}
    rows = []
    for c in checks:
        row = {k: c[k] for k in ("id", "set", "case", "kind", "elsewhere", "rule")}
        for kind in PREMISES:
            row[kind] = round(float(vectors[at[c["claim"]]] @ vectors[at[c[kind]]]), 6)
        rows.append(row)

    dev_real = [c for c in checks if c["set"] == DEV and c["kind"] == "real"]
    target = sum(c["P3"] for c in dev_real) / len(dev_real)
    thresholds = {}
    for kind in PREMISES:
        real = np.array([r[kind] for r in rows if r["set"] == DEV and r["kind"] == "real"])
        fitting = [t for t in sorted(set(real.tolist())) if (real < t).mean() <= target + 1e-12]
        thresholds[kind] = {"t": max(fitting) if fitting else float(real.min()), "reached": bool(fitting),
                            "dev real alert": float((real < (max(fitting) if fitting else real.min())).mean())}

    def auroc(pos, neg):
        pos, neg = np.array(pos), np.array(neg)
        return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum())
                     / (len(pos) * len(neg)))

    curves, summary = {}, {}
    for name in sorted({r["set"] for r in rows}):
        for kind in PREMISES:
            real = np.array([r[kind] for r in rows if r["set"] == name and r["kind"] == "real"])
            edit = np.array([r[kind] for r in rows if r["set"] == name and r["kind"] == "edit"])
            fooled = np.array([r[kind] for r in rows if r["set"] == name and r["kind"] == "edit" and r["elsewhere"]])
            cutoffs = sorted(set(real.tolist()) | set(edit.tolist()))
            curve = [[t, float((real < t).mean()), float((edit < t).mean()),
                      float((fooled < t).mean()) if len(fooled) else None] for t in cutoffs]
            curves[f"{name}|{kind}"] = curve
            at_levels = {}
            for level in LEVELS:
                fit = [p for p in curve if p[1] <= level + 1e-12]
                at_levels[level] = max(fit, key=lambda p: p[0]) if fit else None
            summary[f"{name}|{kind}"] = {"auroc real above edit": auroc(real.tolist(), edit.tolist()),
                                         "levels": at_levels, "mean real": float(real.mean()),
                                         "mean edit": float(edit.mean())}

    OUT.write_text(json.dumps({"model": MODEL, "revision": REVISION, "texts": len(texts),
                               "over 2048 tokens": sum(n > 2048 for n in lengths), "max tokens": max(lengths),
                               "seconds": seconds, "threads": args.threads, "target": target,
                               "thresholds": thresholds, "summary": summary, "curves": curves, "rows": rows}),
                   encoding="utf-8")
    md = ["# Embedding similarity checker (bge-m3)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. Model `{MODEL}` revision "
          f"`{REVISION}`, dense CLS embedding, normalised, cosine. {len(texts)} distinct texts embedded in "
          f"{seconds:.0f} s on {args.threads} CPU threads ({seconds / len(texts) * 1000:.0f} ms per text; the CPU was "
          f"shared with the NLI chain). Longest text {max(lengths)} tokens; none truncated "
          f"({sum(n > 2048 for n in lengths)} over 2048).", "",
          f"Warn when cosine < t. Target: P3's real alert rate on English development at argmax, {target:.4f}.", "",
          "| Premise | t | Reached | Real alert on English development |", "|---|---|---|---|"]
    for kind in PREMISES:
        th = thresholds[kind]
        md.append(f"| {kind} | {th['t']:.6f} | {th['reached']} | {th['dev real alert']:.4f} |")
    md += ["", "## Curve, condensed (the full curve is in the JSON)", "",
           "Per set and premise: the largest cutoff whose real alert rate on that set is at most each level, and the "
           "edit-alert rate there. Descriptive; the operating point is the threshold above.", "",
           "| Set | Premise | AUROC (real above edit) | Mean cosine real / edit | " + " | ".join(
               f"real ≤ {lv}" for lv in LEVELS) + " |", "|---|---|---|---|" + "---|" * len(LEVELS)]
    for key, s in summary.items():
        name, kind = key.split("|")
        cells = []
        for level in LEVELS:
            p = s["levels"][level]
            cells.append("–" if p is None else f"t {p[0]:.3f}: real {p[1]:.3f}, edit {p[2]:.3f}")
        md.append(f"| {name} | {kind} | {s['auroc real above edit']:.3f} | {s['mean real']:.3f} / {s['mean edit']:.3f} | "
                  + " | ".join(cells) + " |")
    (HERE / "results" / "checker_embedding.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
