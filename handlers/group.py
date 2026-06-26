import logging

from aiogram import F, Router
from aiogram.filters import BaseFilter
from aiogram.types import Message

from constants import MENU_BUTTONS
from database.db import (
    get_room_by_name,
    get_room_members,
    get_user,
    join_room,
    leave_room,
)
from keyboards.group_menu import group_chat_menu, group_main_menu
from keyboards.menu import main_menu
from services.anti_spam import is_spam

logger = logging.getLogger(__name__)

router = Router()

ROOM_PUBLIC = "🌐 اتاق عمومی"
ROOM_VIP = "💎 اتاق VIP"


class InRoomFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user = await get_user(message.from_user.id)
        return user is not None and user.room_id is not None


in_room = InRoomFilter()


@router.message(F.text == "👥 چت گروهی")
async def group_menu(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        return

    if user.partner_id:
        await message.answer("❌ اول چت خصوصی را پایان دهید.")
        return

    if user.is_searching:
        await message.answer("❌ اول جستجو را لغو کنید.")
        return

    if user.room_id:
        await message.answer("👥 شما در اتاق گروهی هستید.", reply_markup=group_chat_menu)
        return

    await message.answer(
        "👥 چت گروهی ناشناس\n\n"
        "یک اتاق انتخاب کنید. پیام‌ها برای همه اعضای اتاق ارسال می‌شود "
        "(بدون نمایش هویت شما).",
        reply_markup=group_main_menu,
    )


@router.message(F.text.in_({ROOM_PUBLIC, ROOM_VIP}))
async def join_group_room(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        return

    if user.partner_id:
        await message.answer("❌ اول چت خصوصی را پایان دهید.")
        return

    room = await get_room_by_name(message.text)
    if not room:
        await message.answer("❌ اتاق پیدا نشد.")
        return

    ok, reason = await join_room(user.telegram_id, room.id)
    if not ok:
        if reason == "vip_required":
            await message.answer(
                "❌ این اتاق فقط برای VIP است.\n"
                "از منوی پروفایل → 💎 VIP فعال کنید.",
                reply_markup=group_main_menu,
            )
            return
        if reason == "in_private_chat":
            await message.answer("❌ اول چت خصوصی را پایان دهید.")
            return
        await message.answer("❌ ورود به اتاق ناموفق بود.")
        return

    members = await get_room_members(room.id)
    await message.answer(
        f"✅ وارد {room.name} شدید.\n"
        f"👥 اعضای آنلاین: {len(members)}\n\n"
        "پیام بفرستید تا برای همه ارسال شود.",
        reply_markup=group_chat_menu,
    )


@router.message(F.text == "❌ خروج از اتاق")
async def leave_group_room(message: Message):
    if await leave_room(message.from_user.id):
        await message.answer("✅ از اتاق خارج شدید.", reply_markup=main_menu)
        return
    await message.answer("❌ شما در اتاقی نیستید.", reply_markup=main_menu)


async def _broadcast(message: Message, text: str) -> None:
    if is_spam(message.from_user.id):
        await message.answer("⏳ زیاد سریع پیام می‌فرستی. چند ثانیه صبر کن.")
        return

    user = await get_user(message.from_user.id)
    if not user or not user.room_id:
        return

    members = await get_room_members(user.room_id)
    sent = 0
    for member_id in members:
        if member_id == message.from_user.id:
            continue
        try:
            await message.bot.send_message(member_id, text)
            sent += 1
        except Exception as e:
            logger.warning("Group broadcast to %s failed: %s", member_id, e)

    if sent == 0:
        await message.answer("📭 فعلاً کسی جز شما در اتاق نیست.")
    else:
        await message.answer("✅ ارسال شد.")


@router.message(in_room, F.text)
async def group_text(message: Message):
    if message.text in MENU_BUTTONS:
        return
    if message.text.startswith("/"):
        return

    await _broadcast(message, f"👤 ناشناس:\n{message.text}")


@router.message(in_room, F.photo)
async def group_photo(message: Message):
    user = await get_user(message.from_user.id)
    if not user or not user.room_id:
        return

    if is_spam(message.from_user.id):
        await message.answer("⏳ زیاد سریع پیام می‌فرستی.")
        return

    members = await get_room_members(user.room_id)
    for member_id in members:
        if member_id == message.from_user.id:
            continue
        try:
            await message.bot.send_photo(
                member_id,
                message.photo[-1].file_id,
                caption=f"👤 ناشناس:\n{message.caption or ''}".strip(),
            )
        except Exception:
            pass
    await message.answer("✅ عکس ارسال شد.")


@router.message(in_room, F.sticker)
async def group_sticker(message: Message):
    user = await get_user(message.from_user.id)
    if not user or not user.room_id:
        return

    members = await get_room_members(user.room_id)
    for member_id in members:
        if member_id == message.from_user.id:
            continue
        try:
            await message.bot.send_sticker(member_id, message.sticker.file_id)
        except Exception:
            pass
    await message.answer("✅ استیکر ارسال شد.")
