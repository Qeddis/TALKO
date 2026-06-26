from aiogram import Router, F
from aiogram.types import Message

from database.db import (
    get_user,
    get_waiting_user_by_gender,
    match_partners,
    start_searching,
)
from handlers.chat_helpers import notify_chat_match, notify_searching

router = Router()


@router.message(F.text == "👦 چت با پسر")
async def search_boy(message: Message):
    await start_search(message, "پسر")


@router.message(F.text == "👧 چت با دختر")
async def search_girl(message: Message):
    await start_search(message, "دختر")


async def start_search(message: Message, gender: str):
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

    if not user.gender:
        await message.answer(
            "❌ برای جستجوی جنسیتی، اول جنسیت خود را در پروفایل ثبت کنید."
        )
        return

    waiting_user = await get_waiting_user_by_gender(gender, user_id)

    if waiting_user:
        matched = await match_partners(user_id, waiting_user.telegram_id)
        if matched:
            await notify_chat_match(message.bot, user_id, waiting_user.telegram_id)
            return

    await start_searching(user_id, gender)
    await notify_searching(message, f"🔎 در حال جستجوی {gender}...")
