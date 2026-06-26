from aiogram import Router, F
from aiogram.types import Message

from database.db import cancel_search, get_user
from handlers.search_utils import try_match_or_search
from keyboards.menu import main_menu

router = Router()


@router.message(F.text == "🌍 چت تصادفی")
async def find_partner(message: Message):
    await try_match_or_search(message)


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
