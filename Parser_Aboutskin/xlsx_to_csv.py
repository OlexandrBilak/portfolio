import pandas as pd

# файли
xlsx_path = "aboutskin_products_updated.xlsx"
csv_path = "aboutskin_products_final.csv"

# читаємо xlsx
df = pd.read_excel(xlsx_path, dtype=str).fillna("")

# ФІКСОВАНИЙ порядок колонок
COLUMNS_ORDER = [
    "item_url",
    "category",
    "subcategory",
    "skin-problem",
    "type-product",
    "type-skin",
    "is_tester",
    "is_instock",
    "title",
    "short_description_html",
    "short_descriptions_text",
    "full_description_html",
    "full_description_text",
    "price",
    "currency",
    "amount",
    "brand",
    "article",
    "compound",
    "use_method",
    "img_url",
]

# гарантуємо наявність усіх колонок
for col in COLUMNS_ORDER:
    if col not in df.columns:
        df[col] = ""

# приводимо порядок
df = df[COLUMNS_ORDER]

# зберігаємо CSV
df.to_csv(
    csv_path,
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print(f"[OK] CSV створено успішно: {csv_path}")
