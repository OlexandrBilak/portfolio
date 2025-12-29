import dotenv
import os

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")

cookies = os.getenv("cookies")
headers = os.getenv("headers")