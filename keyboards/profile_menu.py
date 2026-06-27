from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

profile_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📄 مشاهده پروفایل"),
            KeyboardButton(text="✏️ ویرایش پروفایل"),
        ],
        [
            KeyboardButton(text="🎁 دعوت دوستان"),
            KeyboardButton(text="💎 VIP"),
        ],
        [KeyboardButton(text="⬅️ بازگشت")],
    ],
    resize_keyboard=True,
)
