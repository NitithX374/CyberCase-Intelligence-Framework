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
