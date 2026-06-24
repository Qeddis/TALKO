from aiogram import Router, F
from aiogram.types import Message

from database.db import (
    SessionLocal,
    get_waiting_user,
    set_partner,
)
from database.models import User
from sqlalchemy import select

router = Router()


@router.message(F.text == "🔍 پیدا کردن مخاطب")
async def find_partner(message: Message):
    user_id = message.from_user.id

    waiting_user = await get_waiting_user()

    if waiting_user and waiting_user.telegram_id != user_id:
        await set_partner(user_id, waiting_user.telegram_id)
        await set_partner(waiting_user.telegram_id, user_id)

        await message.answer("✅ مخاطب پیدا شد. چت را شروع کنید.")
        await message.bot.send_message(
            waiting_user.telegram_id,
            "✅ مخاطب پیدا شد. چت را شروع کنید."
        )
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one()

        user.is_searching = True
        await session.commit()

    await message.answer("🔎 در حال جستجوی مخاطب...")