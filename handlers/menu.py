from aiogram import Router, F
from aiogram.types import Message

from keyboards.menu import main_menu
from keyboards.more_menu import more_menu

router = Router()


@router.message(F.text == "⚙️ بیشتر")
async def more(message: Message):
    await message.answer(
        "⚙️ منوی بیشتر",
        reply_markup=more_menu
    )


@router.message(F.text == "⬅️ بازگشت")
async def back(message: Message):
    await message.answer(
        "🏠 منوی اصلی",
        reply_markup=main_menu
    )