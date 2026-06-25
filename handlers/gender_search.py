from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.db import (
    SessionLocal,
    get_waiting_user_by_gender,
    set_partner,
)
from database.models import User

router = Router()


@router.message(F.text == "👦 چت با پسر")
async def search_boy(message: Message):
    await start_search(message, "پسر")


@router.message(F.text == "👧 چت با دختر")
async def search_girl(message: Message):
    await start_search(message, "دختر")


async def start_search(message: Message, gender: str):
    user_id = message.from_user.id

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == user_id
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        user.search_gender = gender
        await session.commit()

    waiting_user = await get_waiting_user_by_gender(
    gender,
    user_id
)

    if waiting_user and waiting_user.telegram_id != user_id:
        await set_partner(
            user_id,
            waiting_user.telegram_id
        )

        await set_partner(
            waiting_user.telegram_id,
            user_id
        )

        await message.answer("✅ مخاطب پیدا شد.")

        await message.bot.send_message(
            waiting_user.telegram_id,
            "✅ مخاطب پیدا شد."
        )

        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if user:
            user.is_searching = True
            await session.commit()

    await message.answer(
        f"🔎 در حال جستجوی {gender}..."
    )