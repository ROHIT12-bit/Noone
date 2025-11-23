# main.py
import asyncio
from uvloop import install as uvloop_install
from config import Var, LOGS
from bot.core.auto_animes import fetch_animes
from bot.plugins.up_posts import upcoming_animes
from bot.core.func_utils import clean_up
from pyrogram import idle
from apscheduler.schedulers.asyncio import AsyncIOScheduler

uvloop_install()  # install uvloop at the very top

async def main():
    from pyrogram import Client

    # ✅ Create Client inside async function
    bot = Client(
        name="AutoAniAdvance",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN,
        plugins=dict(root="bot/plugins"),
        parse_mode="html"
    )

    # Scheduler
    sch = AsyncIOScheduler(timezone="Asia/Kolkata", event_loop=asyncio.get_running_loop())
    sch.add_job(upcoming_animes, "cron", hour=0, minute=30)
    sch.start()

    await bot.start()

    # Example: start anime fetching
    asyncio.create_task(fetch_animes())

    await idle()
    await bot.stop()
    await clean_up()

if __name__ == "__main__":
    asyncio.run(main())
