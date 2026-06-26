import logging

from aiogram import Bot
from aiogram.types import Message

from config import ADMIN_IDS
from keyboards.menu import main_menu
from keyboards.more_menu import more_menu
from keyboards.search_menu import search_menu

logger = logging.getLogger(__name__)


async def notify_chat_match(
    bot: Bot,
    user_a: int,
    user_b: int,
    text: str = "✅ مخاطب پیدا شد. چت را شروع کنید.",
) -> None:
    for uid in (user_a, user_b):
        try:
            await bot.send_message(uid, text, reply_markup=more_menu)
        except Exception:
            logger.exception("Failed to notify user %s about chat match", uid)


async def notify_chat_ended(message: Message, text: str = "❌ چت پایان یافت.") -> None:
    await message.answer(text, reply_markup=main_menu)


async def notify_searching(message: Message, text: str) -> None:
    await message.answer(text, reply_markup=search_menu)


async def notify_admins(bot: Bot, text: str) -> None:
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            logger.exception("Failed to notify admin %s", admin_id)
