import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = "# # # TOKEN # # #"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Каталог товарів")],
        [KeyboardButton(text="ℹ️ Про нас"), KeyboardButton(text="📞 Контакти")]
    ],
    resize_keyboard=True
)

# Список товарів (приклад)
products = [
    {
        "name": "Смартфон iPhone 12",
        "price": "15000₴",
        "description": "Новий iPhone 12, 128GB, чорний.",
        "photo": "https://img.jabko.ua/image/cache//catalog/products/2022/06/031208/apple_iphone12mini-iphone12max-h%20(1)full.jpeg.webp"
    },
    {
        "name": "Ноутбук MacBook Pro",
        "price": "25000₴",
        "description": "Ноутбук MacBook Pro, 16GB RAM, SSD 512GB.",
        "photo": "https://www.apple.com/v/macbook-pro/ar/images/overview/welcome/welcome_hero_endframe__c61x1mv7kgqe_large.jpg"
    }
]

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привіт! Це бот-каталог техніки 💻\nОберіть опцію нижче 👇",
        reply_markup=main_menu
    )

@dp.message()
async def handle_menu(message: types.Message):
    if message.text == "📦 Каталог товарів":
        for product in products:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🛒 Замовити", callback_data=f"buy_{product['name']}")]
                ]
            )
            await message.answer_photo(
                photo=product["photo"],
                caption=f"{product['name']}\n{product['description']}\n💰 Ціна: {product['price']}",
                reply_markup=keyboard
            )
    elif message.text == "ℹ️ Про нас":
        await message.answer("Це демо бот-каталог техніки на Python 🐍")
    elif message.text == "📞 Контакти":
        await message.answer("Наш менеджер: @n_o_n_a_m_e_69")
    else:
        await message.answer("❗ Оберіть дію з меню")

@dp.callback_query()
async def handle_order(callback: types.CallbackQuery):
    if callback.data.startswith("buy_"):
        product_name = callback.data[4:]
        await callback.message.answer(f"✅ Дякуємо! Ви замовили {product_name}.\nНаш менеджер скоро зв'яжеться з вами.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
