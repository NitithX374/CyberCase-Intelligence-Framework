from __future__ import annotations

from pathlib import Path


def prompt_template(module_file: str, name: str) -> str:
    folder = Path(module_file).resolve().with_name("prompt_templates")
    return (folder / f"{name}.txt").read_text(encoding="utf-8").strip("\n")


__all__ = ["prompt_template"]
