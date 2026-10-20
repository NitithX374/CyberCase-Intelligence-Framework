import json
import os
import time
from importlib.metadata import version
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

from candidate_adapters import MAX_LENGTH, load_adapter, prepare_inputs
from data import cluster_key, sha256


class CandidateRunner:
    def __init__(self, spec, device, batch_size, precision):
        if batch_size < 1 or device not in {"cpu", "cuda"}:
            raise ValueError("Invalid device/batch size")
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was selected but is unavailable")
        dtypes = {"float32": torch.float32, "float16": torch.float16}
        dtype = dtypes[precision]
        if device == "cpu" and precision != "float32":
            raise ValueError("CPU runs require explicit float32 precision")
        torch.set_num_threads(4)
        torch.manual_seed(20261006)
        torch.backends.cuda.matmul.allow_tf32 = False
        if device == "cuda":
            torch.cuda.reset_peak_memory_stats()
        self.spec, self.device, self.batch_size = spec, device, batch_size
        started = time.perf_counter()
        self.snapshot = Path(snapshot_download(spec.model, revision=spec.revision, local_files_only=True))
        self.tokenizer = AutoTokenizer.from_pretrained(spec.model, revision=spec.revision, local_files_only=True)
        self.adapter = load_adapter(spec, self.tokenizer, dtype, device)
        if self.adapter.model.config._commit_hash != spec.revision:
            raise ValueError("Unexpected resolved model revision")
        self.signature = {
            "key": spec.key, "model": spec.model, "revision": spec.revision, "adapter": spec.kind,
            "language": spec.language, "device": device, "dtype": str(self.adapter.model.dtype),
            "batch_size": batch_size, "max_length": MAX_LENGTH, "labels": spec.labels,
            "supported_index": spec.supported_index, "reference_separator": "\n\n",
            "input_policy": "original references concatenated; right evidence truncation; entire claim/prompt preserved",
            "chunking": "none", "parameters": sum(parameter.numel() for parameter in self.adapter.model.parameters()),
            "torch_threads": torch.get_num_threads(), "tf32": False,
            "attention_implementation": self.adapter.model.config._attn_implementation,
            "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
            "versions": {name: version(name) for name in ("torch", "transformers", "tokenizers", "scikit-learn")},
            **self.adapter.signature,
        }
        self.load_seconds = time.perf_counter() - started
        self.batch_times, self.unit_times, self.computed = [], [], 0
        print(json.dumps({"model_loaded": self.signature, "load_seconds": self.load_seconds}), flush=True)

    def inspect_inputs(self, rows):
        return prepare_inputs(self.tokenizer, self.spec, rows)

    def score(self, rows, split, output_path, inputs, lengths):
        started = time.perf_counter()
        scored = []
        with output_path.open("x", encoding="utf-8", newline="\n") as handle:
            for offset in range(0, len(rows), self.batch_size):
                indices = list(range(offset, min(offset + self.batch_size, len(rows))))
                batch_started = time.perf_counter()
                encoded = self.tokenizer.pad([inputs[index] for index in indices], padding=True, return_tensors="pt").to(self.device)
                if self.device == "cuda":
                    torch.cuda.synchronize()
                with torch.inference_mode():
                    class_scores, score_details = self.adapter.predict(encoded)
                    probabilities = class_scores.softmax(dim=-1)
                if not torch.isfinite(class_scores).all() or not torch.isfinite(probabilities).all():
                    raise FloatingPointError(f"Non-finite {self.spec.key} output")
                values, probs = class_scores.cpu().tolist(), probabilities.cpu().tolist()
                if self.device == "cuda":
                    torch.cuda.synchronize()
                seconds = time.perf_counter() - batch_started
                self.batch_times.append(seconds)
                self.unit_times.extend([seconds / len(indices)] * len(indices))
                for position, index in enumerate(indices):
                    row = rows[index]
                    argmax = max(range(len(values[position])), key=values[position].__getitem__)
                    record = {
                        "split": split, "row_index": index, "id": row["id"], "src_dataset": row["src_dataset"],
                        "gold": row["attribution_label"], "cluster": cluster_key(row), "claim": row["claim"],
                        "references": row["references"], "class_scores": values[position],
                        "class_probabilities": probs[position], "p_supported": probs[position][self.spec.supported_index],
                        "class_argmax": self.spec.labels[argmax], "input_ids": inputs[index]["input_ids"],
                        "lengths": lengths[index], "score_details": score_details[position],
                        "batch_seconds": seconds, "amortized_unit_seconds": seconds / len(indices),
                    }
                    scored.append(record)
                    handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n")
                handle.flush()
                self.computed += len(indices)
                completed = offset + len(indices)
                if completed % 100 == 0 or completed == len(rows):
                    elapsed = time.perf_counter() - started
                    print(f"{self.spec.key}/{split}: {completed}/{len(rows)}, {elapsed:.1f}s, {completed / elapsed:.2f} units/s", flush=True)
        return scored

    def artifact_hashes(self):
        return {path.name: sha256(path) for path in self.snapshot.iterdir() if path.is_file()}

    def resource_usage(self):
        if self.device == "cpu":
            return {"cuda_peak_allocated_bytes": None, "cuda_peak_reserved_bytes": None}
        return {"cuda_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
                "cuda_peak_reserved_bytes": torch.cuda.max_memory_reserved(),
                "cuda_total_bytes": torch.cuda.get_device_properties(0).total_memory}
