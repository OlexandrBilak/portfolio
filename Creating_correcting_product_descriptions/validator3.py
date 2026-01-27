from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_GPT

client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------------
# Стара функція: просто OK / NOT_OK
# ------------------------------
def validate_text(lang: str, data: dict) -> dict:
    """
    Стара функція для логів та перевірки
    Повертає {"status": "OK"} або {"status": "NOT_OK", "comments": "..."}
    """
    prompt_path = f"prompts/validator_{lang.lower()}.txt"
    validator_prompt = open(prompt_path, encoding="utf-8").read()

    full_text = f"""
HTML TITLE:
{data['title']}

META KEYWORDS:
{data['keywords']}

META DESCRIPTION:
{data['description']}

H1:
{data['h1']}

CONTENT:
{data['content']}
"""
    response = client.chat.completions.create(
        model=MODEL_GPT,
        messages=[
            {"role": "system", "content": validator_prompt},
            {"role": "user", "content": full_text}
        ],
        temperature=0
    )

    answer = response.choices[0].message.content.strip()
    if answer.startswith("OK"):
        return {"status": "OK"}
    else:
        return {"status": "NOT_OK", "comments": answer}

# ------------------------------
# Нова функція: реально виправляє текст
# ------------------------------
def correct_text_by_gpt(lang: str, data: dict) -> dict:
    """
    Перевіряє та коригує текст. Повертає словник з ключами:
    title, keywords, description, h1, content
    """
    # Новий промпт для реальної корекції
    validator_prompt = f"""
Ти — незалежний SEO-редактор і копірайтер.
Отримав готовий текст від AI: HTML title, meta description, meta keywords, H1, основний текст.
Твоя задача:
- Виправити текст так, щоб він повністю відповідав критеріям SEO, читабельності та практичної цінності.
- Дотримуватися професійного, людського стилю.
- Зберегти структуру і HTML-теги.

Обов'язково повертати результат у СТРОГОМУ форматі:

[TITLE]
...

[KEYWORDS]
...

[DESCRIPTION]
...

[H1]
...

[CONTENT]
...
"""

    full_text = f"""
HTML TITLE:
{data['title']}

META KEYWORDS:
{data['keywords']}

META DESCRIPTION:
{data['description']}

H1:
{data['h1']}

CONTENT:
{data['content']}
"""

    user_message = f"""
Виправ текст відповідно до вищевказаних інструкцій.
Поверни готовий результат у строгому форматі блоків [TITLE], [KEYWORDS], [DESCRIPTION], [H1], [CONTENT].
"""

    response = client.chat.completions.create(
        model=MODEL_GPT,
        messages=[
            {"role": "system", "content": validator_prompt},
            {"role": "user", "content": full_text + "\n\n" + user_message}
        ],
        temperature=0
    )

    corrected_text = response.choices[0].message.content.strip()

    # Лог для дебагу
    print("=== ChatGPT corrected text ===")
    print(corrected_text)
    print("================================")

    # Парсимо у блоки
    blocks = {"title": "", "keywords": "", "description": "", "h1": "", "content": ""}
    current = None
    for line in corrected_text.splitlines():
        line = line.strip()
        if line.upper() == "[TITLE]": current = "title"; continue
        if line.upper() == "[KEYWORDS]": current = "keywords"; continue
        if line.upper() == "[DESCRIPTION]": current = "description"; continue
        if line.upper() == "[H1]": current = "h1"; continue
        if line.upper() == "[CONTENT]": current = "content"; continue
        if current:
            blocks[current] += line + "\n"

    return {k: v.strip() for k, v in blocks.items()}
