from __future__ import annotations

import argparse
import hashlib
import os
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NLI = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
SEED, SAMPLE, WARM = 2026, 200, 5
NL = chr(10)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"
    sys.path.insert(0, str(HERE))
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from checker_units import LABELS, nli_scores
    from checker_units import checks as load_checks

    torch.set_num_threads(args.threads)
    picked = random.Random(SEED).sample(load_checks(args.backend), SAMPLE + WARM)
    pairs = {kind: [(c[kind], c["claim"]) for c in picked] for kind in ("quote", "window")}
    stored = nli_scores()[1]

    started = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(NLI)
    nli = AutoModelForSequenceClassification.from_pretrained(NLI).eval().to(args.device)
    names = [nli.config.id2label[i].lower() for i in range(nli.config.num_labels)]
    if sorted(names) != sorted(LABELS):
        raise SystemExit(f"unexpected labels: {names}")

    def nli_check(premise, claim):
        batch = tokenizer(premise, claim, truncation="only_first", max_length=512, return_tensors="pt")
        with torch.no_grad():
            probs = torch.softmax(nli(**batch.to(args.device)).logits, dim=-1)[0].cpu().tolist()
        return dict(zip(names, probs))

    nli_check(*pairs["quote"][0])
    cold = time.perf_counter() - started

    runners = [("NLI (mDeBERTa base)", nli_check)]
    if args.device == "cpu":
        from sentence_transformers import SentenceTransformer
        from checker_embedding import SNAPSHOT

        embedder = SentenceTransformer(str(SNAPSHOT), device="cpu")

        def embed_check(premise, claim):
            a, b = embedder.encode([claim, premise], normalize_embeddings=True, convert_to_numpy=True,
                                   show_progress_bar=False)
            return float(a @ b)

        runners.append(("Embedding (bge-m3)", embed_check))

    rows, agree, compared, largest = [], 0, 0, 0.0
    for name, run in runners:
        for kind in ("quote", "window"):
            for premise, claim in pairs[kind][:WARM]:
                run(premise, claim)
            times = []
            for premise, claim in pairs[kind][WARM:]:
                began = time.perf_counter()
                got = run(premise, claim)
                times.append((time.perf_counter() - began) * 1000)
                known = stored.get((premise, claim)) if run is nli_check else None
                if known:
                    compared += 1
                    agree += max(got, key=got.get) == max(known, key=known.get)
                    largest = max(largest, max(abs(got[k] - known[k]) for k in LABELS))
            times.sort()
            rows.append(f"| {name} | {kind} | {times[len(times) // 2]:.0f} | {sum(times) / len(times):.0f} | "
                        f"{times[int(len(times) * 0.9)]:.0f} |")
            print(rows[-1], flush=True)

    hardware = (f"{torch.cuda.get_device_name(0)}, CUDA {torch.version.cuda}" if args.device == "cuda"
                else f"CPU, {args.threads} threads")
    md = [f"# Time per check on {args.device.upper()} (one check at a time, no batching)", "",
          f"Script sha256 `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`. torch {torch.__version__}, "
          f"{hardware}, fp32. {SAMPLE} checks sampled with seed {SEED} across the three sets, after {WARM} untimed "
          f"warm-up checks; run with no other model job on the machine.", "",
          f"- Loading the NLI model and its first check: {cold:.1f} s, in a process that had already imported torch.",
          f"- NLI agreement with the stored CPU scores: argmax {agree}/{compared}; largest probability difference "
          f"{largest:.1e}."]
    if args.device == "cuda":
        md.append(f"- Peak GPU memory allocated: {torch.cuda.max_memory_allocated() / 2 ** 20:.0f} MiB. The embedding "
                  f"model is timed on CPU only.")
    md += ["", "| Checker | Premise | Median ms | Mean ms | 90th percentile ms |", "|---|---|---|---|---|", *rows]
    (HERE / "results" / f"checker_timing_{args.device}.md").write_text(NL.join(md) + NL, encoding="utf-8")
    print(NL.join(md))


if __name__ == "__main__":
    main()
