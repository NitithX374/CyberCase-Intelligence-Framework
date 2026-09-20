"""Chapter 4, sections 4.4 to 4.8: the pipeline, the gate, and grounding."""

from __future__ import annotations

from build_chapter4 import Chapter, source_of

PIPELINE = "backend/app/services/case_analysis/pipeline.py"
VALIDATION = "backend/app/services/case_analysis/validation.py"
RESOLVER = "backend/app/services/case_analysis/source_quote_resolver.py"
GATE = "backend/app/services/case_analysis/mitre_gate"
CONTRACTS = "backend/app/services/case_analysis/contracts"


def pipeline(ch: Chapter) -> None:
    ch.heading("4.4 The Analysis Pipeline as an Ordered List of Stages")
    ch.body(
        "The analysis is written as a list of stages rather than as one function. Each stage "
        "receives what the previous stages produced and returns the next version of it. Two "
        "properties follow from that shape, and the experiment in Chapter 5 depends on both."
    )
    ch.body(
        "First, an ablation runs this same code with one stage left out. What is measured is "
        "therefore the system itself, rather than a second implementation of the system that "
        "drifts away from the first as the code changes. Second, no stage opens a database "
        "connection. Everything a stage needs arrives as an argument, which is what allows the "
        "identical pipeline to run over a dataset file instead of a case row."
    )
    ch.code_figure(
        "\n\n".join(
            [
                source_of(PIPELINE, "AnalysisInput"),
                source_of(PIPELINE, "AnalysisArtifacts"),
                source_of(PIPELINE, "Stage"),
                source_of(PIPELINE, "run_pipeline"),
                source_of(PIPELINE, "without"),
            ]
        ),
        "The pipeline contract: the input, the artifacts, the Stage protocol and the runner",
        [
            (("class AnalysisInput", "question: str | None"), "AnalysisInput is everything the pipeline reads. It is frozen and no "
                          "stage adds to it, so what an analysis saw is fully described by this "
                          "one object."),
            (("class AnalysisArtifacts", "receipt: dict"), "AnalysisArtifacts is what the stages have produced so far. A stage "
                            "returns the next version of it rather than mutating this one."),
            (("class Stage(Protocol)", "async def run(self, data"), "Stage is a Protocol rather than a base class. A stage is anything "
                            "with a name and a run method, so stages stay independent of each "
                            "other and of any shared parent."),
            (("    name: str",), "The name exists so that an ablation can drop a stage by naming it."),
            (("async def run_pipeline", "    return artifacts"), "run_pipeline is the entire engine: fold the stages over the "
                            "artifacts, in order. There is no branching and no error recovery, "
                            "because a stage that cannot do its work returns a status instead of "
                            "raising."),
            (("def without(", "stage.name not in names"), "without() is how an ablation condition is written. Removing a stage "
                            "by name yields a pipeline that is otherwise identical."),
        ],
    )
    ch.plain("4.4.1 The three arms of the experiment", bold=True)
    ch.body(
        "The comparison reported in Chapter 5 is between analyses that differ by one stage. Arm A "
        "is a direct model call with nothing checked afterwards, which is the baseline that "
        "LLM-assisted reporting tools already provide. Arm B adds a verification stage that binds "
        "the analysis to the case sources and hands failed quotations back to the model. A third "
        "arm sits between them: verification that records what failed without asking for a "
        "repair. Separating those two answers a question the pair on its own cannot, namely "
        "whether any benefit comes from the checking or from the extra model call the checking "
        "makes possible."
    )
    ch.code_figure(
        source_of(PIPELINE, "analysis_stages"),
        "Selecting an arm; the setting is read at call time rather than at import",
        [
            (("def analysis_stages", "the same code with a step added"), "The docstring states the design constraint: the arms differ by one "
                          "stage, not by one implementation."),
            (("chosen = arm or settings",), "The arm is read from configuration on every call, so a test or an "
                       "experiment can change arms without rebuilding anything."),
            (("chosen == \"direct\"", "AnalysisStage())"), "Arm A. Retrieve technical context, then make one analysis call. "
                            "Nothing checks what the model wrote."),
            (("chosen == \"revise\"", "case_analysis_max_revisions"), "Arm B. The same two stages plus verification, carrying a revision "
                            "budget, so failed quotations are handed back and asked for again."),
            (("return (TechnicalContextStage(), AnalysisStage(), VerifyStage())",), "The default, and what the product ships: verify and record, do not "
                        "revise. A revision costs a second model call and, as Section 4.8 "
                        "explains, can be answered by deleting the claim."),
        ],
    )
    ch.table(
        "What each arm runs",
        ["CASE_ANALYSIS_ARM", "Stages", "Model calls", "Role in the experiment"],
        [
            ["direct", "technical_context, analysis", "1", "Arm A, the baseline"],
            ["verify", "technical_context, analysis, verify", "1", "Checking alone; shipped default"],
            ["revise", "technical_context, analysis, verify", "1 plus up to N", "Arm B, checking with repair"],
        ],
    )


def gate(ch: Chapter) -> None:
    ch.heading("4.5 The MITRE Applicability Gate")
    ch.body(
        "Not every case needs ATT&CK. A dispute over a transfer that was authorised by telephone "
        "has no adversary technique in it, and retrieving one produces a technical framing the "
        "material does not support. A gate therefore decides, before retrieval, whether the case "
        "calls for technical context at all."
    )
    ch.body(
        "The gate is something this research compares rather than something the system simply "
        "has, so there are three of them and one setting selects between them. The third, which "
        "always declines, is the ablation that measures what the technical context was worth."
    )
    ch.code_figure(
        source_of(f"{GATE}/__init__.py", "chosen_gate")
        + "\n\n"
        + source_of(f"{GATE}/__init__.py", "mitre_gate"),
        "Three gates behind one setting, resolved on each call",
        [
            (("def chosen_gate", "mitre_gate_mode == \"never\""), "The mode is read from settings inside the function. Resolving it at "
                          "import time would freeze whichever mode happened to be set when the "
                          "process started."),
            (("return never_applicable",), "The ablation arm: never retrieve."),
            (("mitre_gate_mode == \"encoder\"", "return evaluate_mitre_applicability_encoder"),
             "The encoder gate is imported lazily, because torch and transformers "
                           "are not in the backend requirements. A deployment that does not use "
                           "the encoder does not pay for the dependency."),
            (("    return evaluate_mitre_applicability",), "The default: a single prompt that reads the whole case."),
            (("async def mitre_gate", "return await chosen_gate()"), "The public entry point. Every caller goes through this, so switching "
                            "gates changes nothing else in the pipeline."),
        ],
    )
    ch.table(
        "The three gates",
        ["MITRE_GATE_MODE", "What decides", "Notes"],
        [
            ["llm (default)", "One prompt over the whole case", "mitre_gate/llm.py, model from CHAT_ASK_MODEL"],
            ["encoder", "XLM-R scoring one sentence at a time", "mitre_gate/encoder.py, needs torch and transformers"],
            ["never", "Nothing; always declines", "The ablation, for measuring the value of technical context"],
        ],
    )
    ch.plain("4.5.1 Sentence segmentation for the encoder gate", bold=True)
    ch.body(
        "The encoder gate judges one sentence at a time, which requires cutting the case into "
        "sentences first. Thai is written without spaces between words, so a sentence has to be "
        "found rather than split off at punctuation. The implementation uses PyThaiNLP crfcut, a "
        "conditional random field trained on Thai prose."
    )
    ch.body(
        "The property that matters is not segmentation quality but exactness: every sentence "
        "returned is an exact substring of the source it came from. The span the gate points at "
        "is therefore grounded by construction, and the query sent to the retrieval service is "
        "text the case actually contains rather than text a model wrote about the case."
    )
    ch.code_figure(
        source_of(f"{GATE}/sentences.py", "split_text"),
        "Cutting a case source into sentences that are exact spans of it",
        [
            (("def split_text", "prose runs together"), "The docstring records why lines are separated before sentences are "
                          "found: a report is full of headings, form fields and table rows, each "
                          "its own unit, which a splitter trained on prose runs together."),
            (("for line in text.splitlines", "return sentences"), "Lines first, then crfcut within each line."),
            ("Lines 15-22", "A fragment shorter than the minimum is attached to the sentence after "
                            "it. crfcut breaks at the dot in names such as PowerShell.exe, and "
                            "cutting there would split a technical phrase in half."),
        ],
    )


def contract(ch: Chapter) -> None:
    ch.heading("4.6 The Analysis Call and Its Output Contract")
    ch.body(
        "The analysis is one model call. It receives the case sources, the technical context if "
        "any was retrieved, and a system prompt; it returns a structured object rather than "
        "prose. The structure is what makes the rest of the chapter possible: a claim that "
        "carries its own citations can be checked, and free text cannot."
    )
    ch.body(
        "Two schemas describe the same object. On the wire, the model is given a weakened schema, "
        "because providers reject several JSON Schema keywords that Pydantic emits. Locally, the "
        "response is validated against the strict Pydantic model. The strict version is the one "
        "that decides what is accepted."
    )
    ch.code_figure(
        source_of(f"{CONTRACTS}/sources.py", "CaseSourceCitation"),
        "A citation: which source, which words, and where they sit in the document",
        [
            (("class CaseSourceCitation", "exact_quote: str"), "source_id names the case source; exact_quote is the wording the model "
                          "says supports the claim. Both are required for the citation to mean "
                          "anything."),
            (("document_id:", "page_numbers: list[int]"), "document_id, filename and page_numbers describe where in the original "
                           "file the quotation was found. The model never writes these: they are "
                           "filled in by the resolver in Section 4.7, because only the resolver "
                           "knows where the text actually is."),
            (("sanitize_page_numbers", "~def sanitize"), "A validator normalises the page list and reject page numbers that are "
                            "not positive integers."),
            (("if not (self.document_id and self.filename",), "A citation that has a document but no located page has its page list "
                            "cleared, so the interface never offers a page link it cannot honour."),
        ],
    )
    ch.code_figure(
        source_of(f"{CONTRACTS}/sources.py", "CaseAnalysisClaim"),
        "A claim, with its epistemic status and the citations that support it",
        [
            (("class CaseAnalysisClaim", "claim_id:"), "claim_id is the key everything else in the trace points at: parties, "
                          "timeline entries, impacts, gaps and ATT&CK associations all reference "
                          "claims by this identifier."),
            (("    claim_type:",), "claim_type separates what the sources reported from what the model "
                       "inferred."),
            (("    epistemic_status:",), "epistemic_status is the claim's standing: reported, suspected, "
                       "contradicted, not_established, unknown or not_confirmed. This is the "
                       "field that lets a report show a reader that a statement is disputed "
                       "rather than settled."),
            (("supporting_source_ids", "contradicting_citations"), "Supporting and contradicting sources are listed separately, so a "
                           "claim that the material argues both ways about can say so."),
            (("field_validator", "~field_validator"), "Validators normalise identifiers and drop citations with empty "
                            "quotations before the object is constructed."),
        ],
    )


def grounding(ch: Chapter) -> None:
    ch.heading("4.7 Binding an Analysis to the Case It Was Written From")
    ch.body(
        "A model asked to quote its sources will sometimes quote wording that is not in them. The "
        "binding step takes the analysis as written and resolves it against the actual source "
        "text: each quotation is looked for in the source it names, and what is found determines "
        "what survives."
    )
    ch.plain("4.7.1 Finding a quotation, and repairing one that nearly matches", bold=True)
    ch.body(
        "An exact string search is too strict for Thai. The same syllable can arrive pre-composed "
        "or as a base character plus combining marks; SARA AM in particular carries a "
        "compatibility decomposition, so the two spellings are different strings that render "
        "identically. A quotation that differs only in that way is the model quoting correctly "
        "and the comparison failing. The resolver therefore tries several strategies before "
        "giving up, and when a repair succeeds the source's own spelling is stored rather than "
        "the model's."
    )
    ch.code_figure(
        source_of(RESOLVER, "find_aligned_quote"),
        "Finding a quotation that an exact search missed, in four escalating attempts",
        [
            (("occurrences = quote_occurrences", "return None"),
             "The exact search comes first and is also the strictest. A quotation found exactly "
             "once is returned unchanged. One found more than once is refused rather than "
             "guessed at, because a citation that could point at two places in the source is "
             "not a citation the reader can follow."),
            (("compatibility_aligned = find_folded", "return compatibility_aligned"),
             "Unicode compatibility folding, which is what catches the Thai case described "
             "above. The fold keeps an index back into the original text, so what is returned "
             "is the source's own spelling rather than the folded form."),
            (("ellipsis_aligned = expand_unique", "return ellipsis_aligned"),
             "A quotation with an ellipsis in the middle, expanded when exactly one stretch of "
             "source text fits both halves."),
            (("clean_quote = re.sub(r\"[*_#`~]\"", "if not words"),
             "Markdown decoration and curly quotation marks are normalised. The model writes "
             "light markdown; the source does not have it."),
            (("def word_to_pattern", "pattern_str = "),
             "The words are turned into a pattern that tolerates decoration and whitespace "
             "between them, which is what catches a quotation the model reflowed."),
            (("if len(matches) == 1", "return content[match.start()"),
             "Only a unique match is accepted, and the span returned is taken from the source, "
             "not from the model's wording."),
            (("~    return None",),
             "If nothing matched, the quotation is not in that source, and the caller counts it "
             "as such rather than treating the failure as an error."),
        ],
    )
    ch.plain("4.7.2 One policy: nothing is rejected, everything is counted", bold=True)
    ch.body(
        "An earlier version of this module raised an exception on nine different structural "
        "problems. One invented technique identifier, or one claim citing a source outside the "
        "bundle, cost the entire analysis, while an invented quotation on the next line was "
        "quietly dropped. Two policies for the same class of mistake, and the harsher one fired "
        "on the less serious error."
    )
    ch.body(
        "The module now has one policy. Everything the model wrote either resolves against a "
        "source, is trimmed so that it stops pointing at something that is not there, or is "
        "counted as lost. The counts are what a reader, and an experiment, are given in place of "
        "a failure. This matters for the research as much as for the product: an arm that raises "
        "on bad output produces no measurement of how bad the output was."
    )
    ch.code_figure(
        source_of(VALIDATION, "resolve_case_trace"),
        "Resolving a whole trace: claims, the things that point at claims, and the counts",
        [
            (("registry = {source.source_id", "document_context = build_document"), "A registry of sources by identifier, and the document context that "
                          "page resolution needs."),
            (("claims = deduplicated_claims", "resolved_claims = ["), "Duplicate claim identifiers are collapsed to the first occurrence. "
                           "Everything keys on the identifier, including the interface, so two "
                           "claims sharing one is a defect that reaches the screen."),
            (("associations, dropped_associations", "has_retrieval="), "ATT&CK associations naming a technique that was not in the retrieved "
                            "context are dropped. An association the model produced rather than "
                            "read is the MITRE equivalent of a quotation that is in no source, "
                            "and it is treated the same way."),
            (("\"involved_parties\": [", "\"gaps\": ["), "Parties, timeline entries, impacts and gaps are trimmed to point only "
                            "at claims that still exist."),
            (("\"grounding\": grounding_report(", "claims_dropped=len("), "The grounding report is built last, from what was written and what "
                            "survived."),
        ],
    )
    ch.plain("4.7.3 The grounding report", bold=True)
    ch.body(
        "The grounding report is the numeric summary of that binding. It is attached to the trace "
        "and stored with it, so every analysis carries a record of how well it was supported."
    )
    ch.body(
        "One distinction in it is deliberate and easy to get wrong. A citation that was dropped is "
        "counted twice over: once as dropped, and once as either a loose quotation of wording "
        "that is genuinely in the source, or wording that is in no source at all. Reporting those "
        "together would place a model that quotes sloppily and a model that invents a quotation "
        "at the same number, and they are not the same failure."
    )
    ch.code_figure(
        source_of(VALIDATION, "grounding_report"),
        "Counting what survived the binding, and what quietly did not",
        [
            (("def grounding_report(", "claims_dropped: int = 0"), "The signature takes what was written and what was kept, which is what "
                           "makes the difference between them measurable."),
            (("claimed = all_citations", "survived = {"), "Claimed citations, and the set that survived."),
            (("for citation in claimed", "if find_aligned_quote"), "Each dropped citation is classified. A quotation that had to be "
                            "repaired to be found is already counted as verified, so it is "
                            "skipped here; without that check the same citation would be counted "
                            "both as verified and as unfound."),
            (("looks_like_a_paraphrase", "unfound += 1"), "A near-match of wording that is in the source counts as paraphrased; "
                            "anything else counts as unfound."),
            (("return CaseGroundingReport", "sources_total="), "The report itself. sources_cited against sources_total is the number "
                            "that exposes an analysis which reached a clean grounding score by "
                            "using less of the case."),
        ],
    )
