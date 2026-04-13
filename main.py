
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, Stream
from youtube_search import YoutubeSearch

# ---------------- CONFIG ----------------
API_ID = 38345261
API_HASH = "6f3784a808cc527fc4bbbc4052103d75"
BOT_TOKEN = "8635411052:AAHljekicmXC9sJNHPxmGMP_R5tPfVXBhq8"

# ---------------- SETUP ----------------
logging.basicConfig(level=logging.INFO)
app = Client("video_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call = PyTgCalls(app)

active_chats = {}

async def search_youtube(query):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if results:
            video = results[0]
            return {
                'url': f"https://youtube.com/watch?v={video['id']}",
                'title': video['title'],
            }
    except Exception as e:
        print(f"Search error: {e}")
    return None

@app.on_message(filters.command(["start", "help"]))
async def start_command(client, message):
    await message.reply_text(
        "🎬 **My Video Bot**\n\n"
        "/video <song> - Play video\n"
        "/stop - Stop\n/pause - Pause\n/resume - Resume\n\n"
        "Add me to group with admin rights!"
    )

@app.on_message(filters.command("video"))
async def video_command(client, message):
    chat_id = message.chat.id
    if chat_id > 0:
        await message.reply_text("❌ Use in a group!")
        return
    if len(message.command) < 2:
        await message.reply_text("❌ Usage: /video <song>")
        return
    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Searching: {query}")
    video = await search_youtube(query)
    if not video:
        await msg.edit_text("❌ No results!")
        return
    await msg.edit_text(f"🎬 Playing: {video['title'][:50]}")
    try:
        await call.join_group_call(chat_id, Stream(video['url']))
        active_chats[chat_id] = video['title']
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:100]}")

@app.on_message(filters.command("pause"))
async def pause_command(client, message):
    if message.chat.id in active_chats:
        await call.pause_stream(message.chat.id)
        await message.reply_text("⏸ Paused!")

@app.on_message(filters.command("resume"))
async def resume_command(client, message):
    if message.chat.id in active_chats:
        await call.resume_stream(message.chat.id)
        await message.reply_text("▶️ Resumed!")

@app.on_message(filters.command("stop"))
async def stop_command(client, message):
    if message.chat.id in active_chats:
        await call.leave_group_call(message.chat.id)
        del active_chats[message.chat.id]
        await message.reply_text("⏹ Stopped!")

async def main():
    print("🚀 Starting...")
    await app.start()
    await call.start()
    print("✅ Bot is running!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
