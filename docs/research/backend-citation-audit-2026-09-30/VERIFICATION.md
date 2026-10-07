# Verification receipt

Date: 2026-09-30  
Scope: citation and documentation audit at commit `4aa8b18ba61c3f94738169d5f54d12d8f480a622`; no application behavior change or model experiment.

## Metadata and support

- `verify_citations.py <audit-folder> --timeout 15`: **PASS, 35/35 verified** through Crossref or official arXiv API.
- `check_citation_lock.py <audit-folder> --main citation_index.txt`: **PASS**. Identifiers, request/metadata/support digests, terminal statuses and freshness agree.
- `check_citations.py citation_index.txt references.bib`: **PASS**. All 35 cited keys resolve, no duplicate or unused entries.
- Claim-support judgments are **manual primary-source review**. A lock pass validates recorded metadata and contracts; it does not independently prove sentence-level semantic support.
- OpenAlex cross-check was not run. Primary publisher pages, official author/institution pages, DOI records and arXiv were used.
- A transient Crossref 429 for AIS resolved on a later fresh lookup. The final verifier reported no unresolved entries.
- The provisional AnnoCTR identifier `2024.lrec-main.720` was rejected; it is a different paper. Published AnnoCTR is `2024.lrec-main.103`. Its official arXiv identity is used for the metadata lock, with official publisher BibTeX for the published reference.
- Publication years of Huang/ICLR 2024 and Perez/ICLR 2025 differ from first-preprint years stored by arXiv. These are explicitly distinguished in the audit and bibliography.
- `technical_references.bib` contains one additional MITRE technical report, checked directly against the official cover. It has no DOI/arXiv identifier and is outside the 35-record lock.

## Files and code evidence

- `code_inventory.json` records SHA-256 hashes and AST symbols for **29 backend paths**.
- Local Markdown file links and line bounds are checked against the actual workspace.
- Application files must still match the saved hashes at final validation; a hash match demonstrates that this audit did not edit those inspected files.
- No copyrighted full papers are bundled. `metadata_sources.json` stores bibliographic fields and paraphrased content-review receipts; bibliography abstracts are omitted.
- No model calls, training runs, API benchmarks or application tests were performed. No performance values from prior workspace experiments were revalidated.
- Pre-existing `tmp_schema.json` deletion and untracked `docs/thesis/component_evaluation_plans_2026-09-30.json` are preserved.
- The report's recommended experiments are proposals, not executed results.

## Reproduce the citation checks

PowerShell, from this folder:

```powershell
python -X utf8 'C:\Users\kkham\.codex\skills\ai-research-writing-skill\scripts\verify_citations.py' . --timeout 15
python -X utf8 'C:\Users\kkham\.codex\skills\ai-research-writing-skill\scripts\check_citations.py' citation_index.txt references.bib
python -X utf8 'C:\Users\kkham\.codex\skills\ai-research-writing-skill\scripts\check_citation_lock.py' . --main citation_index.txt
```

`citation_index.txt` is a plain-text citation coverage index. It is not a TeX manuscript and was not compiled.

## Final consistency check

- **PASS:** all 6 JSON artifacts parse; the inventory, 35 paper profiles, request keys, metadata records and lock keys agree.
- **PASS:** 26 Crossref and 9 arXiv records are terminal verified records in the final lock.
- **PASS:** all 110 local links in the audit report resolve; every referenced line is in bounds. Three links were adjusted to point to the function definition rather than adjacent imports/error handling.
- **PASS:** all 29 backend file hashes match the recorded baseline; no inspected application or checkpoint file changed.
- **PASS:** bibliography contains 35 distinct scholarly keys with no abstract fields; the separate technical bibliography contains the official MITRE report.
- **PASS:** tracked-file diff whitespace check; final working set consists of this citation-audit folder and ledger, plus the two preserved user-owned baseline changes.
- The first document-integrity helper falsely treated the word 'abstractive' in a paper title as an abstract field. The assertion was corrected to test an actual BibTeX field assignment, and the complete integrity check then passed.
