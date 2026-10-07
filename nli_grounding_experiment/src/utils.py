import json
from pathlib import Path
from typing import Any
import pandas as pd

def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_csv(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(path, index=False)

def print_markdown_table(df: pd.DataFrame, title: str = "") -> None:
    if title:
        print(f"\n### {title}\n")
    print(df.to_markdown(index=False))
