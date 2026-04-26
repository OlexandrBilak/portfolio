import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from logic import calculate_payment
from sheets import add_log
from tariff_cache import get_cached_tariffs, tariff_updater


class WorkForm(StatesGroup):
    model = State()
    department = State()
    operation = State()
    value = State()
    order = State()
    route = State()
    barcode = State()
    color = State()
    size = State()
    comment = State()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Основне меню
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="➕ Нове нарахування")]],
    resize_keyboard=True
)


# Навігаційні кнопки
def nav_buttons(back=True):
    row = []
    if back:
        row.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="back"))
    row.append(InlineKeyboardButton(text="❌ Вийти", callback_data="exit"))
    return [row]


# Розбивка кнопок на ряди
def chunk_buttons(items, prefix, size=2):
    rows = []
    for i in range(0, len(items), size):
        row = [InlineKeyboardButton(text=item, callback_data=f"{prefix}_{item}") for item in items[i:i+size]]
        rows.append(row)
    return rows


def model_keyboard():
    df = get_cached_tariffs()
    models = sorted(df["Модель"].unique())
    kb = chunk_buttons(models, "model") + nav_buttons(back=False)
    return InlineKeyboardMarkup(inline_keyboard=kb)


def department_keyboard(model):
    df = get_cached_tariffs()
    df = df[df["Модель"] == model]
    departments = sorted(df["Відділ"].unique())
    kb = chunk_buttons(departments, "dep") + nav_buttons()
    return InlineKeyboardMarkup(inline_keyboard=kb)


def operation_keyboard(model, department):
    df = get_cached_tariffs()
    df = df[(df["Модель"] == model) & (df["Відділ"] == department)]
    operations = sorted(df["Операція"].unique())
    kb = chunk_buttons(operations, "op") + nav_buttons()
    return InlineKeyboardMarkup(inline_keyboard=kb)


def skip_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустити", callback_data="skip")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
             InlineKeyboardButton(text="❌ Вийти", callback_data="exit")]
        ]
    )


# --- Обробники ---
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Система нарахувань", reply_markup=main_keyboard)


@dp.message(F.text == "➕ Нове нарахування")
async def new_record(message: Message, state: FSMContext):
    await message.answer("Оберіть модель", reply_markup=model_keyboard())
    await state.set_state(WorkForm.model)


@dp.callback_query(F.data.startswith("model_"))
async def select_model(callback: CallbackQuery, state: FSMContext):
    model = callback.data.split("_", 1)[1]
    await state.update_data(model=model)
    await callback.message.answer(
        f"Модель: {model}\nОберіть відділ",
        reply_markup=department_keyboard(model)
    )
    await state.set_state(WorkForm.department)
    await callback.answer()


@dp.callback_query(F.data.startswith("dep_"))
async def select_department(callback: CallbackQuery, state: FSMContext):
    department = callback.data.split("_", 1)[1]
    model = (await state.get_data())["model"]
    await state.update_data(department=department)
    await callback.message.answer(
        f"Відділ: {department}\nОберіть операцію",
        reply_markup=operation_keyboard(model, department)
    )
    await state.set_state(WorkForm.operation)
    await callback.answer()


@dp.callback_query(F.data.startswith("op_"))
async def select_operation(callback: CallbackQuery, state: FSMContext):
    operation = callback.data.split("_", 1)[1]
    await state.update_data(operation=operation)
    await callback.message.answer("Введіть кількість або години")
    await state.set_state(WorkForm.value)
    await callback.answer()


@dp.message(WorkForm.value)
async def input_value(message: Message, state: FSMContext):
    try:
        value = float(message.text)
    except:
        await message.answer("Введіть число")
        return
    await state.update_data(value=value)
    await message.answer("№ замовника")
    await state.set_state(WorkForm.order)


@dp.message(WorkForm.order)
async def input_order(message: Message, state: FSMContext):
    await state.update_data(order=message.text)
    await message.answer("№ маршрутного")
    await state.set_state(WorkForm.route)


@dp.message(WorkForm.route)
async def input_route(message: Message, state: FSMContext):
    await state.update_data(route=message.text)
    await message.answer("Штрихкод (необов'язково)", reply_markup=skip_keyboard())
    await state.set_state(WorkForm.barcode)


@dp.message(WorkForm.barcode)
async def input_barcode(message: Message, state: FSMContext):
    await state.update_data(barcode=message.text)
    await message.answer("Колір (необов'язково)", reply_markup=skip_keyboard())
    await state.set_state(WorkForm.color)


@dp.message(WorkForm.color)
async def input_color(message: Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer("Розмір (необов'язково)", reply_markup=skip_keyboard())
    await state.set_state(WorkForm.size)


@dp.message(WorkForm.size)
async def input_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text)
    await message.answer("Коментар (необов'язково)", reply_markup=skip_keyboard())
    await state.set_state(WorkForm.comment)


@dp.message(WorkForm.comment)
async def input_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await save_record(message, state)


@dp.callback_query(F.data == "skip")
async def skip_field(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    if current.endswith("barcode"):
        await state.update_data(barcode="")
        await callback.message.answer("Колір (необов'язково)", reply_markup=skip_keyboard())
        await state.set_state(WorkForm.color)
    elif current.endswith("color"):
        await state.update_data(color="")
        await callback.message.answer("Розмір (необов'язково)", reply_markup=skip_keyboard())
        await state.set_state(WorkForm.size)
    elif current.endswith("size"):
        await state.update_data(size="")
        await callback.message.answer("Коментар (необов'язково)", reply_markup=skip_keyboard())
        await state.set_state(WorkForm.comment)
    elif current.endswith("comment"):
        await state.update_data(comment="")
        await save_record(callback.message, state)
    await callback.answer()


async def save_record(message: Message, state: FSMContext):
    data = await state.get_data()
    calc = calculate_payment(
        data["model"], data["department"], data["operation"], data["value"]
    )
    if calc is None:
        await message.answer("Тариф не знайдено", reply_markup=main_keyboard)
        await state.clear()
        return

    total = calc["total"]
    log_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "name": message.from_user.full_name,
        "department": data["department"],
        "model": data["model"],
        "operation": data["operation"],
        "amount": data["value"],
        "sum": total,
        "order": data["order"],
        "route": data["route"],
        "barcode": data.get("barcode", ""),
        "color": data.get("color", ""),
        "size": data.get("size", ""),
        "comment": data.get("comment", "")
    }
    add_log(log_data)
    await message.answer(f"Запис додано\nСума: {total}", reply_markup=main_keyboard)
    await state.clear()


@dp.callback_query(F.data == "exit")
async def exit_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Операцію скасовано", reply_markup=main_keyboard)
    await callback.answer()


@dp.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery, state: FSMContext):
    current = await state.get_state()
    data = await state.get_data()

    # Визначаємо попередній стан
    if current.endswith("department"):
        # Повертаємо до вибору моделі
        await callback.message.answer("Оберіть модель", reply_markup=model_keyboard())
        await state.set_state(WorkForm.model)

    elif current.endswith("operation"):
        # Повертаємо до вибору відділу
        model = data.get("model")
        await callback.message.answer(f"Модель: {model}\nОберіть відділ", reply_markup=department_keyboard(model))
        await state.set_state(WorkForm.department)

    elif current.endswith("value"):
        # Повертаємо до вибору операції
        model = data.get("model")
        department = data.get("department")
        await callback.message.answer(f"Відділ: {department}\nОберіть операцію", reply_markup=operation_keyboard(model, department))
        await state.set_state(WorkForm.operation)

    elif current.endswith("order"):
        await callback.message.answer("Введіть кількість або години")
        await state.set_state(WorkForm.value)

    elif current.endswith("route"):
        await callback.message.answer("№ замовника")
        await state.set_state(WorkForm.order)

    elif current.endswith("barcode"):
        await callback.message.answer("№ маршрутного")
        await state.set_state(WorkForm.route)

    elif current.endswith("color"):
        await callback.message.answer("Штрихкод (необов'язково)", reply_markup=skip_keyboard())
        await state.set_state(WorkForm.barcode)

    elif current.endswith("size"):
        await callback.message.answer("Колір (необов'язково)", reply_markup=skip_keyboard())
        await state.set_state(WorkForm.color)

    elif current.endswith("comment"):
        await callback.message.answer("Розмір (необов'язково)", reply_markup=skip_keyboard())
        await state.set_state(WorkForm.size)

    await callback.answer()


async def main():
    # запускаємо фонове оновлення тарифів
    asyncio.create_task(tariff_updater())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
