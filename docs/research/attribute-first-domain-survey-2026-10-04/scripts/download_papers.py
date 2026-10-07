import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pypdf import PdfReader


PROJECT = Path(__file__).resolve().parents[1]
PAPERS = PROJECT / "literature" / "papers"
TEXT = PROJECT / "literature" / "text"


def download_paper(paper):
    receipt = {**paper, "checked_at": datetime.now(timezone.utc).isoformat()}
    pdf_path = PAPERS / f"{paper['key']}.pdf"
    text_path = TEXT / f"{paper['key']}.txt"
    try:
        request = Request(paper["url"], headers={"User-Agent": "CyberCase-literature-research/1.0"})
        with urlopen(request, timeout=45) as response:
            data = response.read()
            receipt.update(status_code=response.status, final_url=response.url,
                           content_type=response.headers.get("Content-Type"))
        if not data.startswith(b"%PDF-"):
            raise ValueError("Response is not a PDF; source was not saved as a paper")
        pdf_path.write_bytes(data)
        reader = PdfReader(pdf_path)
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            pages.append(f"\n=== PDF PAGE {index} ===\n{page.extract_text() or ''}\n")
        extracted = "".join(pages)
        text_path.write_text(extracted, encoding="utf-8")
        receipt.update(status="downloaded", bytes=len(data), pages=len(pages),
                       sha256=hashlib.sha256(data).hexdigest(),
                       pdf_path=str(pdf_path.relative_to(PROJECT)),
                       text_path=str(text_path.relative_to(PROJECT)),
                       pdf_metadata={str(k): str(v) for k, v in (reader.metadata or {}).items()},
                       first_page=pages[0][:600])
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        receipt.update(status="error", error_type=type(error).__name__, error=str(error))
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("keys", nargs="*")
    arguments = parser.parse_args()
    PAPERS.mkdir(parents=True, exist_ok=True)
    TEXT.mkdir(parents=True, exist_ok=True)
    papers = json.loads((PROJECT / "candidates.json").read_text(encoding="utf-8"))["papers"]
    if arguments.keys:
        papers = [paper for paper in papers if paper["key"] in arguments.keys]
        if {paper["key"] for paper in papers} != set(arguments.keys):
            raise ValueError("Requested paper key is absent from the manifest")
    receipt_path = PROJECT / "download_receipts.json"
    receipts = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else []
    receipts = [receipt for receipt in receipts if receipt["key"] not in {paper["key"] for paper in papers}]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(download_paper, paper): paper["key"] for paper in papers}
        for future in as_completed(futures):
            receipt = future.result()
            receipts.append(receipt)
            print(json.dumps({key: receipt.get(key) for key in
                              ("key", "status", "pages", "bytes", "error")}, ensure_ascii=True), flush=True)
    receipt_path.write_text(
        json.dumps(sorted(receipts, key=lambda receipt: receipt["key"]), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
