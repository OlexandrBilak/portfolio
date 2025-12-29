# Виведення списку підписок, редагування та видалення підписки

from aiogram import Router, F
from aiogram.types import Message

from db.database import db
from keyboards.kb_subscriptions import keyboard_main as kb_m


list_router = Router()


TYPE_TO_TEXT = {
    "new_listing": "🛒 Нові оголошення (OLX)",
    "price_change": "💰 Зміна ціни конкретного товару (OLX)",
    "vacancies": "🧑‍💻 Нові вакансії з (OLX)",
}

def database_type_reverse(type_code: str) -> str:
    return TYPE_TO_TEXT.get(type_code, type_code)

        

@list_router.message(F.text == "📋 Список активних підписок")
async def list_subscriptions(message: Message):
    list_sub = db.get_all_data(user_id=message.from_user.id)
    for sub in list_sub:
        await message.answer(
            f"🔖 {database_type_reverse(sub[3])} \n " \
            f"ℹ️ ID: {sub[1]} \n" \
            f"🔗 Посилання: {sub[4]} \n" \
            f"🕒 Інтервал: {sub[5]} \n" \
            f"📊 Попередні дані: {sub[6]}"
        )

