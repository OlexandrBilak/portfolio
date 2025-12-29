# Типи моніторингу

from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.kb_subscriptions import keyboard_confirm as kb_c
from keyboards.kb_subscriptions import keyboard_main as kb_m
from keyboards.kb_subscriptions import keyboard_go_back as kb_g
from db.database import db

subscriptions_router = Router()



def database_type_check(data):
    match data['type']:
        case '🛒 Нові оголошення (OLX)':
            data["type"] = "new_listing"
            return data['type']
        case '💰 Зміна ціни конкретного товару (OLX)':
            data["type"] = "price_change"
            return data['type']
        case '🧑‍💻 Нові вакансії з (OLX)':
            data["type"] = 'vacancies'
            return data['type']


class Subscriptions(StatesGroup):
    type = State()
    url = State()
    interval = State()
    confirm = State()


@subscriptions_router.callback_query(F.data == "main_menu")
async def main_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("📎 Головне меню", reply_markup=kb_m)
    await call.answer()


@subscriptions_router.message(F.text == "⬅️ Головне меню")
async def main_menu_message(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📎 Головне меню", reply_markup=kb_m)



# Вибір посилання підписки
@subscriptions_router.message(Subscriptions.url)
async def add_url(message: Message, state: FSMContext):
    
    if not message.text.startswith("http"):
        await message.answer("Посилання має починатись з http", reply_markup=kb_g)
        return
    
    await state.update_data(url=message.text)
    await state.set_state(Subscriptions.interval)

    await message.answer("Який інтервал використовувати? (у хвилинах)", reply_markup=kb_g)


# Вибір інтервалу
@subscriptions_router.message(Subscriptions.interval)
async def add_interval(message: Message, state: FSMContext):
    
    if not message.text.isdigit():
        await message.answer("Інтервал має бути числом", reply_markup=kb_g)
        return
    
    await state.update_data(interval=int(message.text))
    await state.set_state(Subscriptions.confirm)

    await message.answer(
    "Підтвердіть створення підписки",
    reply_markup=kb_c
    )


@subscriptions_router.callback_query(Subscriptions.confirm, F.data == "confirm")
async def confirm_subscription(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.message.answer(
        f"{data['type']}\n" \
        f"За посиланням: {data['url']}\n" \
        f"Інтервал: {data['interval']} хвилин"
    )
    
    database_type_check(data)

    db.add_data(
        name=data['type'],
        user_id=callback.from_user.id,
        type=data['type'],
        url=data['url'],
        interval=data['interval'],
        last_value=None
    )
    print(data, callback.from_user.id)
    await callback.message.answer("Підписку створено ✅", reply_markup=kb_m)
    
    await state.clear()
    await callback.answer()


@subscriptions_router.callback_query(Subscriptions.confirm, F.data == "cancel")
async def cancel_subscription(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Підписку скасовано ❌", reply_markup=kb_m)
    await state.clear()
    await callback.answer()
    
