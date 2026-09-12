import asyncio
from uuid import uuid4

import pytest
from sqlalchemy import func, select

from app.models import Case, CaseAnalysisResult, CaseEvidenceSnapshot, CaseRun, ChatMessage, ChatThread
from app.models.caseMaterials import EvidenceSource
from app.schemas.caseRuns import CaseAnalysisCreate
from app.schemas.chat import ChatMessageCreate
from app.services.case_materials import CaseMaterialsService
from app.services.chat.caseChat import CaseChatError, createCaseChatMessageAndRun
from app.services.followup.caseClarification import get_owned_clarifications
from app.services.workflow.caseAskCompletion import completeCaseAsk
from app.services.workflow.caseRunClaim import claimCaseRun
from app.services.workflow.caseRunCompletion import complete_case_run
from app.services.workflow.caseRunService import enqueue_case_analysis
from run_recovery_support import isolated_database
from test_case_chat_postgres import _output


def test_explicit_clarification_intent_vs_normal_ask():
    async def exercise():
        async with isolated_database() as factory:
            case_id = uuid4()
            thread_id = uuid4()
            async with factory() as db, db.begin():
                case = Case(id=case_id, title="Clarification Intent Test")
                db.add(case)
                db.add(ChatThread(id=thread_id, case_id=case_id, title=case.title))
                source = await CaseMaterialsService(db).admitText(
                    case_id=case_id,
                    user_id=None,
                    source_kind="narrative",
                    exact_text="The witness reported a blue vehicle.",
                    provenance_json={"origin": "analyst-authored"},
                )
                source_id = source.id

            # Initial analysis enqueued & completed with a follow-up question
            async with factory() as db, db.begin():
                init_run = await enqueue_case_analysis(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=CaseAnalysisCreate(idempotency_key="init-run"),
                )
                init_run_id = init_run.id
            async with factory() as db:
                claimed = await claimCaseRun(db, init_run_id, "worker-init")
                snapshot = await db.get(CaseEvidenceSnapshot, claimed.snapshot_id)
            async with factory() as db:
                assert await complete_case_run(
                    db,
                    init_run_id,
                    claimed.attempt_count,
                    _output(snapshot, source_id, followup=True),
                )

            async with factory() as db:
                thread = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                assert thread.status == "awaiting_followup"
                followup_msg = await db.scalar(
                    select(ChatMessage).where(
                        ChatMessage.thread_id == thread.id,
                        ChatMessage.message_kind == "followup_question",
                    )
                )
                assert followup_msg is not None
                clarifications = await get_owned_clarifications(db, case_id)
                pending = next((c for c in clarifications if c.state == "pending"), None)
                assert pending is not None
                assert pending.id == followup_msg.id
                initial_evidence_count = await db.scalar(select(func.count()).select_from(EvidenceSource))
                assert initial_evidence_count == 1

            # 1. Ask normal Q&A while clarification is pending (intent="ask", default)
            ask_request = ChatMessageCreate(
                content="Is there any surveillance footage mentioned?",
                idempotency_key="qa-while-pending",
                intent="ask",
            )
            async with factory() as db, db.begin():
                ask_msg, ask_run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=ask_request,
                )
                assert ask_msg.role == "user"
                assert ask_msg.message_kind == "conversation"
                assert ask_run.operation == "ask"

            # Verify pending clarification is untouched and no new evidence admitted
            async with factory() as db:
                clarifications_after_ask = await get_owned_clarifications(db, case_id)
                pending_after_ask = next((c for c in clarifications_after_ask if c.id == pending.id), None)
                assert pending_after_ask is not None
                assert pending_after_ask.state == "pending"
                evidence_count_after_ask = await db.scalar(select(func.count()).select_from(EvidenceSource))
                assert evidence_count_after_ask == 1

            # Complete the ask run
            async with factory() as db:
                claimed_ask = await claimCaseRun(db, ask_run.id, "worker-ask")
                snapshot_ask = await db.get(CaseEvidenceSnapshot, claimed_ask.snapshot_id)
            async with factory() as db:
                assert await completeCaseAsk(
                    db,
                    ask_run.id,
                    claimed_ask.attempt_count,
                    _output(snapshot_ask, source_id, mode="question_answer"),
                )

            # Crucial check: thread status stays awaiting_followup because pending clarification remains!
            async with factory() as db:
                thread_after_ask = await db.scalar(select(ChatThread).where(ChatThread.case_id == case_id))
                assert thread_after_ask.status == "awaiting_followup"

            # 2. Attempt clarification_answer WITHOUT clarification_id -> 422
            missing_id_req = ChatMessageCreate(
                content="Toyota Camry",
                idempotency_key="clarif-no-id",
                intent="clarification_answer",
                clarification_id=None,
            )
            async with factory() as db, db.begin():
                with pytest.raises(CaseChatError) as exc_info:
                    await createCaseChatMessageAndRun(
                        db,
                        case_id=case_id,
                        user_id=None,
                        request=missing_id_req,
                    )
                assert exc_info.value.code == "clarification_id_required"
                assert exc_info.value.status_code == 422

            # 3. Attempt clarification_answer with wrong/non-existent clarification_id -> 404
            wrong_id_req = ChatMessageCreate(
                content="Toyota Camry",
                idempotency_key="clarif-wrong-id",
                intent="clarification_answer",
                clarification_id=uuid4(),
            )
            async with factory() as db, db.begin():
                with pytest.raises(CaseChatError) as exc_info:
                    await createCaseChatMessageAndRun(
                        db,
                        case_id=case_id,
                        user_id=None,
                        request=wrong_id_req,
                    )
                assert exc_info.value.code == "clarification_not_found"
                assert exc_info.value.status_code == 404

            # 4. Valid clarification_answer with explicit intent + clarification_id
            valid_clarif_req = ChatMessageCreate(
                content="It was a silver Toyota Camry.",
                idempotency_key="valid-clarif-1",
                intent="clarification_answer",
                clarification_id=pending.id,
            )
            async with factory() as db, db.begin():
                c_msg, c_run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=valid_clarif_req,
                )
                assert c_msg.message_kind == "followup_answer"
                assert c_msg.in_reply_to_message_id == pending.id
                assert c_run.operation == "analysis"

            # Verify clarification is now answered and new evidence source admitted
            async with factory() as db:
                clarifications_after_clarif = await get_owned_clarifications(db, case_id)
                answered_clarif = next((c for c in clarifications_after_clarif if c.id == pending.id), None)
                assert answered_clarif is not None
                assert answered_clarif.state == "answered"
                evidence_count_after_clarif = await db.scalar(select(func.count()).select_from(EvidenceSource))
                assert evidence_count_after_clarif == 2

            # 5. Idempotent replay of clarification answer
            async with factory() as db, db.begin():
                rep_msg, rep_run = await createCaseChatMessageAndRun(
                    db,
                    case_id=case_id,
                    user_id=None,
                    request=valid_clarif_req,
                )
                assert rep_msg.id == c_msg.id
                assert rep_run.id == c_run.id

    asyncio.run(exercise())
