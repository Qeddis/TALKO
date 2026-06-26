from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import REPORTS_FOR_BAN
from database.models import Base, BlockedUser, Report, User

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/bot.db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_user(telegram_id: int) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def add_user(telegram_id: int, username: str | None) -> User:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            if username and user.username != username:
                user.username = username
                await session.commit()
            return user

        user = User(telegram_id=telegram_id, username=username)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


async def is_blocked(user_id: int, other_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(BlockedUser).where(
                ((BlockedUser.user_id == user_id) & (BlockedUser.blocked_id == other_id))
                | ((BlockedUser.user_id == other_id) & (BlockedUser.blocked_id == user_id))
            )
        )
        return result.scalar_one_or_none() is not None


async def block_user(user_id: int, blocked_id: int) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(BlockedUser).where(
                BlockedUser.user_id == user_id,
                BlockedUser.blocked_id == blocked_id,
            )
        )
        if result.scalar_one_or_none():
            return

        session.add(BlockedUser(user_id=user_id, blocked_id=blocked_id))
        await session.commit()


def _gender_compatible(searcher: User, candidate: User) -> bool:
    if candidate.banned:
        return False

    if searcher.search_gender:
        if candidate.gender != searcher.search_gender:
            return False
    if candidate.search_gender:
        if not searcher.gender or searcher.gender != candidate.search_gender:
            return False

    return True


def _sort_candidates(candidates: list[User]) -> list[User]:
    return sorted(candidates, key=lambda c: not c.vip)


async def _find_waiting_user(searcher: User) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.is_searching == True,
                User.partner_id == None,
                User.telegram_id != searcher.telegram_id,
                User.banned == False,
            )
        )
        candidates = list(result.scalars().all())

    compatible = []
    for candidate in candidates:
        if await is_blocked(searcher.telegram_id, candidate.telegram_id):
            continue
        if _gender_compatible(searcher, candidate):
            compatible.append(candidate)

    for candidate in _sort_candidates(compatible):
        return candidate

    return None


async def get_waiting_user(my_id: int) -> User | None:
    searcher = await get_user(my_id)
    if not searcher:
        return None
    return await _find_waiting_user(searcher)


async def get_waiting_user_by_gender(
    target_gender: str,
    my_id: int,
) -> User | None:
    searcher = await get_user(my_id)
    if not searcher:
        return None

    searcher.search_gender = target_gender
    return await _find_waiting_user(searcher)


async def match_partners(user_id: int, partner_id: int) -> bool:
    """Atomically set two users as partners. Returns False if either is unavailable."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        result = await session.execute(
            select(User).where(User.telegram_id == partner_id)
        )
        partner = result.scalar_one_or_none()

        if not user or not partner:
            return False
        if partner.partner_id or not partner.is_searching:
            return False

        user.partner_id = partner_id
        user.is_searching = False
        user.search_gender = None

        partner.partner_id = user_id
        partner.is_searching = False
        partner.search_gender = None

        await session.commit()
        return True


async def set_partner(user_id: int, partner_id: int) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.partner_id = partner_id
            user.is_searching = False
            user.search_gender = None
            await session.commit()


async def end_chat(user_id: int) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.partner_id = None
            user.is_searching = False
            user.search_gender = None
            await session.commit()


async def start_searching(user_id: int, search_gender: str | None = None) -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user:
            user.is_searching = True
            user.search_gender = search_gender
            user.partner_id = None
            await session.commit()


async def cancel_search(user_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.is_searching or user.partner_id:
            return False

        user.is_searching = False
        user.search_gender = None
        await session.commit()
        return True


async def get_stats() -> dict[str, int]:
    async with SessionLocal() as session:
        total = await session.scalar(select(func.count()).select_from(User)) or 0
        searching = await session.scalar(
            select(func.count()).select_from(User).where(
                User.is_searching == True,
                User.partner_id == None,
            )
        ) or 0
        in_chat = await session.scalar(
            select(func.count()).select_from(User).where(User.partner_id != None)
        ) or 0
        banned = await session.scalar(
            select(func.count()).select_from(User).where(User.banned == True)
        ) or 0
        vip = await session.scalar(
            select(func.count()).select_from(User).where(User.vip == True)
        ) or 0

    return {
        "total": total,
        "searching": searching,
        "in_chat": in_chat // 2,
        "banned": banned,
        "vip": vip,
    }


async def set_banned(telegram_id: int, banned: bool) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.banned = banned
        if banned:
            user.is_searching = False
            user.partner_id = None
        await session.commit()
        return True


async def set_vip(telegram_id: int, vip: bool = True) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.vip = vip
        await session.commit()
        return True


async def add_coins(telegram_id: int, amount: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.coins = max(0, user.coins + amount)
        await session.commit()
        return True


async def has_reported(reporter_id: int, reported_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(Report).where(
                Report.reporter_id == reporter_id,
                Report.reported_id == reported_id,
            )
        )
        return result.scalar_one_or_none() is not None


async def add_report(reporter_id: int, reported_id: int) -> None:
    async with SessionLocal() as session:
        session.add(Report(reporter_id=reporter_id, reported_id=reported_id))
        await session.commit()


async def increment_reports(telegram_id: int) -> int:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return 0

        user.reports += 1
        if user.reports >= REPORTS_FOR_BAN:
            user.banned = True
            user.is_searching = False
            if user.partner_id:
                partner_result = await session.execute(
                    select(User).where(User.telegram_id == user.partner_id)
                )
                partner = partner_result.scalar_one_or_none()
                if partner:
                    partner.partner_id = None
            user.partner_id = None

        await session.commit()
        return user.reports


async def get_all_telegram_ids() -> list[int]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User.telegram_id).where(User.banned == False)
        )
        return list(result.scalars().all())
