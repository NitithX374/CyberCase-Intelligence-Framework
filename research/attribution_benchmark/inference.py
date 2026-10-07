import json
import os
import time
from collections import Counter
from importlib.metadata import version

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
from huggingface_hub import snapshot_download
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from data import cluster_key, sha256


MODEL = "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
REVISION = "b5113eb38ab63efdd7f280f8c144ea8b13f978ce"
MAX_LENGTH = 512


class NliRunner:
    def __init__(self, device, batch_size):
        if batch_size < 1 or device not in {"cpu", "cuda"}:
            raise ValueError("Invalid device/batch size")
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was selected but is unavailable")
        torch.set_num_threads(4)
        torch.manual_seed(20261006)
        torch.backends.cuda.matmul.allow_tf32 = False
        self.device = device
        self.batch_size = batch_size
        started = time.perf_counter()
        self.snapshot = snapshot_download(MODEL, revision=REVISION, local_files_only=True)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, local_files_only=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            MODEL, revision=REVISION, local_files_only=True, dtype=torch.float32
        ).to(device).eval()
        if self.model.config._commit_hash != REVISION:
            raise ValueError("Model resolved to an unexpected revision")
        self.labels = {int(k): v.lower() for k, v in self.model.config.id2label.items()}
        if set(self.labels.values()) != {"entailment", "neutral", "contradiction"}:
            raise ValueError(f"Unexpected NLI labels: {self.labels}")
        self.entailment_index = next(k for k, v in self.labels.items() if v == "entailment")
        self.signature = {
            "model": MODEL, "revision": REVISION, "device": device, "dtype": str(self.model.dtype),
            "batch_size": batch_size, "max_length": MAX_LENGTH, "truncation": "only_first",
            "reference_separator": "\n\n", "labels": self.labels, "entailment_index": self.entailment_index,
            "torch_threads": torch.get_num_threads(), "tf32": False,
            "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
            "versions": {n: version(n) for n in ("torch", "transformers", "tokenizers", "scikit-learn")},
        }
        self.load_seconds = time.perf_counter() - started
        self.batch_times = []
        self.unit_times = []
        self.computed = 0
        print(json.dumps({"model_loaded": self.signature, "load_seconds": self.load_seconds}), flush=True)

    def inspect_inputs(self, rows):
        premises = ["\n\n".join(row["references"]) for row in rows]
        claims = [row["claim"] for row in rows]
        premise_ids = self.tokenizer(premises, add_special_tokens=False, verbose=False)["input_ids"]
        claim_ids = self.tokenizer(claims, add_special_tokens=False, verbose=False)["input_ids"]
        special = self.tokenizer.num_special_tokens_to_add(pair=True)
        details = []
        for index, (premise, claim) in enumerate(zip(premise_ids, claim_ids, strict=True)):
            budget = MAX_LENGTH - len(claim) - special
            if budget < 1:
                raise ValueError(f"Claim cannot fit without truncation at row {index}: {len(claim)} tokens")
            visible = min(len(premise), budget)
            details.append({
                "premise_tokens": len(premise), "claim_tokens": len(claim),
                "pair_tokens": len(premise) + len(claim) + special,
                "visible_premise_tokens": visible, "removed_premise_tokens": len(premise) - visible,
                "truncated": len(premise) > visible,
            })
        return details

    def score(self, rows, split, output_path, details):
        if output_path.exists():
            raise FileExistsError(f"Score output already exists: {output_path}")
        started = time.perf_counter()
        scored = []
        with output_path.open("x", encoding="utf-8", newline="\n") as handle:
            for offset in range(0, len(rows), self.batch_size):
                indices = list(range(offset, min(offset + self.batch_size, len(rows))))
                batch = [rows[index] for index in indices]
                batch_started = time.perf_counter()
                encoded = self.tokenizer(
                    ["\n\n".join(row["references"]) for row in batch], [row["claim"] for row in batch],
                    truncation="only_first", max_length=MAX_LENGTH, padding=True, return_tensors="pt"
                ).to(self.device)
                if self.device == "cuda":
                    torch.cuda.synchronize()
                with torch.inference_mode():
                    logits = self.model(**encoded).logits
                    probabilities = logits.softmax(dim=-1)
                if not torch.isfinite(logits).all() or not torch.isfinite(probabilities).all():
                    raise FloatingPointError("Non-finite NLI output")
                values = logits.cpu().tolist()
                probabilities = probabilities.cpu().tolist()
                if self.device == "cuda":
                    torch.cuda.synchronize()
                seconds = time.perf_counter() - batch_started
                self.batch_times.append(seconds)
                self.unit_times.extend([seconds / len(batch)] * len(batch))
                for index, row, scores, probs in zip(indices, batch, values, probabilities, strict=True):
                    argmax = max(range(len(scores)), key=scores.__getitem__)
                    record = {
                        "split": split, "row_index": index, "id": row["id"], "src_dataset": row["src_dataset"],
                        "gold": row["attribution_label"], "cluster": cluster_key(row),
                        "claim": row["claim"], "references": row["references"],
                        "logits": scores, "probabilities": probs, "p_entailment": probs[self.entailment_index],
                        "nli_argmax": self.labels[argmax], "lengths": details[index],
                        "batch_seconds": seconds, "amortized_unit_seconds": seconds / len(batch),
                    }
                    scored.append(record)
                    handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                handle.flush()
                self.computed += len(batch)
                completed = offset + len(batch)
                if completed % 50 == 0 or completed == len(rows):
                    elapsed = time.perf_counter() - started
                    print(f"{split}: {completed}/{len(rows)}, {elapsed:.1f}s, {completed / elapsed:.2f} units/s", flush=True)
        print(json.dumps({"split_complete": split, "units": len(rows), "seconds": time.perf_counter() - started,
                          "nli_labels": dict(Counter(row['nli_argmax'] for row in scored))}), flush=True)
        return scored

    def artifact_hashes(self):
        from pathlib import Path

        return {path.name: sha256(path) for path in Path(self.snapshot).iterdir() if path.is_file()}
