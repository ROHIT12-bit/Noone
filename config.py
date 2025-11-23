# ============================================================
#  CLEAN CONFIG FILE — NO EVENT LOOP HERE
# ============================================================

from os import getenv
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

LOGS = logging.getLogger("config")


class Var:
    API_ID = int(getenv("API_ID", "0"))
    API_HASH = getenv("API_HASH")
    BOT_TOKEN = getenv("BOT_TOKEN")
    DB_URI = getenv("DB_URI")
    DB_NAME = getenv("DB_NAME")

    BAN_SUPPORT = getenv("BAN_SUPPORT", "https://t.me/ROHITREDDY69")
    FSUB_LINK_EXPIRY = int(getenv("FSUB_LINK_EXPIRY", "120"))
    CHANNEL_ID = int(getenv("CHANNEL_ID", "-1003262024908"))
    MHCHANNEL_URL = getenv("MHCHANNEL_URL", "")
    ANIME = getenv("ANIME", "")
    CUSTOM_BANNER = getenv("CUSTOM_BANNER", "")

    PROTECT_CONTENT = getenv('PROTECT_CONTENT', "False").lower() == "true"
    BACKUP_CHANNEL = int(getenv("BACKUP_CHANNEL", "0"))
    LOG_CHANNEL = int(getenv("LOG_CHANNEL", "0"))
    MAIN_CHANNEL = int(getenv("MAIN_CHANNEL", "0"))
    FILE_STORE = int(getenv("FILE_STORE", "0"))

    ADMINS = (
        list(map(int, getenv("ADMINS", "").split()))
        if getenv("ADMINS") else []
    )

    RSS_ITEMS = getenv("RSS_ITEMS", "").split()
    SEND_SCHEDULE = getenv("SEND_SCHEDULE", "True").lower() == "true"
    BRAND_UNAME = getenv("BRAND_UNAME", "@AnimeUniverseTeam")

    FFCODE_1080 = getenv("FFCODE_1080")
    FFCODE_720 = getenv("FFCODE_720")
    FFCODE_480 = getenv("FFCODE_480")
    FFCODE_360 = getenv("FFCODE_360")
    FFCODE_HDRip = getenv("FFCODE_HDRip")
    QUALS = getenv("QUALS", "480 720 1080 HDRip").split()

    DISABLE_CHANNEL_BUTTON = getenv("DISABLE_CHANNEL_BUTTON", "False").lower() == "true"
    AS_DOC = getenv("AS_DOC", "True").lower() == "true"
    THUMB = getenv("THUMB")
    START_PIC = getenv("START_PIC", "")
    FORCE_PIC = getenv("FORCE_PIC", "")


# ============================================================
# Logging
# ============================================================

LOG_FILE_NAME = "filesharingbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50_000_000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
