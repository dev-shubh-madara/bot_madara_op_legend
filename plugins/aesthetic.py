"""
Aesthetic / fun commands: /hug /slap /kiss /dice /fvn /spotify
"""
import random
import telebot
from config import POWERED_BY

HUG_GIFS = [
    "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
    "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
    "https://media.giphy.com/media/3bqtLDGB2GlWw/giphy.gif",
]
SLAP_GIFS = [
    "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "https://media.giphy.com/media/uqSU9IEYEKAbS/giphy.gif",
]
KISS_GIFS = [
    "https://media.giphy.com/media/bGm9FuBCGg4SY/giphy.gif",
    "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
]

# Fancy font map (A–Z)
FANCY = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ",
    "f": "ꜰ", "g": "ɢ", "h": "ʜ", "i": "ɪ", "j": "ᴊ",
    "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ", "o": "ᴏ",
    "p": "ᴩ", "q": "Q", "r": "ʀ", "s": "ꜱ", "t": "ᴛ",
    "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}


def to_fancy(text: str) -> str:
    return "".join(FANCY.get(c.lower(), c) for c in text)


def register(bot: telebot.TeleBot):

    # ── /hug ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["hug"])
    def hug_cmd(msg: telebot.types.Message):
        target = ""
        if msg.reply_to_message:
            target = msg.reply_to_message.from_user.first_name
        elif len(msg.text.split()) > 1:
            target = msg.text.split(None, 1)[1]
        sender = msg.from_user.first_name
        caption = f"🤗 {sender} ʜᴜɢꜱ {target}!\n\n💎 {POWERED_BY}"
        bot.send_animation(msg.chat.id, random.choice(HUG_GIFS), caption=caption)

    # ── /slap ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["slap"])
    def slap_cmd(msg: telebot.types.Message):
        target = ""
        if msg.reply_to_message:
            target = msg.reply_to_message.from_user.first_name
        elif len(msg.text.split()) > 1:
            target = msg.text.split(None, 1)[1]
        sender = msg.from_user.first_name
        caption = f"👋 {sender} ꜱʟᴀᴩꜱ {target}!\n\n💎 {POWERED_BY}"
        bot.send_animation(msg.chat.id, random.choice(SLAP_GIFS), caption=caption)

    # ── /kiss ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["kiss"])
    def kiss_cmd(msg: telebot.types.Message):
        target = ""
        if msg.reply_to_message:
            target = msg.reply_to_message.from_user.first_name
        elif len(msg.text.split()) > 1:
            target = msg.text.split(None, 1)[1]
        sender = msg.from_user.first_name
        caption = f"💋 {sender} ᴋɪꜱꜱᴇꜱ {target}!\n\n💎 {POWERED_BY}"
        bot.send_animation(msg.chat.id, random.choice(KISS_GIFS), caption=caption)

    # ── /dice ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["dice"])
    def dice_cmd(msg: telebot.types.Message):
        bot.send_dice(msg.chat.id)

    # ── /fvn ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["fvn"])
    def fvn_cmd(msg: telebot.types.Message):
        parts = msg.text.split(None, 1)
        if len(parts) < 2:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /fvn <text>")
            return
        result = to_fancy(parts[1])
        bot.send_message(msg.chat.id, f"✨ ꜰᴀɴᴄʏ ᴛᴇxᴛ:\n\n{result}\n\n💎 {POWERED_BY}")

    # ── /spotify ───────────────────────────────────────────────────
    @bot.message_handler(commands=["spotify"])
    def spotify_cmd(msg: telebot.types.Message):
        parts = msg.text.split(None, 1)
        if len(parts) < 2:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /spotify <song name>")
            return
        query = parts[1].strip()
        search_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
        bot.send_message(
            msg.chat.id,
            f"🎵 ꜱᴩᴏᴛɪꜰʏ ꜱᴇᴀʀᴄʜ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"🔍 ꜱᴏɴɢ: {query}\n"
            f"🔗 ʟɪɴᴋ: {search_url}\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💎 {POWERED_BY}",
            disable_web_page_preview=True,
        )
