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

MENU_BUTTONS = {
    "👤 پروفایل",
    "📄 مشاهده پروفایل",
    "✏️ ویرایش پروفایل",
    "👤 مشاهده مشخصات مخاطب",
    "👦 چت با پسر",
    "👧 چت با دختر",
    "🌍 چت تصادفی",
    "💎 VIP",
    "⚙️ بیشتر",
    "🔄 مخاطب جدید",
    "❌ پایان چت",
    "⬅️ بازگشت",
}


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


@router.message(F.text == "👤 مشاهده مشخصات مخاطب")
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


async def get_partner(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            return None

        return user.partner_id

@router.message(F.text == "📢 گزارش کاربر")
async def report_user(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == message.from_user.id
            )
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer(
                "❌ شما داخل چتی نیستید."
            )
            return

        result = await session.execute(
            select(User).where(
                User.telegram_id == user.partner_id
            )
        )
        partner = result.scalar_one_or_none()

        if not partner:
            await message.answer(
                "❌ کاربر پیدا نشد."
            )
            return

        partner.reports += 1
        await session.commit()

        await message.answer(
            "✅ گزارش شما ثبت شد."
        )

@router.message(F.photo)
async def send_photo(message: Message):
    partner_id = await get_partner(message)
    if not partner_id:
        return

    await message.bot.send_photo(
        partner_id,
        message.photo[-1].file_id,
        caption=message.caption
    )


@router.message(F.voice)
async def send_voice(message: Message):
    partner_id = await get_partner(message)
    if not partner_id:
        return

    await message.bot.send_voice(
        partner_id,
        message.voice.file_id
    )


@router.message(F.video)
async def send_video(message: Message):
    partner_id = await get_partner(message)
    if not partner_id:
        return

    await message.bot.send_video(
        partner_id,
        message.video.file_id,
        caption=message.caption
    )


@router.message(F.document)
async def send_document(message: Message):
    partner_id = await get_partner(message)
    if not partner_id:
        return

    await message.bot.send_document(
        partner_id,
        message.document.file_id,
        caption=message.caption
    )


@router.message(F.text)
async def anonymous_chat(message: Message):
    if message.text in MENU_BUTTONS:
        return

    if message.text.startswith("/"):
        return

    partner_id = await get_partner(message)

    if not partner_id:
        return

    await message.bot.send_message(
        partner_id,
        message.text
    )
    