import pandas as pd

# файли
xlsx_path = "aboutskin_products_updated.xlsx"
csv_path = "aboutskin_product_sorted.csv"

# бренди, які залишаємо
BRANDS_TO_KEEP = [
    "ACWELL",
    "Bad Skin",
    "Ekseption",
    "Fusion Meso",
    "Koy",
    "La Pianta",
    "Nuselique",
    "Usolab",
]

# читаємо xlsx
df = pd.read_excel(xlsx_path, dtype=str).fillna("")

# фільтр по бренду
df = df[df["brand"].isin(BRANDS_TO_KEEP)]

# фіксований порядок колонок (АКТУАЛЬНИЙ)
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

# гарантуємо, що всі колонки існують
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

print(f"[OK] CSV з фільтрацією по брендах створено: {csv_path}")
