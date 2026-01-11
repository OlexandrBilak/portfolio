from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


mainmenu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🧠 Перетворення"),
            KeyboardButton(text="🌍 Переклад"),
        ],
        [
            KeyboardButton(text="📚 Навчання"),
            KeyboardButton(text="ℹ️ Довідка"),
        ],
    ],
    resize_keyboard=True,
)

mode_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⬅️ Головне меню"),
            KeyboardButton(text="🧹 Очистити історію"),
        ],
    ],
    resize_keyboard=True
)
