
# bot_instance.py
from pyrogram import Client
from pyrogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import Var, LOGS
from asyncio import Queue, Lock
from datetime import datetime
from os import path as ospath, mkdir, system
from uvloop import install as uvloop_install

# Install uvloop
uvloop_install()

# Shared objects
ani_cache = {'fetch_animes': True, 'ongoing': set(), 'completed': set(), 'custom_rss': set()}
ffQueue = Queue()
ffLock = Lock()
ffpids_cache = []
ff_queued = {}

# Ensure directories
for folder in ("encode", "thumbs", "downloads"):
    if not ospath.isdir(folder):
        mkdir(folder)

if Var.THUMB and not ospath.exists("thumb.jpg"):
    system(f"wget -q {Var.THUMB} -O thumb.jpg")
    LOGS.info("Thumbnail saved!")

# Initialize bot
bot = Client(
    name="AutoAniAdvance",
    api_id=Var.API_ID,
    api_hash=Var.API_HASH,
    bot_token=Var.BOT_TOKEN,
    plugins=dict(root="bot/plugins"),
    parse_mode=ParseMode.HTML
)

# Scheduler (will attach loop later in main)
sch = AsyncIOScheduler(timezone="Asia/Kolkata")
