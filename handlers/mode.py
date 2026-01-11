from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import subprocess
from pathlib import Path

from keyboards.keyboard import mainmenu_keyboard, mode_keyboard
from states.states import Mode
from handlers.clear import clear_cmd
from services.chat_gpt import get_transformation, get_translation, get_learn

mode_router = Router()
messages = []


def ogg_to_wav(input_path: str):
    input_path = Path(input_path)
    output_path = input_path.with_suffix(".wav")

    subprocess.run(
        [
            "ffmpeg",
            "-y",                
            "-i", str(input_path),
            "-ar", "16000",      
            "-ac", "1",          
            str(output_path)
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    return str(output_path)




@mode_router.message(Command("mode"))
async def mode(message: Message, state: FSMContext):
    await state.set_state(Mode.choosing_mode)

    await message.answer('''
🔧 Вибір режиму роботи

Обери, як саме я маю обробляти твої повідомлення 👇

🧠 Перетворення  
    • Перетворюю голосові повідомлення у текст  
    • Аналізую відео та витягую текст  
    • Підходить для розшифровки аудіо та відео

🌍 Переклад  
    • Перекладаю текст різними мовами  
    • Можу визначити мову автоматично  
    • Підходить для навчання та роботи

📚 Навчання  
    • Пояснюю складні теми простими словами  
    • Допомагаю з навчанням, термінами та прикладами  
    • Підходить для навчання і саморозвитку

📌 Поточний режим буде застосовуватись до всіх наступних повідомлень

⬇️ Обери режим кнопками нижче
''', reply_markup=mainmenu_keyboard)
    

@mode_router.message(F.text == "⬅️ Головне меню")
async def back_to_main(message: Message, state: FSMContext):
    messages.clear()
    await state.clear()
    await state.set_state(Mode.choosing_mode)

    await message.answer('''
🧹 Історію очищено

🔧 Вибір режиму роботи

Обери, як саме я маю обробляти твої повідомлення 👇

🧠 Перетворення  
    • Перетворюю голосові повідомлення у текст  
    • Аналізую відео та витягую текст  
    • Підходить для розшифровки аудіо та відео

🌍 Переклад  
    • Перекладаю текст різними мовами  
    • Можу визначити мову автоматично  
    • Підходить для навчання та роботи

📚 Навчання  
    • Пояснюю складні теми простими словами  
    • Допомагаю з навчанням, термінами та прикладами  
    • Підходить для навчання і саморозвитку

📌 Поточний режим буде застосовуватись до всіх наступних повідомлень

⬇️ Обери режим кнопками нижче
''', reply_markup=mainmenu_keyboard)


@mode_router.message(F.text == "🧹 Очистити історію")
async def clear_button(message: Message, state: FSMContext):
    await clear_cmd(message, state, messages)


@mode_router.message(Command("clear"))
async def clear_command(message: Message, state: FSMContext):
    await clear_cmd(message, state, messages)


@mode_router.message(Mode.choosing_mode)
async def mode_choose(message: Message, state: FSMContext):
    if message.text == '🧠 Перетворення':
        await state.set_state(Mode.transformation)
        await message.answer('🔤 Тепер я буду перетворювати твої повідомлення на текст', reply_markup=mode_keyboard)

    elif message.text == '🌍 Переклад':
        await state.set_state(Mode.translating)
        await message.answer('🗒 Тепер я буду перекладати твої повідомлення різними мовами', reply_markup=mode_keyboard)

    elif message.text == '📚 Навчання':
        await state.set_state(Mode.learn)
        await message.answer('🤓 Тепер я буду пояснювати складні теми простими словами', reply_markup=mode_keyboard)

    elif message.text == 'ℹ️ Довідка':
        await message.answer('''
ℹ️ Довідка по боту

🤖 Я — ChatGPT-бот, який відповідає з урахуванням контексту діалогу.

📌 Команди:
    /start — почати роботу з ботом
    /help — показати цю довідку
    /mode — змінити режим роботи
    /clear — очистити історію діалогу

🔧 Режими роботи:
    🧠 Перетворення  
        • Перетворюю голосові повідомлення у текст  
        • Аналізую відео та витягую текст  
        • Підходить для розшифровки аудіо та відео

    🌍 Переклад  
        • Перекладаю текст між різними мовами  
        • Можу визначити мову автоматично  
        • Підходить для навчання та роботи

    📚 Навчання  
        • Пояснюю складні теми простими словами  
        • Допомагаю з кодом, термінами та прикладами  
        • Підходить для навчання і саморозвитку

🧠 Контекст:
    • Я памʼятаю попередні повідомлення
    • Можеш очистити історію командою /clear

⚠️ Якщо відповідь довго генерується або сталася помилка — спробуй пізніше

🚀 Просто напиши повідомлення — я відповім!
    ''', reply_markup=mainmenu_keyboard)

    else:
        await message.answer('❗ Будь ласка, обери режим кнопками нижче 👇',reply_markup=mainmenu_keyboard)


@mode_router.message(Mode.transformation, F.voice)
async def transformation_voice(message: Message):
    voice = message.voice

    voice_dir = Path("voice")
    voice_dir.mkdir(exist_ok=True)

    ogg_path = voice_dir / f"{voice.file_id}.ogg"

    file = await message.bot.get_file(voice.file_id)
    await message.bot.download_file(file.file_path, ogg_path)

    wav_path = ogg_to_wav(str(ogg_path))

    result = await get_transformation(audio_file=wav_path, all_message=messages)

    await message.answer(result, reply_markup=mode_keyboard)


@mode_router.message(Mode.transformation, F.video | F.video_note)
async def transformation_video(message: Message):
    video = message.video or message.video_note

    video_dir = Path("video")
    video_dir.mkdir(exist_ok=True)

    video_path = video_dir / f"{video.file_id}.mp4"

    file = await message.bot.get_file(video.file_id)
    await message.bot.download_file(file.file_path, video_path)

    result = await get_transformation(
        audio_file=str(video_path),
        all_message=messages
    )

    await message.answer(result, reply_markup=mode_keyboard)


@mode_router.message(Mode.transformation, F.text)
async def transformation_text_block(message: Message):
    await message.answer(
        "🧠 Режим перетворення працює **тільки з аудіо та відео** 🎧🎥\n\n"
        "ℹ️ Надішли голосове повідомлення або відео.\n"
        "🔄 Для роботи з текстом — зміни режим командою /mode",
        reply_markup=mode_keyboard
    )


@mode_router.message(Mode.translating)
async def translation(message: Message, state: FSMContext):
    if message.text not in ('⬅️ Головне меню', '🧹 Очистити історію'):
        text = message.text

        # Просте визначення: якщо є українські літери, вважаємо українською
        if any("а" <= c <= "я" or "А" <= c <= "Я" for c in text):
            # Запитуємо мову
            await state.set_state(Mode.waiting_for_target_language)
            await state.update_data(source_text=text)
            await message.answer("Текст українською. На яку мову перекласти? ")
        else:
            # Не українська → автоматично переклад на українську
            translated = await get_translation(text=text, target_language="uk")
            await message.answer(translated, reply_markup=mode_keyboard)



@mode_router.message(Mode.waiting_for_target_language)
async def translate_to_target(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("source_text")
    target_language = message.text.strip().lower()

    translated = await get_translation(text=text, target_language=target_language)
    await message.answer(translated, reply_markup=mode_keyboard)
    await state.clear()
    await state.set_state(Mode.translating)


@mode_router.message(Mode.learn)
async def learn(message: Message):
    if message.text not in ('⬅️ Головне меню', '🧹 Очистити історію'):
        text = message.text
        messages.append(text)

        response = await get_learn(text, messages)
        await message.answer(response, reply_markup=mode_keyboard)
    
