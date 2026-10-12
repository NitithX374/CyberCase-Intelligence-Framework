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
