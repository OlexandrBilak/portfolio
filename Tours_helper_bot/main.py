import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "###"
ADMIN_CHAT_ID = ###  
BOT_USERNAME = "###"

bot = telebot.TeleBot(TOKEN)

# ================== ХРАНЕННЯ СТАНІВ ==================
user_lang = {}          # chat_id -> ru / ua
anketa_state = {}       # chat_id -> step
anketa_data = {}        # chat_id -> answers

# ================== АНКЕТА ==================
ANKETA_KEYS = ["country", "city", "dates", "nights", "people", "budget", "hotel", "food", "wishes"]

ANKETA_Q_UA = [
    "▶️ Країна відпочинку?",
    "▶️ Можливі міста вильоту?",
    "▶️ Дати або період поїздки?",
    "▶️ Тривалість (7–10 ночей)?",
    "▶️ Кількість туристів та вік дітей?",
    "▶️ Орієнтовний бюджет?",
    "▶️ Категорія готелю (3*, 4*, 5*)?",
    "▶️ Тип харчування?",
    "❗️ Побажання?"
]

ANKETA_Q_RU = [
    "▶️ Страна отдыха?",
    "▶️ Возможные города вылета?",
    "▶️ Даты или период поездки?",
    "▶️ Продолжительность (7–10 ночей)?",
    "▶️ Количество туристов и возраст детей?",
    "▶️ Примерный бюджет?",
    "▶️ Категория отеля (3*, 4*, 5*)?",
    "▶️ Тип питания?",
    "❗️ Пожелания?"
]

# ================== СТАРТОВЕ ПОВІДОМЛЕННЯ ДЛЯ ГРУП ==================
def group_entry_message(chat_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🤖 Відкрити чат-бот", url=f"https://t.me/{BOT_USERNAME}?start=from_group"))
    bot.send_message(
        chat_id,
        "🤖 Привіт! Натисніть кнопку нижче, щоб відкрити бота в особистих повідомленнях та обрати розділ.",
        reply_markup=kb
    )

# ================== СТАРТ ==================
@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.type in ["group", "supergroup"]:
        group_entry_message(message.chat.id)
        return

    # приватний чат — вибір мови
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")
    )
    bot.send_message(message.chat.id, "Оберіть мову / Выберите язык:", reply_markup=keyboard)

# ================== МЕНЮ ==================
def show_menu(chat_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📄 Анкета", callback_data="anketa"))
    kb.add(InlineKeyboardButton("💳 Оплата", callback_data="oplata"))
    kb.add(InlineKeyboardButton("❌ Аннуляция", callback_data="annual"))
    kb.add(InlineKeyboardButton("🛡 Страховка", callback_data="insurance"))
    kb.add(InlineKeyboardButton("✈️ Вылет", callback_data="vylet"))
    kb.add(InlineKeyboardButton("📄 Важливо знати", callback_data="important"))
    bot.send_message(chat_id, "Выберите раздел:" if user_lang.get(chat_id,"ru")=="ru" else "Оберіть розділ:", reply_markup=kb)

# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id
    data = call.data
    bot.answer_callback_query(call.id)

    # --- вибір мови ---
    if data == "lang_ua":
        user_lang[chat_id] = "ua"
        show_menu(chat_id)
        return
    if data == "lang_ru":
        user_lang[chat_id] = "ru"
        show_menu(chat_id)
        return

    lang = user_lang.get(chat_id, "ru")

    # --- АНКЕТА ---
    if data == "anketa":
        anketa_state[chat_id] = 0
        anketa_data[chat_id] = {}
        intro = "🏖 Хочу на відпочинок\n\nВідповідайте на питання по черзі." if lang=="ua" else "🏖 Хочу на отдых\n\nОтвечайте на вопросы по очереди."
        bot.send_message(chat_id, intro)
        bot.send_message(chat_id, ANKETA_Q_UA[0] if lang=="ua" else ANKETA_Q_RU[0])
        return

    # ==================== ТЕКСТИ ПО КНОПКАМ ====================
    texts = {}
    if lang=="ua":
        texts = {
            "oplata": """🔍 Як відбувається оплата турів в Німеччині!?

❌ Готівкою оплата турів в Німеччині — ЗАБОРОНЕНО!

✔️ Після бронювання туроператор надішле рахунок на email.

✔️ Переказ коштів безпосередньо на рахунок туроператора.

✔️ ОПЛАТИТИ ТУР МОЖЕ БУДЬ ХТО.

✅ Види оплат:
✅ Sofortüberweisung — через банківський додаток
✅ Überweisung — банківський переказ
✅ Оплата через термінал""",
            "annual": """❌ Анулювання туру

1. У Німеччині туристичний договір захищає туроператора, а не покупця.

📌 Скасування пакетного туру майже завжди платне.

✔ Чим ближче дата вильоту — тим вища неустойка (до 90–100%).

✔ Навіть за поважних причин потрібні докази та страховка.""",
            "insurance": """🛡 Страхування від невиїзду

Допомагає компенсувати фінансові втрати при скасуванні поїздки з поважних причин.

✅ Покриває:
• Хвороба/травма
• Смерть близького
• Ускладнення вагітності
• Неочікуване звільнення
• Втрату майна
• Перездачу важливого іспиту

❌ Не покриває:
• Просто передумав
• Робочі причини без звільнення
• Проблеми з візою/паспортом
• Пандемії/епідемії""",
            "vylet": """✈️ Виліт — дуже важливо

⏰ Приїжджайте в аеропорт не пізніше ніж за 2 години до вильоту.

🔴 Не забудьте:
• Закордонний паспорт
• Ваучер на готель та інші документи

✅ Перевірте:
• Час вильоту та термінал
• Паспорт/візу
• Норми багажу""",
            "important": """✈️ Важливо знати

✔️ Виліт із зазначених міст
✔️ Авиаквитки на email або в особистому кабінеті
✔️ Перевірка рейсу, терміналу, документів
✔️ Онлайн-реєстрація відкривається заздалегідь
✔️ В аеропорту за 2 години до вильоту
✔️ Після прильоту отримати багаж та знайти стійку приймаючої сторони"""
        }
    else:
        texts = {
            "oplata": """🔍 Как происходит оплата туров в Германии?

❌ Оплата наличными запрещена!

✔️ После бронирования счёт на email.

✔️ Перевод средств напрямую туроператору.

✔️ ОПЛАТИТЬ ТУР МОЖЕТ ЛЮБОЙ ЧЕЛОВЕК.

✅ Способы оплаты:
✅ Sofortüberweisung
✅ Банковский перевод
✅ Оплата через терминал""",
            "annual": """❌ Аннуляция тура

1. В Германии туристический договор защищает туроператора, а не покупателя.

📌 Отмена пакетного тура почти всегда платная.

✔ Чем ближе дата вылета — тем выше неустойка (до 90–100%).

✔ Даже при уважительных причинах нужны доказательства и страховка.""",
            "insurance": """🛡 Страховка от невыезда

Помогает компенсировать финансовые потери при отмене поездки по уважительной причине.

✅ Покрывает:
• Болезнь/травму
• Смерть близкого
• Беременность с осложнениями
• Неожиданное увольнение
• Потерю имущества
• Пересдачу экзамена

❌ Не покрывает:
• Просто передумал
• Рабочие причины без увольнения
• Проблемы с визой/паспортом
• Пандемии/эпидемии""",
            "vylet": """✈️ Вылет — очень важно

⏰ Приезжайте за 2 часа до вылета.

🔴 Не забудьте:
• Загранпаспорт
• Ваучер на отель и документы

✅ Проверьте:
• Время вылета и терминал
• Паспорт/визу
• Нормы багажа""",
            "important": """✈️ Важно знать

✔️ Вылет из указанных городов
✔️ Авиабилеты на email или в личном кабинете
✔️ Проверка рейса, терминала, документов
✔️ Онлайн-регистрация открывается заранее
✔️ В аэропорту минимум за 2 часа до вылета
✔️ После прилёта получить багаж и найти стойку принимающей стороны"""
        }

    if data in texts:
        bot.send_message(chat_id, texts[data])

# ================== АНКЕТА: ОТВЕТЫ ==================
@bot.message_handler(func=lambda m: m.chat.id in anketa_state and m.text and not m.text.startswith('/'))
def anketa_steps(message):
    chat_id = message.chat.id
    lang = user_lang.get(chat_id, "ru")
    step = anketa_state[chat_id]

    # Зберігаємо відповідь
    anketa_data[chat_id][ANKETA_KEYS[step]] = message.text.strip()

    # Перехід до наступного кроку
    step += 1
    anketa_state[chat_id] = step

    # Якщо ще залишились питання
    if step < len(ANKETA_KEYS):
        bot.send_message(chat_id, ANKETA_Q_UA[step] if lang=="ua" else ANKETA_Q_RU[step])
        return

    # Анкета завершена
    data = anketa_data[chat_id]
    summary = "✅ Анкета заповнена!" if lang=="ua" else "✅ Анкета заполнена!"
    bot.send_message(chat_id, summary)

    # Формуємо повідомлення для адміністратора
    admin_text = f"""📩 Нова анкета / Новая анкета

Chat ID: {chat_id}

Країна/Страна: {data.get('country','')}
Місто/Город: {data.get('city','')}
Дати: {data.get('dates','')}
Ночі: {data.get('nights','')}
Люди: {data.get('people','')}
Бюджет: {data.get('budget','')}
Готель/Отель: {data.get('hotel','')}
Харчування/Питание: {data.get('food','')}
Побажання/Пожелания: {data.get('wishes','')}
"""
    bot.send_message(ADMIN_CHAT_ID, admin_text)

    # Очищаємо стан користувача
    anketa_state.pop(chat_id, None)
    anketa_data.pop(chat_id, None)

# ================== ЗАПУСК БОТА ==================
print("Бот працює")
bot.infinity_polling()
