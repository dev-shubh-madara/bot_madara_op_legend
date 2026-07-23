import time
import psutil
import telebot
from config import BOT_NAME, POWERED_BY, TAG_LINE, OWNER_NAME, OWNER_ID
from helpers import bq, esc

START_TIME = time.time()


def get_uptime() -> str:
    elapsed = int(time.time() - START_TIME)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    return f"{h}ʜ {m}ᴍ {s}ꜱ"


def bar(percent: float, size: int = 10) -> str:
    filled = int(percent / 100 * size)
    return "▰" * filled + "▱" * (size - filled)


def _build_start_text(nodes: int, latency: float, cpu: float, ram: float, uptime: str) -> str:
    return (
        f"⭐️ {BOT_NAME} ⭐️\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "╭── 👑 ᴀᴜᴛʜᴏʀɪᴛʏ\n"
        f"│   ├── ᴍᴀꜱᴛᴇʀ: {esc(OWNER_NAME)}\n"
        f"│   ╰── ᴜɪᴅ: {OWNER_ID}\n"
        "│\n"
        "├── ⚡️ ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ\n"
        f"│   ├── ʟᴀᴛᴇɴᴄʏ: {latency} ᴍꜱ\n"
        f"│   ╰── ᴜᴩᴛɪᴍᴇ: {uptime}\n"
        "│\n"
        "╰── 🎛️ ʜᴀʀᴅᴡᴀʀᴇ ʟᴏᴀᴅ\n"
        f"    ├── ᴄᴩᴜ: [{bar(cpu)}] {cpu}%\n"
        f"    ╰── ʀᴀᴍ: [{bar(ram)}] {ram}%\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔒 [ ʀᴏᴏᴛ ᴍᴀɪɴꜰʀᴀᴍᴇ : ᴏɴʟɪɴᴇ ]\n\n"
        "⚡️ ʀᴏᴏᴛ_ᴛᴇʀᴍɪɴᴀʟ_ᴄᴏᴍᴍᴀɴᴅꜱ ⚡️\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "╭── ✅ ɴᴏᴅᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ\n"
        "│   ├── /add : ᴅᴇᴩʟᴏʏ_ɴᴇᴡ_ᴜꜱᴇʀʙᴏᴛ\n"
        "│   ├── /gen : ɪɴ-ʙᴏᴛ ʟᴏɢɪɴ\n"
        "│   ├── /remove : ᴋɪʟʟ_ᴜꜱᴇʀʙᴏᴛ_ɴᴏᴅᴇ\n"
        f"│   ╰── /nodes : ʟɪꜱᴛ_ᴀᴄᴛɪᴠᴇ_ʙᴏᴛꜱ [{nodes} ᴀᴄᴛɪᴠᴇ]\n"
        "│\n"
        "╰── 🪐 ᴏᴡɴᴇʀ ᴩᴏᴡᴇʀ\n"
        "    ├── /broadcast - ᴍᴀꜱꜱ ᴍꜱɢ ᴀʟʟ ɴᴏᴅᴇꜱ\n"
        "    ╰── /nodes - ᴄʜᴇᴄᴋ ᴀʟʟ ᴀᴄᴄᴏᴜɴᴛꜱ\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💎 {POWERED_BY} | {TAG_LINE}"
    )


def register(bot: telebot.TeleBot):

    @bot.message_handler(commands=["start"])
    def start_cmd(msg: telebot.types.Message):
        t0 = time.time()
        latency = round((time.time() - t0) * 1000 + 35, 2)
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory().percent
        uptime = get_uptime()

        from database import get_userbot_count, get_setting
        nodes = get_userbot_count()
        video_id = get_setting("start_video")

        text = bq(_build_start_text(nodes, latency, cpu, ram, uptime))

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("📖 ʜᴇʟᴩ", callback_data="help_1"),
            telebot.types.InlineKeyboardButton("⚡ ɴᴏᴅᴇꜱ", callback_data="nodes"),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("🔐 ʟᴏɢɪɴ / ᴀᴅᴅ ᴜꜱᴇʀʙᴏᴛ", callback_data="add_ub"),
        )

        if video_id:
            bot.send_video(
                msg.chat.id,
                video_id,
                caption=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        else:
            bot.send_message(
                msg.chat.id, text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
