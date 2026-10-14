# Progress — Ubi-Media 2027 short paper

## 2026-10-12
- Inventoried evidence: `research/attribution_benchmark/` (B1 results, transfer, replay, audits),
  `nli_grounding_experiment/` (WiCE), root `CLAUDE.md` for system design.
- Wrote story and claim boundaries (`paper_story.md`), claim→evidence map, verified 14 references
  from ACL Anthology / Crossref / arXiv / Hugging Face (2 corrections applied).
- Drafted full paper (`main.tex`), 9 pages LNCS, one TikZ figure, three tables. Builds cleanly with
  Tectonic 0.17.0 (one harmless underfull vbox).
- Checks: citation keys pass; TODO check flags only the intentional author/acknowledgement placeholders.

## Remaining before submission
1. Fill authors/affiliations; advisor read-through.
2. Confirm venue anonymity rules and deadline time zone on EasyChair.
3. Optional if time: a worked Thai example case (anonymised) as a figure showing a Claim, its
   bound quotation and its warning label.

## Scientific risks a reviewer will raise
- No evaluation on real cybercrime data (benchmarks are English Wikipedia/web QA + MT Thai).
- Thai gold labels inherited through machine translation.
- Replay sample small (15 observable pairs); gate evaluated, label deployed.

## 2026-10-12 (later) — expanded to 15 pages (regular paper)
- Added: Thai-specific motivation; problem setting with requirements R1–R5; positioning table;
  constructed end-to-end example (Fig. 2, labelled as not system output); binding-check table;
  Implementation section; design-decision table; English checkpoint comparison (negative result for
  mDeBERTa vs MiniCheck); per-split replay rows; failure analysis; cost paragraph; threats to
  validity; ethics and privacy; usability protocol status.
- New verified references: XNLI, MiniCheck, AttrScore, SummaC, PyThaiNLP, BGE-M3.
- Found in the mDeBERTa model card: Thai was held out of its NLI fine-tuning (XNLI th 0.786 vs
  en 0.871), now cited as context for RQ3.
- Build: 15 pages, no overfull boxes; citation check passes; TODO check flags only the author
  placeholder.

## 2026-10-12 — related work rebuilt around traceability and attribute-first generation
- Section 2 now has three subsections: Traceability and Provenance (requirements traceability, why/where
  provenance, W3C PROV, generative-search verifiability audit, domain systems), Attribute First, then
  Generate (post-hoc vs attribute-first, AfG and its descendants, domain uses), Claim Verification.
- 14 new verified references (34 in .bib, 33 cited).
- Removed for space and to reduce system detail: Implementation section (now a 4-line paragraph),
  Fig. 2 constructed example, binding-check table (now one sentence), cost paragraph, long lessons.
- Still 15 pages, no overfull boxes.

## 2026-10-13 — reframed: traceability method as hero, NLI as optional warning layer
- New abstract/contributions; Section 4 "Traceability by Construction" in four steps with
  properties P1–P5; two XeLaTeX infographics (figures/units.tex, figures/provenance.tex, Thai via
  the system Loma font; compiled PDFs committed so the main paper builds anywhere).
- Fixed an accuracy issue: the primary segmenter is SaT (wtpsplit), PyThaiNLP is only the fallback.
- Evaluation retitled "Evaluating the Warning Layer" (RQ1 WiCE, RQ2 MT-TH, RQ3 filter replay).
- 15 pages, no overfull boxes.

## 2026-10-13 (later) — notation and comparison figure
- Added Table 1 (Notation); Section 4 rewritten with symbols (M_R, M_J, C, beta, R(sigma), w(c));
  infographics relabelled to match. Implementation paragraph reduced to one sentence.
- Three result tables replaced by one 3-panel comparison figure made with matplotlib in the
  figures4papers house style (figures/make_results.py).
- 15 pages, no overfull boxes.

## 2026-10-13 (evening) — TofuEval-style figures
- Fig. 1 redrawn as an icon overview (figures/overview.tex, FontAwesome 5) in the style of TofuEval Fig. 1.
- Table 1: green/red ✓/✗ comparison of ALCE, AfG, Worledge et al., Yang et al., AUTOSUMM and ours
  (cells follow each paper's own description; ✗ = not provided or not reported).
- Added AUTOSUMM (ACL 2025 Industry) to related work.
- Fixed a missing Thai glyph in the body text (now transliterated, pointing to Fig. 2).
- 15 pages, no overfull boxes.

## 2026-10-13 (night) — segmentation figure redesigned
- Fig. 2 rebuilt as three panels after Dense X Retrieval Fig. 2 (panels, numbered cards), LongCite
  Fig. 1 (chunk vs sentence comparison) and LumberChunker Fig. 1 (ID cards):
  (A) source -> segmenter -> unit cards with offsets; (B) 40-char fixed chunks split "โอนเงิน" from the
  amount vs. units; (C) content hash, alias, and the stale ID after editing 4,500 -> 4,800
  (h' = 660d3b84ad7f6992, computed with the production formula).

## 2026-10-13 (late night) — provenance figure redesigned
- Fig. 3 rebuilt to match Fig. 2: colour per claim (A-01 green, A-02 blue), unit rows coloured by the
  claim that cites them (grey = uncited), and where-arrows that land on exactly the cited unit rows
  (c1 -> S2/U002 and S1/U003, c2 -> S1/U001) without crossing.
- The binding checks moved to one card under the sources, so no arrow crosses text.
- Caption updated. 15 pages, no overfull boxes.

## 2026-10-14 — provenance figure laid out horizontally
- Fig. 3 now reads left to right: summary sentence -> claims (why: R(sigma)) -> source units
  (where: beta(E+(c))), with the binding card and the bound/mixed/unbound note underneath. Colours as before.
- Claim IDs reassigned so no arrows cross: A-01 = actor claim (S1/U001), A-02 = event claim
  (S1/U003, S2/U002). Not referenced in the text.
- Figs. 1-2 kept as they were (a plainer LongCite-style redraw was tried and set aside at the authors' request).
- 15 pages, no overfull boxes.

## 2026-10-14 — labels written out as prose (ai-research-writing, section revision)
- Removed the bold tags that dominated the text: requirements R1-R5 (Sect. 3), properties (P1)-(P5)
  and "(R2)/(R3)/(R5)" back-references (Sect. 4), RQ1-RQ3 in the evaluation intro and subsection
  headings, and bold variant names B0/B1/B1-LR/B3 (Sect. 5), "P1--P5" in the Discussion.
- Each is now a plain sentence ("Evidence must be verbatim: ...", "Identifiers are therefore safe across
  revisions: ...", "We ask whether ..."). Meaning unchanged.
- Checked: numeric tokens identical to the previous version once tags are removed; \cite set identical.
- 15 pages, no overfull boxes. Only remaining TODO: acknowledgements (authors).
- P1-P5 / R1-R5 remain as internal shorthand in claim_evidence_map.md and paper_story.md only.

## 2026-10-14 — title and keywords
- Title: "Traceable by Construction: Evidence-Grounded LLM Analysis of Case Files" (Thai and cybercrime
  dropped from the title; no real Thai cases were evaluated, so the title no longer implies it).
- Keyword "Thai language" -> "Low-resource languages"; intro: "Thai, a low-resource language for this task, ...".
- Thai stays in the body (segmentation motivation, Fig. 2 example, MT-Thai evaluation). 15 pages.

## 2026-10-14 — venue check (2027umediaconf.com, CFP PDF, submission guidelines PDF)
- Topics now list "Generative AI, large language models, and foundation models", "Privacy, security, and
  trustworthy AI" and "Environmental sustainability and public safety": the paper fits.
- Length: CFP 2027 says 6-16 pages incl. figures, tables and references; guidelines say full papers 12-15.
  The paper is 15 pages.
- Review is not anonymous: the submission must include the list of authors, so author names stay.
- Deadline Oct 15, 2026 (time zone not stated); notification Nov 15; camera-ready Nov 25.
- One author must attend in Okinawa; papers must be in English and not under review elsewhere.

## 2026-10-14 — the main contribution now has numbers (Sect. 5.1, Table 3)
- research/traceability_properties/run.py runs the production evidence_units() (SaT sat-3l-sm) on 500
  ThaiSum test articles and 1,000 AttributionBench references; no model calls, no labels.
- Results: 0 reconstruction failures, 0 re-run differences; after one inserted character all old IDs
  -> stale_id, vs 53.3%/57.1% raw offsets and 33.5%/11.7% position-only IDs returning changed text
  silently; cost: 46.7%/42.9% of IDs invalidated although their text is unchanged; cuts inside a word
  0.49%/0.27% for units vs 74.7%/64.8% for equal-length fixed chunks; 0 digit splits (fixed: 75/79).
- Paper: Sect. 5 renamed "Evaluation"; new 5.1 + Table 3; one abstract sentence; contribution 1 points
  to 5.1; Threats updated (ThaiSum is edited news, not complaints/OCR). "Next steps" folded into the
  Conclusion and the two replay paragraphs merged to make room.
- Length: 16 pages (CFP 2027: 6-16 pages incl. references; the older guidelines PDF says 12-15 for full
  papers). Numbers traced in claim_evidence_map.md.
- Observation: real SaT splits the Fig. 2 example into 2 units ([0,107), [107,157)), not the 3 drawn;
  the caption already says the split is illustrative; the hash 80a1d348f2908e99 matches.

## 2026-10-14 — author name
- Second author's surname corrected to "Khamwiset" (was "Kahmwiset") in \author and \authorrunning.

## 2026-10-14 — ai-tell-audit Phase 2 + paper-writing-style + LNCS v2.24 template
- Audit (Phase 1) found 35 items; the authors approved all E, C1, C2, C7, D1, D2, F1, A2 and the
  LNCS items. Applied exactly those (40 edits); not applied: C6-1, A4-1 (not approved).
- Honesty fixes: "deployed"/"production" -> "the rule the prototype uses"/"the system's"; "never
  writes a quotation" scoped to evidence; abstract now names the two corpora, gives 17.4 in domain
  and 4.4 out of domain, and scopes identifier invalidation to the edited source; Related Work no
  longer lumps Yang et al. with model-written pointers; warn-vs-filter stated as a reported trade-off.
- 0.23 s per claim moved from the Conclusion to Sect. 4.6 with its device (GTX 1650, FINAL_VERDICT.md);
  segmentation timing names the CPU (Intel Xeon 2.10 GHz). Latency x2, MiniLM .650/.618 and 33,583
  confirmed against CROSS_FAMILY_REEVALUATION.md, FINAL_VERDICT.md and B1_RESULTS.
- LNCS: credits environment with the mandatory Disclosure of Interests (llncs v2.26 vendored),
  "Attribute First, Then Generate"; Fig. 4 legend "B1-LR (prototype)". ORCID not added (needs IDs).
- Re-audit: 35 -> 3 (A4-1 and C6-1 unapproved; one new referent issue after C1-2, reported).
- Invariance: no number removed; added only approved values (500, 1,000, 4.4, 9/29, GTX 1650,
  2.10 GHz); citation set identical; one heading changed (capitalisation). 16 pages, fonts embedded.

## 2026-10-14 — Table 1 descriptive; positioning against close work
- Table 1 is now descriptive (evidence unit, what the model writes, when it is checked, domain), with
  no ticks or colours; AUTOSUMM moved to text only; LongCite and Zhang et al. added as rows.
- "We take a different position" replaced: the intro now says the method builds on index-based
  citation (ALCE, LongCite) and verbatim quotation (Zhang et al. 2026, "verifiable by construction"),
  and states the delta (identifiers name exact text and fail visibly on change).
- New citations from a broadened search: zhang2026verifiable, lin2026blip, schreieder2025survey.
- Fixed two referents left by earlier edits ("It may only select" -> "The model may only select";
  AfG "this shortened" -> "the method shortened").
- Abstract trimmed to 250 words (Springer limit); Related Work 2.2 list compressed; Figs. 2-3 at
  0.92 linewidth. 16 pages; citation set = old + 3; no reported number removed.

## 2026-10-14 — retitled; survey now cited as ACL 2026
- Title: "From Lossless Units to Verbatim Spans: Traceable LLM Analysis of Case Files" (authors'
  choice), to avoid a clash with Zhang et al. 2026 "Verifiable by Construction"; running head updated.
- Zhang et al. 2026 kept although it is an arXiv preprint (authors' choice).
- schreieder2025survey: arXiv comment says "Accepted at ACL 2026"; bib now uses the ACL Anthology
  record (2026.acl-long.1430, pp. 30956-31000, DOI). 16 pages.
- Sect. 4 heading: "Traceability by Construction" -> "Traceable Evidence in Four Steps" (authors' choice). 16 pages.
- Fig. 3 redrawn plain (black lines, serif fonts incl. FreeSerif for Thai, grey shading for cited units, no colour chips/icons, binding band moved to the caption and Sect. 4.5). Full width; 16 pages.
- Bib: DeBERTaV3 -> ICLR 2023, GenerationPrograms -> COLM 2025 (COLM 2025 paper list), BLIP -> PVLDB 19(11) 2026 (Crossref). tools/crosscheck_citations.py added. 16 pages.
