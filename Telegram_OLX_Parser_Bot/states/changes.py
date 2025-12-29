# Зміна / видалення підписки

from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from keyboards.kb_subscriptions import keyboard_change as kb_c
from keyboards.kb_subscriptions import keyboard_main as kb_m
from keyboards.kb_subscriptions import keyboard_go_back as kb_g
from db.database import db

changes_router = Router()



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


class Changes(StatesGroup):
    id = State()
    url = State()
    interval = State()

class Delete(StatesGroup):
    id = State()

@changes_router.message(F.text == "❌ Видалити підписку")
async def delete_subscription(message: Message, state: FSMContext):
    await message.answer("Введіть ID підписки, яку хочете видалити\n", reply_markup=kb_g)
    await state.set_state(Delete.id)


@changes_router.message(Delete.id)
async def delete(message: Message, state: FSMContext):
    id = int(message.text)
    print(id)
    
    await message.answer(db.delete_data(user_id=message.from_user.id, global_id=id), reply_markup=kb_m)
    await state.finish()
    

# Вибір інтервалу
@changes_router.message(F.text == "🔄 Змінити існуючу підписку")
async def change_subscription(message: Message, state=FSMContext):
    await message.answer("Введіть ID підписки, яку хочете змінити\n", reply_markup=kb_g)
    await state.set_state(Changes.id)
    


@changes_router.message(Changes.id)
async def change_sub(message: Message, state: FSMContext):
    await message.answer("Що змінити?\n", reply_markup=kb_c)
    await state.update_data(id=message.text)

@changes_router.callback_query(F.data == "change_url")
async def change_url(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введіть нове посилання: \n", reply_markup=kb_g)
    await state.set_state(Changes.url)
    await call.answer()


@changes_router.message(Changes.url)
async def update_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    data = await state.get_data()

    await message.answer(db.update_url(url=data['url'], user_id=message.from_user.id, global_id=data['id']), reply_markup=kb_m)

    await message.answer("Зміни успішно внесено ✅", reply_markup=kb_m)
    await state.clear()


@changes_router.callback_query(F.data == "change_interval")
async def change_interval(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введіть новий інтервал: \n", reply_markup=kb_g)
    await state.set_state(Changes.interval)
    await call.answer()


@changes_router.message(Changes.interval)
async def update_interval(message: Message, state: FSMContext):
    await state.update_data(interval=message.text)
    data = await state.get_data()

    await message.answer(db.update_interval(interval=data['interval'], user_id=message.from_user.id, global_id=data['id']), reply_markup=kb_m)

    await message.answer("Зміни успішно внесено ✅", reply_markup=kb_m)
    await state.finish()
    
