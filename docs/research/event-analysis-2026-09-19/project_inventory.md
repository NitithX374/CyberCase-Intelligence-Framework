# Project and data inspection

2026-09-19 [TOOL] Read-only application inspection; no runtime or model evaluation performed.

## Runtime

- `backend/app/services/case_analysis/pipeline.py`: frozen input/artifact dataclasses, Stage protocol, TechnicalContextStage then AnalysisStage, run_pipeline and without helpers. Appropriate stable insertion point.
- `backend/app/services/case_analysis/pipeline_config.py`: only raw_direct is currently configured.
- `backend/app/services/case_analysis/provider_stage.py`: reusable typed provider request boundary; already dirty before this work and left unchanged.
- `backend/app/services/case_workflow/analysis.py`, `backend/app/services/chat/followup.py`, `backend/app/services/reports/`: surrounding ownership boundaries, not proposed research treatments.
- `docs/research/CURRENT_PROJECT_DIRECTION.md` contains older admission/run/downstream-MITRE and OCR research descriptions inconsistent with the supplied current instructions and inspected stage order. No authority reset performed.

## Existing changes

Baseline status included modified provider_stage.py and frontend/e2e/provider-stub.mjs, plus lr_helpers.py and two OCR text outputs. They were not edited.

## Artifact receipts

- CASIE raw `data/annotation/10001.json` was inspected: content, cyberevent.hopper, nugget offsets, subtype, argument spans/types/roles, and Actual realis are present. The top-level repository tree exposed no LICENSE file; permission scope remains unconfirmed.
- AEC `datasets/paper_eval_splits/casie/metadata.json` reports a final 50-window test sample, seed 42 and five source splits. Sample processed data is JSONL despite its .json suffix; full original CASIE remains preferable for status/coreference analysis.
- Downloaded the [ChronoCTI Figshare v3 archive](https://figshare.com/articles/dataset/ChronoCTI_Mining_Knowledge_Graph_of_Temporal_Relations_among_Cyberattack_Actions/26039518) to the OS temporary folder, not the repository. File: ChronoCTI-main.zip, 140926901 bytes.
- Inspected `Datasets/Dataset/temporal_relation_dataset.xlsx`, Sheet1: 2104 report-bearing rows across 94 reports; masks span 73 train reports and 21 evaluation reports. Counts before cleaning: 1338 NEXT, 564 OVERLAP, 92 CONCURRENT, 110 blank relations.
- Complete endpoint/relation rows: 1994; unique ordered report/T1/T2 pairs: 1935; 11 such pairs have multiple distinct relation labels. These are local inspection counts, not claimed published dataset statistics.
- `temporal-learner-code/report_sentences.json` contains sentence records for all 94 reports with report, line and index fields.
- `construct_final_dataset_for_conventional_learning.py` symmetrizes OVERLAP/CONCURRENT and generates NULL for candidate pairs absent from annotation lookup. One loop overwrites labels per matching row; a new evaluator should preserve the union of labels rather than silently copying this behavior. No released score reproduction was attempted.
- Figshare declares Apache 2.0; archive also contains CC_BY-SA-4.0 notices for technique-classifier assets. Third-party report rights require separate attention.
- SIABench dataset card declares Apache 2.0, with 25 forensic scenarios; its descriptive split table and config metadata disagree. Verify actual files; do not assume artifact binaries are included merely because question files are public.
- Microsoft SecRL now links downloadable ExCyTIn logs and QA and reports ICML 2026 acceptance. Its official README distinguishes o1 paper-test questions from newer o3 questions; do not mix benchmark versions. Hugging Face declares CDLA-Permissive-2.0 for the dataset.

## Missing experiment evidence

No predictions, empirical result tables, calibrated semantic scorer, frozen model identifier, cost pilot, or new benchmark split has been produced. The files in this directory are a research design, not completed experiments.
