import csv
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]


def load_json(name):
    return json.loads((PROJECT / name).read_text(encoding="utf-8"))


def bibtex_value(value):
    return " ".join(str(value).split()).replace("&", "\\&").replace("%", "\\%")


def bibliography(records):
    entries = []
    for record in records:
        if record["status"] != "verified":
            raise ValueError(f"Unverified bibliographic record: {record['key']}")
        metadata = record["metadata"]
        fields = {
            "title": "{" + bibtex_value(metadata["title"]) + "}",
            "author": " and ".join(bibtex_value(name) for name in metadata["authors"]),
            "year": str(metadata["year"]),
        }
        if "doi" in metadata:
            fields.update(doi=metadata["doi"], url="https://doi.org/" + metadata["doi"])
        else:
            fields.update(eprint=metadata["arxiv_id"], archivePrefix="arXiv",
                          url="https://arxiv.org/abs/" + metadata["arxiv_id"])
        body = ",\n".join(f"  {name} = {{{value}}}" for name, value in fields.items())
        entries.append(f"@misc{{{record['key']},\n{body}\n}}")
    return "\n\n".join(entries) + "\n"


def main():
    profiles = load_json("profiles.json")
    records = load_json("citation_lock.json")["records"]
    metadata = {record["key"]: record for record in records}
    candidates = {paper["key"]: paper for paper in load_json("candidates.json")["papers"]}
    receipts = {receipt["key"]: receipt for receipt in load_json("download_receipts.json")}
    for profile in profiles:
        record = metadata.get(profile["citation_key"])
        if record:
            profile["title"] = " ".join(record["metadata"]["title"].split())
            profile["bibliographic_status"] = record["status"]
        else:
            profile["title"] = "Auditable Evidence Trails for Pedagogy-Grounded LLM Judging"
            profile["bibliographic_status"] = "UNCONFIRMED anonymous submission"
        profile["source"] = profile.get("source", candidates[profile["key"]]["source"])
        profile["access"] = receipts[profile["key"]]["status"]
        profile["pdf_sha256"] = receipts[profile["key"]].get("sha256")
        profile["pdf_pages"] = receipts[profile["key"]].get("pages")
    (PROJECT / "comparison_matrix.json").write_text(
        json.dumps(profiles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (PROJECT / "comparison_matrix.csv").open("w", newline="", encoding="utf-8-sig") as stream:
        columns = list(dict.fromkeys(column for profile in profiles for column in profile))
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(profiles)
    (PROJECT / "references.bib").write_text(bibliography(records), encoding="utf-8")
    print(json.dumps({"profiles": len(profiles), "bibliographic_records": len(records),
                      "full_pdfs": sum(profile["access"] == "downloaded" for profile in profiles)}))


if __name__ == "__main__":
    main()
