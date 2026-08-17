"""
Fetch Thai statute texts from Wikisource
=========================================
Downloads the acts relevant to cybercrime and caches the rendered HTML under
data/raw/, one file per act, plus a manifest recording what was fetched.

Why the rendered HTML and not the wikitext: on Thai Wikisource these acts are
Proofread transclusions — the parent page is a `<pages index="...pdf"/>` stub
and the text lives in the Page: namespace, one wiki page per scanned PDF page.
Asking for wikitext returns the stub (about 700 characters). Asking the parser
for `prop=text` makes MediaWiki assemble the transclusion, which is the whole
statute.

Two things about Thai legal text that the parser downstream has to handle, both
visible in the output here:

  - Section numbers are Thai numerals (มาตรา ๙, not มาตรา 9).
  - A number after "มาตรา" is not always a section of *this* act. The 2566
    decree yields 1-14 plus 26, 32, 36, 37, 40 and 172, which are references to
    sections of other statutes quoted in its body. Splitting on every match
    would invent sections that do not exist.

Wikisource is a volunteer transcription, not the authoritative text. It is used
here because it is machine-readable; every section still has to be checked
against the Krisdika consolidated version before anything is asserted from it.
The manifest carries `verified_by_human: false` for exactly that reason.

Usage:
    cd rag_service/app
    python -m RAG.LegalRAG.fetch_wikisource
    python -m RAG.LegalRAG.fetch_wikisource --list
"""

from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = "https://th.wikisource.org/w/api.php"
# Wikimedia rejects the default urllib agent outright (HTTP 403). Their policy
# asks for something identifying with a contact address.
USER_AGENT = (
    "CyberCase-Intelligence-Framework/0.1 "
    "(academic research; https://github.com/NitithX374/CyberCase-Intelligence-Framework)"
)

RAW_DIR = Path(__file__).resolve().parent / "data" / "raw"
MANIFEST = Path(__file__).resolve().parent / "data" / "manifest.json"

THAI_DIGITS = "๐๑๒๓๔๕๖๗๘๙"


def thai_to_arabic(s: str) -> str:
    return s.translate(str.maketrans(THAI_DIGITS, "0123456789"))


# slug -> (wikisource page title, human label, why it matters for cybercrime)
ACTS: dict[str, tuple[str, str, str]] = {
    "cca_2550": (
        "พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ พ.ศ. 2550",
        "พ.ร.บ.คอมพิวเตอร์ 2550",
        "ฐานความผิดหลัก — มาตรา 5-17 คือการกระทำต่อระบบและข้อมูล",
    ),
    "cca_2560_amend": (
        "พระราชบัญญัติว่าด้วยการกระทำความผิดเกี่ยวกับคอมพิวเตอร์ (ฉบับที่ 2) พ.ศ. 2560",
        "พ.ร.บ.คอมพิวเตอร์ ฉบับที่ 2 (2560)",
        "แก้ไข 2550 — ต้องอ่านคู่กัน ไม่งั้นได้ตัวบทที่ถูกยกเลิกไปแล้ว",
    ),
    "tech_crime_decree_2566": (
        "พระราชกำหนดมาตรการป้องกันและปราบปรามอาชญากรรมทางเทคโนโลยี พ.ศ. 2566",
        "พ.ร.ก.อาชญากรรมทางเทคโนโลยี 2566",
        "บัญชีม้า ซิมม้า การอายัดบัญชี ความรับผิดของธนาคาร",
    ),
    "tech_crime_decree_2568_amend": (
        "พระราชกำหนดมาตรการป้องกันและปราบปรามอาชญากรรมทางเทคโนโลยี (ฉบับที่ 2) พ.ศ. 2568",
        "พ.ร.ก.อาชญากรรมทางเทคโนโลยี ฉบับที่ 2 (2568)",
        "บังคับใช้ 13 เม.ย. 2568 — เพิ่มความรับผิดของสถาบันการเงิน",
    ),
    "pdpa_2562": (
        "พระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562",
        "พ.ร.บ.คุ้มครองข้อมูลส่วนบุคคล 2562",
        "ข้อมูลส่วนบุคคลรั่ว — หน้าที่แจ้งเหตุ",
    ),
    # The Criminal Code itself has no page — the text is carried by the 1956
    # act that enacted it. That page holds the ORIGINAL 1956 wording, and the
    # Code has been amended dozens of times since; fine amounts in particular
    # were raised across the board in 2560. Sections fetched from here give the
    # right conduct but frequently the wrong penalty, so they are usable as a
    # starting point for locating a section and not as text to quote.
    "criminal_code_1956_original": (
        "พระราชบัญญัติให้ใช้ประมวลกฎหมายอาญา พ.ศ. 2499",
        "ประมวลกฎหมายอาญา (ฉบับดั้งเดิม 2499)",
        "ฉ้อโกง ม.341/343 กรรโชก ม.337 รีดเอาทรัพย์ ม.338 "
        "ลักทรัพย์ ม.334/335 ทำให้เสียทรัพย์ ม.358 — โทษล้าสมัย ต้องเทียบฉบับปัจจุบัน",
    ),
}

# Not on Thai Wikisource at all — searching returns nothing matching. These have
# to come from Krisdika or the Royal Gazette, and the Gazette PDFs are scans, so
# expect OCR plus a full human check rather than a parse.
NOT_ON_WIKISOURCE = {
    "พ.ร.บ.การรักษาความมั่นคงปลอดภัยไซเบอร์ พ.ศ. 2562":
        "โครงสร้างพื้นฐานสำคัญทางสารสนเทศ (CII) ถูกโจมตี",
    "ประมวลกฎหมายอาญา ฉบับรวมแก้ไขปัจจุบัน":
        "ต้องใช้ฉบับ Krisdika — ฉบับ 2499 บน Wikisource มีโทษที่ถูกแก้ไปแล้ว",
}


def _get(params: dict) -> dict:
    params = {"format": "json", "formatversion": "2", **params}
    request = urllib.request.Request(
        f"{API}?{urllib.parse.urlencode(params)}", headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_rendered(title: str) -> tuple[str | None, str | None]:
    """Return (rendered HTML, error). MediaWiki assembles the transclusion."""
    try:
        data = _get({"action": "parse", "page": title, "prop": "text"})
    except Exception as e:  # noqa: BLE001 — one act failing must not stop the rest
        return None, str(e)
    if "error" in data:
        return None, data["error"].get("info", "unknown API error")
    return data["parse"]["text"], None


def to_plain_text(rendered_html: str) -> str:
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", rendered_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"[ \t ]+", " ", html.unescape(text)).strip()


def section_numbers(text: str) -> list[int]:
    """Every number written after มาตรา, deduped and sorted.

    Deliberately not a section splitter: this counts *mentions*, including
    references to other statutes, so the caller can see at a glance whether a
    download looks complete. Splitting properly needs the heading structure.
    """
    return sorted({int(thai_to_arabic(m)) for m in re.findall(r"มาตรา\s*([๐-๙]+)", text)})


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Thai statutes from Wikisource")
    parser.add_argument("--list", action="store_true", help="Show the act list and exit")
    parser.add_argument("--only", type=str, default="", help="Comma-separated slugs")
    args = parser.parse_args()

    if args.list:
        for slug, (title, label, why) in ACTS.items():
            print(f"{slug:32} {label}\n{'':32} {why}\n{'':32} {title}\n")
        return

    wanted = {s.strip() for s in args.only.split(",") if s.strip()} or set(ACTS)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []

    for slug, (title, label, why) in ACTS.items():
        if slug not in wanted:
            continue
        print(f"[LEGAL] {label} …", end=" ", flush=True)
        rendered, error = fetch_rendered(title)
        if error:
            print(f"ไม่สำเร็จ — {error}")
            manifest.append({"slug": slug, "title": title, "label": label,
                             "status": "missing", "error": error})
            continue

        (RAW_DIR / f"{slug}.html").write_text(rendered, encoding="utf-8")
        plain = to_plain_text(rendered)
        (RAW_DIR / f"{slug}.txt").write_text(plain, encoding="utf-8")
        nums = section_numbers(plain)
        print(f"{len(plain):,} ตัวอักษร | พบเลขมาตรา {len(nums)} ค่า")

        manifest.append({
            "slug": slug,
            "title": title,
            "label": label,
            "relevance": why,
            "status": "fetched",
            "source": "th.wikisource.org",
            "source_url": f"https://th.wikisource.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
            "fetched_on": date.today().isoformat(),
            "chars": len(plain),
            "section_numbers_mentioned": nums,
            # Wikisource is a volunteer transcription. Nothing here may be
            # asserted as the law until checked against Krisdika.
            "verified_by_human": False,
            "authoritative_source": "https://www.krisdika.go.th",
        })
        time.sleep(1)  # be polite to a volunteer-run API

    for label, why in NOT_ON_WIKISOURCE.items():
        manifest.append({
            "label": label, "relevance": why, "status": "not_on_wikisource",
            "next_step": "ดึงจาก krisdika.go.th (ฉบับรวมแก้ไข) หรือราชกิจจานุเบกษา",
        })

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for m in manifest if m["status"] == "fetched")
    print(f"\n[LEGAL] สำเร็จ {ok}/{len(ACTS)} ฉบับ -> {RAW_DIR}")
    for m in manifest:
        if m["status"] == "missing":
            print(f"  ไม่ได้: {m['label']} — {m['error']}")
        elif m["status"] == "not_on_wikisource":
            print(f"  ต้องหาแหล่งอื่น: {m['label']}")


if __name__ == "__main__":
    main()
