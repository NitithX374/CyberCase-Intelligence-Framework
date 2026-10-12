# Claim → evidence map

Every number in `main.tex` and the file it comes from. Paths are repo-relative.

| Claim in paper | Value | Evidence |
|---|---|---|
| WiCE test N, gold split | 1,070; 330 / 740 | `nli_grounding_experiment/outputs/canonical/final_metrics.json` (`mdeberta.B1-LR.gold_pos/neg`) |
| Table 1 rows B0/B1/B1-LR/B3 | acc, macro-F1, supp P/R, FSR | same file, `mdeberta.{B0,B1,B1-LR,B3}` |
| Latency 390 / 227 / 227 / 449 ms | approx. | `nli_grounding_experiment/FINAL_VERDICT.md` §B.1 table |
| B1-LR vs B0: ΔMacro-F1 +0.0333 [0.0128, 0.0533]; ΔSupp-F1 +0.0576 [0.0286, 0.0868]; ΔFSR +0.75 [−1.09, +2.70] | | `FINAL_VERDICT.md` §B.2 (canonical `final_bootstrap.json`) |
| B1-LR vs B3: ΔMacro-F1 −0.0020 [−0.0113, +0.0065] | | `FINAL_VERDICT.md` §B.2 |
| Design choices on DEV | | `FINAL_VERDICT.md` decision table (DEV gates) |
| MiniLM post-hoc B1-LR macro-F1 .650 | 0.6496 | `final_metrics.json` `minilm.B1-LR`; `experiment_config.json` marks it `backbone_post_hoc_sensitivity` |
| LR weights/intercept | 1.4108, −1.0513, −0.3023, 0.0583 | `research/attribution_benchmark/results/b1_20261007.json` `production_artifact` |
| Selector τ = 0.20, longest-first 512 | | same, `production_artifact` |
| AttributionBench ID/OOD N 1,610 / 1,686 | | `results/b1_20261007.json` `paired_en_mt_th.test{,_ood}` |
| Table 2 all cells | | same, `paired_en_mt_th.test{,_ood}.{en,th}` |
| ΔFAR ID +17.39 [+13.73, +21.24]; OOD +4.39 [+1.10, +7.59] | | `B1_RESULTS_2026-10-07.md` paired-differences table |
| OOD ΔF1 −0.040 [−0.063, −0.018] | −.04046 [−.06266, −.01798] | same table |
| ID: 140 more FP, 65 more TP | 419−279, 568−503 | `paired_en_mt_th.test` confusions |
| 33,583 unique texts translated, Google NMT | | `results/b1_20261007.json` `translation` |
| BGE-M3 mean cosine 0.846 | 0.8455 | `BGE_MT_TH_RESULTS_2026-10-07.md` |
| Replay: 20 clusters, 60 rows, 29/31 | | `results/b1_20261007.json` `downstream.overall` |
| Table 3 all cells | | same, `downstream.overall.{unfiltered,verified}` |
| Utilisation Δ −77.8 pp [−95.2, −53.3] | | `downstream.overall.utilization_delta_cluster_bootstrap95` |
| McNemar 7 vs 0, p = 0.015625 | | `downstream.overall.paired_test` |
| 4 zero-admission clusters; 6 failed of 36 calls | | `B1_RESULTS` “40 conditions: 30 completed, 6 failed, 4 abstentions” |
| Judgement mean latency 114 s / 169 s | 114,237.65 / 169,277.44 ms | `downstream.overall.*.stage_mean_ms` |
| Gemma 4 26B, temperature 0 | | `downstream.protocol` |
| Extra-claim figure from a cited passage (32,550) | 1 cluster | `CITATION_CONTEXT_AUDIT_2026-10-08.md` |
| 0.23 s/Claim GPU, ~1 s/Claim CPU | 227 ms; 1,025.79 ms | `FINAL_VERDICT.md`; `B1_RESULTS` cost table (CPU smoke) |
| Production uses the verdict as a warning label | | `B1_INTEGRATION.md`, note at top of `B1_RESULTS`, root `CLAUDE.md` |
| Structural guarantees (offsets, ID checks, no generated quotes) | design | `backend/app/sources/evidence.py`, `backend/app/trace/evidence_binding.py`, `CLAUDE.md` |

## Claims deliberately not made
Native Thai case accuracy; factual/legal correctness; reduced hallucination in prose; investigator
benefit; best backbone; population-level effects.

## Added in the 15-page version (2026-10-12)

| Claim in paper | Value | Evidence |
|---|---|---|
| Table 4 design decisions (47.2% removed, 93.52% recall, 25.3% shorter; margin recall 56.66–72.05%; SW-NLI −0.0597, >10× calls; XGBoost +0.0035 test, FAR +3.95 [1.91, 5.88]; MLP .6367 vs .6397; B4 admitted 0; XLM-R .6316 vs .6397, space-joined) | | `nli_grounding_experiment/FINAL_VERDICT.md` §C–D; `CHECKPOINT_AUDIT_2026-10-07.md` |
| B1-LR vs B1 FAR −5.42 [−7.17, −3.70]; 0.76 ms overhead | | `FINAL_VERDICT.md` §B.2, §C |
| Table 5 checkpoints (ID/OOD macro-F1, paired Δ with CIs, FAR) | | `research/attribution_benchmark/runs/candidates_en_20261006T010418Z/comparison.md` |
| Params 279M / 435M / 560M / 783M | 278,811,651 etc. | `CHECKPOINT_AUDIT_2026-10-07.md` |
| mDeBERTa: Thai held out of NLI fine-tuning; XNLI th 0.786, en 0.871 | | model card README at revision b5113eb (`laurer2022mdeberta`) |
| Truncated pairs ID 288/311, OOD 124/154 | | `B1_RESULTS_2026-10-07.md` cost table |
| Replay per split (ID 6/20, 8/15, 1/10, 6/12; OOD 3/11, 12/14, 3/8, 11/12; p = .125 / .25; 7 and 8 pairs) | | `results/b1_20261007.json` `downstream.splits` |
| 6 failures, 3 per arm, ~40,800 output tokens mostly reasoning | | `B1_RESULTS_2026-10-07.md` |
| Cost paragraph: 287–414 ms mean, p95 ≤1,099 ms, 1.86 GiB, CPU 1,025.79 ms | | `B1_RESULTS_2026-10-07.md` cost table |
| Follow-up defaults 3 rounds × 3 questions | | `backend/app/config.py` lines 85–86 |
| 40,000-token source budget; refused not truncated | | root `CLAUDE.md` (sources route, 413 `source_too_large`) |
| SSE heartbeat 15 s; retry once after 2 s on drop/429/500/502/503/504 | | root `CLAUDE.md` (`analysis/stream.py`, `llm/request.py`) |
| Views extractor 4,096 tokens, 60 s; unknown-ID items dropped | | root `CLAUDE.md` (Claim views) |
| Summary/gap with unknown Claim ID → analysis fails | | `backend/app/analysis/claim_gate.py` `check_judgement_references` |
| 266 backend + 76 frontend tests + 2 real-model tests at integration time | | `B1_RESULTS_2026-10-07.md` validation |
| Usability protocol 5–10 participants, prepared, not run | | `docs/research/USABILITY_PROTOCOL.md` |
| Fig. 2 example | constructed | not system output; stated in caption |
