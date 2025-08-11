from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os

# ❗️Chrome профіль для збереження сесії 
PROFILE_DIR = os.path.join(os.getcwd(), "fb_profile")

options = Options()
options.add_argument(f"--user-data-dir={PROFILE_DIR}")
options.add_experimental_option("detach", True)  

print("🟢 Відкриваємо браузер. Увійди у Facebook вручну, потім закрий вкладку.")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.facebook.com/marketplace")
