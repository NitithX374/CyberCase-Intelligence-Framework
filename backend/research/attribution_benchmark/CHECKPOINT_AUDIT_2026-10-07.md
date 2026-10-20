# Larger checkpoint and combination audit — 2026-10-07

Read-only inspection of existing results while the independent BGE-M3 EN/MT-TH similarity run continues. No new model inference, training, threshold selection or production change is performed by this audit.

## Existing English checkpoint comparison

All six candidates in `runs/candidates_en_20261006T010418Z/comparison.md` use the same 1,198 EN dev, 1,610 ID and 1,686 OOD benchmark rows under the documented 512-token adapters. Thresholds are selected on EN dev. Parameters below are the loaded-model counts recorded in each run manifest.

| Checkpoint | Parameters | ID mean source Macro-F1 | OOD mean source Macro-F1 |
|---|---:|---:|---:|
| mDeBERTa-v3-base | 278,811,651 | 64.36% | 69.87% |
| MiniCheck-DeBERTa-v3-Large | 435,063,810 | 71.80% | 79.36% |
| XLM-R-large-XNLI | 559,893,507 | 65.34% | 75.20% |
| AttrScore FLAN-T5-large | 783,150,080 | 66.22% | 75.70% |

MiniCheck is larger and performs better than the matched standalone mDeBERTa checkpoint in this English protocol. Paired source-stratified cluster-bootstrap differences: ID +7.44 percentage points [4.16, 10.84]; OOD +9.49 points [6.54, 12.46]. False acceptance is 22.86% ID and 27.28% OOD, versus 44.22% and 44.96% for the matched standalone mDeBERTa.

These are checkpoint/adapter results, not the deployed B1-LR method. The metric is unweighted mean source-subset Macro-F1, which must not be mixed with pooled Macro-F1 in the B1-LR tables. MiniCheck uses its native binary head without the author's evidence-chunk/max wrapper; AttrScore uses label-sequence likelihoods. Different tokenizers, training and input formats prevent attributing the differences to parameter count alone. Training-data overlap has not been audited.

No existing completed run was found for **MiniCheck + the B1 semantic filter + a newly TRAIN-fitted LR boundary**. Neither the standalone comparison nor the current B1 EN/MT-TH experiment measures MiniCheck Thai transfer. A larger-model combination cannot be declared superior to the current gate from these standalone results.

MiniCheck's recorded head emits two classes, `unsupported` and `supported`. The current frozen B1-LR boundary expects three ordered NLI probabilities, `[P_E, P_N, P_C]`; its coefficients cannot be reused with MiniCheck by renaming the checkpoint. Any future comparison needs a declared feature adapter, TRAIN-only fitting/frozen selection and matched held-out evaluation. This audit does not implement that experiment.

Sources: [matched comparison](runs/candidates_en_20261006T010418Z/comparison.md), [MiniCheck protocol and results](runs/candidates_en_20261006T010418Z/minicheck_cuda_float32_b1/report.md), and their `run_manifest.json` files.

## Existing XLM-R filter + LR attempt

`nli_grounding_experiment/stage5_backbone.py` constructs filtered premises at MPNet similarity .20, fits LR on WiCE TRAIN features, and evaluates WiCE DEV (N=1,043). Its saved result is:

| WiCE DEV metric | mDeBERTa B1-LR | XLM-R-large + filter + LR |
|---|---:|---:|
| Accuracy | 68.65% | 69.51% |
| Macro-F1 | 63.97% | 63.16% |
| Supported F1 | 50.97% | 47.87% |
| Supported recall | 49.71% | 42.69% |
| False acceptance | 22.11% | 17.40% |

The saved stage rejected the candidate on its selected Macro-F1/Supported-F1 development criterion. Accuracy and false acceptance favor XLM-R, while supported coverage is lower. This does not show that every metric worsens with a larger backbone.

**Input confound found:** the XLM-R script uses `" ".join(...)` for retained units, whereas the original champion filter uses `"\n".join(...)`. Thus this is not a fully matched backbone-only comparison, and the score difference cannot be attributed solely to the backbone. Cached XLM-R feature files also do not carry per-text input hashes. This audit does not rerun the old script, which would fit LR.

Sources: `nli_grounding_experiment/outputs/stage5_backbone_results.json`, `stage5_backbone.py` (`get_premises`) and `src/semantic_filter.py` (`filtered_evidence_text`). The canonical B1-LR production method, coefficients and completed experiments are unchanged.

The present mDeBERTa B1-LR choice is the selected method under its recorded research protocol. It is not evidence that mDeBERTa is the highest-scoring English checkpoint, that no larger combination can beat it, or that native Thai Case performance is established.
