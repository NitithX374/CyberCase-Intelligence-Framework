from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class SourceError(ValueError):
    pass


@dataclass(frozen=True)
class DatasetSources:
    root: Path
    corpus_root: Path
    linking_path: Path
    text_root: Path
    split_documents: dict[str, tuple[str, ...]]
    native_candidates: tuple[Path, ...]


def _document_splits(text_root: Path) -> dict[str, tuple[str, ...]]:
    seen: dict[str, str] = {}
    result: dict[str, tuple[str, ...]] = {}
    for split in ("train", "dev", "test"):
        split_root = text_root / split
        if not split_root.is_dir():
            raise SourceError(f"Missing AnnoCTR text split: {split_root}")
        documents = tuple(sorted(path.stem for path in split_root.glob("*.txt")))
        if not documents:
            raise SourceError(f"AnnoCTR text split is empty: {split_root}")
        for document in documents:
            previous = seen.get(document)
            if previous is not None:
                raise SourceError(
                    f"Document occurs in multiple official splits: {document} "
                    f"({previous}, {split})"
                )
            seen[document] = split
        result[split] = documents
    return result


def _native_candidates(corpus_root: Path) -> tuple[Path, ...]:
    candidates = []
    for path in corpus_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".json", ".jsonl", ".tsv"}:
            continue
        name = path.name.casefold()
        if "sentence" in name and any(token in name for token in ("class", "detect", "label")):
            candidates.append(path)
    return tuple(sorted(candidates))


def resolve_sources(root: Path) -> DatasetSources:
    resolved_root = root.expanduser().resolve()
    corpus_root = resolved_root / "AnnoCTR"
    linking_path = corpus_root / "linking_mitre_only" / "test_w_neg.jsonl"
    text_root = corpus_root / "text"
    if not corpus_root.is_dir():
        raise SourceError(f"Missing AnnoCTR corpus directory: {corpus_root}")
    if not linking_path.is_file():
        raise SourceError(f"Missing AnnoCTR linking source: {linking_path}")
    return DatasetSources(
        root=resolved_root,
        corpus_root=corpus_root,
        linking_path=linking_path,
        text_root=text_root,
        split_documents=_document_splits(text_root),
        native_candidates=_native_candidates(corpus_root),
    )
