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
