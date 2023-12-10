import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(".env")

DB_URL = os.getenv('DB_URL')
BOT_TOKEN = os.getenv("BOT_TOKEN")
WORKDIR = Path(__file__).parent

GOOGLE_CRED = WORKDIR / 'google_drive_creds.json'
PARENT_FOLDER_ID = "1aFpp1dI6AhL5ze4m3pQkhM9BhI3Dgski"
SHEET_ID = "1dM_JEexIh9MgK3HLPUwCz5lgqLvh-PahJru_B7KSd9g"
LOCALES_DIR = 'locales/'
type_of_meter = ["Gas", "Water", "Light", "Газ", "Світло", "Вода"]
