from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 شروع چت")],
        [KeyboardButton(text="👤 پروفایل")],
        [KeyboardButton(text="⚙️ بیشتر")]
    ],
    resize_keyboard=True
)