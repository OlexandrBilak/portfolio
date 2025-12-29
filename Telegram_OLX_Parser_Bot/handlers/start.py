# Вітальне повідомлення

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.kb_subscriptions import keyboard_main as kb_m

start_router = Router()


@start_router.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Привіт\n" \
    "🛒 Це Telegram-Бот, який автоматично парсить OLX та повідомляє користувача про нові або змінені дані сайту\n" \
    "📩 Бот працює у фоновому режимі, регулярно виконує scraping і надсилає повідомлення при появі змін.\n\n" \
    "/help - Переглянути типи підписок\n", reply_markup=kb_m)
