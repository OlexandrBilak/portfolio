import asyncio
import aiohttp
import pandas as pd
import ssl
import certifi
import os
import json
import time
from datetime import datetime

INPUT_FILE = "input.xlsx"
OUTPUT_FILE = "fixed_output.xlsx"
AUDIT_FILE = "fixed_audit.xlsx"
CHECKPOINT_FILE = "checkpoint.json"

COINGECKO_COIN_URL = "https://api.coingecko.com/api/v3/coins/{}"

MIN_INTERVAL = 12.5

LAST_REQUEST_TIME = 0

async def rate_limit():
    global LAST_REQUEST_TIME

    now = time.time()
    wait_time = MIN_INTERVAL - (now - LAST_REQUEST_TIME)

    if wait_time > 0:
        await asyncio.sleep(wait_time)

    LAST_REQUEST_TIME = time.time()


# -------------------------
# SESSION
# -------------------------
def get_session():
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    return aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=ssl_context),
    )


# -------------------------
# CHECKPOINT
# -------------------------
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f).get("last_index", -1)
    return -1


def save_checkpoint(index):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump({"last_index": index}, f)


# -------------------------
# SAVE PROGRESS
# -------------------------
def save_progress(final, audit):
    pd.DataFrame(final).to_excel(OUTPUT_FILE, index=False)
    pd.DataFrame(audit).to_excel(AUDIT_FILE, index=False)


# -------------------------
# FETCH (RETRY SAFE)
# -------------------------
async def fetch_json(session, url, retries=5, delay=3):
    for attempt in range(retries):
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()

                if resp.status == 429:
                    print(f"[429] retry {attempt+1}, backoff {delay}s")

        except Exception as e:
            print(f"[ERROR] {e}")

        await asyncio.sleep(delay)
        delay *= 2

    return None


# -------------------------
# MEXC CHECK
# -------------------------
def is_mexc_listed(coin):
    for t in coin.get("tickers", []):
        market = t.get("market", {})
        if market.get("name", "").lower() == "mexc":
            return True
    return False


# -------------------------
# EXTRACT
# -------------------------
def extract_data(coin):
    links = coin.get("links", {})

    website = (links.get("homepage") or [""])[0]

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

        if not name:
            continue

        exchanges.add(name)

        if "dex" in (market.get("identifier") or ""):
            dex.add(name)
        else:
            cex.add(name)

    return website, twitter_link, telegram_link, exchanges, cex, dex


# -------------------------
# MAIN
# -------------------------
async def fix_tokens():
    df = pd.read_excel(INPUT_FILE)

    last_index = load_checkpoint()
    print(f"RESUME FROM: {last_index + 1}")

    final = []
    audit = []

    if os.path.exists(OUTPUT_FILE):
        try:
            final = pd.read_excel(OUTPUT_FILE).to_dict("records")
        except:
            final = []

    if os.path.exists(AUDIT_FILE):
        try:
            audit = pd.read_excel(AUDIT_FILE).to_dict("records")
        except:
            audit = []

    async with get_session() as session:

        for idx, row in df.iterrows():

            if idx <= last_index:
                continue

            symbol = row["token_symbol"]
            coin_id = row["external_token_id"]

            print(f"[{idx}] Checking {symbol} ({coin_id})")

            # 🔥 RATE LIMIT HERE (CRITICAL)
            await rate_limit()

            coin = await fetch_json(session, COINGECKO_COIN_URL.format(coin_id))

            if not coin:
                row["reason"] = "FETCH_FAILED"
                audit.append(row.to_dict())
                save_progress(final, audit)
                save_checkpoint(idx)
                continue

            if not is_mexc_listed(coin):
                row["reason"] = "NO_MEXC_LISTING"
                audit.append(row.to_dict())
                save_progress(final, audit)
                save_checkpoint(idx)
                continue

            website, twitter, telegram, exchanges, cex, dex = extract_data(coin)

            if len(exchanges) > 5:
                row["reason"] = "TOO_MANY_EXCHANGES"
                audit.append(row.to_dict())
                save_progress(final, audit)
                save_checkpoint(idx)
                continue

            fixed_row = {
                "token_name": coin.get("name"),
                "token_symbol": symbol,
                "mexc_24h_volume_usd": row["mexc_24h_volume_usd"],
                "external_source_used": "coingecko",
                "external_token_id": coin_id,
                "distinct_total_exchange_count": len(exchanges),
                "distinct_cex_exchange_count": len(cex),
                "distinct_dex_exchange_count": len(dex),
                "all_exchange_names": ";".join(exchanges),
                "website": website,
                "telegram_links": telegram,
                "twitter_links": twitter,
                "source_last_checked_at_utc": datetime.utcnow().isoformat(),
                "notes": ""
            }

            final.append(fixed_row)

            save_progress(final, audit)
            save_checkpoint(idx)

            print(f"[OK] {symbol}")

    print("DONE")


if __name__ == "__main__":
    asyncio.run(fix_tokens())
