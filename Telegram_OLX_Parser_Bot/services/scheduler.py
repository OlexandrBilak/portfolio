import asyncio
from aiogram import Bot
from functools import partial

from db.database import db
from db.scraper_database import db as db_s
from scrapers import base
from config import TOKEN

USER_ID = 731681925

bot = Bot(token=TOKEN)

PARSER_MAP = {
    "new_listing": base.get_new_listing,
    "price_change": base.get_price_change,
    "vacancies": base.get_vacancies
}

PARSER_NAME = {
    "new_listing": "🛒 Нові оголошення (OLX)",
    "price_change": "💰 Зміна ціни (OLX)",
    "vacancies": "🧑‍💻 Нові вакансії (OLX)"
}

async def get_active_parser(user_id):
    subscriptions = db.get_all_data(user_id=user_id)
    active_parser = []

    for sub in subscriptions:
        type_ = sub[3]
        url = sub[4]
        interval = sub[5]

        active_parser.append({
            "type": type_,
            "url": url,
            "interval": interval,
        })
    
    return active_parser


async def run_parser(user_id, type_, url):
    parser_func = PARSER_MAP.get(type_)
    parser_name = PARSER_NAME.get(type_)

    while True:
        # Отримуємо підписку з БД
        subscriptions = db.get_all_data(user_id)
        sub = None
        for s in subscriptions:
            # s = (id, global_id, user_id, type, url, interval, last_value, created_at, table_name)
            if s[3] == type_ and s[4] == url:
                sub = s
                break

        if not sub:
            print(f"Підписку {type_} для {url} видалено. Таска зупинена.")
            break

        current_url = sub[4]
        current_interval = sub[5]  # інтервал в хвилинах

        print(f"Запуск парсера {type_} для {current_url} з інтервалом {current_interval} хв")
        data = await asyncio.to_thread(partial(parser_func, current_url))

        if data:
            for el in data:
                if db_s.exists(type_, el["link"]):
                    continue
                db_s.add_data(type_, user_id, current_url, el["title"], el["price"], el["link"])
                await bot.send_message(
                    chat_id=user_id,
                    text=f"{parser_name}:\n🔎 {el['title']}\n💰 {el['price']}\n🔗 {el['link']}"
                )

        print(f"Пауза {current_interval} хвилин для {type_}")
        await asyncio.sleep(current_interval * 60)


async def create_scheduler(user_id):
    tasks = {}
    while True:
        active_parser = await get_active_parser(user_id=user_id)  # повертає type+url+interval

        for parser in active_parser:
            key = (parser["type"], parser["url"])
            if key not in tasks or tasks[key].done():
                tasks[key] = asyncio.create_task(
                    run_parser(user_id, parser["type"], parser["url"])
                )

        await asyncio.sleep(60)  # перевіряємо нові підписки кожну хвилину



async def main():
    await create_scheduler(USER_ID)


if __name__ == "__main__":
    asyncio.run(main())
