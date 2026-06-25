from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌍 چت تصادفی")],
        [
            KeyboardButton(text="👦 چت با پسر"),
            KeyboardButton(text="👧 چت با دختر")
        ],
        [KeyboardButton(text="👤 پروفایل")],
        [KeyboardButton(text="⚙️ بیشتر")]
    ],
    resize_keyboard=True
)