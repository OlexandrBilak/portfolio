import asyncio
import pandas as pd
from sheets import get_tariffs

tariffs_df = pd.DataFrame()


async def tariff_updater():
    """Фонове оновлення тарифів кожні 60 секунд"""
    global tariffs_df
    while True:
        try:
            tariffs_df = get_tariffs()
            print("Tariffs updated:", len(tariffs_df))
        except Exception as e:
            print("Tariff update error:", e)
        await asyncio.sleep(60)


def get_cached_tariffs():
    """Повертає останній кеш тарифів"""
    return tariffs_df