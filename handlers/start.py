import logging

from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from config import REFERRAL_BONUS, REFERRAL_REWARD
from database.db import add_user
from utils.referral import parse_referrer_id
from keyboards.menu import main_menu

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def start(message: Message, command: CommandObject):
    referrer_id = parse_referrer_id(command.args)
    result = await add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        referrer_id=referrer_id,
    )

    user = result.user
    if user.banned:
        await message.answer("❌ حساب شما مسدود شده است.")
        return

    bonus_line = ""
    if result.is_new and result.referrer_id:
        bonus_line = (
            f"\n🎁 {REFERRAL_BONUS} سکه هدیه دعوت به موجودی اضافه شد!\n"
        )
        try:
            await message.bot.send_message(
                result.referrer_id,
                "🎁 یک نفر با لینک دعوت تو عضو شد!\n"
                f"+{REFERRAL_REWARD} سکه به حسابت اضافه شد.",
            )
        except Exception as e:
            logger.warning("Referral notify to %s failed: %s", result.referrer_id, e)

    welcome = (
        "👋 به TALKO — چت ناشناس تلگرام خوش آمدی!\n\n"
        "🌍 چت تصادفی | 👥 چت گروهی | 👤 پروفایل\n"
        "💎 VIP با سکه یا استار | 🎁 دعوت دوستان | 📖 /help\n\n"
        "حریم خصوصی را رعایت کن و به قوانین (/rules) احترام بذار."
    )
    if result.is_new:
        welcome += f"\n\n🪙 {user.coins} سکه خوش‌آمدگویی دریافت کردی!{bonus_line}"

    await message.answer(welcome, reply_markup=main_menu)
