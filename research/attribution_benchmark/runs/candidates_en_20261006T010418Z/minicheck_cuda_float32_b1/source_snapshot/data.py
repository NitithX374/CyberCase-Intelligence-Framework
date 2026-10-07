import hashlib
import json
import shutil
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import hf_hub_download


ROOT = Path(__file__).resolve().parent
DATASET = "osunlp/AttributionBench"
REVISION = "62569e644f4186606f54f742178a4517431b42e1"
FILES = {
    "train": "train_all_subset_balanced.jsonl",
    "dev": "dev_all_subset_balanced.jsonl",
    "test": "test_all_subset_balanced.jsonl",
    "test_ood": "test_ood_all_subset_balanced.jsonl",
}
EXPECTED = {"train": 13322, "dev": 1198, "test": 1610, "test_ood": 1686}
LABELS = ("not attributable", "attributable")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_split(split):
    path = ROOT / "data" / FILES[split]
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    if len(rows) != EXPECTED[split]:
        raise ValueError(f"Unexpected {split} count: {len(rows)}")
    for index, row in enumerate(rows):
        for field in ("id", "claim", "question", "response", "src_dataset"):
            if not isinstance(row[field], str):
                raise ValueError(f"Invalid {field} at {split}:{index}")
        if not row["claim"].strip() or row["attribution_label"] not in LABELS:
            raise ValueError(f"Invalid claim/label at {split}:{index}")
        if not isinstance(row["references"], list) or not all(isinstance(x, str) for x in row["references"]):
            raise ValueError(f"Invalid references at {split}:{index}")
    return rows


def cluster_key(row):
    content = json.dumps([row["src_dataset"], row["question"], row["response"]], ensure_ascii=False)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_manifest():
    manifest = json.loads((ROOT / "data" / "manifest.json").read_text(encoding="utf-8"))
    if manifest["dataset"] != DATASET or manifest["revision"] != REVISION:
        raise ValueError("Dataset manifest identity/revision mismatch")
    for item in manifest["files"].values():
        if sha256(ROOT / "data" / item["filename"]) != item["sha256"]:
            raise ValueError(f"Dataset hash mismatch: {item['filename']}")
    return manifest


def prepare():
    target = ROOT / "data"
    target.mkdir(parents=True, exist_ok=True)
    files = {}
    ids = {}
    for split, filename in FILES.items():
        cached = Path(hf_hub_download(DATASET, filename, repo_type="dataset", revision=REVISION))
        destination = target / filename
        if destination.exists() and sha256(destination) != sha256(cached):
            raise ValueError(f"Existing dataset differs: {destination}")
        if not destination.exists():
            shutil.copyfile(cached, destination)
        rows = read_split(split)
        ids[split] = set(row["id"] for row in rows)
        files[split] = {
            "filename": filename, "sha256": sha256(destination), "bytes": destination.stat().st_size,
            "rows": len(rows), "unique_ids": len(ids[split]),
            "labels": dict(Counter(row["attribution_label"] for row in rows)),
            "source_subsets": dict(Counter(row["src_dataset"] for row in rows)),
            "empty_references": sum(not row["references"] for row in rows),
            "clusters": len({cluster_key(row) for row in rows}),
        }
        print(json.dumps({"split": split, **files[split]}, ensure_ascii=False), flush=True)
    splits = list(FILES)
    overlaps = {f"{a}/{b}": len(ids[a] & ids[b]) for i, a in enumerate(splits) for b in splits[i + 1:]}
    if overlaps["dev/test"] or overlaps["dev/test_ood"]:
        raise ValueError(f"Development/test ID overlap: {overlaps}")
    manifest = {
        "dataset": DATASET, "configuration": "subset_balanced", "revision": REVISION,
        "downloaded_at": datetime.now(timezone.utc).isoformat(), "files": files,
        "cross_split_id_overlap": overlaps,
        "loading": "Pinned official raw JSONL, preserved without type casting or row filtering",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    prepare()
