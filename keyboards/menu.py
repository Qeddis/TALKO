from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 پیدا کردن مخاطب")],
        [KeyboardButton(text="👦 چت با پسر")],
        [KeyboardButton(text="👧 چت با دختر")],
        [KeyboardButton(text="👤 پروفایل")],
        [KeyboardButton(text="👤 مشاهده مشخصات")],
        [KeyboardButton(text="💎 VIP")],
        [KeyboardButton(text="⚙️ تنظیمات")],
        [KeyboardButton(text="🔄 مخاطب جدید")],
        [KeyboardButton(text="❌ پایان چت")]
    ],
    resize_keyboard=True
)