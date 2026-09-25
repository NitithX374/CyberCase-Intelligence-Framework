from __future__ import annotations

import pytest
from isolated_database import isolated_database
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.errors import AppError
from app.schemas.auth import RegisterRequest
from app.services.auth.auth_service import register_user

pytestmark = pytest.mark.asyncio


def registration(email: str) -> RegisterRequest:
    return RegisterRequest(email=email, name="Analyst", password="correct horse")


async def test_a_taken_email_is_refused_as_an_existing_account():
    async with isolated_database() as session_factory:
        async with session_factory() as db:
            await register_user(db, registration("analyst@example.com"))

        async with session_factory() as db:
            with pytest.raises(AppError) as refusal:
                await register_user(db, registration("Analyst@Example.com"))

        assert (refusal.value.code, refusal.value.status_code) == ("account_exists", 409)


async def test_a_column_the_model_does_not_fill_is_not_reported_as_an_existing_account():
    async with isolated_database() as session_factory:
        async with session_factory() as db, db.begin():
            await db.execute(
                text("ALTER TABLE users ADD COLUMN oauth_subject_id varchar(255) NOT NULL")
            )

        async with session_factory() as db:
            with pytest.raises(IntegrityError) as failure:
                await register_user(db, registration("analyst@example.com"))

        assert failure.value.orig.sqlstate == "23502"
