from aiogram import Router, F
from aiogram.types import Message

from database.db import cancel_search, get_user
from keyboards.group_menu import group_chat_menu
from keyboards.menu import main_menu
from keyboards.more_menu import more_menu
from keyboards.search_menu import search_menu

router = Router()


@router.message(F.text == "⚙️ بیشتر")
async def more(message: Message):
    user = await get_user(message.from_user.id)

    if user and user.partner_id:
        await message.answer("⚙️ منوی بیشتر", reply_markup=more_menu)
        return

    if user and user.is_searching:
        await message.answer(
            "🔎 الان در صف جستجو هستید.\n"
            "برای لغو از «⏹ لغو جستجو» استفاده کنید.",
            reply_markup=search_menu,
        )
        return

    await message.answer(
        "⚙️ منوی بیشتر فقط در حین چت فعال است.\n"
        "اول با «🌍 چت تصادفی» وارد چت شوید.",
        reply_markup=main_menu,
    )


@router.message(F.text == "⬅️ بازگشت")
async def back(message: Message):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user and user.room_id:
        await message.answer(
            "👥 در اتاق گروهی هستید.\n"
            "برای خروج «❌ خروج از اتاق» را بزنید.",
            reply_markup=group_chat_menu,
        )
        return

    if user and user.is_searching and not user.partner_id:
        await cancel_search(user_id)
        await message.answer("✅ جستجو لغو شد.", reply_markup=main_menu)
        return

    if user and user.partner_id:
        await message.answer(
            "💬 هنوز در چت هستید.",
            reply_markup=more_menu,
        )
        return

    await message.answer("🏠 منوی اصلی", reply_markup=main_menu)
