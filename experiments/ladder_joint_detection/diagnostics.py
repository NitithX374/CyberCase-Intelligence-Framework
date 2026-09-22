from __future__ import annotations

from difflib import SequenceMatcher
from heapq import nlargest

from .models import AuditBundle, ClassificationRecord, DiagnosticCandidate
from .normalization import diagnostic_punctuation_text, diagnostic_quote_text


def _category(classification: ClassificationRecord, candidate_text: str) -> str:
    classification_text = classification.normalized_text
    if diagnostic_quote_text(classification.original_text) == diagnostic_quote_text(candidate_text):
        return "unicode_or_quote_normalization"
    if diagnostic_punctuation_text(classification_text) == diagnostic_punctuation_text(candidate_text):
        return "punctuation_or_spacing"
    if "".join(classification_text.split()) == "".join(candidate_text.split()):
        return "token_reconstruction"
    if classification_text in candidate_text or candidate_text in classification_text:
        return "sentence_segmentation"
    return "different_sentence"


def _diagnostic_score(left: str, right: str) -> float:
    return SequenceMatcher(None, left[:2000], right[:2000], autojunk=True).ratio()


def _quick_score(left: str, right: str) -> float:
    return SequenceMatcher(None, left[:2000], right[:2000], autojunk=True).quick_ratio()


def build_diagnostics(bundle: AuditBundle) -> dict[str, DiagnosticCandidate]:
    diagnostics: dict[str, DiagnosticCandidate] = {}
    for row in bundle.rows:
        classification = row.classification
        if classification.sentence_label != 1 or row.entity_ids:
            continue
        candidates = bundle.source_data.entities[classification.split]
        if not candidates:
            continue
        shortlist = nlargest(
            8,
            candidates,
            key=lambda entity: (_quick_score(classification.normalized_text, entity.normalized_text), entity.record_id),
        )
        candidate = max(
            shortlist,
            key=lambda entity: (_diagnostic_score(classification.normalized_text, entity.normalized_text), entity.record_id),
        )
        diagnostics[classification.record_id] = DiagnosticCandidate(
            candidate.record_id,
            candidate.reconstructed_text,
            candidate.normalized_text,
            _diagnostic_score(classification.normalized_text, candidate.normalized_text),
            _category(classification, candidate.reconstructed_text),
        )
    return diagnostics
