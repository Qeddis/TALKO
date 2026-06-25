from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from database.models import Base, User

BASE_DIR = Path(__file__).resolve().parent.parent
(BASE_DIR / "data").mkdir(exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/bot.db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_user(telegram_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def add_user(telegram_id: int, username: str | None):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )

        user = result.scalar_one_or_none()

        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user


async def get_waiting_user():
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.is_searching == True,
                User.partner_id == None
            )
        )
        return result.scalar_one_or_none()


async def set_partner(user_id, partner_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.partner_id = partner_id
            user.is_searching = False
            await session.commit()


async def end_chat(user_id):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.partner_id = None
            user.is_searching = False
            await session.commit()

async def get_waiting_user_by_gender(gender: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.is_searching == True,
                User.gender == gender,
                User.partner_id == None
            )
        )
        return result.scalars().first()