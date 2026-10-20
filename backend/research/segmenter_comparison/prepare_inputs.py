import hashlib
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

SNAPSHOT = Path(
    "C:/Users/kkham/.cache/huggingface/hub/datasets--csebuetnlp--xlsum/snapshots/"
    "ab04842511fc357feae53281fd104aa3c36dff07"
)
SPLITS = {"th": "thai/test/0000.parquet", "en": "english/test/0000.parquet"}
PER_LANGUAGE = 100
NL = chr(10)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(out_path: str) -> None:
    out = Path(out_path)
    rows = []
    provenance = {"snapshot": str(SNAPSHOT), "per_language": PER_LANGUAGE, "files": {}}
    for lang, relative in SPLITS.items():
        path = SNAPSHOT / relative
        provenance["files"][lang] = {"path": str(path), "sha256": sha256(path)}
        table = pq.read_table(path, columns=["id", "text"]).slice(0, PER_LANGUAGE)
        for record in table.to_pylist():
            rows.append({"id": record["id"], "lang": lang, "text": record["text"]})
    payload = NL.join(json.dumps(row, ensure_ascii=True) for row in rows) + NL
    out.write_text(payload, encoding="utf-8")
    provenance["output"] = {"path": str(out), "rows": len(rows), "sha256": sha256(out)}
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main(sys.argv[1])
