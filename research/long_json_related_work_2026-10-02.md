# Related work: LLMs that must write long JSON (2026-10-02)

Search and verification: four search angles, each followed by a verifier that opened every paper and checked its
numbers. Only verified, corrected values are used below. Papers already in
`research/structured_output_reliability/related_work.md`, `docs/research/runaway-review-2026-09-30.md` and
`docs/research/cybercase-positioning-fulltext-2026-09-30/` are not repeated.

CyberCase for comparison: the reading call writes one JSON object of roughly 5-15k output tokens (up to 64 claims, each
with a verbatim quotation that code checks), and parties, timeline and impacts that point at claim ids.

## What the literature says, in five points

1. **The main failure of long structured output is omission, not wrong values.** Precision stays high while recall
   falls: MulitaMiner, AZERG, Mezzi et al., Piccioli et al., CLAIM-BENCH, ExtractBench (Zhang et al.), MatViX, DocETL.
   An LLM judge is also bad at noticing omissions (Fox et al.). CyberCase's thin trace (claims and quotations left out)
   is the same failure.
2. **Output volume predicts failure.** ExtractBench (Ferguson et al.) attributes failure to total output volume (fields
   times array expansion) rather than input length or nesting depth. LongProc shows scores falling as the output budget
   grows from 0.5K to 8K tokens. DeepJSONEval finds depth hurts exact match while response length barely correlates, so
   the two are not settled.
3. **Grammar-constrained decoding does not reliably help, and sometimes hurts.** ExtractBench: provider structured-output
   mode gave fewer valid outputs than the prompt (77/210 vs 107/210). SO-Bench: lower field match with the
   structured-output API for all six API models. Draft-conditioned decoding (ICML 2026): masking alone costs 9.4-27.6
   points on MATH500. SWYB names "budget saturation": local masking keeps a prefix completable but gives no signal to
   stop. This supports CyberCase's move to a prompt-described JSON validated in code.
4. **Splitting the work raises recall, at a cost.** DocETL (+67% recall, about 18x cost), CLAIM-BENCH (multi-pass removes
   the recall drop on long papers), Piccioli et al. (split long judgments because one prompt "prefers" a length), the
   CACAO playbook pipeline (one prompt gave about 3x the syntax errors), the CRF 2026 shared task (grouped extractors beat
   one all-items call, 68.3 vs 52.4). Counter-example: CTINexus does well with one call, but its outputs are small.
5. **Validate-then-repair works for format, and can damage content.** A clinical repair loop went from 89.0% to 99.0%
   compliance, converging by the second round. The CACAO refinement loop reached near-zero syntax errors while metadata
   fidelity dropped by up to about 20%. A re-ask should send the specific failures and must not force every field to be
   filled.

**Not found in any paper:** a measurement of the whitespace runaway under grammar-constrained JSON decoding (it appears
only in GitHub issues); a system where one call writes a multi-thousand-token JSON in which every item carries a
verbatim quotation checked by code (closest: aCTIon checks entity names against the text; CLAIM-BENCH asks for
exact-quote fields; Piccioli et al. filter hallucinated citations); a measured re-ask policy for outputs of 5k+ tokens.

**Name collision:** two different 2026 papers are called ExtractBench (Ferguson et al., Contextual AI; Zhang et al.,
LlamaIndex). Cite both with authors.

## Security and threat intelligence

**MulitaMiner** — B. Machado, D. Lautert, C. Kapelinski, D. Kreutz, I. Garcia Ferrão, A. Bof. *MulitaMiner: A
Multi-Version Evaluation of LLM-Based Vulnerability Report Extraction.* SBSeg 2026 (main track).
https://sol.sbc.org.br/index.php/sbseg/article/download/44328/44091 . arXiv 2511.15745 is a separate, earlier paper by
the same group (ERRC 2025), not a version of this one.
- Task: OpenVAS / Tenable WAS PDF reports to one 18-field record per vulnerability (baselines of 34, 58 and 116).
- Approach: chunk at scanner markers, one call per chunk, schema in the prompt, JSON repair then up to 3 retries,
  de-duplication and schema check; V3 sets the token budget per model.
- Results: vulnerability omission 20.5% → 8.1% → 1.7% across versions; field omission 25.1% → 12.5% → 8.3%;
  hallucination stayed at 7.1% / 5.7% / 6.8%. GPT-5 under V1 omitted 66-81% of vulnerabilities because its reasoning used
  up the shared 1,000-token response budget.
- For CyberCase: reasoning eating the output budget is the same cause as the earlier 502; measure omission and
  hallucination separately.

**CACAO playbooks** — M. Akbari Gurabi, L. Nitz, R.-M. Castravet, R. Matzutt, A. Mandal, S. Decker. *From Legacy to
Standard: LLM-Assisted Transformation of Cybersecurity Playbooks into CACAO Format.* ESORICS 2025 International
Workshops, LNCS, Springer 2026, pp. 491-510, doi:10.1007/978-3-032-16092-8_27; arXiv 2508.03342.
- Approach: four calls (metadata, workflow skeleton, step attributes with injected schema snippets, variables), a JSON
  Schema checker, and an error-feedback refinement loop (up to 5 rounds, run on the whole playbook).
- Results: one prompt gave about 3x the syntax errors of the decomposed pipeline; refinement reached near-zero syntax
  errors while metadata fidelity fell by up to about 20%. The paper hedges its explanation that the model invents values.

**AZERG** — A. Lekssays, H. T. Sencar, T. Yu. *From Text to Actionable Intelligence: Automating STIX Entity and
Relationship Extraction.* RAID 2025; arXiv 2507.16576.
- Approach: the model never writes the STIX bundle; four small tasks per passage (entities, types, yes/no relation
  candidates, relation labels), code assembles the JSON.
- Results: GPT-4o entity extraction precision 0.86, recall 0.49; fine-tuned Mistral-7B P 0.91 / R 0.79.

**aCTIon** — G. Siracusano, D. Sanvito, R. Gonzalez, M. Srinivasan, S. Kamatchi, W. Takahashi, M. Kawakita,
T. Kakumaru, R. Bifulco. *Time for aCTIon: Automated Analysis of Cyber Threat Intelligence in the Wild.* arXiv
2307.10214 (2023, preprint).
- Gold STIX bundles average 177.1 objects (max 1,255). The model answers one question per entity type; code builds the
  bundle. A string check found 2 invented entities (0.9%); the LLM self-check found none.

**CTINexus** — Y. Cheng, O. Bajaber, S. A. Tsegai, D. Song, P. Gao. *CTINexus: Automatic Cyber Threat Intelligence
Knowledge Graph Construction Using Large Language Models.* IEEE EuroS&P 2025; arXiv 2410.21060.
- One call extracts all triplets (two kNN demonstrations); F1 87.65 (P 93.69, R 82.34); far fewer tokens than per-type
  questioning. Outputs are small (about 13 triplets per report in the STIX side test).

**LLMs unreliable for CTI** — E. Mezzi, F. Massacci, K. Tuma. *Large Language Models Are Unreliable for Cyber Threat
Intelligence.* ARES 2025, LNCS, Springer, pp. 343-364, doi:10.1007/978-3-032-00627-1_17; arXiv 2503.23175.
- Even tiny JSON outputs missed 10-28% of requested items (zero-shot recall campaign 0.72-0.77, CVE 0.87-0.90); few-shot
  and fine-tuning did not help; confidence poorly calibrated (ECE 0.13-0.48).

## Other domains

**Legal judgments** — G. Piccioli, A. Fidelangeli, P. Santin, P. Vivo. *From Judgments to Issues: Structured Extraction
of Legal Reasoning with Citation-Hallucination Control.* arXiv 2607.03325 (2026, preprint).
- Prompt-only DeepSeek V3; long judgments are split into two calls because one prompt "prefers" an output length and
  drops issues.
- Results: issue precision 93.3-94.4%, recall 59.6-82.3%; 31 of 264 citations (11.7%) hallucinated before the citation
  filter, 0.9% after, with 7 valid ones (3.0%) removed.

**CLAIM-BENCH** — S. R. Javaji, Y. Cao, H. Li, Y. Yu, N. Muralidhar, Z. Zhu. *Can AI Validate Science? Benchmarking LLMs
on Claim→Evidence Reasoning in AI Papers.* IJCNLP-AACL 2025 (long), pp. 2355-2379; arXiv 2506.08235.
- Claims and evidence with exact-quote fields from whole papers. Single-pass recall falls with paper length (LLaMA-70B
  about 0.60 → 0.40 at 20k+ tokens); three-pass and one-by-one strategies mostly remove the drop.
- Closest published design to CyberCase's claims-with-verbatim-quotes.

**ExtractBench (Contextual AI)** — N. Ferguson, J. Pennington, N. Beghian, A. Mohan, D. Kiela, S. Agrawal, T. H. Nguyen.
*ExtractBench: A Benchmark and Evaluation Methodology for Complex Structured Extraction.* arXiv 2602.12247 (2026; the
HTML uses a KDD '26 template with placeholder DOI, acceptance unconfirmed).
- 13 to 369 keys, depth up to 6, gold outputs up to about 25k tokens; one call per document, six frontier models.
- Results: prompt mode 107/210 valid (51%), structured-output mode 77/210 (37%); SEC 10-K/Q 0 valid in both. Failures:
  empty responses, trailing commas, page limits, truncation. The authors attribute failure to output volume.

**ExtractBench (LlamaIndex)** — B. Zhang, A. Lyjak, E. Stewart, Z. Li, S. Suo. *ExtractBench: A Benchmark for
Schema-Guided Enterprise Document Extraction.* arXiv 2607.29677 (2026, technical report; the authors' product ranks
first).
- Long documents: value F1 falls (Gemini 3.5 Flash 87.9 → 27.9) and it is a recall failure (P 83.7 vs R 26.5), which the
  authors attribute to systems stopping early.

**CRF 2026 shared task** — P. Ferrazzi, S. Ghosh, A. Lavelli, B. Magnini. *Overview of the CRF 2026 Shared Task on
Clinical Case Report Forms Filling.* CL4Health @ LREC 2026, pp. 245-254.
- 134 items per note, about 95% "unknown". Here the error runs the other way (models fill unsupported values). Grouped
  extractors (68.3 macro-F1) beat one all-items call (52.4) and the per-item baseline (47.0).

**MatViX** — G. Khalighinejad, S. Scott, O. Liu, K. L. Anderson, R. Stureborg, A. Tyagi, B. Dhingra. *MatViX: Multimodal
Information Extraction from Visually Rich Articles.* NAACL 2025, pp. 3636-3655; arXiv 2410.20494.
- Staged extraction (text first, then per figure, then merge) because one whole-paper call worked worse; recall is far
  below precision for every model. Numbers differ between arXiv v1 and the NAACL version; cite the NAACL tables.

## Benchmarks on size and depth

**LongProc** — X. Ye, F. Yin, Y. He, J. Zhang, H. Yen, T. Gao, G. Durrett, D. Chen. *LongProc: Benchmarking
Long-Context Language Models on Long Procedural Generation.* COLM 2025; arXiv 2501.05414.
- Average score at 0.5K / 2K / 8K output budgets: GPT-4o 94.8 / 83.4 / 38.1; Claude 3.5 Sonnet 78.4 / 57.5 / 22.0.
  Output is TSV and procedural text, not JSON.

**DeepJSONEval** — Z. Zhou, J. Li, S. Qiu, J. Huang, L. Qiu, Z. Sun. *DeepJSONEval: Benchmarking Complex Nested JSON Data
Mining for Large Language Models.* arXiv 2509.25922 (2025).
- Depth 3-4 to 5-7: strict match drops 17.22-37.53%, format drops 1.39-13.71%; response length barely correlates
  (r -0.335 to -0.040). Do not state whether constrained decoding was used; the paper does not say.

**SO-Bench** — D. Feng et al. (Apple). *SO-Bench: A Structural Output Evaluation of Multimodal LLMs.* arXiv 2511.21750
(v3 2026).
- Schemas up to depth 22 and over 2K fields; validity and field match fall with depth; the structured-output API gave
  lower field match than the prompt for all six API models (GPT-5 62.67 vs 64.52; Gemini-2.5-Pro 71.83 vs 76.17).

**StructuredRAG** — C. Shorten et al. (Weaviate). *StructuredRAG: JSON Response Formatting with Large Language Models.*
arXiv 2408.11061 (2024).
- Even tiny JSON fails: 82.55% average success; lists of objects 67.6%; most common failure is chatter before the JSON.

## Methods

**DocETL** — S. Shankar, T. Chambers, T. Shah, A. G. Parameswaran, E. Wu. *DocETL: Agentic Query Rewriting and
Evaluation for Complex Document Processing.* PVLDB 18(9):3035-3048, 2025, doi:10.14778/3746405.3746426.
- Splitting a 41-type contract extraction into 21 calls raised recall 0.430 → 0.719 and removed hallucinated categories,
  at about 18x cost ($0.08 → $1.46 for 50 contracts).

**Draft-conditioned constrained decoding** — A. Reddy, T. T. Walker, J. S. Ide, A. S. Bedi. *The Hidden Cost of
Structured Generation in LLMs: Draft-Conditioned Constrained Decoding.* ICML 2026 (PMLR 306); arXiv 2603.03305.
- Decode-time masking alone costs 9.4-27.6 points on MATH500 (14B: 70.8 → 47.6), traced to forced early structural
  tokens with little valid probability mass. Draft first, then constrain, recovers most of it. Small outputs only.

**SWYB** — V. Collura, K. Tit, E. Giunchiglia, M. Papadakis, M. Cordy. *Stay Within Your Bounds: Distance-Guided Decoding
for Guaranteed Context-Free Grammar Compliance.* Findings of EMNLP 2026; arXiv 2608.28229.
- Names "budget saturation": local masking keeps every prefix completable but gives no signal to finish. Prunes tokens
  whose distance to completion exceeds the remaining budget; 100% schema validity on small JSON. No whitespace-loop data.

**Validation-repair loop** — J. Shen. *Closed-Loop Validation-Repair for Healthcare Interoperability: A Multi-Model
Study of Schema Compliance in Clinical LLMs.* IEEE SMC 2026; arXiv 2607.24371.
- A deterministic validator feeds field-level errors back, up to 3 repairs: 89.0% → 99.0% compliance, all convergence by
  round two, 1.11-1.20 calls per case. Short records.

**Omission blindness** — S. Fox, L. Markham, R. Lail, M. Karotsieris. *LLM Judges Verify Presence, Not Absence: Omission
Blindness in AI Clinical Notes and What Recovers It.* arXiv 2608.31016 (2026, preprint).
- Judges separate altered content well (0.79-0.94) but omissions barely above chance (0.50-0.63); enumerate-then-check
  recovers some (24.6% flagged at 2.7% false alarms).

## Checks this suggests for CyberCase (no model calls needed)

- Report omitted claims and omitted quotations separately from unbound or wrong ones (MulitaMiner, Piccioli).
- Keep the re-ask specific: send the claim ids whose quotation failed, and allow dropping a claim instead of forcing a
  quote (CACAO, Shen).
- The request sends no repetition penalty; keep it that way. A 2026 study (Hollows, arXiv 2607.09791) reports that a
  multiplicative penalty of 1.3 dropped schema-valid JSON from 97% to 23%. That paper was opened by the search but not
  re-checked by the verifier, so confirm the numbers before citing them.
