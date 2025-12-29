import asyncio

from aiogram import Bot, Dispatcher

from config import TOKEN
from handlers.start import start_router
from handlers.help import help_router
from handlers.add import add_router
from handlers.list import list_router
from states.subscriptions import subscriptions_router
from states.changes import changes_router



async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        start_router,
        help_router,
        add_router,
        subscriptions_router,
        list_router,
        changes_router
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("[*]INFO Бот запущено!")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("[*]INFO Бот зупинено!")