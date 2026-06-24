from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from database.db import (
    SessionLocal,
    end_chat,
    get_waiting_user,
    set_partner,
)
from database.models import User

router = Router()


@router.message(F.text == "❌ پایان چت")
async def stop_chat(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer("❌ شما داخل چتی نیستید.")
            return

        partner_id = user.partner_id

        await end_chat(user.telegram_id)
        await end_chat(partner_id)

        await message.answer("❌ چت پایان یافت.")

        await message.bot.send_message(
            partner_id,
            "❌ طرف مقابل چت را پایان داد."
        )


@router.message(F.text == "🔄 مخاطب جدید")
async def new_partner(message: Message):
    user_id = message.from_user.id

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == user_id
            )
        )
        user = result.scalar_one_or_none()

        if user and user.partner_id:
            partner_id = user.partner_id

            await end_chat(user_id)
            await end_chat(partner_id)

            await message.bot.send_message(
                partner_id,
                "❌ طرف مقابل چت را ترک کرد."
            )

    waiting_user = await get_waiting_user()

    if waiting_user and waiting_user.telegram_id != user_id:
        await set_partner(user_id, waiting_user.telegram_id)
        await set_partner(waiting_user.telegram_id, user_id)

        await message.answer("✅ مخاطب جدید پیدا شد.")

        await message.bot.send_message(
            waiting_user.telegram_id,
            "✅ مخاطب جدید پیدا شد."
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

    await message.answer("🔎 در حال جستجوی مخاطب جدید...")


MENU_BUTTONS = {
    "👤 پروفایل",
    "👤 مشاهده مشخصات",
    "👦 چت با پسر",
    "👧 چت با دختر",
    "💎 VIP",
    "⚙️ تنظیمات",
    "🔍 پیدا کردن مخاطب",
    "🔄 مخاطب جدید",
    "❌ پایان چت",
}


@router.message(F.text)
async def anonymous_chat(message: Message):
    # دکمه‌های منو را رد کن
    if message.text in MENU_BUTTONS:
        return

    # دستورات /age و /bio و ... را رد کن
    if message.text.startswith("/"):
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        # اگر داخل چت نیست، کاری نکن
        if not user or not user.partner_id:
            return

        # ارسال پیام به طرف مقابل
        await message.bot.send_message(
            user.partner_id,
            message.text
        )

        @router.message(F.text == "👤 مشاهده مشخصات")
async def show_partner_profile(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer("❌ شما داخل چتی نیستید.")
            return

        result = await session.execute(
            select(User).where(
                User.telegram_id == user.partner_id
            )
        )
        partner = result.scalar_one_or_none()

        if not partner:
            await message.answer("❌ اطلاعات مخاطب پیدا نشد.")
            return

        text = (
            f"👤 مشخصات مخاطب\n\n"
            f"🎂 سن: {partner.age or 'ثبت نشده'}\n"
            f"🚻 جنسیت: {partner.gender or 'ثبت نشده'}\n"
            f"🌍 کشور: {partner.country or 'ثبت نشده'}\n"
            f"📝 بیو:\n{partner.bio or 'ثبت نشده'}"
        )

        await message.answer(text)