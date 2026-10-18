from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DOI = "10.18653/v1/2024.acl-long.182"


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "CyberCase-literature-research/1.0"})
    with urlopen(request, timeout=45) as response:
        return json.load(response)


def openalex_citers(identifier: str) -> dict:
    lookup_url = f"https://api.openalex.org/works/https://doi.org/{identifier}"
    original = fetch_json(lookup_url)
    work_id = original["id"].rsplit("/", 1)[-1]
    query = urlencode({"filter": f"cites:{work_id}", "per-page": 200})
    citations_url = f"https://api.openalex.org/works?{query}"
    citations = fetch_json(citations_url)
    return {"lookup_url": lookup_url, "original": original, "citations_url": citations_url, "citations": citations}


def semantic_scholar_citers() -> dict:
    original_url = "https://api.semanticscholar.org/graph/v1/paper/ARXIV:2403.17104?fields=title,year,citationCount,externalIds"
    original = fetch_json(original_url)
    query = urlencode({"fields": "title,year,abstract,externalIds,openAccessPdf,url", "limit": 100})
    citations_url = f"https://api.semanticscholar.org/graph/v1/paper/{original['paperId']}/citations?{query}"
    citations = fetch_json(citations_url)
    return {"lookup_url": original_url, "original": original, "citations_url": citations_url, "citations": citations}


def run_provider(name: str, operation) -> tuple[str, dict]:
    try:
        return name, {"status": "ok", "data": operation()}
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        return name, {"status": "error", "error_type": type(error).__name__, "error": str(error)}


def main() -> None:
    providers = [
        ("openalex_acl", lambda: openalex_citers(DOI)),
        ("openalex_arxiv", lambda: openalex_citers("10.48550/arXiv.2403.17104")),
        ("semantic_scholar_arxiv", semantic_scholar_citers),
    ]
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_provider, name, operation) for name, operation in providers]
        results = dict(future.result() for future in futures)
    results["checked_at"] = datetime.now(timezone.utc).isoformat()
    target = ROOT / "discovery" / "forward_citations_extended.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, result in results.items():
        if not isinstance(result, dict):
            continue
        if result["status"] == "error":
            print(name, result["error"])
            continue
        if name.startswith("openalex"):
            works = result["data"]["citations"]["results"]
        else:
            works = [row["citingPaper"] for row in result["data"]["citations"]["data"]]
        print(name, "returned", len(works))
        for work in works:
            print(json.dumps({"title": work.get("title"), "year": work.get("publication_year", work.get("year")), "date": work.get("publication_date"), "doi": work.get("doi"), "ids": work.get("externalIds"), "url": work.get("id", work.get("url"))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
