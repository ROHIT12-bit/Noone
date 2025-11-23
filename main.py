# main.py
import asyncio
from pyrogram import idle
from bot.core.bot_instance import bot, sch, ffQueue, ffLock, ffpids_cache, ff_queued
from bot.core.auto_animes import fetch_animes
from bot.core.reporter import rep
from bot.core.func_utils import clean_up, new_task
from bot.plugins.up_posts import upcoming_animes
from config import Var, LOGS

async def queue_loop():
    while True:
        if not ffQueue.empty():
            post_id = await ffQueue.get()
            await asyncio.sleep(1.5)
            ff_queued[post_id].set()
            async with ffLock:
                ffQueue.task_done()
        await asyncio.sleep(10)

async def main():
    # Attach APScheduler to the running event loop
    loop = asyncio.get_running_loop()
    sch._loop = loop
    sch.add_job(upcoming_animes, "cron", hour=0, minute=30)
    sch.start()

    await bot.start()

    try:
        me = await bot.get_me()
        bot.username = me.username
        LOGS.info(f"Bot username: {bot.username}")
    except Exception as e:
        LOGS.error(f"Failed to get bot username: {e}")
        await bot.stop()
        return

    # Start queue loop & anime fetch
    asyncio.create_task(queue_loop())
    await fetch_animes()

    await rep.report("✅ Bot Started")
    await idle()

    await bot.stop()
    await clean_up()

if __name__ == "__main__":
    asyncio.run(main())
