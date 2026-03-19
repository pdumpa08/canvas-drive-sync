import os
from dotenv import load_dotenv

load_dotenv()

# Canvas (Direct Access)
CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_ACCESS_TOKEN = os.getenv("CANVAS_ACCESS_TOKEN") # New!

# Google (OAuth still needed)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SYNC_INTERVAL_SECONDS = int(os.getenv("SYNC_INTERVAL_SECONDS", 1))
DB_PATH = os.getenv("DB_PATH", "sync.db")