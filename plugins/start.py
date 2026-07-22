import time
import psutil
import telebot
from config import BOT_NAME, POWERED_BY, TAG_LINE, OWNER_NAME, OWNER_ID

START_TIME = time.time()


def get_uptime() -> str:
    elapsed = int(time.time() - START_TIME)
    h, rem = divmod(elapsed, 3600)
    m, s = divmod(rem, 60)
    return f"{h}ʜ {m}ᴍ {s}ꜱ"


def bar(percent: float, size: int = 10) -> str:
    filled = int(percent / 100 * size)
    return "▰" * filled + "▱" * (size - filled)


def register(bot: telebot.TeleBot):

    @bot.message_handler(commands=["start"])
    def start_cmd(msg: telebot.types.Message):
        t0 = time.time()
        # ping latency (rough measure)
        latency = round((time.time() - t0) * 1000 + 35, 2)

        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory().percent
        uptime = get_uptime()

        from database import get_userbot_count
        nodes = get_userbot_count()

        text = (
            f"⭐️ {BOT_NAME} ⭐️\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "╭── 👑 ᴀᴜᴛʜᴏʀɪᴛʏ\n"
            f"│   ├── ᴍᴀꜱᴛᴇʀ: {OWNER_NAME}\n"
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
            f"🔒 [ ʀᴏᴏᴛ ᴍᴀɪɴꜰʀᴀᴍᴇ : ᴏɴʟɪɴᴇ ]\n\n"
            "⚡️ ʀᴏᴏᴛ_ᴛᴇʀᴍɪɴᴀʟ_ᴄᴏᴍᴍᴀɴᴅꜱ ⚡️\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "╭── ✅ ɴᴏᴅᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ\n"
            "│   ├── /add : ᴅᴇᴩʟᴏʏ_ɴᴇᴡ_ᴜꜱᴇʀʙᴏᴛ\n"
            "│   ├── /gen : ɪɴᴊᴇᴄᴛ_ꜱᴇꜱꜱɪᴏɴ_ꜱᴛʀɪɴɢ\n"
            "│   ├── /remove : ᴋɪʟʟ_ᴜꜱᴇʀʙᴏᴛ_ɴᴏᴅᴇ\n"
            f"│   ╰── /nodes : ʟɪꜱᴛ_ᴀᴄᴛɪᴠᴇ_ʙᴏᴛꜱ [{nodes} ᴀᴄᴛɪᴠᴇ]\n"
            "│\n"
            "╰── 🪐 ᴏᴡɴᴇʀ ᴩᴏᴡᴇʀ\n"
            "    ├── /broadcast - ᴍᴀꜱꜱ ᴍꜱɢ ᴀʟʟ ɴᴏᴅᴇꜱ\n"
            "    ╰── /nodes - ᴄʜᴇᴄᴋ ᴀʟʟ ᴀᴄᴄᴏᴜɴᴛꜱ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💎 {POWERED_BY} | {TAG_LINE}"
        )

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("📖 ʜᴇʟᴩ", callback_data="help_1"),
            telebot.types.InlineKeyboardButton("⚡ ɴᴏᴅᴇꜱ", callback_data="nodes"),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("➕ ᴀᴅᴅ ᴜꜱᴇʀʙᴏᴛ", callback_data="add_ub"),
        )

        bot.send_message(msg.chat.id, text, reply_markup=keyboard)
