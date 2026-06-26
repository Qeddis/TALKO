import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from config import ADMIN_IDS
from database.db import (
    add_coins,
    get_all_telegram_ids,
    get_stats,
    get_user,
    set_banned,
    set_vip,
)

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not _is_admin(message.from_user.id):
        return

    await message.answer(
        "🛠 پنل ادمین\n\n"
        "/stats — آمار ربات\n"
        "/ban <id> — مسدود کردن\n"
        "/unban <id> — رفع مسدودی\n"
        "/setvip <id> — فعال‌سازی VIP\n"
        "/unsetvip <id> — غیرفعال VIP\n"
        "/coins <id> <amount> — افزودن سکه\n"
        "/user <id> — اطلاعات کاربر\n"
        "/broadcast <متن> — پیام همگانی\n"
        "/deploy — راهنمای deploy"
    )


@router.message(Command("stats"))
async def admin_stats(message: Message):
    if not _is_admin(message.from_user.id):
        return

    stats = await get_stats()
    await message.answer(
        "📊 آمار TALKO\n\n"
        f"👥 کل کاربران: {stats['total']}\n"
        f"🔎 در صف جستجو: {stats['searching']}\n"
        f"💬 چت فعال: {stats['in_chat']}\n"
        f"🚫 مسدود: {stats['banned']}\n"
        f"💎 VIP: {stats['vip']}"
    )


@router.message(Command("ban"))
async def admin_ban(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("❌ فرمت: /ban <telegram_id>")
        return

    target_id = int(command.args.strip())
    if await set_banned(target_id, True):
        await message.answer(f"✅ کاربر {target_id} مسدود شد.")
    else:
        await message.answer("❌ کاربر پیدا نشد.")


@router.message(Command("unban"))
async def admin_unban(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("❌ فرمت: /unban <telegram_id>")
        return

    target_id = int(command.args.strip())
    if await set_banned(target_id, False):
        await message.answer(f"✅ مسدودی کاربر {target_id} برداشته شد.")
    else:
        await message.answer("❌ کاربر پیدا نشد.")


@router.message(Command("setvip"))
async def admin_setvip(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("❌ فرمت: /setvip <telegram_id>")
        return

    target_id = int(command.args.strip())
    if await set_vip(target_id, True):
        await message.answer(f"💎 VIP برای {target_id} فعال شد.")
    else:
        await message.answer("❌ کاربر پیدا نشد.")


@router.message(Command("unsetvip"))
async def admin_unsetvip(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("❌ فرمت: /unsetvip <telegram_id>")
        return

    target_id = int(command.args.strip())
    if await set_vip(target_id, False):
        await message.answer(f"✅ VIP کاربر {target_id} غیرفعال شد.")
    else:
        await message.answer("❌ کاربر پیدا نشد.")


@router.message(Command("coins"))
async def admin_coins(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    parts = (command.args or "").split()
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].lstrip("-").isdigit():
        await message.answer("❌ فرمت: /coins <telegram_id> <amount>")
        return

    target_id = int(parts[0])
    amount = int(parts[1])
    if await add_coins(target_id, amount):
        user = await get_user(target_id)
        await message.answer(
            f"✅ {amount} سکه به {target_id} اضافه شد.\n"
            f"🪙 موجودی: {user.coins if user else '?'}"
        )
    else:
        await message.answer("❌ کاربر پیدا نشد.")


@router.message(Command("user"))
async def admin_user(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    if not command.args or not command.args.strip().isdigit():
        await message.answer("❌ فرمت: /user <telegram_id>")
        return

    target_id = int(command.args.strip())
    user = await get_user(target_id)
    if not user:
        await message.answer("❌ کاربر پیدا نشد.")
        return

    await message.answer(
        f"👤 کاربر {target_id}\n\n"
        f"username: @{user.username or '-'}\n"
        f"سن: {user.age or '-'}\n"
        f"جنسیت: {user.gender or '-'}\n"
        f"کشور: {user.country or '-'}\n"
        f"🪙 سکه: {user.coins}\n"
        f"💎 VIP: {'بله' if user.vip else 'خیر'}\n"
        f"🚫 ban: {'بله' if user.banned else 'خیر'}\n"
        f"📢 گزارش‌ها: {user.reports}\n"
        f"🔎 در جستجو: {'بله' if user.is_searching else 'خیر'}\n"
        f"💬 partner: {user.partner_id or '-'}"
    )


@router.message(Command("broadcast"))
async def admin_broadcast(message: Message, command: CommandObject):
    if not _is_admin(message.from_user.id):
        return

    text = (command.args or "").strip()
    if not text:
        await message.answer("❌ فرمت: /broadcast <متن پیام>")
        return

    user_ids = await get_all_telegram_ids()
    sent = 0
    failed = 0

    await message.answer(f"📤 در حال ارسال به {len(user_ids)} کاربر...")

    for user_id in user_ids:
        try:
            await message.bot.send_message(user_id, f"📢 پیام مدیریت:\n\n{text}")
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(f"✅ ارسال شد: {sent} | ❌ ناموفق: {failed}")
