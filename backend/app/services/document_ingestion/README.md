# Region-aware document ingestion prototype

This module converts PDF, DOCX, PNG, and JPEG inputs into page- and region-traceable text. It does not persist cases or call RAG, case analysis, gap analysis, MITRE retrieval, follow-up, or report generation.

## Architecture

The existing deterministic native extraction remains the first decision:

1. DOCX uses structured native extraction and one warned logical page.
2. Every PDF page is independently assessed by the native-text heuristic.
3. Pages with usable native text bypass every recognition provider.
4. Other PDF pages and images are rendered within configured limits.
5. `mode=unified` sends the rendered page to the configured whole-page recognizer and is the runtime default.
6. `mode=routed` preserves the provider-neutral region pipeline, but currently emits one `unknown` whole-page region because region classification and HTR are disabled.

The API remains `POST /api/v1/document-ingestion/preview`. It accepts `mode=unified|routed`; `segmentation=true|false` is an alias for routed or unified mode.

## Active providers

### Segmentation and region-type signals

No external segmenter is active. The local `WholePageRegionSegmenter` emits one deterministic `unknown` region covering the page, with no fabricated confidence. This keeps the routed contract executable while clearly warning that region classification is disabled.

Google Document AI was removed from the runtime path because it required project, processor, billing, and credential configuration while its official support matrix does not support Thai handwriting. Routed output must not be treated as a region-aware research baseline until a verified Thai-capable classifier is selected.

### Printed OCR and unified baseline

Typhoon OCR 1.5 remains the printed and whole-page provider through `typhoon-ocr==0.4.1` and API model `typhoon-ocr`. The adapter uses the official `prepare_ocr_messages` helper with `task_type="v1.5"`, `figure_language="Thai"`, and the OpenAI-compatible `/chat/completions` API.

Verified sources:

- [Typhoon OCR 1.5 release](https://opentyphoon.ai/blog/en/typhoon-ocr-release)
- [Official Typhoon OCR model page](https://opentyphoon.ai/model/typhoon-ocr)
- [Official package repository](https://github.com/scb-10x/typhoon-ocr)
- [PyPI package 0.4.1](https://pypi.org/project/typhoon-ocr/0.4.1/)

Official Typhoon output uses `<figure>...</figure>` for generated chart, image, and QR descriptions. The adapter removes these spans from canonical transcription and merged text. It retains each description only as `generated_visual_description` with `non_authoritative` status.

### HTR

HTR is disabled by default. Pure handwriting regions are preserved with their page, bounding box, and `needs_review` status, but no recognizer is called and no transcription is produced.

The production router keeps HTR off directly and does not require an environment variable. The provider-neutral HTR contract and review adapter remain isolated for future benchmarking.

## Configuration

- `DOCUMENT_MIXED_REGION_POLICY=unified|review`
- `DOCUMENT_UNKNOWN_REGION_POLICY=unified|review`
- `TYPHOON_OCR_API_KEY`
- `TYPHOON_OCR_BASE_URL`, default `https://api.opentyphoon.ai/v1`
- `TYPHOON_OCR_MODEL`, default `typhoon-ocr`
- `DOCUMENT_RECOGNITION_TIMEOUT_SECONDS`, default 60 seconds

Existing file-size, page-count, image-pixel, and rendered-edge limits remain configurable through application settings.

## Deterministic routing

- `printed_text` routes to Typhoon OCR.
- `handwriting` routes to no recognizer, remains `needs_review`, and emits an HTR-disabled warning.
- `mixed_text` routes to the configured fallback; the default unified Typhoon candidate is `needs_review`.
- `table` routes to OCR unless the segmenter reports handwriting, then it uses the mixed policy.
- `figure` and `signature` are non-text and non-authoritative by default.
- `unknown` uses the configured fallback.

No document text participates in routing decisions. Prompt-like text remains inert output data.

## Canonical region fields

Each page contains `regions`, `merged_text`, and `routing_summary`. Every region preserves:

- `region_id`, page number, and bounding box
- region type and handwriting flag
- recognition method and recognizer
- transcription, provider confidence when available, and verification status
- content role
- recognition candidates and selected candidate index
- separately retained generated visual descriptions
- controlled warning text when a provider fails

The earlier `blocks` and `full_text` fields remain populated for compatibility. Canonical evidence text is built only from region `transcribed_text`; generated descriptions and non-text regions never enter `merged_text` or document `full_text`.

## Evaluation input

`backend/tools/document_ingestion_eval.py` accepts JSON or JSONL. A single sample can compare both modes without maintaining unrelated datasets:

```json
{
  "sample_id": "case-001-page-03-region-04",
  "region_type": "handwriting",
  "ground_truth": "manually verified text",
  "predictions": {
    "unified": "whole-page prediction",
    "routed": "region-aware prediction"
  },
  "critical_fields": {
    "amount": "131000",
    "person_name": "สมชาย"
  },
  "predicted_critical_fields": {
    "amount": "131000",
    "person_name": "สมชาย"
  },
  "generated_content_count": 1,
  "unsupported_generated_content_count": 0
}
```

Run from `backend/`:

```powershell
python -m tools.document_ingestion_eval path\to\samples.json
```

The utility reports CER, whitespace-tokenized WER, printed/handwritten aggregates, exact-match metrics for date, time, amount, account number, transaction ID, person name, and case number, handwriting-region coverage, and unsupported generated-content rate. It does not infer critical fields or invent evaluation samples.

## Known limitations

- No live Typhoon request runs in automated tests; the model boundary is mocked.
- Region classification is disabled. Routed mode currently preserves a single unknown whole-page region and is not an accuracy baseline.
- Complex tables, mixed printed/handwritten fields, and cross-column reading order require a future verified segmenter.
- HTR is disabled; handwriting regions intentionally produce a manual-review warning instead of fabricated text.
- Figure and signature routing is implemented in the canonical contract and router, but the selected OCR processor does not guarantee semantic figure or signature region labels.
- DOCX uses a logical page because native parsing cannot reproduce renderer-dependent page boundaries.
- Thai WER uses whitespace tokenization, so CER is usually more informative without a dedicated tokenizer.
- The frontend exposes preview-only upload and provenance display. It does not create cases or pass extracted text into analysis, MITRE, RAG, reports, or persistence.
