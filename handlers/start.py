from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from database.db import add_user, get_user
from keyboards.menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
    )

    user = await get_user(message.from_user.id)
    if user and user.banned:
        await message.answer("❌ حساب شما مسدود شده است.")
        return

    await message.answer(
        "👋 به TALKO — چت ناشناس تلگرام خوش آمدی!\n\n"
        "🌍 چت تصادفی بزن یا جنسیت انتخاب کن.\n"
        "📖 راهنما و 📜 /rules را بخوان.\n\n"
        "حریم خصوصی حفظ کن و به قوانین احترام بذار.",
        reply_markup=main_menu,
    )
