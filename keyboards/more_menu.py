from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

more_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 مشاهده مشخصات مخاطب")],
        [KeyboardButton(text="🔄 مخاطب جدید")],
        [KeyboardButton(text="❌ پایان چت")],
        [KeyboardButton(text="🚫 بلاک کاربر")],
        [KeyboardButton(text="📢 گزارش کاربر")],
        [KeyboardButton(text="ℹ️ راهنما")],
        [KeyboardButton(text="⬅️ بازگشت")]
    ],
    resize_keyboard=True
)