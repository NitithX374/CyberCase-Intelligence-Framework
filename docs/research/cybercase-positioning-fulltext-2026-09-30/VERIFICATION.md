# Verification record

2026-09-30. Scope: literature positioning and saved-receipt inspection, not submission preparation or a new experiment.

## Full-text access and reading

- Seven requested and five close new papers: **12full reads** of methods/results/discussion and supplied methodological appendices.
- URLs/cache paths/pages/SHA-256 in paper_inventory.json; third-party PDFs stay in OS temp cache and are not redistributed.
- Cadet/Shiri published venues verified; locators refer to arXiv author versions read.
- Quote-Tuning official21-page NAACL version including supplement read.
- Dehing publisher/universityPDF403; NFI repository provided complete10-page author manuscript. Published pages1–11 are bibliographic metadata, not pages read. Placeholder DOI in author header not copied.
- RAEE arXiv2410.09418 is Lu et al., preprint; separate NAACL2025BEMEAE not claimed as full-read evidence.
- Relins abstract only: PMC200 was anti-bot page. UAS2026preprint not verified fulltext403. Neither used to support verdict.

## Metadata versus claim support

- **11/11 fresh DOI records verified**: Crossref7, DataCite4(arXiv-issuedDOIs), citation_lock.json.
- First arXiv API429/timeouts saved in citation_lock_initial_attempt.json. Canonical DataCite DOI/title/authors verified before requests updated and unmodified skill verifier rerun; final lock is fresh for current requests.
- **Kramer separately publisher-verified**, publisher_verification.json: USENIX/SOUPS2025title/authors/pages/fullPDF. No DOI/arXiv verified, so none invented to fit schema.
- **12/12 BibTeX keys exist**. Lock check covers11 DOI records; full key check covers all12. Do not conflate scopes.
- Sentence support hand-read and recorded with sections/tables/page locators in citation_requests.json; metadata alone does not support substantive claims.
- Explicit preprints: DeepFaith, Wen, RAEE, ClinicalQuotes and inaccessible UAS. Published versions cited for Cadet, AEC, Shiri, Quote-Tuning.

## Public artifact access

GitHub API200: AEC, Cadet, Quote-Tuning, ClinicalQuotes, Dehing repos. Wen release page200 links OSF5dnhg. This does not certify every download or underlying dataset licence. CASIE missing licence not interpreted as evaluation-only permission.

## Completed checks

- verify_citations.py with timeout12:11 VERIFIED.
- check_citations.py citation_index.txt references.bib:passed12keys.
- check_citation_lock.py --main citation_index_doi_arxiv.txt --max-age-days1:passed.
- Markdown local-link/table/PDF-hash/RelatedWork validation: artifact_checks.json.
- git diff --check and scope inspection after artifact generation.
- Existing same-day29-path backend hash baseline: **29unchanged**, local_receipts.json.
- English Related Work206words, six verified references.
- Documentation-only audit; no application tests, provider inference or experiment reruns.

## Number/version boundaries

Dev/order numbers from saved tables. Report-v1 1755 means585unique claim records x3renders, conditional on26valid input traces;4/30failed. Deterministic source IDs63.19% disclosed. Byte inequality not equated to semantic error; LLMstatus changes0/1707 disclosed.

Held-out snapshot2026-09-30T03:54:51UTC:368of400records, no partialJSONline, file changing; report-v2 main summary absent. No interim effect/significance or successful replication stated. Snapshot may become stale as user-owned run continues.

## Scientific work still pending

External Shiri/AEC comparisons, held-out/current-renderer main results, and semantic truth/entailment evaluation are not complete. They do not block this positioning audit; they block claims of prior-method superiority, current end-to-end preservation and unrestricted factual accuracy.

