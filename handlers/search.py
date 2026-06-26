from aiogram import Router, F
from aiogram.types import Message

from database.db import (
    cancel_search,
    get_user,
    get_waiting_user,
    match_partners,
    start_searching,
)
from handlers.chat_helpers import notify_chat_match, notify_searching
from keyboards.menu import main_menu

router = Router()


async def _begin_random_search(message: Message) -> None:
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        return

    if user.partner_id:
        await message.answer("❌ اول چت فعلی را پایان دهید.")
        return

    if user.room_id:
        await message.answer("❌ اول از اتاق گروهی خارج شوید.")
        return

    if user.is_searching:
        await message.answer("🔎 همین الان در صف جستجو هستید.")
        return

    await start_searching(user_id, None)

    waiting_user = await get_waiting_user(user_id)

    if waiting_user:
        matched = await match_partners(user_id, waiting_user.telegram_id)
        if matched:
            await notify_chat_match(message.bot, user_id, waiting_user.telegram_id)
            return

    await notify_searching(message, "🔎 در حال جستجوی مخاطب...")


@router.message(F.text == "🌍 چت تصادفی")
async def find_partner(message: Message):
    await _begin_random_search(message)


@router.message(F.text == "⏹ لغو جستجو")
async def cancel_search_handler(message: Message):
    if await cancel_search(message.from_user.id):
        await message.answer("✅ جستجو لغو شد.", reply_markup=main_menu)
        return

    user = await get_user(message.from_user.id)
    if user and user.partner_id:
        await message.answer("❌ برای لغو، از «پایان چت» استفاده کنید.")
        return

    await message.answer("❌ در حال جستجو نیستید.", reply_markup=main_menu)
