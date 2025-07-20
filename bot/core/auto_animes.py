from asyncio import gather, create_task, sleep as asleep, Event
from asyncio.subprocess import PIPE
from os import path as ospath, system
from aiofiles import open as aiopen
from aiofiles.os import remove as aioremove
from traceback import format_exc
from base64 import urlsafe_b64encode
from time import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import Var
from bot.core.bot_instance import bot, bot_loop, ani_cache, ffQueue, ffLock, ff_queued
from .tordownload import TorDownloader
from .database import db
from .func_utils import getfeed, encode, editMessage, sendMessage, convertBytes
from .text_utils import TextEditor
from .ffencoder import FFEncoder
from .tguploader import TgUploader
from .reporter import rep

btn_formatter = {
    'HDRip':'𝗛𝗗𝗥𝗶𝗽',
    '1080':'𝟭𝟬𝟴𝟬𝗣', 
    '720':'𝟳𝟮𝟬𝗣',
    '480':'𝟰𝟴𝟬𝗣',
    '360':'𝟯𝟲𝟬𝗣'
}

@bot.on_message(filters.command("add_rss") & filters.user(Var.ADMINS))
async def add_custom_rss(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❗ Usage:\n<code>/addrss https://example.com/rss</code>")
        return

    url = message.command[1]
    if not url.startswith("http"):
        await message.reply_text("⚠️ Invalid URL format.")
        return

    ani_cache["custom_rss"].add(url)
    await message.reply_text(f"✅ RSS feed added:\n<code>{url}</code>")

@bot.on_message(filters.command("list_rss") & filters.user(Var.ADMINS))
async def list_rss(client, message: Message):
    feeds = list(ani_cache.get("custom_rss", []))
    if not feeds:
        await message.reply_text("⚠️ No custom RSS links added yet.")
    else:
        await message.reply_text("📡 Custom RSS Feeds:\n" + "\n".join([f"• {f}" for f in feeds]))

@bot.on_message(filters.command("remove_rss") & filters.user(Var.ADMINS))
async def remove_rss(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❗ Usage:\n<code>/removerss https://example.com/rss</code>")
        return

    url = message.command[1]
    if url in ani_cache.get("custom_rss", set()):
        ani_cache["custom_rss"].remove(url)
        await message.reply_text(f"❌ Removed:\n<code>{url}</code>")
    else:
        await message.reply_text("⚠️ RSS link not found in custom list.")

async def fetch_animes():
    await rep.report("Fetching Anime Started !!!", "info")
    processed_links = set()  # Avoid duplicates across feeds
    while True:
        await asleep(5)
        if ani_cache['fetch_animes']:
            # ✅ Merge default RSS and custom RSS
            all_rss = Var.RSS_ITEMS + list(ani_cache.get("custom_rss", []))
            for link in all_rss:
                if (info := await getfeed(link, 0)):
                    if info.link in processed_links:
                        continue
                    processed_links.add(info.link)
                    bot_loop.create_task(get_animes(info.title, info.link))

async def get_animes(name, torrent, force=False):
    try:
        aniInfo = TextEditor(name)
        await aniInfo.load_anilist()
        ani_id, ep_no = aniInfo.adata.get('id'), aniInfo.pdata.get("episode_number")
        if ani_id not in ani_cache['ongoing']:
            ani_cache['ongoing'].add(ani_id)
        elif not force:
            return
        if not force and ani_id in ani_cache['completed']:
            return
        if force or (not (ani_data := await db.get_anime(ani_id)) \
            or (ani_data and not (qual_data := ani_data.get(ep_no))) \
            or (ani_data and qual_data and not all(qual for qual in qual_data.values()))):

            if "[Batch]" in name:
                await rep.report(f"Torrent Skipped!\n\n{name}", "warning")
                return

            await rep.report(f"New Anime Torrent Found!\n\n{name}", "info")
            anime_name = name
            photo_url = None
            photo_path = None

            # Determine photo source
            if Var.ANIME in anime_name:
                photo_url = Var.CUSTOM_BANNER
            else:
                photo_url = await aniInfo.get_poster()

            # Validate photo_url
            if not photo_url:
                await rep.report(f"No valid poster URL for {name}, using default message", "warning")
                post_msg = await bot.send_message(
                    Var.MAIN_CHANNEL,
                    text=await aniInfo.get_caption()
                )
            else:
                try:
                    # Check if photo_url is a local file path
                    if ospath.exists(photo_url):
                        with open(photo_url, 'rb') as photo_file:
                            post_msg = await bot.send_photo(
                                Var.MAIN_CHANNEL,
                                photo=photo_file,
                                caption=await aniInfo.get_caption()
                            )
                    else:
                        # Assume photo_url is a URL
                        post_msg = await bot.send_photo(
                            Var.MAIN_CHANNEL,
                            photo=photo_url,
                            caption=await aniInfo.get_caption()
                        )
                except Exception as e:
                    await rep.report(f"Failed to send photo for {name}: {str(e)}", "error")
                    # Fallback to text message if photo fails
                    post_msg = await bot.send_message(
                        Var.MAIN_CHANNEL,
                        text=await aniInfo.get_caption()
                    )

            await asleep(1.5)
            stat_msg = await sendMessage(Var.MAIN_CHANNEL, f"<blockquote>‣ <b>Aɴɪᴍᴇ Nᴀᴍᴇ :</b> <b><i>{name}</i></b></blockquote>\n\n<blockquote><i>Dᴏᴡɴʟᴏᴀᴅɪɴɢ....</i></blockquote>")
            dl = await TorDownloader("./downloads").download(torrent, name)
            if not dl or not ospath.exists(dl):
                await rep.report(f"File Download Incomplete, Try Again", "error")
                await stat_msg.delete()
                return

            # ... rest of the code remains unchanged ...

            post_id = post_msg.id
            ffEvent = Event()
            ff_queued[post_id] = ffEvent
            if ffLock.locked():
                await editMessage(stat_msg, f"<blockquote>‣ <b>Aɴɪᴍᴇ Nᴀᴍᴇ :</b> <b><i>{name}</i></b></blockquote>\n\n<blockquote><i>Qᴜᴇᴜᴇᴅ ᴛᴏ Eɴᴄᴏᴅᴇ...</i></blockquote>")
                await rep.report("Aᴅᴅᴇᴅ Tᴀsᴋ ᴛᴏ Qᴜᴇᴜᴇ...", "info")
            await ffQueue.put(post_id)
            await ffEvent.wait()
            
            await ffLock.acquire()
            btns = []
            for qual in Var.QUALS:
                filename = await aniInfo.get_upname(qual)
                await editMessage(stat_msg, f"<blockquote>‣ <b>Aɴɪᴍᴇ Nᴀᴍᴇ :</b> <b><i>{name}</i></b><blockquote>\n\n</blockquote><i>Rᴇᴀᴅʏ ᴛᴏ Eɴᴄᴏᴅᴇ...</i>")
                
                await asleep(1.5)
                await rep.report("Sᴛᴀʀᴛɪɴɢ Eɴᴄᴏᴅᴇ...", "info")
                try:
                    out_path = await FFEncoder(stat_msg, dl, filename, qual).start_encode()
                except Exception as e:
                    await rep.report(f"Error: {e}, Cancelled,  Retry Again !", "error")
                    await stat_msg.delete()
                    ffLock.release()
                    return
                await rep.report("Sᴜᴄᴄᴇsғᴜʟʟʏ Cᴏᴍᴘʀᴇssᴇᴅ Nᴏᴡ Gᴏɪɴɢ Tᴏ Uᴘʟᴏᴀᴅ...", "info")
                
                await editMessage(stat_msg, f"<blockquote>‣ <b>Aɴɪᴍᴇ Nᴀᴍᴇ :</b> <b><i>{filename}</i></b></blockquote>\n\n<blockquote><i>Rᴇᴀᴅʏ ᴛᴏ Uᴘʟᴏᴀᴅ...</i></blockquote>")
                await asleep(1.5)
                try:
                    msg = await TgUploader(stat_msg).upload(out_path, qual)
                except Exception as e:
                    await rep.report(f"Error: {e}, Cancelled,  Retry Again !", "error")
                    await stat_msg.delete()
                    ffLock.release()
                    return
                await rep.report("Sᴜᴄᴄᴇssғᴜʟʟʏ Uᴘʟᴏᴀᴅᴇᴅ Fɪʟᴇ ɪɴᴛᴏ Cʜᴀɴɴᴇʟ...", "info")
                
                msg_id = msg.id
                link = f"https://telegram.me/{(await bot.get_me()).username}?start={await encode('get-'+str(msg_id * abs(Var.FILE_STORE)))}"
                
                if post_msg:
                    if len(btns) != 0 and len(btns[-1]) == 1:
                        btns[-1].insert(1, InlineKeyboardButton(f"{btn_formatter[qual]}", url=link))
                    else:
                        btns.append([InlineKeyboardButton(f"{btn_formatter[qual]}", url=link)])
                    await editMessage(post_msg, post_msg.caption.html if post_msg.caption else "", InlineKeyboardMarkup(btns))
                    
                await db.save_anime(ani_id, ep_no, qual, post_id)
                bot_loop.create_task(extra_utils(msg_id, out_path))
            ffLock.release()
            
            await stat_msg.delete()
            await aioremove(dl)
        ani_cache['completed'].add(ani_id)
    except Exception as error:
        await rep.report(format_exc(), "error")

async def extra_utils(msg_id, out_path):
    msg = await bot.get_messages(Var.FILE_STORE, message_ids=msg_id)

    if Var.BACKUP_CHANNEL != 0:
        for chat_id in str(Var.BACKUP_CHANNEL).split():
            await msg.copy(int(chat_id))
            
    # MediaInfo, ScreenShots, Sample Video ( Add-ons Features )
