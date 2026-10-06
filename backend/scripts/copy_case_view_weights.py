import argparse
import json
import shutil
import sys
from pathlib import Path

backend_folder = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(backend_folder))


def main():
    from huggingface_hub import snapshot_download

    from app.analysis.view_model import VIEW_MODEL_FILES, VIEW_MODEL_ID, VIEW_MODEL_REVISION

    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=backend_folder / "gliner_case_views")
    arguments = parser.parse_args()
    target = arguments.target.resolve()
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"Model target must be empty: {target}")
    snapshot = Path(
        snapshot_download(
            VIEW_MODEL_ID,
            revision=VIEW_MODEL_REVISION,
            allow_patterns=[*VIEW_MODEL_FILES, "added_tokens.json"],
        )
    )
    target.mkdir(parents=True, exist_ok=True)
    for name in VIEW_MODEL_FILES:
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(snapshot / name, destination)
    added_tokens = snapshot / "added_tokens.json"
    if added_tokens.is_file():
        shutil.copyfile(added_tokens, target / added_tokens.name)
    (target / "cybercase_model.json").write_text(
        json.dumps(
            {
                "model": VIEW_MODEL_ID,
                "revision": VIEW_MODEL_REVISION,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps({"model": VIEW_MODEL_ID, "revision": VIEW_MODEL_REVISION, "target": str(target)})
    )


if __name__ == "__main__":
    main()
