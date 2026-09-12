"""Keep CaseRun request messages available for retained run lineage."""

from alembic import op
import sqlalchemy as sa


revision = "0003_case_run_request_no_action"
down_revision = "0002_drop_chat_status_and_context_result"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE chat_messages AS answer
            SET analysis_result_id = question.analysis_result_id
            FROM chat_messages AS question
            WHERE answer.analysis_result_id IS NULL
              AND answer.role = 'assistant'
              AND answer.message_kind = 'conversation'
              AND answer.in_reply_to_message_id = question.id
              AND question.role = 'user'
              AND question.message_kind = 'conversation'
              AND question.analysis_result_id IS NOT NULL
              AND question.thread_id = answer.thread_id
              AND EXISTS (
                  SELECT 1
                  FROM chat_threads AS thread
                  JOIN case_analysis_results AS result
                    ON result.id = question.analysis_result_id
                   AND result.case_id = thread.case_id
                  WHERE thread.id = answer.thread_id
              )
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE chat_messages AS answer
            SET analysis_result_id = question.analysis_result_id
            FROM chat_messages AS question
            WHERE answer.analysis_result_id IS NULL
              AND answer.role = 'user'
              AND answer.message_kind = 'followup_answer'
              AND answer.in_reply_to_message_id = question.id
              AND question.role = 'assistant'
              AND question.message_kind = 'followup_question'
              AND question.analysis_result_id IS NOT NULL
              AND question.thread_id = answer.thread_id
              AND EXISTS (
                  SELECT 1
                  FROM chat_threads AS thread
                  JOIN case_analysis_results AS result
                    ON result.id = question.analysis_result_id
                   AND result.case_id = thread.case_id
                  WHERE thread.id = answer.thread_id
              )
            """
        )
    )
    op.drop_constraint("fk_case_runs_request_message_id", "case_runs", type_="foreignkey")
    op.create_foreign_key(
        "fk_case_runs_request_message_id",
        "case_runs",
        "chat_messages",
        ["request_message_id"],
        ["id"],
        ondelete="NO ACTION",
        deferrable=False,
    )


def downgrade() -> None:
    op.drop_constraint("fk_case_runs_request_message_id", "case_runs", type_="foreignkey")
    op.create_foreign_key(
        "fk_case_runs_request_message_id",
        "case_runs",
        "chat_messages",
        ["request_message_id"],
        ["id"],
        ondelete="SET NULL",
        deferrable=False,
    )
