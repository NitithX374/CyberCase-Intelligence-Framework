from __future__ import annotations

import re
from collections import Counter
from typing import Any


PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("url", re.compile(r"https?://[^\s<>\"')]+", re.IGNORECASE)),
    ("ipv4", re.compile(r"(?<![\w.])(?:25[0-5]|2[0-4]\d|1?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\w.])")),
    ("ipv6", re.compile(r"(?<![\w])(?:[0-9A-Fa-f]{1,4}:){2,7}[0-9A-Fa-f:]{1,4}(?![\w])")),
    ("hash", re.compile(r"\b(?:[0-9a-f]{32}|[0-9a-f]{40}|[0-9a-f]{64}|[0-9a-f]{128})\b", re.IGNORECASE)),
    ("cve", re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)),
    ("mitre_id", re.compile(r"\b[TSG]\d{4}(?:\.\d{3})?\b", re.IGNORECASE)),
    ("windows_path", re.compile(r"\b[A-Za-z]:\\[^\s<>\"|]+")),
    ("unix_path", re.compile(r"(?<![\w:])/(?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+")),
    ("process_name", re.compile(r"\b[A-Za-z0-9_.-]+\.(?:exe|dll|sys|bat|cmd|ps1|sh|so)\b", re.IGNORECASE)),
    ("command_line", re.compile(r"(?im)^(?:\s*)(?:sudo|powershell(?:\.exe)?|pwsh|cmd(?:\.exe)?|bash|sh|curl|wget|python(?:\.exe)?|net|ipconfig|whoami|schtasks|reg(?:\.exe)?|rundll32|wmic|sc(?:\.exe)?|certutil|bitsadmin|mshta|systemctl)\b[^\n]*")),
    ("account_name", re.compile(r"(?i)\b(?:user(?:name)?|account|principal|login|uid|sid)\s*[:=]\s*([^\s,;]+)")),
    ("well_known_account", re.compile(r"\b(?:NT AUTHORITY\\)?(?:SYSTEM|LOCAL SERVICE|NETWORK SERVICE|Administrator|root)\b", re.IGNORECASE)),
    ("timestamp", re.compile(r"\b\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?\b")),
    ("time", re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(?:UTC|GMT|AM|PM)?\b", re.IGNORECASE)),
    ("domain", re.compile(r"(?<![@\w])(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}(?::\d+)?(?:/[^\s<>\"')]+)?", re.IGNORECASE)),
)


def extract_protected_spans(text: str) -> list[dict[str, Any]]:
    spans: set[tuple[str, str, int, int]] = set()
    for span_type, pattern in PATTERNS:
        for match in pattern.finditer(text):
            value = match.group(1) if span_type == "account_name" and match.lastindex else match.group(0)
            value = value.rstrip(".,;:)")
            if value:
                spans.add((span_type, value, match.start(), match.end()))
    return [
        {"type": span_type, "value": value, "start": start, "end": end}
        for span_type, value, start, end in sorted(spans, key=lambda item: (item[2], item[0], item[1]))
    ]


def compare_protected_spans(raw_context: str, refined_context: str) -> dict[str, Any]:
    spans = extract_protected_spans(raw_context)
    annotated = [
        {**span, "preserved": span["value"] in refined_context}
        for span in spans
    ]
    by_type = Counter(span["type"] for span in annotated)
    missing_by_type = Counter(span["type"] for span in annotated if not span["preserved"])
    return {
        "total": len(annotated),
        "preserved": sum(span["preserved"] for span in annotated),
        "missing": sum(not span["preserved"] for span in annotated),
        "by_type": dict(sorted(by_type.items())),
        "missing_by_type": dict(sorted(missing_by_type.items())),
        "spans": annotated,
    }

