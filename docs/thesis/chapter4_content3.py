"""Chapter 4, sections 4.8 to 4.13: verification, follow-up, report, frontend, tests."""

from __future__ import annotations

from build_chapter4 import Chapter, source_of

PIPELINE = "backend/app/services/case_analysis/pipeline.py"
REPORTS = "backend/app/services/reports"


def verification(ch: Chapter) -> None:
    ch.heading("4.8 Verification and Revision")
    ch.body(
        "Verification is the stage that separates the two arms. It binds the analysis to the case "
        "using the resolver of Section 4.7, records the resulting grounding report, and, if a "
        "revision budget was given, hands the failed quotations back to the model and asks again."
    )
    ch.body(
        "Verifying and revising are separate settings because they answer different questions. "
        "Verifying alone drops a quotation that is in no source and records the loss. Revising "
        "asks for those quotations again, which costs a model call and may be answered by "
        "deleting the claims instead."
    )
    ch.code_figure(
        source_of(PIPELINE, "VerifyStage"),
        "The verification stage, with an optional revision budget",
        [
            (("class VerifyStage", "the product ships"), "The docstring records why the two settings are separate, and that a "
                           "budget of zero is what the product ships."),
            (("table = (so_far.technical_context", "rounds: list"), "Bind the analysis as written, and record the first grounding report. "
                            "Attempt zero is the unrevised state, which is what a comparison "
                            "against arm A needs."),
            (("for attempt in range(1", "break"), "Each round recomputes which quotations failed. A model that fixed "
                            "everything ends the loop here, so a sound analysis costs no second "
                            "call."),
            (("output = await self.analysis_request", "revision=revision_note"), "The revision call. It is the same analysis request with a correction "
                            "appended to the system prompt, so the revised analysis is produced "
                            "by the same code path as the first one."),
            (("trace = resolve_case_trace(output.trace", "rounds.append"), "Rebind and record. Every round is kept, not only the last."),
            (("receipt={**so_far.receipt",), "The receipt carries the full list of rounds."),
        ],
    )
    ch.plain("4.8.1 Naming what failed, rather than restating the rules", bold=True)
    ch.body(
        "The correction sent back to the model names each quotation that could not be found and "
        "the claim it was written for. A general restatement of the citation rules would not "
        "tell the model which of its quotations was the problem, and a model that cannot tell "
        "which line was wrong tends to rewrite all of them."
    )
    ch.code_figure(
        source_of(PIPELINE, "unbound_citations") + "\n\n" + source_of(PIPELINE, "revision_note"),
        "Finding the quotations that missed, and writing the correction",
        [
            (("def unbound_citations", "survived = {"), "The comparison is between what the model wrote and what survived "
                          "binding. A citation present in the first and absent from the second is "
                          "one the sources did not contain."),
            (("claim.supporting_citations + claim.contradicting_citations", "not in survived"), "Both supporting and contradicting citations are checked, because a "
                           "claim can be wrong about what contradicts it."),
            (("def revision_note", "CASE_TRACE_REVISION_PROMPT"), "The correction lists each failure as a claim identifier and the exact "
                            "quotation that failed, so the model can repair one line without "
                            "touching the others."),
        ],
    )
    ch.plain("4.8.2 The trap this measurement has to avoid", bold=True)
    ch.body(
        "A revising model has a shortcut available: deleting every claim whose quotation failed "
        "produces a grounding report with no unfound citations at all. The score is then perfect "
        "and the analysis says less than it did before."
    )
    ch.body(
        "Two things guard against reading that as an improvement. The prompt states explicitly "
        "that a claim is not to be removed merely because its quotation was wrong, and that an "
        "analysis which says less is not a better one. More importantly, the receipt records "
        "every round, so the claim count is visible alongside the grounding count. A run whose "
        "unfound citations fall from one to zero while its claim count falls from two to one is "
        "reported as exactly that. An automated test asserts this reading directly, because a "
        "metric that can be satisfied by producing nothing is not a metric."
    )


def followup(ch: Chapter) -> None:
    ch.heading("4.9 Gap Detection and Bounded Follow-Up")
    ch.body(
        "An analysis records not only what it found but what it could not settle. Each gap "
        "carries a topic, a status, a priority, and the question worth asking about it. The four "
        "statuses distinguish material that was never mentioned from material the sources "
        "explicitly say is unavailable, which is the distinction that keeps the system from "
        "asking a question the case has already answered with no."
    )
    ch.table(
        "The gap statuses",
        ["Status", "Meaning", "Worth asking?"],
        [
            ["NOT_PROVIDED", "The topic was never mentioned in any source", "Yes"],
            ["EXPLICITLY_UNKNOWN", "A source states the information is unavailable", "No, never re-asked"],
            ["AMBIGUOUS", "Stated, but not precisely enough to rely on", "Yes"],
            ["CONFLICTING", "Two sources give incompatible values", "Yes"],
        ],
    )
    ch.body(
        "The follow-up policy is deliberately narrow. One question is outstanding at a time, so a "
        "reply needs no marking: it answers the question above it and becomes a case source bound "
        "to that gap. The case is analysed again only once a round of questions has been spent, "
        "so a round of three questions costs one analysis rather than three. Two settings bound "
        "the whole mechanism: the number of rounds, and the number of gaps asked per round."
    )


def reports(ch: Chapter) -> None:
    ch.heading("4.10 The Report Compiler")
    ch.body(
        "The report is built from the stored analysis, not from a fresh model call. Given the "
        "same analysis it produces the same report every time, which is the property that lets a "
        "report be cited in a case file at all. A generated report that differs between two "
        "downloads cannot be referred to by a version number."
    )
    ch.body(
        "Compilation is a projection. The template decides the structure and the wording of "
        "everything except the claims themselves, and the claims are copied from the analysis "
        "with their citations attached. Nothing in the report is written by a model at report "
        "time."
    )
    ch.table(
        "The seven sections of a report",
        ["Section identifier", "Heading"],
        [
            ["case_summary", "1. Case summary"],
            ["case_evidence", "2. Indicators found"],
            ["mitre_attack_mapping", "3. MITRE ATT&CK mapping"],
            ["mapping_rationale", "4. Reasoning for the mapping"],
            ["evidence_to_examine", "5. Material to examine further"],
            ["preliminary_recommendations", "6. Preliminary recommendations"],
            ["system_limitations", "7. Limitations of the system"],
        ],
    )
    ch.body(
        "Section 3 is separated from sections 1 and 2 on purpose. ATT&CK is external technical "
        "context, not a finding about the case, and the report says so in the section itself "
        "rather than relying on the reader to know. A technique appearing in a report means the "
        "retrieval service returned it, not that the technique was used."
    )
    ch.body(
        "Reports are versioned per case. Asking twice for a report of the same analysis returns "
        "the version already built rather than compiling a second one, so a report identifier "
        "always refers to one fixed document. Export is available as HTML, which the interface "
        "previews in place, and as PDF."
    )
    ch.code_figure(
        source_of(f"{REPORTS}/assembly.py", "build_case_report"),
        "Building a report, and checking it once",
        [
            (("def build_case_report", "rather than being stored"), "The docstring records the policy: the report is a template render, so "
                          "a failure here means the renderer is wrong, not that the analysis was."),
            (("report = build_case_template_report",), "The template does the work."),
            (("validate_case_structured_report(", "mitre_ids="), "The result is checked once: the sections are in the required order, "
                           "claim identifiers are unique, every cited source belongs to this "
                           "case, and every technique named was one the analysis actually "
                           "associated. A failure raises rather than being stored as a report "
                           "that failed."),
        ],
    )


def frontend(ch: Chapter) -> None:
    ch.heading("4.11 The Web Interface")
    ch.body(
        "The frontend is a Next.js 16 application using the App Router. Each case is a workspace "
        "with five views, reached from one header, and the case identifier in the route is the "
        "only state the pages share."
    )
    ch.table(
        "The pages of the application",
        ["Route", "View", "What it is for"],
        [
            ["/case", "Case library", "Every case the investigator owns"],
            ["/case/[caseId]", "Intake", "Write a narrative or upload a document"],
            ["/case/[caseId]/overview", "Overview", "The analysis: findings, parties, timeline, impacts"],
            ["/case/[caseId]/sources", "Sources", "What the case is analysed from, and the original files"],
            ["/case/[caseId]/technical-context", "Technical context", "Retrieved ATT&CK techniques and why they were associated"],
            ["/case/[caseId]/report", "Report", "Report versions, previewed as HTML and exported as PDF"],
            ["/login, /register", "Authentication", "Cookie session"],
        ],
    )
    ch.body(
        "Server state is held by TanStack Query rather than in components. A mutation invalidates "
        "the queries it affects, and the views re-read; no view keeps its own copy of the case. "
        "This removed a class of defect where two panels showed different versions of the same "
        "analysis after one of them had refreshed."
    )
    ch.plain("4.11.1 Showing a claim with its source", bold=True)
    ch.body(
        "The interface presents each finding with the wording from the case that supports it. "
        "Clicking a citation opens the source at the quoted passage, and where the source came "
        "from a document with located pages, the page number is shown. The reader can therefore "
        "check a statement against the original material without leaving the finding, which is "
        "the whole purpose of resolving citations in the first place."
    )
    ch.body(
        "Where a claim is marked as something other than reported, that standing is shown next to "
        "it rather than only in the report. A suspicion presented in the same visual weight as a "
        "finding is a defect of the interface, not of the model."
    )


def testing(ch: Chapter) -> None:
    ch.heading("4.12 Automated Testing")
    ch.body(
        "The backend carries a pytest suite that runs against the real code paths rather than "
        "against mocks of them. The model provider is stubbed, because a test that calls a paid "
        "endpoint is a test nobody runs; everything below that is exercised for real, including "
        "the database, using a PostgreSQL instance for the tests that touch persistence."
    )
    ch.bullets(
        [
            "Route surface - the exact set of routes is asserted, so an undocumented route fails",
            "Schema parity - the SQLAlchemy models and the Alembic migrations are compared",
            "Quote resolution - each repair strategy, and the Thai composition case in particular",
            "Grounding arithmetic - verified, paraphrased and unfound must sum to what was claimed",
            "The arms - arm A leaves an invented quotation in place; arm B hands it back",
            "The deletion trap - a run that improves its score by dropping claims is reported as such",
            "Follow-up policy - one question outstanding, rounds bounded, EXPLICITLY_UNKNOWN never re-asked",
            "Report determinism - the same analysis compiles to the same report",
        ]
    )
    ch.body(
        "An end-to-end suite drives the browser against a running stack with a stubbed provider, "
        "covering the path from intake through analysis to report export."
    )


def summary(ch: Chapter) -> None:
    ch.heading("4.13 Summary")
    ch.body(
        "The implementation described in this chapter has three properties that the evaluation in "
        "Chapter 5 relies on. The analysis is a list of stages, so a condition can be created by "
        "removing one rather than by writing a second system. The pipeline holds no database "
        "connection, so the same code runs over a dataset as over a case. And binding an analysis "
        "to its sources produces counts rather than exceptions, so an analysis that was poorly "
        "supported still yields a measurement of how poorly."
    )
    ch.body(
        "What the chapter does not claim is that any of this eliminates error. The system checks "
        "that a quotation exists in the source it names; it does not check that the quotation "
        "supports the claim it was attached to. That limit is stated here because Chapter 5 "
        "measures against it rather than around it."
    )
