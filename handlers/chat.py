from aiogram import Router, F
from aiogram.types import Message

from database.db import SessionLocal
from database.models import User
from sqlalchemy import select

router = Router()


@router.message(F.text)
async def anonymous_chat(message: Message):
    if message.text.startswith("/"):
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            return

        await message.bot.send_message(
            user.partner_id,
            message.text
        )