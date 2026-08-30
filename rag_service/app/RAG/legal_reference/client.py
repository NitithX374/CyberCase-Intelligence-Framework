"""
Thanoy legal reference client
=============================
Sends the incident text to an external Thai legal service and returns the
provisions it names.

This module owns none of the law. It does not parse statutes, hold a corpus, or
judge whether a provision applies — those were removed on purpose. What it does
is ask a service that specialises in Thai legal text, and pass on what comes
back with its provenance attached.

**The response shape is not yet confirmed.** The endpoint and credentials have
to be supplied (see `config.py`), and until a real response has been seen,
`extract_provisions` reads defensively: it accepts a bare list or an object
wrapping one under any of the usual keys, and reads each row through a table of
likely field names. When the real contract is known this should be narrowed to
it — a tolerant reader is right while the shape is unknown and wrong once it is,
because it will silently accept a response that changed.

Every failure is downward. A missing key, an unreachable host, a timeout or an
unreadable body all produce an empty result carrying `degraded`, so that a
legal-reference outage cannot take the MITRE mapping down with it.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from .config import (
    THANOY_API_KEY,
    THANOY_API_URL,
    THANOY_AUTH_HEADER,
    THANOY_AUTH_SCHEME,
    THANOY_MAX_RESULTS,
    THANOY_PROVIDER_NAME,
    THANOY_QUERY_FIELD,
    THANOY_TIMEOUT_SECONDS,
)
from .schema import LegalProvision, LegalReferenceResult

# Keys an object-wrapped list is likely to hide behind.
_LIST_KEYS = ("results", "data", "documents", "items", "provisions", "laws", "hits")

# Field names to try, in order, for each part of a provision.
_FIELDS = {
    "citation": ("citation", "reference", "law", "section", "name", "title", "label"),
    "title": ("title", "name", "heading", "law_name", "act"),
    "text": ("text", "content", "body", "detail", "description", "snippet"),
    "url": ("url", "link", "source_url", "href", "reference_url"),
    "score": ("score", "relevance", "similarity", "confidence", "rank_score"),
}


def _first(row: dict, names: tuple[str, ...]) -> str:
    for name in names:
        value = row.get(name)
        if isinstance(value, (str, int, float)) and str(value).strip():
            return str(value).strip()
    return ""


def _score(row: dict) -> float | None:
    for name in _FIELDS["score"]:
        value = row.get(name)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def extract_provisions(payload, limit: int) -> list[LegalProvision]:
    """Pull provisions out of a response whose shape is not yet pinned down."""
    rows = payload if isinstance(payload, list) else None
    if rows is None and isinstance(payload, dict):
        for key in _LIST_KEYS:
            if isinstance(payload.get(key), list):
                rows = payload[key]
                break
    if rows is None:
        return []

    provisions: list[LegalProvision] = []
    for row in rows[:limit]:
        if not isinstance(row, dict):
            # A plain list of strings is still usable as citations.
            if isinstance(row, str) and row.strip():
                provisions.append(LegalProvision(citation=row.strip()))
            continue
        provision = LegalProvision(
            citation=_first(row, _FIELDS["citation"]),
            title=_first(row, _FIELDS["title"]),
            text=_first(row, _FIELDS["text"]),
            url=_first(row, _FIELDS["url"]),
            score=_score(row),
        )
        # A row with neither a citation nor any text says nothing.
        if provision.citation or provision.text:
            provisions.append(provision)
    return provisions


class ThanoyClient:
    """Thin HTTP client. Never raises; returns a degraded result instead."""

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
    ):
        self.url = (url if url is not None else THANOY_API_URL).strip()
        self.api_key = api_key if api_key is not None else THANOY_API_KEY
        self.timeout = timeout if timeout is not None else THANOY_TIMEOUT_SECONDS
        self.last_status: int | None = None
        self.last_elapsed_ms: int = 0

    @property
    def configured(self) -> bool:
        return bool(self.url)

    def search(self, query: str, limit: int | None = None) -> LegalReferenceResult:
        limit = limit or THANOY_MAX_RESULTS
        result = LegalReferenceResult(provider=THANOY_PROVIDER_NAME, query_sent=query)

        if not self.configured:
            result.degraded = "ยังไม่ได้ตั้งค่า THANOY_API_URL — ข้ามการค้นอ้างอิงตัวบท"
            return result
        if not query.strip():
            result.degraded = "ไม่มีข้อความสำหรับค้นอ้างอิงตัวบท"
            return result

        started = time.perf_counter()
        try:
            payload = self._post(query, limit)
        except urllib.error.HTTPError as exc:
            self.last_status = exc.code
            result.degraded = f"บริการอ้างอิงตัวบทตอบ HTTP {exc.code}"
            return result
        except Exception as exc:  # noqa: BLE001 — an outage must not fail the query
            result.degraded = f"เรียกบริการอ้างอิงตัวบทไม่สำเร็จ: {exc}"
            return result
        finally:
            self.last_elapsed_ms = int((time.perf_counter() - started) * 1000)

        provisions = extract_provisions(payload, limit)
        if not provisions:
            result.degraded = "บริการอ้างอิงตัวบทไม่พบตัวบทที่เกี่ยวข้อง หรืออ่านรูปแบบผลลัพธ์ไม่ได้"
        result.provisions = provisions
        return result

    def _post(self, query: str, limit: int):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.api_key:
            value = f"{THANOY_AUTH_SCHEME} {self.api_key}".strip()
            headers[THANOY_AUTH_HEADER] = value
        body = json.dumps({THANOY_QUERY_FIELD: query, "limit": limit}).encode("utf-8")
        request = urllib.request.Request(self.url, data=body, headers=headers)
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            self.last_status = response.status
            return json.loads(response.read().decode("utf-8"))
