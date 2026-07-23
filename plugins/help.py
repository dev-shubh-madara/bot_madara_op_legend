import telebot
from config import BOT_NAME, POWERED_BY, TAG_LINE
from datetime import datetime
from helpers import bq

HELP_PAGES = [
    {
        "title": "🚀 ᴀᴄᴛɪᴠᴇʙᴏᴛ  &  🩸 ᴀᴅᴍɪɴ",
        "body": (
            "╭━━ [ 🚀 ᴀᴄᴛɪᴠᴇʙᴏᴛ ]\n"
            "╰ ⇛ /activebot — ꜱʜᴏᴡ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴜꜱᴇʀʙᴏᴛ ɪɴꜰᴏ\n"
            "│\n"
            "╭━━ [ 🩸 ᴀᴅᴍɪɴ ]\n"
            "╰ ⇛ /ban • /unban • /mute • /unmute\n"
            "    /promote • /demote • /purge"
        ),
    },
    {
        "title": "🚀 ᴀᴅᴍɪɴʟɪꜱᴛ",
        "body": (
            "╭━━ [ 🚀 ᴀᴅᴍɪɴʟɪꜱᴛ ]\n"
            "╰ ⇛ /adminlist — ʟɪꜱᴛ ɢʀᴏᴜᴩ ᴀᴅᴍɪɴꜱ\n"
            "│\n"
            "╭━━ [ 🤖 ʙᴏᴛʟɪꜱᴛ ]\n"
            "╰ ⇛ /botlist — ʟɪꜱᴛ ᴀʟʟ ʙᴏᴛꜱ ɪɴ ᴄʜᴀᴛ\n"
            "│\n"
            "╭━━ [ 👤 ᴏᴡɴꜱ ]\n"
            "╰ ⇛ /owns — ɢʀᴏᴜᴩꜱ ʏᴏᴜʀ ᴜʙ ᴏᴡɴꜱ"
        ),
    },
    {
        "title": "✨ ᴀᴇꜱᴛʜᴇᴛɪᴄ_ʜᴀᴄᴋꜱ",
        "body": (
            "╭━━ [ ✨ ᴀᴇꜱᴛʜᴇᴛɪᴄ_ʜᴀᴄᴋꜱ ]\n"
            "╰ ⇛ /hug @user — ꜱᴇɴᴅ ᴀ ʜᴜɢ ɢɪꜰ\n"
            "│\n"
            "╭━━ [ 🎵 ꜱᴩᴏᴛɪꜰʏ ]\n"
            "╰ ⇛ /spotify ‹song› — ꜱᴇᴀʀᴄʜ ꜱᴏɴɢ ɪɴꜰᴏ\n"
            "│\n"
            "╭━━ [ 🔤 ꜰᴠɴ ]\n"
            "╰ ⇛ /fvn ‹text› — ꜰᴀɴᴄʏ ꜰᴏɴᴛ ᴄᴏɴᴠᴇʀᴛᴇʀ"
        ),
    },
    {
        "title": "🛠️ ɴᴏᴅᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ",
        "body": (
            "╭━━ [ 🛠️ ɴᴏᴅᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ]\n"
            "╰ ⇛ /gen — ʟᴏɢɪɴ ᴅɪʀᴇᴄᴛʟʏ ɪɴꜱɪᴅᴇ ᴛʜᴇ ʙᴏᴛ\n"
            "│\n"
            "╭━━ [ ➕ ᴍᴀɴᴜᴀʟ ]\n"
            "╰ ⇛ /add — ᴩᴀꜱᴛᴇ ᴀ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ\n"
            "│\n"
            "╭━━ [ ❌ ʀᴇᴍᴏᴠᴇ ]\n"
            "╰ ⇛ /remove — ᴋɪʟʟ ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɴᴏᴅᴇ\n"
            "│\n"
            "╭━━ [ 📋 ɴᴏᴅᴇꜱ ]\n"
            "╰ ⇛ /nodes — ʟɪꜱᴛ ᴀʟʟ ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇꜱ"
        ),
    },
    {
        "title": "🪐 ᴏᴡɴᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ",
        "body": (
            "╭━━ [ 🪐 ᴏᴡɴᴇʀ ᴏɴʟʏ ]\n"
            "╰ ⇛ /broadcast ‹msg› — ꜱᴇɴᴅ ᴍꜱɢ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀꜱ\n"
            "│\n"
            "╭━━ [ 🎬 ꜱᴇᴛᴠɪᴅᴇᴏ ]\n"
            "╰ ⇛ /setvideo start — ꜱᴇᴛ /start ᴠɪᴅᴇᴏ\n"
            "    /setvideo ping  — ꜱᴇᴛ /ping ᴠɪᴅᴇᴏ\n"
            "│\n"
            "╭━━ [ 👥 ᴜꜱᴇʀ ᴍɢᴍᴛ ]\n"
            "╰ ⇛ /nodes — ᴠɪᴇᴡ ᴀʟʟ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛꜱ\n"
            "    /remove ‹uid› — ᴋɪʟʟ ᴀɴʏ ɴᴏᴅᴇ"
        ),
    },
    {
        "title": "💬 ᴜꜱᴇʀ ɪɴꜰᴏ",
        "body": (
            "╭━━ [ 💬 ᴜꜱᴇʀ ɪɴꜰᴏ ]\n"
            "╰ ⇛ /userinfo @user — ɪɴꜰᴏ ᴀʙᴏᴜᴛ ᴀ ᴜꜱᴇʀ\n"
            "│\n"
            "╭━━ [ 📊 ꜱᴛᴀᴛꜱ ]\n"
            "╰ ⇛ /stats — ʟɪᴠᴇ ꜱᴇʀᴠᴇʀ ꜱᴛᴀᴛꜱ\n"
            "│\n"
            "╭━━ [ 🔍 ᴩɪɴɢ ]\n"
            "╰ ⇛ /ping — ʟᴀᴛᴇɴᴄʏ ᴄʜᴇᴄᴋ"
        ),
    },
    {
        "title": "📌 ᴩɪɴ / ᴜɴᴩɪɴ",
        "body": (
            "╭━━ [ 📌 ᴩɪɴ ]\n"
            "╰ ⇛ /pin — ᴩɪɴ ᴀ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ᴄʜᴀᴛ\n"
            "│\n"
            "╭━━ [ 📌 ᴜɴᴩɪɴ ]\n"
            "╰ ⇛ /unpin — ᴜɴᴩɪɴ ᴛʜᴇ ʟᴀꜱᴛ ᴩɪɴɴᴇᴅ ᴍᴇꜱꜱᴀɢᴇ\n"
            "│\n"
            "╭━━ [ 📌 ᴜɴᴩɪɴᴀʟʟ ]\n"
            "╰ ⇛ /unpinall — ᴜɴᴩɪɴ ᴀʟʟ ᴍᴇꜱꜱᴀɢᴇꜱ"
        ),
    },
    {
        "title": "🔕 ᴅɴᴅ / ᴀꜰᴋ",
        "body": (
            "╭━━ [ 🔕 ᴅɴᴅ ]\n"
            "╰ ⇛ /dnd — ᴍᴜᴛᴇ ᴀʟʟ ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴꜱ\n"
            "│\n"
            "╭━━ [ 💤 ᴀꜰᴋ ]\n"
            "╰ ⇛ /afk ‹reason› — ꜱᴇᴛ ᴀᴜᴛᴏ ᴀꜰᴋ ʀᴇᴩʟʏ\n"
            "│\n"
            "╭━━ [ ✅ ᴜɴᴀꜰᴋ ]\n"
            "╰ ⇛ /unafk — ʀᴇᴍᴏᴠᴇ ᴀꜰᴋ ꜱᴛᴀᴛᴜꜱ"
        ),
    },
    {
        "title": "📝 ɴᴏᴛᴇꜱ",
        "body": (
            "╭━━ [ 📝 ꜱᴀᴠᴇɴᴏᴛᴇ ]\n"
            "╰ ⇛ /savenote ‹name› — ꜱᴀᴠᴇ ᴀ ɴᴏᴛᴇ\n"
            "│\n"
            "╭━━ [ 📋 ɢᴇᴛɴᴏᴛᴇ ]\n"
            "╰ ⇛ /getnote ‹name› — ɢᴇᴛ ᴀ ꜱᴀᴠᴇᴅ ɴᴏᴛᴇ\n"
            "│\n"
            "╭━━ [ ❌ ᴅᴇʟɴᴏᴛᴇ ]\n"
            "╰ ⇛ /delnote ‹name› — ᴅᴇʟᴇᴛᴇ ᴀ ɴᴏᴛᴇ\n"
            "│\n"
            "╭━━ [ 📜 ɴᴏᴛᴇꜱ ]\n"
            "╰ ⇛ /notes — ʟɪꜱᴛ ᴀʟʟ ɴᴏᴛᴇꜱ"
        ),
    },
    {
        "title": "🎨 ᴩʀᴏꜰɪʟᴇ / ʙɪᴏ",
        "body": (
            "╭━━ [ 🎨 ꜱᴇᴛʙɪᴏ ]\n"
            "╰ ⇛ /setbio ‹text› — ꜱᴇᴛ ᴜꜱᴇʀʙᴏᴛ ʙɪᴏ\n"
            "│\n"
            "╭━━ [ 🖼️ ꜱᴇᴛᴩꜰᴩ ]\n"
            "╰ ⇛ /setpfp — ꜱᴇᴛ ᴜꜱᴇʀʙᴏᴛ ᴩʀᴏꜰɪʟᴇ ᴩʜᴏᴛᴏ\n"
            "│\n"
            "╭━━ [ 📛 ꜱᴇᴛɴᴀᴍᴇ ]\n"
            "╰ ⇛ /setname ‹name› — ꜱᴇᴛ ᴜꜱᴇʀʙᴏᴛ ɴᴀᴍᴇ"
        ),
    },
    {
        "title": "🌐 ᴜꜱᴇʀɪɴꜰᴏ / ɪᴅ",
        "body": (
            "╭━━ [ 🌐 ᴜꜱᴇʀɪɴꜰᴏ ]\n"
            "╰ ⇛ /userinfo @user — ɢᴇᴛ ᴜꜱᴇʀ ɪɴꜰᴏ\n"
            "│\n"
            "╭━━ [ 🆔 ɪᴅ ]\n"
            "╰ ⇛ /id — ɢᴇᴛ ʏᴏᴜʀ / ᴄʜᴀᴛ ɪᴅ\n"
            "│\n"
            "╭━━ [ 📡 ᴅᴄ ]\n"
            "╰ ⇛ /dc @user — ɢᴇᴛ ᴅᴀᴛᴀᴄᴇɴᴛᴇʀ ɪɴꜰᴏ"
        ),
    },
    {
        "title": "🤖 ᴀᴜᴛᴏ ʀᴇᴩʟʏ",
        "body": (
            "╭━━ [ 🤖 ᴀᴜᴛᴏ ʀᴇᴩʟʏ ]\n"
            "╰ ⇛ /autoreply add ‹trigger› | ‹reply›\n"
            "    /autoreply del ‹trigger›\n"
            "    /autoreply list"
        ),
    },
    {
        "title": "📣 ꜰᴏʀᴡᴀʀᴅ / ᴄᴏᴩʏ",
        "body": (
            "╭━━ [ 📣 ꜰᴏʀᴡᴀʀᴅ ]\n"
            "╰ ⇛ /forward ‹chat› — ꜰᴏʀᴡᴀʀᴅ ᴍꜱɢ\n"
            "│\n"
            "╭━━ [ 📩 ᴄᴏᴩʏ ]\n"
            "╰ ⇛ /copy ‹chat› — ᴄᴏᴩʏ ᴍꜱɢ ᴛᴏ ᴄʜᴀᴛ"
        ),
    },
    {
        "title": "🧹 ᴄʟᴇᴀɴᴜᴩ",
        "body": (
            "╭━━ [ 🧹 ᴅᴇʟ ]\n"
            "╰ ⇛ /del — ᴅᴇʟᴇᴛᴇ ʀᴇᴩʟɪᴇᴅ ᴍᴇꜱꜱᴀɢᴇ\n"
            "│\n"
            "╭━━ [ 🗑️ ᴩᴜʀɢᴇ ]\n"
            "╰ ⇛ /purge — ᴩᴜʀɢᴇ ꜰʀᴏᴍ ʀᴇᴩʟɪᴇᴅ ᴛᴏ ʟᴀꜱᴛ\n"
            "│\n"
            "╭━━ [ 🧼 ᴅᴇʟᴀʟʟ ]\n"
            "╰ ⇛ /delall — ᴅᴇʟᴇᴛᴇ ᴀʟʟ ᴜʙ ᴍꜱɢꜱ ɪɴ ᴄʜᴀᴛ"
        ),
    },
    {
        "title": "🎲 ꜰᴜɴ",
        "body": (
            "╭━━ [ 🎲 ꜰᴜɴ ]\n"
            "╰ ⇛ /hug • /slap • /kiss @user\n"
            "│\n"
            "╭━━ [ 🎰 ᴅɪᴄᴇ ]\n"
            "╰ ⇛ /dice — ʀᴏʟʟ ᴀ ᴅɪᴄᴇ"
        ),
    },
    {
        "title": "🔧 ᴀᴅᴠᴀɴᴄᴇᴅ (ᴏᴡɴᴇʀ)",
        "body": (
            "╭━━ [ 🔧 ᴇᴠᴀʟ ]\n"
            "╰ ⇛ /eval ‹code› — ʀᴜɴ ᴩʏᴛʜᴏɴ\n"
            "│\n"
            "╭━━ [ 🖥️ ꜱʜᴇʟʟ ]\n"
            "╰ ⇛ /sh ‹cmd› — ʀᴜɴ ꜱʜᴇʟʟ ᴄᴏᴍᴍᴀɴᴅ\n"
            "│\n"
            "╭━━ [ 🔄 ʀᴇꜱᴛᴀʀᴛ ]\n"
            "╰ ⇛ /restart — ʀᴇꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"
        ),
    },
    {
        "title": "ℹ️ ᴀʙᴏᴜᴛ",
        "body": (
            f"╭━━ [ ℹ️ ᴀʙᴏᴜᴛ {BOT_NAME} ]\n"
            f"╰ ⇛ {POWERED_BY}\n"
            f"    {TAG_LINE}\n"
            "│\n"
            "╭━━ [ 🎬 ᴠɪᴅᴇᴏꜱ (ᴏᴡɴᴇʀ) ]\n"
            "╰ ⇛ /setvideo start — ꜱᴇᴛ /start ᴠɪᴅᴇᴏ\n"
            "    /setvideo ping  — ꜱᴇᴛ /ping ᴠɪᴅᴇᴏ"
        ),
    },
]

TOTAL_PAGES = len(HELP_PAGES)


def help_text(page: int) -> str:
    idx = max(0, min(page - 1, TOTAL_PAGES - 1))
    p = HELP_PAGES[idx]
    now = datetime.now().strftime("%I:%M %p")
    inner = (
        f"💀 [ {BOT_NAME} ] 💀\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"{p['body']}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧬 ᴍᴏᴅᴜʟᴇꜱ: {TOTAL_PAGES} │ 📑 ᴩᴀɢᴇ: {page}/{TOTAL_PAGES}\n"
        f"⏳ ᴛɪᴍᴇ: {now}\n"
        f"💎 ꜱʏꜱᴛᴇᴍ: ᴏɴʟɪɴᴇ 🟢 │ {POWERED_BY}"
    )
    return bq(inner)


def help_keyboard(page: int) -> telebot.types.InlineKeyboardMarkup:
    kb = telebot.types.InlineKeyboardMarkup()
    row = []
    if page > 1:
        row.append(telebot.types.InlineKeyboardButton("◀️ ᴩʀᴇᴠ", callback_data=f"help_{page-1}"))
    row.append(telebot.types.InlineKeyboardButton(f"📑 {page}/{TOTAL_PAGES}", callback_data="noop"))
    if page < TOTAL_PAGES:
        row.append(telebot.types.InlineKeyboardButton("▶️ ɴᴇxᴛ", callback_data=f"help_{page+1}"))
    kb.row(*row)
    kb.row(telebot.types.InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="home"))
    return kb


def register(bot: telebot.TeleBot):

    @bot.message_handler(commands=["help"])
    def help_cmd(msg: telebot.types.Message):
        bot.send_message(msg.chat.id, help_text(1), parse_mode="HTML", reply_markup=help_keyboard(1))

    @bot.callback_query_handler(func=lambda c: c.data.startswith("help_"))
    def help_page_cb(call: telebot.types.CallbackQuery):
        page = int(call.data.split("_")[1])
        bot.edit_message_text(
            help_text(page),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=help_keyboard(page),
        )
        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda c: c.data == "noop")
    def noop_cb(call: telebot.types.CallbackQuery):
        bot.answer_callback_query(call.id)
