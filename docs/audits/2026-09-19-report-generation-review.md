# Is report generation over-engineered? — `refactor/remove-case-run` @ `4d13a18`

2026-09-19 [USER] Check the report generation path in particular: is it over-engineered?

2026-09-19 [TOOL] Inspection only. Backend report code is 1,568 lines across
`services/reports/` (9 modules), `schemas/reports.py`, `models/report.py` and
`routers/case_reports.py`; the frontend adds 445. One test module covers it
(`tests/test_case_report_presentation.py`). The development database has **0 report rows**.

## The short answer

Yes, in one specific way: **the report is a deterministic template render, and it is
wrapped in the machinery of an unreliable model call.** Provider, model, latency, token
counts, prompt version, a validation pass, a second validation pass on read, two status
columns and an idempotency key all describe a request that never leaves the process.

The PDF renderer is *not* the problem. 463 lines for A4 layout with registered Thai fonts
is what that job costs.

## 1. Telemetry for a call that does not happen

`case_report_template.py:36` hardcodes `provider="deterministic"`, `model="case-template"`.
No module under `services/reports/` imports `httpx`, a provider stage, or any model client —
the report is built from the saved analysis by `case_report_content.py` and nothing else.

Around that, the system records:

| Field | Where | What it describes |
|---|---|---|
| `provider`, `model` | `ReportRunResult` | constants |
| `latency_ms` | result, DB column, API | how long a string build took |
| `input_tokens`, `output_tokens` | result, DB column, API | always NULL; nothing sets them |
| `prompt_version` | result, DB column, API | a prompt that does not exist |

That is 5 columns on `case_reports`, 5 fields on `CaseReportRead`, and 5 on `ReportRunResult`.

## 2. The system validates its own output, then validates it again on every read

`validate_case_structured_report` checks that section ids match the required order, that
claim ids are unique, and that cited sources and techniques are subsets of the input. It runs:

1. in `run_case_report_generation`, on the report just built, and
2. in `validated_report_input`, **again**, every time a PDF or HTML is requested.

Both inputs are the output of `build_case_template_report`, a pure function over data the
system already validated when it stored the analysis. If the section order can be wrong, the
renderer has a bug, and checking the same value a second time on read does not find it any
sooner — it only turns it into a 409 for the user.

## 3. Version indirection with exactly one version

```python
REPORT_SECTION_IDS_BY_VERSION: dict[str, tuple[str, ...]] = {
    "preliminary_analysis_report_v1": PRELIMINARY_REPORT_SECTION_IDS,
}
REPORT_SECTION_HEADINGS_BY_VERSION: dict[str, dict[str, str]] = {
    "preliminary_analysis_report_v1": PRELIMINARY_REPORT_SECTION_HEADINGS,
}
```

Two dictionaries keyed by a `Literal` with one member. `ReportVersion` and `ReportStatus` are
also one-value literals. The constants they wrap are already exported directly and used
directly; the lookup tables have no reader that needs the indirection.

## 4. Five columns to say whether one pure function worked

`status` (`completed|failed`), `validation_status` (`validated|failed`),
`validation_errors_json`, `failure_code`, `failure_message` — for an operation that either
returns a `StructuredReport` or raises. `validation_status` is derived from `status` on the
line that sets it:

```python
status=generation.status,
validation_status="validated" if generation.status == "completed" else "failed",
```

## 5. A bug becomes a stored row

```python
except Exception as error:
    return ReportRunResult(status="failed", ..., validation_errors=(str(error),), ...)
```

Any exception in the renderer — an attribute error, a bad assumption about the trace — is
caught, stringified, and persisted as a *failed report*. The stack trace is gone, the case
now owns a permanent row describing the failure, and the user is told the report could not
be generated from their analysis when the truth is that the code is broken. `AGENTS.md` asks
for the opposite: let development failures surface.

## 6. One document, three renderers

| Renderer | Lines | Used by |
|---|---|---|
| `case_report_pdf.py` | 463 | download |
| `case_report_html.py` + Jinja template | 51 + template | the preview iframe |
| `PersistedReportCard.tsx` | 234 | the card around the iframe |

PDF and HTML share `build_case_report_display` (133 lines) — but each also carries its own
copy of `strip_reference_text` with the same three regexes, and its own text cleaner
(`plain_text`/`formatted_text` in the PDF, `clean_report_text` in the HTML). The frontend
fetches rendered HTML as a blob and shows it in an iframe rather than rendering the
structured report it already has typed.

## 7. An idempotency key that mostly derives itself

```python
idempotency_key = request.idempotency_key or f"report-{result.id}-{result.evidence_revision}"
```

The derived form is what makes regeneration safe. The client-supplied one adds a nullable
API field, a normalising validator, a NOT NULL column and a unique constraint — and the
frontend generates a random UUID for it, which defeats the deduplication the column exists
for. A unique constraint on `(case_id, analysis_result_id)` says the same thing without a key.

## What to cut

| Change | Lines |
|---|---|
| Drop provider/model/latency/token/prompt_version from result, model, schema and migration | ~60 |
| Validate once, at generation; delete the read-path re-validation | ~40 |
| Delete the two `*_BY_VERSION` tables and the one-value literals | ~20 |
| Collapse `status` + `validation_status` + three failure columns to one nullable `error` | ~50 |
| Let the renderer raise; no `except Exception` | ~15 |
| One text-cleaning module shared by PDF and HTML | ~40 |
| Key reports on `(case_id, analysis_result_id)`; drop `idempotency_key` | ~30 |

About **255 lines** and **8 of the 18 columns** on `case_reports`, with no change to what the
user gets: a versioned report they can preview and download.

## What to keep

The PDF renderer, the Thai font registration, the section content builders, the display model
shared by both renderers, and report versioning per case. Those are the feature.


---

## Applied, 2026-09-19

All seven cuts landed on `refactor/remove-case-run`:

- `ReportRunResult` → `BuiltReport`, holding only the report. Provider, model,
  prompt version, latency and token counts are gone from the result, the model,
  the schema and the API.
- `run_case_report_generation` → `build_case_report`, which validates once and
  raises instead of catching every exception into a stored failure.
- `validated_report_input` → `stored_report`: the read path renders what was
  stored without checking it again.
- `REPORT_SECTION_IDS_BY_VERSION`, `REPORT_SECTION_HEADINGS_BY_VERSION`,
  `ReportPersistenceStatus` and `ReportValidationStatus` deleted.
- `case_reports` keeps six columns: `id, case_id, analysis_result_id,
  version_number, structured_report, created_at`, with `structured_report` now
  NOT NULL and a unique constraint on `analysis_result_id`.
- `idempotency_key` gone: one report per analysis, so regenerating returns the
  existing one. The frontend no longer invents a UUID per page load.
- `case_report_text.py` holds the cleaning both renderers were duplicating; the
  failed-report card in `PersistedReportCard.tsx` is deleted with the columns
  that fed it.

Backend report code is 1,656 → 1,435 lines, the frontend report components lose
another 45, and `case_reports` goes from 18 columns to 6. Migration
`0007_report_content_only` drops the columns and deletes any report row that
never produced content. Verified: 162 backend tests pass, `alembic check` reports
no drift, frontend tsc clean, lint back to two warnings, build succeeds.
