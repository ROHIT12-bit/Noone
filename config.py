import asyncio
from os import getenv
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# 🩹 Ensure there is always a running asyncio event loop (Python 3.10+ fix)
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Load environment variables
load_dotenv()

# Configure logger
LOGS = logging.getLogger(__name__)

class Var:
    # ─────────────────────────────
    # Required credentials
    # ─────────────────────────────
    API_ID = getenv("API_ID")
    API_HASH = getenv("API_HASH")
    BOT_TOKEN = getenv("BOT_TOKEN")
    DB_URI = getenv("DB_URI")
    DB_NAME = getenv("DB_NAME")

    # ─────────────────────────────
    # Optional and custom settings
    # ─────────────────────────────
    BAN_SUPPORT = getenv("BAN_SUPPORT", "https://t.me/ROHITREDDY69")
    FSUB_LINK_EXPIRY = int(getenv("FSUB_LINK_EXPIRY", "120"))
    CHANNEL_ID = int(getenv("CHANNEL_ID", "-1003262024908"))
    MHCHANNEL_URL = getenv("MHCHANNEL_URL", "https://t.me/+3ZQCsmH9k0sxNTNl")
    ANIME = getenv("ANIME", "Is It Wrong to Try to Pick Up Girls in a Dungeon?")
    CUSTOM_BANNER = getenv("CUSTOM_BANNER", "https://envs.sh/im5.jpg")

    PROTECT_CONTENT = True if getenv('PROTECT_CONTENT', "False") == "True" else False
    BACKUP_CHANNEL = int(getenv("BACKUP_CHANNEL", "0"))
    LOG_CHANNEL = int(getenv("LOG_CHANNEL", "0"))
    MAIN_CHANNEL = int(getenv("MAIN_CHANNEL", "0"))
    FILE_STORE = int(getenv("FILE_STORE", "0"))
    ADMINS = list(map(int, getenv("ADMINS", "").split()))

    RSS_ITEMS = getenv("RSS_ITEMS", "").split()
    SEND_SCHEDULE = getenv("SEND_SCHEDULE", "True").lower() == "true"
    BRAND_UNAME = getenv("BRAND_UNAME", "@AnimeUniverseTeam")

    # ─────────────────────────────
    # Encoding / FFmpeg parameters
    # ─────────────────────────────
    FFCODE_1080 = getenv("FFCODE_1080")
    FFCODE_720 = getenv("FFCODE_720")
    FFCODE_480 = getenv("FFCODE_480")
    FFCODE_360 = getenv("FFCODE_360")
    FFCODE_HDRip = getenv("FFCODE_HDRip")
    QUALS = getenv("QUALS", "480 720 1080 HDRip").split()

    # ─────────────────────────────
    # UI and customization
    # ─────────────────────────────
    DISABLE_CHANNEL_BUTTON = getenv("DISABLE_CHANNEL_BUTTON", None) == 'True'
    AS_DOC = getenv("AS_DOC", "True").lower() == "true"
    THUMB = getenv("THUMB")
    START_PIC = getenv("START_PIC", "https://envs.sh/im5.jpg")
    FORCE_PIC = getenv("FORCE_PIC", "https://envs.sh/im5.jpg")


# ✅ Validate required environment variables
REQUIRED_VARS = ["API_ID", "API_HASH", "BOT_TOKEN", "DB_URI"]
for var_name in REQUIRED_VARS:
    if not getattr(Var, var_name):
        LOGS.critical(f"❌ Missing required environment variable: {var_name}")
        exit(1)

# ─────────────────────────────
# Logging setup
# ─────────────────────────────
LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50_000_000,   # 50MB
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

# Reduce Pyrogram noise
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    """Helper function to get a logger by name."""
    return logging.getLogger(name)
