# (©)CodeFlix_Bots
# rohit_1888 on Tg  # Don't remove this line

import asyncio
import logging
from asyncio import (
    create_subprocess_exec,
    all_tasks,
    gather,
    sleep as asleep,
)
from aiofiles import open as aiopen
from pyrogram import idle
from pyrogram.filters import command, user
from os import path as ospath, execl, kill
from sys import executable
from signal import SIGKILL

from bot.core.bot_instance import bot, bot_loop, sch, ffQueue, ffLock, ffpids_cache, ff_queued
from bot.core.reporter import rep
from config import Var, LOGS
from bot.core.auto_animes import fetch_animes
from bot.core.func_utils import clean_up, new_task
from bot.plugins.up_posts import upcoming_animes

# ─────────────────────────────
# 🩹 Ensure an asyncio loop exists (Python 3.10 + fix)
# ─────────────────────────────
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# Attach reporter instance to bot
bot.rep = rep


@bot.on_message(command("restart") & user(Var.ADMINS))
@new_task
async def restart(client, message):
    """Handle /restart from admin."""
    rmessage = await message.reply("<i>Restarting...</i>")
    if sch.running:
        sch.shutdown(wait=False)
    await clean_up()

    # Kill active ffmpeg processes
    if ffpids_cache:
        for pid in ffpids_cache:
            try:
                kill(pid, SIGKILL)
            except (OSError, ProcessLookupError):
                continue

    # Run updater
    await (await create_subprocess_exec("python3", "update.py")).wait()

    # Save restart message
    async with aiopen(".restartmsg", "w") as f:
        await f.write(f"{rmessage.chat.id}\n{rmessage.id}\n")

    # Relaunch bot
    execl(executable, executable, "-m", "bot")


async def restart_bot():
    """Edit restart message after bot relaunch."""
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            lines = f.readlines()
            chat_id, msg_id = map(int, lines)
        try:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=msg_id, text="<i>Restarted!</i>"
            )
        except Exception as e:
            LOGS.error(e)


async def queue_loop():
    """Handle ffmpeg queue loop."""
    while True:
        if not ffQueue.empty():
            post_id = await ffQueue.get()
            await asleep(1.5)
            ff_queued[post_id].set()
            await asleep(1.5)
            async with ffLock:
                ffQueue.task_done()
        await asleep(10)


async def main():
    """Main bot entrypoint."""
    # Schedule daily job
    sch.add_job(upcoming_animes, "cron", hour=0, minute=30)

    # Start Pyrogram client
    await bot.start()

    # Get bot username
    try:
        me = await bot.get_me()
        bot.username = me.username
        LOGS.info(f"✅ Bot username set to @{bot.username}")
    except Exception as e:
        LOGS.error(f"Failed to set bot username: {e}")
        await bot.stop()
        return

    await restart_bot()
    await bot.rep.report("✅ Bot Started")

    # Test channel access
    try:
        db_channel = await bot.get_chat(Var.CHANNEL_ID)
        test_msg = await bot.send_message(chat_id=db_channel.id, text="✅ Startup Test")
        await test_msg.delete()
        bot.db_channel = db_channel
    except Exception as e:
        await bot.rep.report(f"❌ MAIN_CHANNEL error: {e}", "critical")
        await bot.stop()
        return

    # Notify admins
    try:
        for admin_id in Var.ADMINS:
            await bot.send_message(admin_id, "<b>✅ Bᴏᴛ Rᴇsᴛᴀʀᴛᴇᴅ</b>")
    except Exception:
        pass

    # Start scheduler & background tasks
    sch.start()
    bot_loop.create_task(queue_loop())

    # Load anime data
    await fetch_animes()

    # Keep bot alive
    await idle()

    # Cleanup on exit
    await bot.stop()
    for task in all_tasks():
        task.cancel()
    await clean_up()


if __name__ == "__main__":
    # Run safely inside event loop
    bot_loop.run_until_complete(main()) 
