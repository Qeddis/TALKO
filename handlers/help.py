from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.menu import main_menu

router = Router()

HELP_TEXT = (
    "📖 راهنمای TALKO\n\n"
    "🌍 چت تصادفی — اتصال به یک نفر تصادفی\n"
    "👦/👧 چت با پسر/دختر — جستجوی جنسیتی (نیاز به ثبت جنسیت در پروفایل)\n"
    "👤 پروفایل — مشاهده و ویرایش اطلاعات\n"
    "⚙️ بیشتر — کنترل چت (پایان، بلاک، گزارش، ...)\n\n"
    "در حین چت:\n"
    "• پیام متنی، عکس، ویس، ویدیو، استیکر و فایل ارسال می‌شود\n"
    "• ❌ پایان چت — قطع مکالمه\n"
    "• 🔄 مخاطب جدید — تعویض مخاطب\n"
    "• 🚫 بلاک — دیگر match نمی‌شوید\n"
    "• 📢 گزارش — گزارش تخلف\n\n"
    "⏹ لغو جستجو — لغو جستجو وقتی در صف هستید"
)

RULES_TEXT = (
    "📜 قوانین TALKO\n\n"
    "1. توهین، آزار و محتوای نامناسب ممنوع است\n"
    "2. اسپم و ارسال پیام پشت سر هم ممنوع است\n"
    "3. انتشار اطلاعات شخصی دیگران ممنوع است\n"
    "4. نقض قوانین = گزارش = مسدودی حساب\n\n"
    "با استفاده از ربات، این قوانین را می‌پذیرید."
)


@router.message(Command("help"))
@router.message(F.text == "📖 راهنما")
async def help_command(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu)


@router.message(Command("rules"))
async def rules_command(message: Message):
    await message.answer(RULES_TEXT)
