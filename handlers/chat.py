import logging

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select

from config import REPORTS_FOR_BAN
from constants import MENU_BUTTONS
from database.db import (
    SessionLocal,
    add_report,
    block_user,
    end_chat,
    get_user,
    get_waiting_user,
    has_reported,
    increment_reports,
    match_partners,
    start_searching,
)
from database.models import User
from handlers.chat_helpers import (
    notify_admins,
    notify_chat_ended,
    notify_chat_match,
    notify_searching,
)
from keyboards.menu import main_menu
from services.anti_spam import is_spam

logger = logging.getLogger(__name__)

router = Router()


async def get_partner(message: Message) -> int | None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            return None

        return user.partner_id


async def _forward(message: Message, send) -> None:
    if is_spam(message.from_user.id):
        await message.answer("⏳ زیاد سریع پیام می‌فرستی. چند ثانیه صبر کن.")
        return

    partner_id = await get_partner(message)
    if not partner_id:
        return

    try:
        await send(partner_id)
    except Exception:
        await message.answer("❌ ارسال پیام ناموفق بود.")


@router.message(F.text == "❌ پایان چت")
async def stop_chat(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer("❌ شما داخل چتی نیستید.")
            return

        partner_id = user.partner_id

        await end_chat(user.telegram_id)
        await end_chat(partner_id)

        await notify_chat_ended(message)

        try:
            await message.bot.send_message(
                partner_id,
                "❌ طرف مقابل چت را پایان داد.",
                reply_markup=main_menu,
            )
        except Exception as e:
            logger.warning("Failed to notify partner %s: %s", partner_id, e)


@router.message(F.text == "🔄 مخاطب جدید")
async def new_partner(message: Message):
    user_id = message.from_user.id

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()

        if user and user.partner_id:
            partner_id = user.partner_id

            await end_chat(user_id)
            await end_chat(partner_id)

            try:
                await message.bot.send_message(
                    partner_id,
                    "❌ طرف مقابل چت را ترک کرد.",
                    reply_markup=main_menu,
                )
            except Exception as e:
                logger.warning("Failed to notify partner %s: %s", partner_id, e)

    waiting_user = await get_waiting_user(user_id)

    if waiting_user:
        matched = await match_partners(user_id, waiting_user.telegram_id)
        if matched:
            await notify_chat_match(message.bot, user_id, waiting_user.telegram_id)
            return

    await start_searching(user_id, None)
    await notify_searching(message, "🔎 در حال جستجوی مخاطب جدید...")


@router.message(F.text == "👤 مشاهده مشخصات مخاطب")
async def show_partner_profile(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer("❌ شما داخل چتی نیستید.")
            return

        result = await session.execute(
            select(User).where(User.telegram_id == user.partner_id)
        )
        partner = result.scalar_one_or_none()

        if not partner:
            await message.answer("❌ اطلاعات مخاطب پیدا نشد.")
            return

        vip = " 💎" if partner.vip else ""
        text = (
            f"👤 مشخصات مخاطب{vip}\n\n"
            f"🎂 سن: {partner.age or 'ثبت نشده'}\n"
            f"🚻 جنسیت: {partner.gender or 'ثبت نشده'}\n"
            f"🌍 کشور: {partner.country or 'ثبت نشده'}\n"
            f"📝 بیو:\n{partner.bio or 'ثبت نشده'}"
        )

        await message.answer(text)


@router.message(F.text == "🚫 بلاک کاربر")
async def block_partner(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer("❌ شما داخل چتی نیستید.")
            return

        partner_id = user.partner_id

        await block_user(user.telegram_id, partner_id)
        await end_chat(user.telegram_id)
        await end_chat(partner_id)

        await notify_chat_ended(message, "🚫 کاربر بلاک شد و چت پایان یافت.")

        try:
            await message.bot.send_message(
                partner_id,
                "❌ طرف مقابل چت را پایان داد.",
                reply_markup=main_menu,
            )
        except Exception as e:
            logger.warning("Failed to notify partner %s: %s", partner_id, e)


@router.message(F.text == "📢 گزارش کاربر")
async def report_user(message: Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if not user or not user.partner_id:
            await message.answer("❌ شما داخل چتی نیستید.")
            return

        partner_id = user.partner_id

        result = await session.execute(
            select(User).where(User.telegram_id == partner_id)
        )
        partner = result.scalar_one_or_none()

        if not partner:
            await message.answer("❌ کاربر پیدا نشد.")
            return

    if await has_reported(message.from_user.id, partner_id):
        await message.answer("⚠️ شما قبلاً این کاربر را گزارش کرده‌اید.")
        return

    await add_report(message.from_user.id, partner_id)
    reports = await increment_reports(partner_id)

    await message.answer("✅ گزارش شما ثبت شد.")

    await notify_admins(
        message.bot,
        f"📢 گزارش جدید\n\n"
        f"گزارش‌دهنده: {message.from_user.id}\n"
        f"گزارش‌شونده: {partner_id}\n"
        f"تعداد گزارش: {reports}/{REPORTS_FOR_BAN}\n"
        f"{'🚫 خودکار ban شد' if reports >= REPORTS_FOR_BAN else ''}",
    )


@router.message(F.photo)
async def send_photo(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_photo(
            pid,
            message.photo[-1].file_id,
            caption=message.caption,
        ),
    )


@router.message(F.voice)
async def send_voice(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_voice(pid, message.voice.file_id),
    )


@router.message(F.video)
async def send_video(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_video(
            pid,
            message.video.file_id,
            caption=message.caption,
        ),
    )


@router.message(F.video_note)
async def send_video_note(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_video_note(pid, message.video_note.file_id),
    )


@router.message(F.audio)
async def send_audio(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_audio(
            pid,
            message.audio.file_id,
            caption=message.caption,
        ),
    )


@router.message(F.sticker)
async def send_sticker(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_sticker(pid, message.sticker.file_id),
    )


@router.message(F.animation)
async def send_animation(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_animation(
            pid,
            message.animation.file_id,
            caption=message.caption,
        ),
    )


@router.message(F.document)
async def send_document(message: Message):
    await _forward(
        message,
        lambda pid: message.bot.send_document(
            pid,
            message.document.file_id,
            caption=message.caption,
        ),
    )


@router.message(F.text)
async def anonymous_chat(message: Message):
    if message.text in MENU_BUTTONS:
        return

    if message.text.startswith("/"):
        return

    if is_spam(message.from_user.id):
        await message.answer("⏳ زیاد سریع پیام می‌فرستی. چند ثانیه صبر کن.")
        return

    partner_id = await get_partner(message)

    if not partner_id:
        user = await get_user(message.from_user.id)
        if user and user.is_searching:
            await message.answer(
                "🔎 در حال جستجو هستید. لطفاً صبر کنید یا «⏹ لغو جستجو» بزنید."
            )
        elif user and user.room_id:
            await message.answer(
                "👥 در اتاق گروهی هستید — پیامتان برای اعضا ارسال می‌شود."
            )
        return

    try:
        await message.bot.send_message(partner_id, message.text)
    except Exception:
        await message.answer("❌ ارسال پیام ناموفق بود.")
