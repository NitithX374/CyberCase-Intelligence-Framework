# Verification receipts

Date: 2026-10-04. Research-only work at CyberCase HEAD `5fdfb4d6608477ed748afbf687a804c4930c7f21`.

## Source access and reading

- Public PDF acquisition: 12 successful downloads, 1 explicit HTTP 403 (OpenReview education submission). Download receipts retain requested/final URL, time, SHA-256, byte count and page count.
- Reading scope: method/evaluation/appendix sections associated with each survey claim, recorded by PDF page in comparison_matrix.json. Full PDFs are available locally; this is not a claim that every appendix page was read.
- Visual checks: rendered and inspected AfG p.7 (Tables 3/4), Default Assistant p.6 (Table 2 and UI), FinRAGBench-V p.6 (visual citation figure/metrics), and Dehing p.5 (two-stage flow and gold-validation caveat). Rendering used the preinstalled pypdfium2 library.
- Anonymous education submission: indexed primary PDF excerpts only; direct full access and acceptance remain UNCONFIRMED. Three IEEE domain candidates have insufficient method access and remain excluded.

## Citation metadata and support

Bundled Python:

`C:/Users/kkham/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`

Commands executed from `F:/Cybercase Framework`:

```powershell
& 'C:/Users/kkham/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:/Users/kkham/.codex/skills/ai-research-writing-skill/scripts/verify_citations.py' 'docs/research/attribute-first-domain-survey-2026-10-04' --timeout 15
& 'C:/Users/kkham/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' 'C:/Users/kkham/.codex/skills/ai-research-writing-skill/scripts/check_citation_lock.py' 'docs/research/attribute-first-domain-survey-2026-10-04' --main README.md --max-age-days 1
```

- Fresh metadata resolution: **12/12 VERIFIED**, eight Crossref and four arXiv records; exit 0.
- Fresh lock consistency: **passed**, exit 0. Checks record/request hashes, metadata/support hashes, provider provenance, terminal status and freshness. Markdown uses source URLs, so the separate BibTeX key-set check is needed; there are no TeX citation keys in README.md.
- references.bib is generated from the primary-provider metadata in the fresh lock. Its deliberately minimal `@misc` entries preserve verified title/authors/year/identifier/URL; no guessed conference acceptance, venue or pagination is added to preprints.
- Claim-support records come from human reading by this assistant, with method pages and relation types. The metadata verifier does not independently validate semantic claims or re-run reported experiments.
- Initial lock check without `--main` expected a paper_state.json. The corrected command supplies README.md because this deliverable is a survey, not a full paper project.

## Artifact integrity

Final integrity checks passed:

- 12/12 PDF SHA-256 values and byte counts match download receipts.
- 12/12 extracted text files have the recorded number of PDF page markers.
- CSV and JSON contain the same 13 profile keys/rows.
- All 12 BibTeX keys match the fresh lock; the anonymous partial-access submission is excluded.
- All 18 local Markdown link targets exist, including code/metric pointers. Source line numbers were rechecked at the current HEAD.
- All five research helper scripts parse with Python AST; largest is 77 lines. No application unit tests were added or run.
- Read application/metric paths have no Git diff. `git diff --check` passed; final baseline preservation was checked separately.

## Workspace scope

- Created only docs/research/attribute-first-domain-survey-2026-10-04/ and updated CONTINUITY.md.
- Downloaded copyrighted originals and render/extraction caches are ignored by the new folder's .gitignore. No commit/push/publishing was performed.
- Four pre-existing deletions (three .whl files and tmp_schema.json) and pre-existing untracked research/architecture/thesis folders were preserved.
- `git diff --check` passed before final ledger update. Application source files were read only. No application tests, provider inference, case-data writes, or experiment reruns were required or performed.

The survey does not claim to enumerate all AfG descendants, prove novel ontology/attribution algorithms, or establish that CyberCase beats the surveyed systems.
