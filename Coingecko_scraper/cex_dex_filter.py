import pandas as pd

INPUT_FILE = "coingecko_all.xlsx"
OUTPUT_FILE = "coingecko.xlsx"

# Читаємо файл
df = pd.read_excel(INPUT_FILE)

# Фільтруємо рядки: тільки ті, де CEX_count <=2 і DEX_count <=2
df_filtered = df[(df["CEX_count"] <= 2) & (df["DEX_count"] <= 2)]

# Зберігаємо у новий файл
df_filtered.to_excel(OUTPUT_FILE, index=False)

print(f"[DONE] Фільтрована таблиця збережена: {OUTPUT_FILE} ({len(df_filtered)} рядків)")
