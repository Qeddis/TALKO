from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS, REFERRAL_BONUS, REFERRAL_REWARD, VIP_COIN_PRICE, VIP_STARS_PRICE
from keyboards.menu import main_menu

router = Router()

HELP_TEXT = (
    "📖 راهنمای TALKO\n\n"
    "🌍 چت تصادفی — اتصال به یک نفر تصادفی\n"
    "👦/👧 چت با پسر/دختر — جستجوی جنسیتی (نیاز به ثبت جنسیت)\n"
    "👥 چت گروهی — اتاق عمومی یا VIP (ناشناس)\n"
    "👤 پروفایل — مشاهده و ویرایش اطلاعات\n"
    "💎 VIP — خرید با سکه یا استار تلگرام\n"
    "🎁 دعوت دوستان — سکه رایگان با لینک دعوت\n"
    "در حین چت خصوصی (منوی کنترل خودکار):\n"
    "• متن، عکس، ویس، ویدیو، استیکر و فایل\n"
    "• ❌ پایان چت | 🔄 مخاطب جدید\n"
    "• 🚫 بلاک | 📢 گزارش\n\n"
    f"💎 VIP: {VIP_COIN_PRICE} سکه یا {VIP_STARS_PRICE} استار\n"
    f"🎁 دعوت: +{REFERRAL_REWARD} سکه برای تو، +{REFERRAL_BONUS} برای دوست\n"
    "⏹ لغو جستجو — وقتی در صف هستید"
)

RULES_TEXT = (
    "📜 قوانین TALKO\n\n"
    "1. توهین، آزار و محتوای نامناسب ممنوع است\n"
    "2. اسپم و ارسال پیام پشت سر هم ممنوع است\n"
    "3. انتشار اطلاعات شخصی دیگران ممنوع است\n"
    "4. نقض قوانین = گزارش = مسدودی حساب\n\n"
    "با استفاده از ربات، این قوانین را می‌پذیرید."
)

DEPLOY_TEXT = (
    "🚀 راهنمای Deploy (خلاصه)\n\n"
    "1. فایل .env را با BOT_TOKEN و ADMIN_IDS بساز\n"
    "2. pip install -r requirements.txt\n"
    "3. python bot.py\n\n"
    "برای VPS / Railway / Render جزئیات کامل را در فایل DEPLOY.md بخوان.\n\n"
    "متغیرهای مهم:\n"
    "• BOT_TOKEN — توکن @BotFather\n"
    "• ADMIN_IDS — آیدی عددی ادمین\n"
    "• DATABASE_URL — PostgreSQL (اختیاری)\n"
    "• VIP_COIN_PRICE / VIP_STARS_PRICE\n"
    "• REFERRAL_REWARD / REFERRAL_BONUS\n\n"
    "⭐ Stars: نیازی به تنظیم BotFather نیست — currency=XTR"
)


@router.message(Command("help"))
@router.message(F.text == "📖 راهنما")
async def help_command(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu)


@router.message(Command("rules"))
async def rules_command(message: Message):
    await message.answer(RULES_TEXT)


@router.message(Command("deploy"))
async def deploy_guide(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(DEPLOY_TEXT)
