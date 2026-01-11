from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.keyboard import mainmenu_keyboard 


start_router = Router()


@start_router.message(Command("start"))
async def start(message: Message):
    await message.answer('''
    👋 Привіт! Я - ChatGPT Bot 🤖

Я допоможу тобі:
    • перетворювати аудіо в текст 💻
    • перекладати тексти 🌍
    • зрозуміти складні теми простими словами 📘

🔧 У мене є кілька режимів роботи:
    🧠 Перетворення - перетворюю голосові/відео у текст
    🌍 Переклад - перекладаю текст різними мовами
    📚 Навчання - допомагаю зrozуміти складні теми

📌 Обери режим командою /mode або кнопками нижче
ℹ️ Детальніше — команда /help
''', reply_markup=mainmenu_keyboard)