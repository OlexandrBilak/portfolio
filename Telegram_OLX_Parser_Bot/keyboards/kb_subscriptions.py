from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛒 Нові оголошення (OLX)"),
            KeyboardButton(text="💰 Зміна ціни конкретного товару (OLX)")
        ],
        [
            KeyboardButton(text="🧑‍💻 Нові вакансії з (OLX)"),
            KeyboardButton(text="⬅️ До головного меню")
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Оберіть тип моніторингу"
)

keyboard_confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Створити ✅", callback_data="confirm")],
        [InlineKeyboardButton(text="Скасувати ❌", callback_data="cancel")],
    ],
    
)

keyboard_main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📋 Список активних підписок"), 
            KeyboardButton(text="➕ Створити підписку")
        ],
        [ 
            KeyboardButton(text="🔄 Змінити існуючу підписку"), 
            KeyboardButton(text="❌ Видалити підписку")
        ],
    ],
    resize_keyboard=True
)

keyboard_change = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Посилання", callback_data="change_url")],
        [InlineKeyboardButton(text="🕒 Інтервал", callback_data="change_interval")],
        [InlineKeyboardButton(text="⬅️ До головного меню", callback_data="main_menu")]
    ],
)

keyboard_go_back = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ До головного меню", callback_data="main_menu")]
    ]
)
    
