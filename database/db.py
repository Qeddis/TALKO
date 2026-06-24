from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/data/bot.db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)