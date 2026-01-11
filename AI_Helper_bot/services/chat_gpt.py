from openai import AsyncOpenAI 
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def get_transformation(audio_file, all_message: list[str]):
    # Whisper — аудіо → текст
    with open(audio_file, "rb") as f:
        transcription = await client.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )
    raw_text = transcription.text

    return raw_text


async def get_translation(text: str, target_language: str = "uk"):
    system_prompt = f"""
Ти — професійний перекладач.

Правила:
- Перекладай ТІЛЬКИ текст користувача
- Перекладай на мову: {target_language}
- Не додавай пояснень або коментарів
- Не змінюй зміст
- Зберігай форматування (абзаци, списки)
"""

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


async def get_learn(user_text, all_message: list[str]):
    system_prompt = """
Ти — професійний AI-асистент для навчання та пояснень.

Твоя задача:
- Пояснювати будь-які терміни, концепції, явища, теми простими словами.
- Наводити зрозумілі приклади, порівняння або аналогії.
- Розбивати складні теми на зрозумілі кроки.
- Використовувати короткі абзаци та просту мову.
- Не використовувати складні терміни без пояснення.
- Не давати непотрібні додаткові відомості, які не стосуються запиту.
- Відповідай українською мовою.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in all_message[-5:]:
        messages.append({"role": "user", "content": msg})
        
    messages.append({"role": "user", "content": user_text})
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.3
    )
    
    return response.choices[0].message.content
