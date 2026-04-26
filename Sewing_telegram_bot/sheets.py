import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from config import *

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
client = gspread.authorize(creds)

sheet = client.open(SHEET_NAME)

tariff_ws = sheet.worksheet(TARIFF_SHEET)
log_ws = sheet.worksheet(LOG_SHEET)


def get_tariffs():
    data = tariff_ws.get_all_records()
    return pd.DataFrame(data)


def find_tariff(model, department, operation):

    df = get_tariffs()

    row = df[
        (df["Модель"] == model) &
        (df["Відділ"] == department) &
        (df["Операція"] == operation)
    ]

    if row.empty:
        return None

    return row.iloc[0]


def add_log(data):

    log_ws.append_row([
        data["date"],
        data["name"],
        data["department"],
        data["model"],
        data["operation"],
        data["amount"],
        data["sum"],
        data["order"],
        data["route"],
        data["barcode"],
        data["color"],
        data["size"],
        data["comment"]
    ])