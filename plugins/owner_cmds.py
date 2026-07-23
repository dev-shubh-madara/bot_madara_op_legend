"""
Owner-only commands: /eval /sh /restart
"""
import os
import sys
import subprocess
import traceback
import telebot
from config import OWNER_ID, BOT_NAME, POWERED_BY
from helpers import bq, esc


def _is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def register(bot: telebot.TeleBot):

    @bot.message_handler(commands=["eval"])
    def eval_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return
        code = msg.text.partition(" ")[2].strip()
        if not code:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /eval ‹python code›"), parse_mode="HTML")
            return
        try:
            result = eval(code)  # noqa: S307
            bot.send_message(msg.chat.id, bq(f"✅ ʀᴇꜱᴜʟᴛ:\n\n{esc(str(result))}"), parse_mode="HTML")
        except Exception:
            bot.send_message(msg.chat.id, bq(f"❌ ᴇʀʀᴏʀ:\n\n{esc(traceback.format_exc())}"), parse_mode="HTML")

    @bot.message_handler(commands=["sh"])
    def sh_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return
        cmd = msg.text.partition(" ")[2].strip()
        if not cmd:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /sh ‹command›"), parse_mode="HTML")
            return
        try:
            out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=15)
            result = out.decode("utf-8", errors="replace").strip() or "(ɴᴏ ᴏᴜᴛᴩᴜᴛ)"
        except subprocess.CalledProcessError as e:
            result = e.output.decode("utf-8", errors="replace").strip()
        except Exception as e:
            result = str(e)
        bot.send_message(
            msg.chat.id,
            bq(f"🖥️ ꜱʜᴇʟʟ ᴏᴜᴛᴩᴜᴛ:\n\n{esc(result[:3800])}"),
            parse_mode="HTML",
        )

    @bot.message_handler(commands=["restart"])
    def restart_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return
        bot.send_message(
            msg.chat.id,
            bq(f"🔄 ʀᴇꜱᴛᴀʀᴛɪɴɢ {BOT_NAME}…\n\n💎 {POWERED_BY}"),
            parse_mode="HTML",
        )
        os.execl(sys.executable, sys.executable, *sys.argv)
