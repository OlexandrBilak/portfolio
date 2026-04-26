import asyncio
import aiohttp
import pandas as pd
import ssl
import os
import certifi
from datetime import datetime

# -------------------------
# URLS
# -------------------------
MEXC_URL = "https://api.mexc.com/api/v3/ticker/24hr"
COINGECKO_LIST_URL = "https://api.coingecko.com/api/v3/coins/list"
COINGECKO_COIN_URL = "https://api.coingecko.com/api/v3/coins/{}"

USD_QUOTES = ["USDT", "USDC", "BUSD"]
TIMEOUT = aiohttp.ClientTimeout(total=30)
REQUEST_DELAY = 12  # секунд = 5 запитів/хв

FINAL_FILE = "erum_mexc_low_volume_tokens_final.xlsx"
AUDIT_FILE = "erum_mexc_low_volume_tokens_full_audit.xlsx"

# -------------------------
# RESUME
# -------------------------
def load_processed_tokens():
    processed = set()

    # FINAL
    if os.path.exists(FINAL_FILE):
        df = pd.read_excel(FINAL_FILE)
        if "token_symbol" in df.columns:
            processed.update(df["token_symbol"].astype(str).str.upper())

    # AUDIT
    if os.path.exists(AUDIT_FILE):
        df = pd.read_excel(AUDIT_FILE)
        if "token_symbol" in df.columns:
            processed.update(df["token_symbol"].astype(str).str.upper())

    print(f"[RESUME] Total already processed (final + audit): {len(processed)} tokens")

    return processed


# -------------------------
# FAST APPEND (NO DUPES / NO FULL REWRITE)
# -------------------------
def append_row_to_excel(file, row: dict):
    df = pd.DataFrame([row])

    if not os.path.exists(file):
        df.to_excel(file, index=False)
        return

    with pd.ExcelWriter(file, mode="a", engine="openpyxl", if_sheet_exists="overlay") as writer:
        sheet = writer.sheets.get("Sheet1")
        startrow = sheet.max_row if sheet else 0
        df.to_excel(writer, index=False, header=False, startrow=startrow)

    print(f"[APPEND] {row['token_symbol']} appended to {file}")


# -------------------------
# SESSION
# -------------------------
def get_session():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context, limit=20),
        timeout=TIMEOUT
    )

# -------------------------
# FETCH WITH RETRY
# -------------------------
async def fetch_json(session, url, retries=5, delay=2):
    for attempt in range(retries):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 429:
                    print(f"[RATE LIMIT] {url} attempt {attempt+1}, sleep {delay}s")
        except Exception as e:
            print(f"[ERROR] {url} attempt {attempt+1}: {e}")

        await asyncio.sleep(delay)
        delay *= 2

    return None

# -------------------------
# SYMBOL PARSER
# -------------------------
def parse_symbol(symbol: str):
    for quote in USD_QUOTES + ["BTC", "ETH"]:
        if symbol.endswith(quote):
            return symbol[:-len(quote)], quote
    return None, None

# -------------------------
# AGGREGATE
# -------------------------
def aggregate_tokens(data):
    tokens = {}
    btc_price = None
    eth_price = None

    for item in data:
        if item["symbol"] == "BTCUSDT":
            btc_price = float(item["lastPrice"])
        if item["symbol"] == "ETHUSDT":
            eth_price = float(item["lastPrice"])

    for item in data:
        symbol = item.get("symbol")
        quote_volume = float(item.get("quoteVolume", 0))
        base, quote = parse_symbol(symbol)
        if not base:
            continue

        if base not in tokens:
            tokens[base] = {"pairs": [], "volume_usd": 0}

        tokens[base]["pairs"].append(symbol)

        if quote in USD_QUOTES:
            tokens[base]["volume_usd"] += quote_volume
        elif quote == "BTC" and btc_price:
            tokens[base]["volume_usd"] += quote_volume * btc_price
        elif quote == "ETH" and eth_price:
            tokens[base]["volume_usd"] += quote_volume * eth_price

    return tokens

# -------------------------
# FILTER
# -------------------------
def filter_low_volume(tokens, threshold=200_000):
    final = []
    for token, data in tokens.items():
        vol = data["volume_usd"]
        if 0 < vol < threshold:
            final.append({
                "token_symbol": token,
                "mexc_24h_volume_usd": round(vol, 2),
                "pairs": ";".join(data["pairs"])
            })
    return final

# -------------------------
# COINGECKO
# -------------------------
async def fetch_coingecko_list(session):
    return await fetch_json(session, COINGECKO_LIST_URL)

def build_symbol_map(coins):
    mapping = {}
    for c in coins:
        symbol = c["symbol"].upper()
        mapping.setdefault(symbol, []).append(c)
    return mapping

async def fetch_coin(session, coin_id):
    return await fetch_json(session, COINGECKO_COIN_URL.format(coin_id))

# -------------------------
# SAFE EXTRACT
# -------------------------
def extract_data(coin):
    links = coin.get("links", {})

    homepage_list = links.get("homepage") or []
    website = homepage_list[0] if homepage_list else ""

    twitter = links.get("twitter_screen_name")
    telegram = links.get("telegram_channel_identifier")

    twitter_link = f"https://twitter.com/{twitter}" if twitter else ""
    telegram_link = f"https://t.me/{telegram}" if telegram else ""

    exchanges = set()
    cex = set()
    dex = set()

    for t in coin.get("tickers", []):
        market = t.get("market", {})
        name = market.get("name")
        identifier = market.get("identifier", "")

        if not name:
            continue

        exchanges.add(name)

        if "dex" in identifier:
            dex.add(name)
        else:
            cex.add(name)

    return website, twitter_link, telegram_link, exchanges, cex, dex

# -------------------------
# ENRICH (MAIN FIXED)
# -------------------------
async def enrich_tokens(session, tokens, pause=4):
    print("Fetching CoinGecko list...")
    cg_list = await fetch_coingecko_list(session)

    if not cg_list:
        print("[ERROR] CoinGecko list failed")
        return

    symbol_map = build_symbol_map(cg_list)

    for idx, t in enumerate(tokens, start=1):
        symbol = t["token_symbol"]
        candidates = symbol_map.get(symbol, [])

        if not candidates:
            t["reason"] = "NOT_FOUND_IN_COINGECKO"
            append_row_to_excel(AUDIT_FILE, t)
            continue

        coin_id = candidates[0]["id"]
        coin = await fetch_coin(session, coin_id)

        if not coin:
            t["reason"] = "FETCH_FAILED"
            append_row_to_excel(AUDIT_FILE, t)
            continue

        website, twitter, telegram, exchanges, cex, dex = extract_data(coin)

        if len(exchanges) > 5:
            t["reason"] = "TOO_MANY_EXCHANGES"
            append_row_to_excel(AUDIT_FILE, t)
        else:
            row = {
                "token_name": coin.get("name"),
                "token_symbol": symbol,
                "mexc_24h_volume_usd": t["mexc_24h_volume_usd"],
                "external_token_id": coin_id,
                "distinct_total_exchange_count": len(exchanges),
                "distinct_cex_exchange_count": len(cex),
                "distinct_dex_exchange_count": len(dex),
                "all_exchange_names": ";".join(exchanges),
                "website": website,
                "telegram_links": telegram,
                "twitter_links": twitter,
                "checked_at": datetime.utcnow().isoformat()
            }

            append_row_to_excel(FINAL_FILE, row)

        # 🔥 rate limit control (5 req/min)
        print(f"[LOG] {idx}/{len(tokens)} processed")
        await asyncio.sleep(REQUEST_DELAY)


# -------------------------
# MAIN
# -------------------------
async def main():
    async with get_session() as session:
        print("Fetching MEXC...")
        mexc_data = await fetch_json(session, MEXC_URL)

        print(f"Pairs: {len(mexc_data)}")

        tokens = aggregate_tokens(mexc_data)
        print(f"Tokens: {len(tokens)}")

        filtered = filter_low_volume(tokens)

        processed = load_processed_tokens()

        filtered = [
            t for t in filtered
            if t["token_symbol"].upper() not in processed
        ]

        print(f"[RESUME] Remaining: {len(filtered)}")

        await enrich_tokens(session, filtered)

    print("DONE")


if __name__ == "__main__":
    asyncio.run(main())