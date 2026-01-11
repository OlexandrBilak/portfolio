import asyncio
from aiogram import Bot, Dispatcher

from config import TELEGRAM_TOKEN
from handlers.start import start_router
from handlers.help import help_router
from handlers.mode import mode_router


async def main():
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.include_routers(
        start_router,
        help_router,
        mode_router,
    )

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        print("[*] Бот запущено...")
        asyncio.run(main())
    except:
        print("[*] Бот зупинено...")