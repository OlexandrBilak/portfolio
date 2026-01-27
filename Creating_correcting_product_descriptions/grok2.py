import requests
from config import GROK_API_KEY, MODEL_GROK
from threading import Semaphore

GROK_LIMIT = Semaphore(1)

def parse_grok_response(text: str) -> dict:
    blocks = {
        "title": "",
        "keywords": "",
        "description": "",
        "h1": "",
        "content": ""
    }

    current = None
    for line in text.splitlines():
        line = line.strip()
        if line.upper() == "[TITLE]": current = "title"; continue
        if line.upper() == "[KEYWORDS]": current = "keywords"; continue
        if line.upper() == "[DESCRIPTION]": current = "description"; continue
        if line.upper() == "[H1]": current = "h1"; continue
        if line.upper() == "[CONTENT]": current = "content"; continue
        if current: blocks[current] += line + "\n"

    return {k: v.strip() for k, v in blocks.items()}

def grok_generate(lang, name, brand, category, prev_result=None, validator_comments=None):
    with GROK_LIMIT:
        prompt = open(f"prompts/grok_product_{lang.lower()}.txt", encoding="utf-8").read()

        correction_block = ""
        if prev_result and validator_comments:
            correction_block = f"""
ПОПЕРЕДНІЙ ТЕКСТ:
TITLE:
{prev_result['title']}

KEYWORDS:
{prev_result['keywords']}

DESCRIPTION:
{prev_result['description']}

H1:
{prev_result['h1']}

CONTENT:
{prev_result['content']}

ЗАУВАЖЕННЯ ВАЛІДАТОРА:
{validator_comments}

ЗАВДАННЯ:
Виправ ТІЛЬКИ зазначені зауваження.
Не переписуй текст заново.
Не погіршуй SEO, структуру і стиль.
"""

        payload = {
            "model": MODEL_GROK,
            "messages": [
                {
                    "role": "user",
                    "content": f"""
Название товара: {name}
Бренд: {brand}
Категория: {category}

{prompt}

{correction_block}
"""
                }
            ]
        }

        r = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=120
        )
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]

        return parse_grok_response(text)
