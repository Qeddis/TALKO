from aiogram import F, Router
from aiogram.types import Message

from config import REFERRAL_BONUS, REFERRAL_REWARD
from database.db import get_referral_count, get_user
from keyboards.menu import main_menu
from utils.referral import referral_link

router = Router()


@router.message(F.text == "🎁 دعوت دوستان")
async def referral_info(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("❌ پروفایل پیدا نشد.")
        return

    me = await message.bot.get_me()
    if not me.username:
        await message.answer("❌ نام کاربری ربات تنظیم نشده.")
        return

    count = await get_referral_count(message.from_user.id)
    link = referral_link(me.username, message.from_user.id)
    earned = count * REFERRAL_REWARD

    await message.answer(
        "🎁 دعوت دوستان\n\n"
        f"لینک اختصاصی تو:\n{link}\n\n"
        f"• تو به ازای هر عضو جدید: +{REFERRAL_REWARD} سکه\n"
        f"• دوستت هم +{REFERRAL_BONUS} سکه اضافه می‌گیرد\n\n"
        f"👥 دعوت‌های موفق: {count}\n"
        f"🪙 سکه از دعوت: {earned}\n"
        f"🪙 موجودی فعلی: {user.coins}",
        reply_markup=main_menu,
    )
