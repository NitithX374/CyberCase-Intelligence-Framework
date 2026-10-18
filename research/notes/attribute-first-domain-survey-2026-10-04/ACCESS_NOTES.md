# Access and interpretation notes

Checked 2026-10-04. These are retrieval facts, not evidence of domain method adoption.

## Full PDF access

Twelve PDFs were downloaded from ACL Anthology, arXiv, or the authors' Netherlands Forensic Institute repository. The exact URL, final URL, date, SHA-256, byte count, page count and extraction path are in download_receipts.json. Read method/evaluation pages are listed in comparison_matrix.json. Four source pages were rendered with pypdfium2 and visually inspected: AfG p.7, Default Assistant p.6, FinRAGBench-V p.6 and Dehing p.5.

Version boundaries:

- Default Assistant: use arXiv:2607.01256v1, titled AI Assistance for Human Review of Default Judgments. The older Stanford PDF uses a different title and results. It is not mixed into this survey's reported study numbers. The arXiv manuscript's reference entry for Slobodkin has incorrect-looking title/coauthor metadata relative to the official ACL original; cite the independently verified original record.
- MedGraphRAG: the published ACL 2025 PDF has a different author roster/title from the earlier arXiv record. The survey uses published metadata and published methods.
- GenerationPrograms: full text is arXiv:2506.14580v1; the fresh bibliographic lock verifies the preprint. No acceptance inference is made from a downloaded preprint.
- Dehing: a fresh download of the 10-page author manuscript was read. It contains a placeholder publisher DOI and differs in pagination from the 11-page published bibliographic record. Crossref independently confirms the actual published DOI. Sections 4.1 and 4.5 conflict on manual gold validation; Section 4.5 explicitly says it was not performed. The report does not call the gold independently human-validated.

## Partial access: education

Auditable Evidence Trails for Pedagogy-Grounded LLM Judging:

- Primary forum: https://openreview.net/forum?id=CF3TqONsjF
- Primary PDF: https://openreview.net/pdf?id=CF3TqONsjF
- Indexed stable PDF: https://openreview.net/pdf/18fca98950e6d2957a20e706f0480ddb67b588a4.pdf
- Direct PDF download: HTTP 403. Browser extraction: challenge page.
- Search-indexed primary excerpts expose abstract, method p.3 Sections 3.1-3.4, and appendix pipeline/evidence-trail description. Those support the staged rubric/scoring and deterministic-verifier comparison. They do not support a claim that all evaluation/limitations pages were read.
- Anonymous ACL submission; authors, stable DOI/arXiv identity and acceptance UNCONFIRMED. Kept out of references.bib and the verified scholarly citation lock. Direct AfG lineage UNCONFIRMED.

## Discovered but not used as method evidence

OpenAlex's forward-citation records surfaced:

| Title | Indexed identifier | Access outcome | Interpretation |
|---|---|---|---|
| EC-MRAG: Evidence-Constrained Multimodal RAG for Fire Safety Compliance Assessment | 10.1109/EITCE70137.2026.11634436 | DOI inaccessible via web; IEEE document/11634436 returns robot/JavaScript verification | Method and AfG adoption UNCONFIRMED; omitted from comparison findings |
| Evidence-Grounded Generative Narratives for Scientific Profiles: A Traceable and Auditable Framework for Trustworthy AI | 10.1109/ICEDEG70169.2026.11695401 | IEEE DOI/document inaccessible; official ICEDEG 2026 program independently lists the title/presenter | Program confirms title presence, not implementation/evaluation; omitted from method findings |
| Evidence-Driven Chain-of-Thought Prompting with Multi-Dimensional Evidence Evaluation for Medical Question Answering | 10.1109/ISCAIT69154.2026.11477466 | DOI inaccessible via web; IEEE document/11477466 returns verification | Indexed title/citation only; method and AfG adoption UNCONFIRMED |

Official program: https://www.edem-egov.org/ICEDEG-2026/program . The three DOI strings above are discovery identifiers, not fresh primary-metadata-verified records in citation_lock.json. No bypass of a paywall, captcha or access-control challenge was performed.

## Search coverage

The query set covered exact AfG title, hyphenated attribute-first-then-generate, Slobodkin and domain terms for law, medicine, finance, education, digital forensics, scientific profiles and fire-safety compliance. Primary texts were preferred over blogs/reposts. Semantic Scholar's DOI lookup returned 404 and its arXiv query returned 429. OpenAlex returned 14 citations for its ACL record and 2 for its arXiv record (duplicates). These index snapshots miss known papers found through title searches; they are not an exhaustive citation count or proof of absence.

No-direct-lineage labels mean that this survey did not establish a direct methodological adoption in the inspected text. They do not claim that authors were uninfluenced by AfG or that the broader literature lacks similar work.
