"""
Owner-only commands: /eval /sh /restart
"""
import os
import sys
import subprocess
import traceback
import telebot
from config import OWNER_ID, BOT_NAME, POWERED_BY


def _is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def register(bot: telebot.TeleBot):

    # ── /eval ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["eval"])
    def eval_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ.")
            return
        code = msg.text.partition(" ")[2].strip()
        if not code:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /eval <python code>")
            return
        try:
            result = eval(code)  # noqa: S307
            bot.send_message(msg.chat.id, f"✅ ʀᴇꜱᴜʟᴛ:\n\n{result}")
        except Exception:
            bot.send_message(msg.chat.id, f"❌ ᴇʀʀᴏʀ:\n\n{traceback.format_exc()}")

    # ── /sh ───────────────────────────────────────────────────────
    @bot.message_handler(commands=["sh"])
    def sh_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ.")
            return
        cmd = msg.text.partition(" ")[2].strip()
        if not cmd:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /sh <command>")
            return
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=15)
            result = out.decode("utf-8", errors="replace").strip() or "(ɴᴏ ᴏᴜᴛᴩᴜᴛ)"
        except subprocess.CalledProcessError as e:
            result = e.output.decode("utf-8", errors="replace").strip()
        except Exception as e:
            result = str(e)
        bot.send_message(msg.chat.id, f"🖥️ ꜱʜᴇʟʟ ᴏᴜᴛᴩᴜᴛ:\n\n{result[:4000]}")

    # ── /restart ───────────────────────────────────────────────────
    @bot.message_handler(commands=["restart"])
    def restart_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ.")
            return
        bot.send_message(msg.chat.id, f"🔄 ʀᴇꜱᴛᴀʀᴛɪɴɢ {BOT_NAME}…\n\n💎 {POWERED_BY}")
        os.execl(sys.executable, sys.executable, *sys.argv)
