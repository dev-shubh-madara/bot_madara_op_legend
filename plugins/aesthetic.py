"""
Aesthetic / fun commands: /hug /slap /kiss /dice /fvn /spotify
"""
import random
import telebot
from config import POWERED_BY
from helpers import bq, esc

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

    @bot.message_handler(commands=["hug"])
    def hug_cmd(msg: telebot.types.Message):
        target = (msg.reply_to_message.from_user.first_name
                  if msg.reply_to_message
                  else msg.text.split(None, 1)[1] if len(msg.text.split()) > 1 else "")
        sender = msg.from_user.first_name
        bot.send_animation(
            msg.chat.id, random.choice(HUG_GIFS),
            caption=bq(f"🤗 {esc(sender)} ʜᴜɢꜱ {esc(target)}!\n\n💎 {POWERED_BY}"),
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["slap"])
    def slap_cmd(msg: telebot.types.Message):
        target = (msg.reply_to_message.from_user.first_name
                  if msg.reply_to_message
                  else msg.text.split(None, 1)[1] if len(msg.text.split()) > 1 else "")
        sender = msg.from_user.first_name
        bot.send_animation(
            msg.chat.id, random.choice(SLAP_GIFS),
            caption=bq(f"👋 {esc(sender)} ꜱʟᴀᴩꜱ {esc(target)}!\n\n💎 {POWERED_BY}"),
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["kiss"])
    def kiss_cmd(msg: telebot.types.Message):
        target = (msg.reply_to_message.from_user.first_name
                  if msg.reply_to_message
                  else msg.text.split(None, 1)[1] if len(msg.text.split()) > 1 else "")
        sender = msg.from_user.first_name
        bot.send_animation(
            msg.chat.id, random.choice(KISS_GIFS),
            caption=bq(f"💋 {esc(sender)} ᴋɪꜱꜱᴇꜱ {esc(target)}!\n\n💎 {POWERED_BY}"),
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["dice"])
    def dice_cmd(msg: telebot.types.Message):
        bot.send_dice(msg.chat.id)

    @bot.message_handler(commands=["fvn"])
    def fvn_cmd(msg: telebot.types.Message):
        parts = msg.text.split(None, 1)
        if len(parts) < 2:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /fvn ‹text›"), parse_mode="HTML")
            return
        result = to_fancy(parts[1])
        bot.send_message(
            msg.chat.id,
            bq(f"✨ ꜰᴀɴᴄʏ ᴛᴇxᴛ:\n\n{esc(result)}\n\n💎 {POWERED_BY}"),
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["spotify"])
    def spotify_cmd(msg: telebot.types.Message):
        parts = msg.text.split(None, 1)
        if len(parts) < 2:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /spotify ‹song name›"), parse_mode="HTML")
            return
        query = parts[1].strip()
        search_url = f"https://open.spotify.com/search/{query.replace(' ', '%20')}"
        bot.send_message(
            msg.chat.id,
            bq(
                f"🎵 ꜱᴩᴏᴛɪꜰʏ ꜱᴇᴀʀᴄʜ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"🔍 ꜱᴏɴɢ: {esc(query)}\n"
                f"🔗 ʟɪɴᴋ: {search_url}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"💎 {POWERED_BY}"
            ),
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
