# Adaptive Case Gap Clarification with LangChain and LangGraph

Status: implementation plan and current design record. Date: 2026-09-17.

## Goal

The first redesigned workflow is adaptive clarification of a validated Main Analysis gap. Main Analysis uses LangChain structured output. LangGraph owns only the paused, multi-turn clarification workflow. Ordinary Case Q&A remains a later feature and is not the source of Case evidence.

The existing Case domain stays authoritative. PostgreSQL owns Case, CaseSource, evidence_revision, ChatMessage, CaseAnalysisResult, CaseRun, document provenance, and MITRE augmentation metadata. LangGraph checkpoints only workflow position and explicit clarification state. No model call has database or SQL tools.

Ordinary Ask can receive an empty canonical source bundle and use LangChain to ask for missing Case context. Main Analysis and formal Gap clarification continue to require persisted Case evidence.

## Production flow

```text
CaseRun
  -> request_case_analysis
  -> LangChain ChatModel.with_structured_output(CaseProviderAnalysis)
  -> CyberCase exact-quote, claim/source, gap, and MITRE validation
  -> CaseAnalysisResult
  -> deterministic eligible-gap selection
  -> LangGraph select_question
  -> ChatMessage(followup_question)
  -> interrupt and HTTP response
  -> API resume with the question/session identifier
  -> LangChain GapAnswerInterpretation
  -> optional CaseSource(followup_answer) and evidence_revision increment
  -> gap evaluation
  -> another adaptive question or terminal state
  -> one fresh CaseRun only after a completed factual clarification
```

Main Analysis is deliberately not a graph. It loads current sources, optionally loads MITRE technical context, invokes one structured LangChain stage, validates the result, and persists it. Clarification is the stateful part and therefore uses LangGraph interrupt/resume.

## LangChain boundary

`backend/app/services/case_analysis/provider_stage.py` keeps `request_stage` as the caller boundary while production calls construct `ChatOpenAI` for OpenRouter or `ChatAnthropic` for Anthropic. `ChatPromptTemplate`, bounded conversation messages, `.with_structured_output(schema)`, and `ainvoke()` replace production transport parsing. An explicit HTTP client remains only as an injected fixture seam for deterministic legacy transport tests; normal CaseRun and clarification calls pass no client and therefore use LangChain.

`CaseProviderAnalysis` still goes through the existing heavy CyberCase validators. LangChain does not replace exact quote validation, source binding, gap reference validation, correction handling, or MITRE isolation. Question-answer output uses the bounded `CaseQuestionAnswerResponse` contract and does not create an analysis trace.

`backend/app/services/case_materials/case_source_bundle.py` is the canonical source serializer for Main Analysis and later clarification stages. It keeps actual CaseSource identifiers, source text, document quality metadata, and bounded follow-up provenance together. Conversation history is reference context only.

## Graph state and nodes

`GapClarificationState` contains explicit application-visible workflow data: `case_id`, `graph_thread_id`, `source_analysis_id`, `source_evidence_revision`, response language and pipeline config, selected `gap`, `questions_asked`, `answers_received`, pending question/message/target, latest answer and interpretation, attempt count, resolution status, newly committed source IDs, and the last structured decision. It contains no hidden reasoning and no authoritative evidence copy.

The graph in `backend/app/services/gap_clarification/graph.py` has these nodes:

```text
START -> select_question -> persist_question -> ask_user
       -> interrupt/resume -> interpret_answer -> commit_answer
       -> evaluate_gap -> select_question or END
```

`select_gap` is deterministic: askable gaps are eligible, higher priority is selected first, claim-linked gaps win ties, and explicitly unknown gaps are excluded. `GapNextStep` allows `ask`, `resolved`, `explicitly_unknown`, or `not_productive`; an equivalent normalized question immediately terminates the session instead of looping.

`ask_user` persists the question first, then calls LangGraph `interrupt` with the Case, clarification session, question message, question text, and attempt. The HTTP request returns after the interrupt. A later submission resumes the same checkpoint thread with `Command(resume=...)`.

`GapAnswerInterpretation` classifies `case_fact`, `scope_clarification`, `explicitly_unknown`, `skip`, or `unrelated`. Only a concrete `case_fact` with a normalized fact may create a normal CaseSource. Scope clarification, unknown, skip, and unrelated responses remain ChatMessage/workflow state.

The default maximum is three questions per selected gap. The graph also ends when the gap is resolved, the user does not know, the user skips, no productive question remains, or the active evidence revision becomes stale.

## Persistence and concurrency

`backend/app/services/gap_clarification/persistence.py` locks the Case before writing a question, answer, or source. Questions and answers are ordinary ChatMessage rows with bounded `chat_followup` metadata. Factual answers use `CaseSource(source_kind="followup_answer")`, preserve the raw user answer as authoritative `exact_text`, record the selected gap/question/session provenance, deduplicate by normalized answer fingerprint, and increment `Case.evidence_revision` once.

`backend/app/services/gap_clarification/checkpoint.py` opens `AsyncPostgresSaver` using `LANGGRAPH_CHECKPOINT_DATABASE_URL`, then `DATABASE_URL`, then the configured PostgreSQL components. It runs the checkpointer migrations once per process and uses a deterministic session UUID as `thread_id`. LangGraph checkpoint tables may share the PostgreSQL server with CyberCase tables, but they are not a second Case truth store.

Resume verifies Case ownership, question ownership, gap/session identity, idempotency payload, and the persisted source revision before invoking the graph. A changed revision returns `clarification_stale`; it is never silently reconciled. A second request with the same idempotency key returns the existing answer, while a different key cannot answer an already answered question.

When a session ends after a factual answer, `enqueue_completion_analysis` creates at most one idempotent fresh CaseRun for the new evidence revision. Intermediate adaptive answers do not trigger re-analysis.

## API and UI minimum

The existing Case chat endpoint accepts `intent=followup_answer`, the target question ID, the gap ID, optional clarification session ID, and disposition `answered`, `unavailable`, or `skipped`. The response can include the persisted answer, an adaptive next question, and a fresh analysis run.

The existing Case workspace displays the current formal clarification question, keeps pending questions after refresh from ChatMessage state, supports an answer, “I don’t have this information”, and “Skip clarification”, and renders an adaptive next question without redesigning ordinary Ask chat.

## Legacy boundary

The old `case_answer.py` claims-only Q&A adapter was removed after production callers were redirected to the shared CaseSource reasoning boundary. The old single-turn follow-up submission path was removed after the graph path passed its focused and full suites. The existing read-only `/followups` history surface and deterministic helper contracts remain because they represent current API/history behavior. The old completion-time automatic question creation was removed; questions now originate from the graph after validated analysis.

## Dependencies and validation

Backend requirements now declare `langchain-core`, `langchain-openai`, `langchain-anthropic`, `langgraph`, `langgraph-checkpoint-postgres`, and `psycopg[binary,pool]`. Docker exposes `LANGGRAPH_CHECKPOINT_DATABASE_URL` while retaining existing PostgreSQL settings.

Focused graph tests cover interrupt/resume, adaptive question changes, duplicate-question termination, and structured contract validation. PostgreSQL tests cover the real CaseRun-to-graph-to-CaseSource-to-reanalysis path, bounded provenance, and empty-Case Chat clarification. Existing exact quote, MITRE, source persistence, recovery, and shared Q&A tests remain in the suite. Final validation passed with 192 backend tests, 107 frontend unit tests, API type checking, lint with one pre-existing warning, and three Playwright E2E tests.

