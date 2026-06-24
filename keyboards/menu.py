from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 پیدا کردن مخاطب")],
        [KeyboardButton(text="👤 پروفایل")],
        [KeyboardButton(text="💎 VIP")],
        [KeyboardButton(text="⚙️ تنظیمات")]
        [KeyboardButton(text="🔄 مخاطب جدید")]
        [KeyboardButton(text="❌ پایان چت")]
    
    ],
    resize_keyboard=True
)