from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Protocol

from app.config import settings
from app.errors import CaseAnalysisFailure

VIEW_MODEL_ID = "fastino/gliner2-multi-v1"
VIEW_MODEL_REVISION = "ce747d79a8e362d3dee0b0b26d1201f7f1a8615a"
VIEW_LIBRARY_VERSION = "1.3.2"
VIEW_MODEL_FILES = (
    "config.json",
    "encoder_config/config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "spm.model",
)


class ClaimExtractor(Protocol):
    def batch_extract_json(self, texts, structures, **kwargs) -> list[dict[str, object]]: ...


class ClaimWordSplitter:
    def __init__(self, whitespace_splitter):
        self.whitespace_splitter = whitespace_splitter

    def __call__(self, text: str, lower: bool = True):
        if not any("\u0e00" <= character <= "\u0e7f" for character in text):
            yield from self.whitespace_splitter(text, lower=lower)
            return
        from pythainlp.tokenize import word_tokenize

        words = word_tokenize(text, engine="newmm", keep_whitespace=True)
        if "".join(words) != text:
            raise ValueError("Thai tokenization must preserve the original Claim text")
        offset = 0
        for word in words:
            end = offset + len(word)
            if word.strip():
                yield word.lower() if lower else word, offset, end
            offset = end


@dataclass
class CaseViewModel:
    extractor: ClaimExtractor
    lock: Lock = field(default_factory=Lock)

    def extract(
        self, texts: list[str], structures: dict[str, list[str]]
    ) -> list[dict[str, object]]:
        with self.lock:
            return self.extractor.batch_extract_json(
                texts,
                structures,
                batch_size=1,
                threshold=settings.case_view_threshold,
                include_confidence=True,
                include_spans=True,
                max_len=None,
            )


@lru_cache(maxsize=1)
def load_view_model() -> CaseViewModel:
    import json
    from importlib.metadata import PackageNotFoundError, version

    folder = Path(settings.case_view_model_path)
    missing = [
        name
        for name in (*VIEW_MODEL_FILES, "cybercase_model.json")
        if not (folder / name).is_file()
    ]
    if missing:
        raise CaseAnalysisFailure(
            "case_view_model_missing",
            "GLiNER2 weights are missing. Run backend/scripts/copy_case_view_weights.py.",
            503,
        )
    manifest = json.loads((folder / "cybercase_model.json").read_text(encoding="utf-8"))
    if manifest != {"model": VIEW_MODEL_ID, "revision": VIEW_MODEL_REVISION}:
        raise CaseAnalysisFailure(
            "case_view_model_invalid",
            "GLiNER2 model manifest does not match the pinned checkpoint",
            503,
        )
    try:
        library_version = version("gliner2")
    except PackageNotFoundError as error:
        raise CaseAnalysisFailure(
            "case_view_library_missing",
            "GLiNER2 is missing. Install backend/requirements-encoder.txt.",
            503,
        ) from error
    if library_version != VIEW_LIBRARY_VERSION:
        raise CaseAnalysisFailure(
            "case_view_library_mismatch",
            f"Case view extraction requires gliner2=={VIEW_LIBRARY_VERSION}",
            503,
        )

    from gliner2 import GLiNER2
    from gliner2.processor import WhitespaceTokenSplitter

    model = GLiNER2.from_pretrained(str(folder), map_location=settings.case_view_device)
    model.eval()
    model.processor.word_splitter = ClaimWordSplitter(WhitespaceTokenSplitter())
    return CaseViewModel(model)
