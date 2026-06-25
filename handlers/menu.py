from aiogram import Router, F
from aiogram.types import Message

from keyboards.menu import main_menu
from keyboards.chat_menu import chat_menu
from keyboards.profile_menu import profile_menu
from keyboards.edit_profile_menu import edit_profile_menu
from keyboards.more_menu import more_menu

router = Router()


@router.message(F.text == "🔍 شروع چت")
async def chat_menu_handler(message: Message):
    await message.answer(
        "💬 بخش چت",
        reply_markup=chat_menu
    )


@router.message(F.text == "👤 پروفایل")
async def profile_menu_handler(message: Message):
    await message.answer(
        "👤 بخش پروفایل",
        reply_markup=profile_menu
    )


@router.message(F.text == "✏️ ویرایش پروفایل")
async def edit_profile_handler(message: Message):
    await message.answer(
        "✏️ ویرایش پروفایل",
        reply_markup=edit_profile_menu
    )


@router.message(F.text == "⚙️ بیشتر")
async def more_handler(message: Message):
    await message.answer(
        "⚙️ تنظیمات و امکانات",
        reply_markup=more_menu
    )


@router.message(F.text == "⬅️ بازگشت")
async def back_handler(message: Message):
    await message.answer(
        "🏠 منوی اصلی",
        reply_markup=main_menu
    )