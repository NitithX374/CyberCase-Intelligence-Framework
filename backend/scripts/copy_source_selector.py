import argparse
import hashlib
import json
import shutil
from pathlib import Path


def digest(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Provision the frozen local B1-LR Source selector")
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    backend = Path(__file__).resolve().parents[1]
    artifact = json.loads((backend / "app/trace/b1_lr.json").read_text(encoding="utf-8"))
    source = args.snapshot.resolve()
    if source.name != artifact["selector_revision"]:
        raise ValueError("Use the selected pinned snapshot revision")
    for filename, expected in artifact["selector_hashes"].items():
        if digest(source / filename) != expected:
            raise ValueError(f"Frozen selector asset differs: {filename}")
    target = backend / "source_selector_mpnet"
    if target.exists():
        for filename, expected in artifact["selector_hashes"].items():
            if digest(target / filename) != expected:
                raise ValueError(f"Existing selector differs: {filename}")
        print("Existing frozen selector verified")
    else:
        shutil.copytree(source, target)
        print(f"Provisioned frozen selector at {target}")


if __name__ == "__main__":
    main()
