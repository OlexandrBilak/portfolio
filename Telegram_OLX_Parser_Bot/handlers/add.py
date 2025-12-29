# Старт створення підписки

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.subscriptions import Subscriptions
from keyboards.kb_subscriptions import keyboard_go_back as kb_g

add_router = Router()


# Вибір типу підписки
@add_router.message(F.text == "🛒 Нові оголошення (OLX)")
async def add_list(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(Subscriptions.url)

    await message.answer("Надішліть посилання на сторінку з оголошеннями:", reply_markup=kb_g)


@add_router.message(F.text == "💰 Зміна ціни конкретного товару (OLX)")
async def add_item(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(Subscriptions.url)

    await message.answer("Надішліть посилання на товар:", reply_markup=kb_g)


@add_router.message(F.text == "🧑‍💻 Нові вакансії з (OLX)")
async def add_vac(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(Subscriptions.url)

    await message.answer("Надішліть посилання на сторінку з вакансіями:", reply_markup=kb_g)

