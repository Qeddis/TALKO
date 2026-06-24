from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from database.models import Base, User
from sqlalchemy import select, update

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/bot.db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

BASE_DIR = Path(__file__).resolve().parent.parent
(BASE_DIR / "data").mkdir(exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/bot.db"


async def get_waiting_user():
    ...

async def set_partner(user_id, partner_id):
    ...

async def end_chat(user_id):
    ...

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)