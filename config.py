import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

BOT_TOKEN = os.getenv("BOT_TOKEN")

_admin_raw = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = {
    int(x.strip())
    for x in _admin_raw.split(",")
    if x.strip().isdigit()
}

REPORTS_FOR_BAN = int(os.getenv("REPORTS_FOR_BAN", "5"))
SPAM_MAX_MESSAGES = int(os.getenv("SPAM_MAX_MESSAGES", "6"))
SPAM_WINDOW_SECONDS = float(os.getenv("SPAM_WINDOW_SECONDS", "3"))

VIP_COIN_PRICE = int(os.getenv("VIP_COIN_PRICE", "100"))
VIP_STARS_PRICE = int(os.getenv("VIP_STARS_PRICE", "50"))
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "")
STARTER_COINS = int(os.getenv("STARTER_COINS", "20"))

_ref = os.getenv("DATABASE_URL")
if _ref:
    _db = _ref
    if _db.startswith("postgres://"):
        _db = "postgresql+asyncpg://" + _db[len("postgres://"):]
    elif _db.startswith("postgresql://") and "+asyncpg" not in _db:
        _db = "postgresql+asyncpg://" + _db[len("postgresql://"):]
    DATABASE_URL = _db
else:
    DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'database' / 'bot.db'}"

REFERRAL_REWARD = int(os.getenv("REFERRAL_REWARD", "10"))
REFERRAL_BONUS = int(os.getenv("REFERRAL_BONUS", "10"))
