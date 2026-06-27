from dataclasses import dataclass

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config import (
    DATABASE_URL,
    REFERRAL_BONUS,
    REFERRAL_REWARD,
    REPORTS_FOR_BAN,
    STARTER_COINS,
    VIP_COIN_PRICE,
)
from database.models import Base, BlockedUser, ChatRoom, Report, User

_engine_kwargs: dict = {"echo": False}
if DATABASE_URL.startswith("postgresql"):
    _engine_kwargs["pool_pre_ping"] = True

engine = create_async_engine(DATABASE_URL, **_engine_kwargs)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@dataclass
class AddUserResult:
    user: User
    is_new: bool
    referrer_id: int | None = None


async def _migrate_schema() -> None:
    """Add columns missing from older databases."""
    is_sqlite = DATABASE_URL.startswith("sqlite")
    is_postgres = DATABASE_URL.startswith("postgresql")

    if not is_sqlite and not is_postgres:
        return

    async with engine.begin() as conn:
        if is_postgres:
            await conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS referred_by BIGINT"
                )
            )
        elif is_sqlite:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            columns = {row[1] for row in result.fetchall()}
            if "referred_by" not in columns:
                await conn.execute(
                    text("ALTER TABLE users ADD COLUMN referred_by BIGINT")
                )


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _migrate_schema()
    await seed_default_rooms()


async def seed_default_rooms() -> None:
    defaults = [
        ("🌐 اتاق عمومی", False),
        ("💎 اتاق VIP", True),
    ]
    async with SessionLocal() as session:
        for name, vip_only in defaults:
            result = await session.execute(
                select(ChatRoom).where(ChatRoom.name == name)
            )
            if result.scalar_one_or_none() is None:
                session.add(ChatRoom(name=name, vip_only=vip_only))
        await session.commit()


async def get_user(telegram_id: int) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()


async def add_user(
    telegram_id: int,
    username: str | None,
    referrer_id: int | None = None,
) -> AddUserResult:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            if username and user.username != username:
                user.username = username
                await session.commit()
            return AddUserResult(user=user, is_new=False)

        valid_referrer_id: int | None = None
        if referrer_id and referrer_id != telegram_id:
            ref_result = await session.execute(
                select(User).where(User.telegram_id == referrer_id)
            )
            referrer = ref_result.scalar_one_or_none()
            if referrer and not referrer.banned:
                valid_referrer_id = referrer_id

        starter = STARTER_COINS + (REFERRAL_BONUS if valid_referrer_id else 0)
        user = User(
            telegram_id=telegram_id,
            username=username,
            coins=starter,
            referred_by=valid_referrer_id,
        )
        session.add(user)

        if valid_referrer_id:
            ref_result = await session.execute(
                select(User).where(User.telegram_id == valid_referrer_id)
            )
            referrer = ref_result.scalar_one()
            referrer.coins += REFERRAL_REWARD

        await session.commit()
        await session.refresh(user)
        return AddUserResult(
            user=user,
            is_new=True,
            referrer_id=valid_referrer_id,
        )


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


def _gender_compatible(
    searcher: User,
    candidate: User,
    search_gender: str | None = None,
) -> bool:
    if candidate.banned:
        return False

    target = search_gender if search_gender is not None else searcher.search_gender

    if target:
        if candidate.gender != target:
            return False
    if candidate.search_gender:
        if not searcher.gender or searcher.gender != candidate.search_gender:
            return False

    return True


def _sort_candidates(candidates: list[User]) -> list[User]:
    return sorted(candidates, key=lambda c: not c.vip)


async def _find_waiting_user(
    searcher: User,
    search_gender: str | None = None,
) -> User | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.is_searching == True,
                User.partner_id == None,
                User.room_id == None,
                User.telegram_id != searcher.telegram_id,
                User.banned == False,
            )
        )
        candidates = list(result.scalars().all())

    compatible = []
    for candidate in candidates:
        if await is_blocked(searcher.telegram_id, candidate.telegram_id):
            continue
        if _gender_compatible(searcher, candidate, search_gender):
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
    return await _find_waiting_user(searcher, target_gender)


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
        if user.telegram_id == partner_id:
            return False
        if user.partner_id or partner.partner_id:
            return False
        if user.room_id or partner.room_id:
            return False
        if not partner.is_searching:
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
            user.room_id = None
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
        referrals = await session.scalar(
            select(func.count()).select_from(User).where(User.referred_by != None)
        ) or 0

    return {
        "total": total,
        "searching": searching,
        "in_chat": in_chat // 2,
        "banned": banned,
        "vip": vip,
        "referrals": referrals,
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
            user.room_id = None
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
            user.room_id = None
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


async def get_room_by_name(name: str) -> ChatRoom | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(ChatRoom).where(ChatRoom.name == name)
        )
        return result.scalar_one_or_none()


async def get_room_members(room_id: int) -> list[int]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User.telegram_id).where(
                User.room_id == room_id,
                User.banned == False,
            )
        )
        return list(result.scalars().all())


async def join_room(user_id: int, room_id: int) -> tuple[bool, str]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False, "no_user"

        result = await session.execute(
            select(ChatRoom).where(ChatRoom.id == room_id)
        )
        room = result.scalar_one_or_none()
        if not room:
            return False, "no_room"

        if room.vip_only and not user.vip:
            return False, "vip_required"

        if user.partner_id:
            return False, "in_private_chat"

        user.room_id = room_id
        user.is_searching = False
        user.search_gender = None
        await session.commit()
        return True, "ok"


async def leave_room(user_id: int) -> bool:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.room_id:
            return False

        user.room_id = None
        await session.commit()
        return True


async def purchase_vip_with_coins(telegram_id: int) -> tuple[bool, str]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False, "no_user"
        if user.vip:
            return False, "already_vip"
        if user.coins < VIP_COIN_PRICE:
            return False, "insufficient"

        user.coins -= VIP_COIN_PRICE
        user.vip = True
        await session.commit()
        return True, "ok"


async def activate_vip(telegram_id: int) -> tuple[bool, str]:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            return False, "no_user"
        if user.vip:
            return False, "already_vip"

        user.vip = True
        await session.commit()
        return True, "ok"


async def get_referral_count(telegram_id: int) -> int:
    async with SessionLocal() as session:
        return (
            await session.scalar(
                select(func.count())
                .select_from(User)
                .where(User.referred_by == telegram_id)
            )
            or 0
        )
