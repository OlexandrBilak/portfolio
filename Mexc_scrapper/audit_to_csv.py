import pandas as pd
import re

# =========================
# 1. HARD WHITELISTS
# =========================

CEX = {
    "MEXC", "Binance", "KuCoin", "Gate", "OKX", "Bybit", "Bitget",
    "HTX", "Kraken", "Coinbase", "BitMart", "WhiteBIT", "LBank",
    "BingX", "Bitrue", "CoinEx", "Poloniex", "WEEX", "KCEX",
    "XT.COM", "AscendEX", "BitKan", "Coinstore", "Tokpie",
    "Indodax", "Bitfinex", "HitBTC", "CEX.IO", "Bilaxy",
    "BigONE", "Bithumb", "Bitvavo", "DigiFinex", "ProBit"
}

DEX = {
    "Uniswap", "PancakeSwap", "Sushiswap", "Raydium",
    "Orca", "Meteora", "Curve", "DODO", "Quickswap",
    "Camelot", "Aerodrome", "BabySwap", "Netswap",
    "PulseX", "Phux", "SundaeSwap", "xExchange",
    "DeDust", "SquadSwap", "THENA", "LFJ", "Hydrex",
    "PumpSwap"
}

IGNORE = {
    "Ondo Global Markets",
    "Subnet Tokens",
    "Komodo Wallet",
    "First Ledger",
    "PearlFi V1.5",
    "Tapbit",
    "GoPax",
    "MMFinance (Cronos)"
}

# =========================
# 2. NORMALIZATION
# =========================

def normalize(name: str) -> str:
    if pd.isna(name):
        return ""

    name = str(name).strip()

    # Uniswap variants → one bucket
    if "uniswap" in name.lower():
        return "Uniswap"

    # Pancake variants
    if "pancakeswap" in name.lower():
        return "PancakeSwap"

    # Sushiswap variants
    if "sushi" in name.lower():
        return "Sushiswap"

    # Raydium variants
    if "raydium" in name.lower():
        return "Raydium"

    # Remove version suffixes
    name = re.sub(r"\(.*?\)", "", name).strip()
    name = re.sub(r"\s+V[0-9]+", "", name).strip()

    return name


# =========================
# 3. CLASSIFICATION
# =========================

def classify(exchange: str):
    if not exchange:
        return "UNKNOWN"

    if exchange in IGNORE:
        return "IGNORE"

    if exchange in CEX:
        return "CEX"

    if exchange in DEX:
        return "DEX"

    # fallback rules
    low = exchange.lower()

    if "swap" in low:
        return "DEX"

    if "dex" in low:
        return "DEX"

    if "ondo" in low:
        return "IGNORE"

    return "UNKNOWN"


# =========================
# 4. MAIN PROCESSOR
# =========================

def process_file(input_path: str, output_path: str):
    df = pd.read_excel(input_path)

    cex_counts = []
    dex_counts = []
    cleaned_all = []

    for _, row in df.iterrows():
        exchanges = str(row["all_exchange_names"]).split(";")

        cex_set = set()
        dex_set = set()
        final_list = []

        for ex in exchanges:
            ex = normalize(ex)
            cls = classify(ex)

            if cls == "CEX":
                cex_set.add(ex)
                final_list.append(ex)

            elif cls == "DEX":
                dex_set.add(ex)
                final_list.append(ex)

            else:
                # UNKNOWN/IGNORE → не рахуємо в статистику
                continue

        cex_counts.append(len(cex_set))
        dex_counts.append(len(dex_set))
        cleaned_all.append(";".join(sorted(set(final_list))))

    df["distinct_cex_exchange_count"] = cex_counts
    df["distinct_dex_exchange_count"] = dex_counts
    df["distinct_total_exchange_count"] = df["distinct_cex_exchange_count"] + df["distinct_dex_exchange_count"]
    df["all_exchange_names"] = cleaned_all

    df.to_excel(output_path, index=False)
    df.to_csv(output_path.replace(".xlsx", ".csv"), index=False)

    print("DONE:", output_path)


# =========================
# 5. RUN
# =========================

if __name__ == "__main__":
    process_file(
        input_path="output_fixed.xlsx",
        output_path="output_fixed2.xlsx"
    )