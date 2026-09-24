import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

if settings.database_url:
    engine = create_async_engine(
        settings.async_database_url,
        echo=False,
        pool_pre_ping=True,
    )
else:
    engine = create_async_engine(
        "postgresql+asyncpg://",
        connect_args={
            "host": settings.postgres_host,
            "port": int(settings.postgres_port),
            "user": settings.postgres_user,
            "password": settings.postgres_password,
            "database": settings.postgres_db,
            "server_settings": {"application_name": "cybercase_backend"},
        },
        echo=False,
        pool_pre_ping=True,
    )


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def commit_dependency_transaction(session: AsyncSession) -> None:
    if session.in_transaction():
        await session.commit()
