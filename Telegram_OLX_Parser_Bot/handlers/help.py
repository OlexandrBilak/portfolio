# Інформація про типи моніторингу

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.kb_subscriptions import keyboard as kb
from keyboards.kb_subscriptions import keyboard_main as kb_m

help_router = Router()


@help_router.message(Command("help"))
async def help_command(message: Message):
    await send_help(message)


@help_router.message(F.text == "➕ Створити підписку")
async def help_button(message: Message):
    await send_help(message)


async def send_help(message: Message):

    await message.answer(
        "Бот підтримує один або кілька типів підписок:\n"
        "🛒 Нові оголошення (OLX)\n"
        "💰 Зміна ціни конкретного товару (OLX)\n"
        "🧑‍💻 Нові вакансії з (OLX)\n"
    )

    await message.answer(
        "Оберіть тип підписки для створення:",
        reply_markup=kb
    )


@help_router.message(F.text == "⬅️ До головного меню")
async def back_to_main(message: Message):
    await message.answer(
        'Головне меню',
        reply_markup=kb_m
    )
