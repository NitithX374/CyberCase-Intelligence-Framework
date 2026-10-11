from __future__ import annotations

import shutil
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.trace.nli_model import (
    MODEL_NAME,
    MODEL_REVISION,
    WEIGHTS_FILE,
    WEIGHTS_SHA256,
    file_sha256,
)

FILES = (
    "added_tokens.json",
    "config.json",
    WEIGHTS_FILE,
    "special_tokens_map.json",
    "spm.model",
    "tokenizer.json",
    "tokenizer_config.json",
)


def main() -> None:
    cache = Path(
        sys.argv[1] if len(sys.argv) > 1 else Path.home() / ".cache" / "huggingface" / "hub"
    )
    snapshot = cache / f"models--{MODEL_NAME.replace('/', '--')}" / "snapshots" / MODEL_REVISION
    target = Path(__file__).resolve().parents[1] / "models" / "nli_mdeberta"
    if not snapshot.is_dir():
        raise SystemExit(f"not in the local cache: {snapshot}")
    target.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copyfile(snapshot / name, target / name)
    if file_sha256(target / WEIGHTS_FILE) != WEIGHTS_SHA256:
        raise SystemExit("the copied weights do not match the pinned hash")
    print(f"copied {len(FILES)} files to {target}")


main()
