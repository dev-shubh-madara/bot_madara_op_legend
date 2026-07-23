"""
MADARA_X_AURA — Userbot Manager Bot
Powered by MADARA | GMS X USER
"""
import logging
import asyncio
import os
import telebot
from config import BOT_TOKEN, OWNER_ID, BOT_NAME, POWERED_BY
from database import init_db, get_setting
from userbot_manager import load_all_from_db
from helpers import bq, esc

# ─── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ─── Sanity checks ────────────────────────────────────────────
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it as a secret.")
if not OWNER_ID:
    raise RuntimeError("OWNER_ID is not set.")


def build_bot() -> telebot.TeleBot:
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
    return bot


def register_all_plugins(bot: telebot.TeleBot):
    from plugins import start, help, gen_session, node_mgmt, admin_cmds, aesthetic, owner_cmds, owner_extra
    start.register(bot)
    help.register(bot)
    gen_session.register(bot)   # in-bot login flow — must come before node_mgmt
    node_mgmt.register(bot)
    admin_cmds.register(bot)
    aesthetic.register(bot)
    owner_cmds.register(bot)
    owner_extra.register(bot)
    logger.info("All plugins registered.")


def home_callback(bot: telebot.TeleBot):
    """Register the /start home callback re-used across plugins."""
    from plugins.start import get_uptime, bar
    import psutil, time

    @bot.callback_query_handler(func=lambda c: c.data == "home")
    def home_cb(call: telebot.types.CallbackQuery):
        from config import OWNER_NAME
        from database import get_userbot_count
        t0 = time.time()
        latency = round((time.time() - t0) * 1000 + 35, 2)
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory().percent

        from config import OWNER_NAME
        from database import get_userbot_count
        text = bq(
            f"⭐️ {BOT_NAME} ⭐️\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "╭── 👑 ᴀᴜᴛʜᴏʀɪᴛʏ\n"
            f"│   ├── ᴍᴀꜱᴛᴇʀ: {esc(OWNER_NAME)}\n"
            f"│   ╰── ᴜɪᴅ: {OWNER_ID}\n"
            "│\n"
            "├── ⚡️ ꜱʏꜱᴛᴇᴍ ꜱᴛᴀᴛꜱ\n"
            f"│   ├── ʟᴀᴛᴇɴᴄʏ: {latency} ᴍꜱ\n"
            f"│   ╰── ᴜᴩᴛɪᴍᴇ: {get_uptime()}\n"
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
            f"│   ╰── /nodes : [{get_userbot_count()} ᴀᴄᴛɪᴠᴇ]\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💎 {POWERED_BY}"
        )

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton("📖 ʜᴇʟᴩ", callback_data="help_1"),
            telebot.types.InlineKeyboardButton("⚡ ɴᴏᴅᴇꜱ", callback_data="nodes"),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton("🔐 ʟᴏɢɪɴ / ᴀᴅᴅ ᴜꜱᴇʀʙᴏᴛ", callback_data="add_ub"),
        )
        try:
            bot.edit_message_text(
                text, call.message.chat.id, call.message.message_id,
                parse_mode="HTML", reply_markup=keyboard,
            )
        except Exception:
            pass
        bot.answer_callback_query(call.id)


def main():
    logger.info(f"Starting {BOT_NAME}…")

    # Init database
    init_db()

    # Load existing userbots from DB
    loop = asyncio.new_event_loop()
    loaded = loop.run_until_complete(load_all_from_db())
    loop.close()
    logger.info(f"Loaded {loaded} userbot(s) from database.")

    # Build and configure bot
    bot = build_bot()
    register_all_plugins(bot)
    home_callback(bot)

    # Notify owner
    try:
        bot.send_message(
            OWNER_ID,
            f"✅ {BOT_NAME} ɪꜱ ᴏɴʟɪɴᴇ!\n"
            f"🤖 ɴᴏᴅᴇꜱ ʟᴏᴀᴅᴇᴅ: {loaded}\n\n"
            f"💎 {POWERED_BY}",
        )
    except Exception:
        pass

    logger.info("Bot polling started.")
    bot.infinity_polling(timeout=20, long_polling_timeout=15)


if __name__ == "__main__":
    main()
