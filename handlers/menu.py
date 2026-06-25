from aiogram import Router, F
from aiogram.types import Message

from database.db import get_user
from keyboards.menu import main_menu
from keyboards.more_menu import more_menu

router = Router()


@router.message(F.text == "⚙️ بیشتر")
async def more(message: Message):
    await message.answer("⚙️ منوی بیشتر", reply_markup=more_menu)


@router.message(F.text == "⬅️ بازگشت")
async def back(message: Message):
    await message.answer("🏠 منوی اصلی", reply_markup=main_menu)


@router.message(F.text == "💎 VIP")
async def vip_info(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        await message.answer("❌ پروفایل پیدا نشد.")
        return

    if user.vip:
        await message.answer(
            "💎 شما کاربر VIP هستید!\n\n"
            "مزایا:\n"
            "• جستجوی سریع‌تر\n"
            "• اولویت در matching\n"
            "• نشان VIP در پروفایل"
        )
        return

    await message.answer(
        "💎 VIP\n\n"
        "با VIP می‌توانید:\n"
        "• سریع‌تر مخاطب پیدا کنید\n"
        "• نشان VIP داشته باشید\n\n"
        f"🪙 سکه شما: {user.coins}\n"
        "برای فعال‌سازی VIP با پشتیبانی تماس بگیرید."
    )
