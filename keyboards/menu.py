from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌍 چت تصادفی")],
        [
            KeyboardButton(text="👦 چت با پسر"),
            KeyboardButton(text="👧 چت با دختر"),
        ],
        [KeyboardButton(text="👥 چت گروهی")],
        [KeyboardButton(text="👤 پروفایل")],
        [
            KeyboardButton(text="⚙️ بیشتر"),
            KeyboardButton(text="📖 راهنما"),
        ],
    ],
    resize_keyboard=True,
)
