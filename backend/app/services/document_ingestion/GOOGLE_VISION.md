# Google Vision confidence baseline

## Architecture characterized before implementation

2026-09-04: inspected clean `main` at `744a7ba861025ac58c7f2c125e363ee0ed6ddc73`, matching remote main.

- `service.py` handles native DOCX, page-local native PDF selection, rendered images and recognition warnings. Preview does not persist data or call analysis/RAG.
- `recognition/base.py` already defines `DocumentRecognizer`, `OCRRecognizer`, `RecognizedPage`, `RecognitionResult`, `RenderedPage` and `RenderedRegion`.
- `recognition/typhoon.py` implements both recognition protocols, separates generated descriptions, and reports no recognition confidence.
- `region_pipeline.py` routes cropped regions and preserves selected candidates. HTR is disabled in the production router; the current segmenter emits an unknown whole-page region.
- `contracts.py` has nullable confidence on blocks, regions and candidates, but no words. Before this change, routed `DocumentRegion.confidence` was segmentation confidence, while unified confidence was recognition confidence. Routed blocks inherited the ambiguity.
- `frontend/src/lib/case-narrative-document.ts` previously consumed that ambiguous region field for `confidence_status` and `minimum_confidence`. Frontend types and this metadata projection need a coordinated correction; no UI redesign is needed.
- `config.py` and the preview router currently select Typhoon only. Existing tests cover native bypass, per-page routing, safe warnings, HTR shutdown and ingestion isolation.

## Implementation decisions

Use the official Vision REST `images:annotate` endpoint with only `DOCUMENT_TEXT_DETECTION`, authenticated by the official `google-auth[requests]` package. JSON preserves field presence: missing confidence remains null and an explicitly returned zero remains zero. This does not require the Google Vision SDK or unrelated Cloud packages. Synchronous ADC/auth/HTTP work runs in a worker thread with request and coroutine timeouts.

Keep page text from `fullTextAnnotation.text`, and traverse pages, blocks, paragraphs, words, then symbols in provider order. Words are metadata, not a source for reconstructing page formatting. The existing raw-output field can retain provider JSON in memory; it is not exposed in the product contract or persisted.

## Configuration and authentication

Install backend dependencies using the existing requirements file:

```powershell
.\env_mitre\Scripts\python.exe -m pip install -r backend/requirements.txt
$env:DOCUMENT_RECOGNIZER = "google_vision"
$env:DOCUMENT_RECOGNITION_TIMEOUT_SECONDS = "60"
```

`DOCUMENT_RECOGNIZER=typhoon` is still the default. Native PDF pages and DOCX bypass either provider. Provider construction is lazy with respect to credentials, so native documents do not require Google authentication even when Google is selected.

2026-09-04 operational choice: keep Typhoon active for now and retain Google as an optional selectable provider. The router imports the Google adapter only when selected; a Typhoon deployment can start without Google packages. Selecting Google requires installing the declared dependency first.

Enable the Cloud Vision API and billing for the Google Cloud project used for requests. Supply Application Default Credentials (ADC) to the backend process through one of Google's supported mechanisms:

- Local development: `gcloud auth application-default login`; configure an appropriate ADC quota project with `gcloud auth application-default set-quota-project PROJECT_ID` when needed. The identity must be permitted to use that project's services.
- An existing service account: set `GOOGLE_APPLICATION_CREDENTIALS` in the process environment to the path of its credential file, kept outside this repository.
- Google Cloud deployment: use the attached service account/workload credentials supported by ADC.

No CyberCase Google project-ID setting is required. The official auth library handles credential refresh and ADC quota-project headers. The request uses the `cloud-vision` OAuth scope. A backend `.env` setting does not automatically export `GOOGLE_APPLICATION_CREDENTIALS` to Google's library; set it in the actual process/container environment.

The existing Compose file already forwards `DOCUMENT_RECOGNIZER`. For local Docker with file-based ADC, use a private Compose override outside the repository, for example:

```yaml
services:
  backend:
    environment:
      DOCUMENT_RECOGNIZER: google_vision
      GOOGLE_APPLICATION_CREDENTIALS: /run/secrets/google-adc.json
    volumes:
      - type: bind
        source: C:/secure/google-adc.json
        target: /run/secrets/google-adc.json
        read_only: true
```

Rebuild the backend image after installing the new dependency. Do not bake credentials into an image or commit credentials/credential JSON. The adapter never prints credentials, provider errors or provider bodies. Failed authentication, HTTP/transport errors, timeouts and invalid responses map to existing recognition errors, which the ingestion pipeline exposes as controlled page/region warnings. There is no provider fallback or application-level retry. Synchronous discovery, refresh and HTTP work run via `asyncio.to_thread`, with bounded HTTP/auth timeouts plus a coroutine deadline. Cancellation does not terminate an already-running thread; its network timeouts remain active.

## Normalized response flow

`Vision DOCUMENT_TEXT_DETECTION → fullTextAnnotation.text + ordered words → RecognizedPage / RecognitionResult → DocumentPage.regions + candidates → preview JSON`

Each `OCRWord` has `text`, nullable `confidence`, and nullable `bbox`. The page's whitespace and newlines remain Google's full annotation text. Word text concatenates symbols in provider order, including Thai combining characters. No offsets, word highlighting, threshold, calibrated probabilities or LLM instructions are generated.

Bounding boxes are the min/max of four complete pixel vertices. Missing/incomplete polygons produce null, including omitted coordinate components; V1 does not assume missing coordinates are zero. Normalized-only polygons are not converted without explicit pixel vertices. Word coordinates refer to the image sent to recognition: the rendered/resized page in unified mode and the crop in routed mode. Region bounding boxes remain page coordinates. These are not original-PDF coordinates. Segmentation type is not inferred from the provider's name, so unified Google output remains unknown-source machine transcription rather than claiming handwriting detection.

## Confidence semantics

| Field | Meaning |
| --- | --- |
| `SegmentedRegion.confidence` | Internal segmentation/classification measurement only |
| `DocumentRegion.segmentation_confidence` | That segmentation measurement, independently preserved |
| `DocumentRegion.recognition_confidence` | Recognizer aggregate; for Google, minimum reported word confidence |
| `RecognizedPage.confidence`, `RecognitionResult.confidence` | Recognition confidence only |
| `RecognitionCandidate.confidence` | Candidate recognition confidence only |
| `DocumentBlock.confidence` | Recognition confidence only when the block represents the entire recognition result/region; text-split blocks retain null |
| `OCRWord.confidence` | Provider-reported value in 0..1; missing/null remains null, explicit zero remains zero |

The ambiguous `DocumentRegion.confidence` field is removed. Backend and frontend types change together; no alias copies segmentation confidence into recognition confidence. A cached older preview lacking the new recognition field retains its text but is treated as recognition confidence not reported. No database contract changes are required.

Google's page/region aggregate is **the minimum of non-null word confidences**, or null if none are reported. This is a conservative descriptive statistic of the reported words, not a probability that the document is correct. Missing word measurements remain visible as null in `words`; a non-null minimum does not imply all words have measurements. Invalid, nonnumeric, nonfinite or out-of-range confidence fails as a controlled invalid response rather than being clamped.

The existing narrative projection takes the minimum of recognition aggregates for nonempty transcribed machine-read regions. It preserves the existing conservative coverage rule: if any such region has no aggregate, `confidence_status=not_reported` and `minimum_confidence=null`. Otherwise it reports the minimum across those regions. Native-only PDF/DOCX regions remain `not_applicable`, including native documents with unrelated warnings. Typhoon remains `not_reported` with null aggregate and `words=[]`. Segmentation measurements never participate. No confidence value changes verification status; existing routed unknown/mixed/manual-review policies remain unchanged.

Page/block/paragraph provider confidence is not substituted for missing word confidence or copied into the aggregate. It remains available only in the in-memory raw JSON debugging field. Raw JSON is not part of the API or database schema.

## Synthetic research receipt

`backend/tests/fixtures/google_vision_synthetic.json` contains both a synthetic Google-shaped response and the asserted normalized result. It is explicitly labeled **mock data, not a live Google response**. The Thai text contains fictitious `นาย ก.` and the amount `52,000`; the illustrative minimum is 0.71. Tests verify the receipt rather than presenting those numbers as measured accuracy.

## Validation receipt — 2026-09-04

- Existing ingestion tests: 28 passed.
- New Google normalization, transport and integration tests: 51 passed.
- Full backend suite: 336 passed and 2 subtests passed; one existing Starlette/httpx deprecation warning.
- TypeScript typecheck passed; focused frontend ingestion/narrative suite: 17 passed across 3 files.
- Scoped Ruff passed and all 33 checked ingestion/config/router/test Python files passed formatting. Compileall and `git diff --check` passed. All 17 changed/new code files are below 300 lines (largest: 247).
- Full backend Ruff found 14 existing violations in unchanged files outside this task. Full backend format check also reports pre-existing differences outside the changed files.
- Scoped frontend ESLint passed. The first unrestricted full frontend run had 126 passes and 3 five-second rendering timeouts; **the complete two-worker rerun passed all 129 tests across 31 files with the same timeout**. No test configuration was changed.
- ADC discovery returned unavailable. The optional live smoke was skipped. No Google OCR request ran, and no real case data was sent to Google.

Commands run from the relevant workspace directory:

```powershell
python -m pytest -q tests/test_document_ingestion.py tests/test_document_ingestion_routing.py tests/test_document_ingestion_api.py tests/test_document_ingestion_segmentation.py tests/test_document_ingestion_eval.py
python -m pytest -q tests/test_document_ingestion_google_response.py tests/test_document_ingestion_google_transport.py tests/test_document_ingestion_google_service.py
python -m pytest -q
ruff check backend
ruff format --check backend
python -m compileall -q backend/app backend/tests
git diff --check
npx tsc --noEmit
npm run test -- src/test/lib/case-narrative-document.test.ts src/test/components/intake/DocumentIngestionPreview.test.tsx src/test/components/intake/CaseIntakeView.test.tsx
npm run test
npm run test -- --maxWorkers=2
```

Backend Python commands used `env_mitre/Scripts/python.exe` (Python 3.12.2). Google-auth 2.57.0 and requests 2.34.2 were already installed there; the new declared requirement is `google-auth[requests]>=2.38.0`.

## Changed files

Paths are relative to the repository root.

- Configuration/factory: `backend/app/config.py`, `backend/app/routers/document_ingestion.py`, `backend/requirements.txt`.
- Provider and normalization: `backend/app/services/document_ingestion/recognition/google_vision.py`, `backend/app/services/document_ingestion/recognition/google_vision_response.py`.
- Shared contract and preview plumbing: `backend/app/services/document_ingestion/contracts.py`, `backend/app/services/document_ingestion/recognition/base.py`, `backend/app/services/document_ingestion/recognized_region.py`, `backend/app/services/document_ingestion/region_pipeline.py`, `backend/app/services/document_ingestion/service.py`. The unified-region helper was extracted to keep the service below 300 lines.
- Backend tests and receipt: `backend/tests/test_document_ingestion_google_response.py`, `backend/tests/test_document_ingestion_google_transport.py`, `backend/tests/test_document_ingestion_google_service.py`, `backend/tests/fixtures/google_vision_synthetic.json`.
- Frontend contract/metadata only: `frontend/src/lib/document-ingestion.ts`, `frontend/src/lib/case-narrative-document.ts`.
- Frontend tests: `frontend/src/test/lib/case-narrative-document.test.ts`, `frontend/src/test/components/intake/CaseIntakeView.test.tsx`, `frontend/src/test/components/intake/DocumentIngestionPreview.test.tsx`.
- Documentation: this file, `backend/app/services/document_ingestion/README.md`, `CONTINUITY.md`.

## Typhoon activation follow-up — 2026-09-04

Local settings, Compose defaults and the running backend select `typhoon`. The existing container lacked Google packages and initially failed router import; importing the Google adapter only inside its factory branch restored Typhoon startup. The backend health endpoint reports ok/database connected. All 17 focused provider/API tests pass, including an isolated subprocess that blocks Google imports. Scoped Ruff/format checks pass. No live OCR call was made for this follow-up.

## Deferred scope

Threshold calibration; low-confidence word classification; frontend uncertainty highlighting; human correction workflow; OCR uncertainty propagation to LLM; Azure benchmarking; downstream summarization experiments. No analysis/gap/follow-up prompt, additional LLM call, RAG/MITRE behavior, report generation, database migration or HTR-enablement change is included.

## Official references

- [Vision images:annotate REST API](https://cloud.google.com/vision/docs/reference/rest/v1/images/annotate)
- [Full text hierarchy and word confidence](https://cloud.google.com/vision/docs/reference/rest/v1/AnnotateImageResponse#Word)
- [Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
- [Google-auth AuthorizedSession and timeouts](https://google-auth.readthedocs.io/en/latest/reference/google.auth.transport.requests.html)
