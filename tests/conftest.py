import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from database.models import Base, User


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest.fixture
def make_user():
    """Factory to create User instances with sensible defaults."""

    def _make(
        telegram_id=1000,
        username="testuser",
        age=None,
        gender=None,
        search_gender=None,
        country=None,
        bio=None,
        coins=0,
        vip=False,
        banned=False,
        reports=0,
        is_searching=False,
        partner_id=None,
    ):
        user = User(
            telegram_id=telegram_id,
            username=username,
            age=age,
            gender=gender,
            search_gender=search_gender,
            country=country,
            bio=bio,
            coins=coins,
            vip=vip,
            banned=banned,
            reports=reports,
            is_searching=is_searching,
            partner_id=partner_id,
        )
        return user

    return _make


@pytest.fixture
def mock_message():
    """Create a mock aiogram Message object."""
    message = AsyncMock()
    message.from_user = MagicMock()
    message.from_user.id = 12345
    message.from_user.username = "testuser"
    message.answer = AsyncMock()
    message.bot = AsyncMock()
    return message
