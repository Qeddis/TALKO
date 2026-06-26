from aiogram.types import Message

from database.db import (
    get_user,
    get_waiting_user,
    get_waiting_user_by_gender,
    match_partners,
    start_searching,
)
from handlers.chat_helpers import notify_chat_match, notify_searching


async def try_match_or_search(
    message: Message,
    search_gender: str | None = None,
    require_gender_set: bool = False,
) -> None:
    user_id = message.from_user.id
    user = await get_user(user_id)

    if not user:
        return

    if user.partner_id:
        await message.answer("❌ اول چت فعلی را پایان دهید.")
        return

    if user.is_searching:
        await message.answer("🔎 همین الان در صف جستجو هستید.")
        return

    if require_gender_set and not user.gender:
        await message.answer(
            "❌ برای جستجوی جنسیتی، اول جنسیت خود را در پروفایل ثبت کنید."
        )
        return

    if search_gender:
        waiting_user = await get_waiting_user_by_gender(search_gender, user_id)
    else:
        waiting_user = await get_waiting_user(user_id)

    if waiting_user:
        matched = await match_partners(user_id, waiting_user.telegram_id)
        if matched:
            await notify_chat_match(message.bot, user_id, waiting_user.telegram_id)
            return

    await start_searching(user_id, search_gender)
    if search_gender:
        search_text = f"🔎 در حال جستجوی {search_gender}..."
    else:
        search_text = "🔎 در حال جستجوی مخاطب..."
    await notify_searching(message, search_text)
