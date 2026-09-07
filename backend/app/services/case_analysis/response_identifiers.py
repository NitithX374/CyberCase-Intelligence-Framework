import re
from copy import deepcopy


def _format_identifier(value: object, prefix: str, aliases: str) -> object:
    if not isinstance(value, str):
        return value
    match = re.fullmatch(rf"(?:{aliases})[-_]?([0-9]+)", value.strip(), re.I)
    return f"{prefix}-{int(match[1]):02d}" if match else value


def normalize_analysis_identifiers(payload: dict[str, object]) -> dict[str, object]:
    normalized = deepcopy(payload)
    for collection, field, prefix, aliases in (
        ("claims", "claim_id", "A", "A|claim|c"),
        ("mitre_associations", "association_id", "MA", "MA|assoc|association"),
    ):
        rows = normalized.get(collection)
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            if field in row:
                row[field] = _format_identifier(row[field], prefix, aliases)
            references = row.get("claim_ids")
            if isinstance(references, list):
                row["claim_ids"] = [
                    _format_identifier(value, "A", "A|claim|c") for value in references
                ]
    return normalized
