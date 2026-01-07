import pandas as pd
import re

# читаємо Excel
df = pd.read_excel("aboutskin_products.xlsx", dtype=str).fillna("")


# функція для витягання тексту після ключового слова
def extract_after_keyword(text, keyword):
    """
    Повертає текст після ключового слова до кінця блоку або рядка
    """
    pattern = re.compile(rf"{keyword}\s*[:\s]*(.+?)(?=(\n\S|$))", re.IGNORECASE | re.DOTALL)
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return ""


# проходимо по всім рядкам
for idx, row in df.iterrows():
    text = row.get("short_descriptions_text", "") + "\n" + row.get("full_description_text", "")

    # оновлюємо тільки якщо поле пусте
    if not row.get("compound", ""):
        compound = extract_after_keyword(text, "Склад")
        df.at[idx, "compound"] = compound

    if not row.get("use_method", ""):
        use_method = extract_after_keyword(text, "Спосіб використання")
        df.at[idx, "use_method"] = use_method

# зберігаємо результат
df.to_excel("aboutskin_products_updated.xlsx", index=False)
print("[OK] Колонки compound та use_method оновлено лише для порожніх полів.")
