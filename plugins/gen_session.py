"""
In-bot session string generator.
Flow: /gen → phone number → OTP → (2FA password if needed) → session string → auto-add userbot
"""
import asyncio
import logging
import telebot
from pyrogram import Client
from pyrogram.errors import (
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    BadRequest,
)
from config import API_ID, API_HASH, POWERED_BY, BOT_NAME
from database import add_userbot, get_userbot
from userbot_manager import start_client, get_client
from helpers import bq, esc

logger = logging.getLogger(__name__)

# uid -> dict with keys: state, phone, phone_code_hash, client
_state: dict[int, dict] = {}

STATES = {
    "PHONE": "awaiting_phone",
    "OTP":   "awaiting_otp",
    "PWD":   "awaiting_2fa",
}


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _cleanup(uid: int):
    entry = _state.pop(uid, None)
    if entry and entry.get("client"):
        try:
            _run(entry["client"].disconnect())
        except Exception:
            pass


def _is_in_gen_flow(uid: int) -> bool:
    return uid in _state


def register(bot: telebot.TeleBot):

    @bot.message_handler(commands=["gen"])
    def gen_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        existing = get_userbot(uid)
        client = get_client(uid)
        if existing and client:
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(
                telebot.types.InlineKeyboardButton("✅ ᴋᴇᴇᴩ ᴄᴜʀʀᴇɴᴛ", callback_data="gen_keep"),
                telebot.types.InlineKeyboardButton("🔄 ʀᴇᴩʟᴀᴄᴇ", callback_data="gen_replace"),
            )
            bot.send_message(
                msg.chat.id,
                bq("⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴜꜱᴇʀʙᴏᴛ.\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴩʟᴀᴄᴇ ɪᴛ?"),
                parse_mode="HTML",
                reply_markup=kb,
            )
            return
        _start_gen_flow(bot, msg.chat.id, uid)

    @bot.callback_query_handler(func=lambda c: c.data in ("gen_keep", "gen_replace"))
    def gen_replace_cb(call: telebot.types.CallbackQuery):
        bot.answer_callback_query(call.id)
        if call.data == "gen_keep":
            bot.edit_message_text(
                bq("✅ ᴋᴇᴩᴛ ʏᴏᴜʀ ᴇxɪꜱᴛɪɴɢ ᴜꜱᴇʀʙᴏᴛ."),
                call.message.chat.id, call.message.message_id, parse_mode="HTML",
            )
            return
        _start_gen_flow(bot, call.message.chat.id, call.from_user.id)

    # ── /cancel (handles both gen flow and /add pending state) ────
    @bot.message_handler(commands=["cancel"])
    def cancel_gen(msg: telebot.types.Message):
        uid = msg.from_user.id
        from plugins.node_mgmt import _pending_add
        cleared = False
        if _is_in_gen_flow(uid):
            _cleanup(uid)
            cleared = True
        if uid in _pending_add:
            _pending_add.discard(uid)
            cleared = True
        bot.send_message(
            msg.chat.id,
            bq("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ." if cleared else "❌ ɴᴏᴛʜɪɴɢ ᴛᴏ ᴄᴀɴᴄᴇʟ."),
            parse_mode="HTML",
        )

    # ── Universal text handler for the gen flow ───────────────────
    @bot.message_handler(func=lambda m: m.from_user.id in _state and not m.text.startswith("/"))
    def gen_flow_text(msg: telebot.types.Message):
        uid = msg.from_user.id
        entry = _state.get(uid)
        if not entry:
            return
        state = entry["state"]
        if state == STATES["PHONE"]:
            _handle_phone(bot, msg, uid, entry)
        elif state == STATES["OTP"]:
            _handle_otp(bot, msg, uid, entry)
        elif state == STATES["PWD"]:
            _handle_2fa(bot, msg, uid, entry)


# ── Flow helpers ──────────────────────────────────────────────────

def _start_gen_flow(bot: telebot.TeleBot, chat_id: int, uid: int):
    _state[uid] = {"state": STATES["PHONE"], "client": None}
    bot.send_message(
        chat_id,
        bq(
            f"🔐 {BOT_NAME} — ɪɴ-ʙᴏᴛ ʟᴏɢɪɴ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "ꜱᴛᴇᴩ 1/3 — ᴩʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n\n"
            "📱 ꜱᴇɴᴅ ʏᴏᴜʀ ᴩʜᴏɴᴇ ɴᴜᴍʙᴇʀ ᴡɪᴛʜ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ:\n"
            "  ᴇxᴀᴍᴩʟᴇ: +919876543210\n\n"
            "⚠️ ᴛʏᴩᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ.\n\n"
            f"💎 {POWERED_BY}"
        ),
        parse_mode="HTML",
    )


def _handle_phone(bot: telebot.TeleBot, msg: telebot.types.Message, uid: int, entry: dict):
    phone = msg.text.strip()
    chat_id = msg.chat.id
    wait = bot.send_message(chat_id, bq("⏳ ꜱᴇɴᴅɪɴɢ ᴏᴛᴩ…"), parse_mode="HTML")

    async def _send_code():
        client = Client(f"gen_{uid}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
        await client.connect()
        sent = await client.send_code(phone)
        return client, sent.phone_code_hash

    try:
        client, phone_code_hash = _run(_send_code())
    except PhoneNumberInvalid:
        bot.edit_message_text(
            bq("❌ ɪɴᴠᴀʟɪᴅ ᴩʜᴏɴᴇ ɴᴜᴍʙᴇʀ. ᴛʀʏ ᴀɢᴀɪɴ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )
        return
    except Exception as e:
        _cleanup(uid)
        bot.edit_message_text(
            bq(f"❌ ᴇʀʀᴏʀ: {esc(str(e))}\n\nᴜꜱᴇ /gen ᴛᴏ ʀᴇᴛʀʏ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )
        return

    entry.update({"state": STATES["OTP"], "phone": phone, "phone_code_hash": phone_code_hash, "client": client})
    bot.edit_message_text(
        bq(
            f"✅ ᴏᴛᴩ ꜱᴇɴᴛ ᴛᴏ {esc(phone)}!\n\n"
            "ꜱᴛᴇᴩ 2/3 — ᴇɴᴛᴇʀ ᴏᴛᴩ\n\n"
            "📨 ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴀᴩᴩ ꜰᴏʀ ᴛʜᴇ ʟᴏɢɪɴ ᴄᴏᴅᴇ.\n"
            "ꜱᴇɴᴅ ᴛʜᴇ 5-ᴅɪɢɪᴛ ᴄᴏᴅᴇ ʜᴇʀᴇ.\n\n"
            "⚠️ /cancel ᴛᴏ ᴀʙᴏʀᴛ."
        ),
        chat_id, wait.message_id, parse_mode="HTML",
    )


def _handle_otp(bot: telebot.TeleBot, msg: telebot.types.Message, uid: int, entry: dict):
    otp = msg.text.strip().replace(" ", "")
    chat_id = msg.chat.id
    client: Client = entry["client"]
    phone = entry["phone"]
    phone_code_hash = entry["phone_code_hash"]
    wait = bot.send_message(chat_id, bq("⏳ ᴠᴇʀɪꜰʏɪɴɢ ᴏᴛᴩ…"), parse_mode="HTML")

    async def _sign_in():
        return await client.sign_in(phone, phone_code_hash, otp)

    try:
        _run(_sign_in())
        _finish_login(bot, chat_id, uid, entry, wait.message_id)
    except SessionPasswordNeeded:
        entry["state"] = STATES["PWD"]
        bot.edit_message_text(
            bq(
                "🔐 ᴛᴡᴏ-ꜰᴀᴄᴛᴏʀ ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ ᴇɴᴀʙʟᴇᴅ.\n\n"
                "ꜱᴛᴇᴩ 3/3 — 2ꜰᴀ ᴩᴀꜱꜱᴡᴏʀᴅ\n\n"
                "🔑 ꜱᴇɴᴅ ʏᴏᴜʀ ᴛᴇʟᴇɢʀᴀᴍ ᴄʟᴏᴜᴅ ᴩᴀꜱꜱᴡᴏʀᴅ.\n\n"
                "⚠️ /cancel ᴛᴏ ᴀʙᴏʀᴛ."
            ),
            chat_id, wait.message_id, parse_mode="HTML",
        )
    except PhoneCodeInvalid:
        bot.edit_message_text(
            bq("❌ ᴡʀᴏɴɢ ᴏᴛᴩ. ᴩʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴄᴏᴅᴇ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )
    except PhoneCodeExpired:
        _cleanup(uid)
        bot.edit_message_text(
            bq("❌ ᴏᴛᴩ ᴇxᴩɪʀᴇᴅ. ᴜꜱᴇ /gen ᴛᴏ ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )
    except Exception as e:
        _cleanup(uid)
        bot.edit_message_text(
            bq(f"❌ ᴇʀʀᴏʀ: {esc(str(e))}\n\nᴜꜱᴇ /gen ᴛᴏ ʀᴇᴛʀʏ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )


def _handle_2fa(bot: telebot.TeleBot, msg: telebot.types.Message, uid: int, entry: dict):
    password = msg.text.strip()
    chat_id = msg.chat.id
    client: Client = entry["client"]
    try:
        bot.delete_message(chat_id, msg.message_id)
    except Exception:
        pass
    wait = bot.send_message(chat_id, bq("⏳ ᴠᴇʀɪꜰʏɪɴɢ 2ꜰᴀ…"), parse_mode="HTML")

    async def _check_pwd():
        await client.check_password(password)

    try:
        _run(_check_pwd())
        _finish_login(bot, chat_id, uid, entry, wait.message_id)
    except BadRequest:
        bot.edit_message_text(
            bq("❌ ᴡʀᴏɴɢ ᴩᴀꜱꜱᴡᴏʀᴅ. ᴩʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )
    except Exception as e:
        _cleanup(uid)
        bot.edit_message_text(
            bq(f"❌ ᴇʀʀᴏʀ: {esc(str(e))}\n\nᴜꜱᴇ /gen ᴛᴏ ʀᴇᴛʀʏ."),
            chat_id, wait.message_id, parse_mode="HTML",
        )


def _finish_login(bot: telebot.TeleBot, chat_id: int, uid: int, entry: dict, edit_msg_id: int):
    client: Client = entry["client"]

    async def _export():
        session_string = await client.export_session_string()
        me = await client.get_me()
        await client.disconnect()
        return session_string, me

    try:
        session_string, me = _run(_export())
    except Exception as e:
        _cleanup(uid)
        bot.edit_message_text(
            bq(f"❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴇxᴩᴏʀᴛ ꜱᴇꜱꜱɪᴏɴ: {esc(str(e))}"),
            chat_id, edit_msg_id, parse_mode="HTML",
        )
        return

    _state.pop(uid, None)
    username = getattr(me, "username", "") or ""
    first_name = getattr(me, "first_name", "") or ""
    add_userbot(uid, session_string, username, first_name)

    async def _start():
        return await start_client(uid, session_string)

    live = _run(_start())

    if live:
        bot.edit_message_text(
            bq(
                "✅ ʟᴏɢɪɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 ɴᴀᴍᴇ  : {esc(first_name)}\n"
                f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{esc(username)}\n"
                f"🔗 ᴜɪᴅ   : {me.id}\n"
                "📡 ꜱᴛᴀᴛᴜꜱ : 🟢 ᴏɴʟɪɴᴇ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🚀 ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴡ ᴀᴄᴛɪᴠᴇ!\n"
                "ᴜꜱᴇ /help ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ.\n\n"
                f"💎 {POWERED_BY}"
            ),
            chat_id, edit_msg_id, parse_mode="HTML",
        )
    else:
        bot.edit_message_text(
            bq(
                "⚠️ ʟᴏɢɢᴇᴅ ɪɴ ʙᴜᴛ ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ʟɪᴠᴇ ᴄʟɪᴇɴᴛ.\n"
                "ᴜꜱᴇ /add ᴛᴏ ᴍᴀɴᴜᴀʟʟʏ ʀᴇᴄᴏɴɴᴇᴄᴛ."
            ),
            chat_id, edit_msg_id, parse_mode="HTML",
        )
