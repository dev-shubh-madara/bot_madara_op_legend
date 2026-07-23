"""
Node management: /add /remove /nodes /broadcast /stats /ping /setvideo
"""
import time
import psutil
import asyncio
import telebot
from config import OWNER_ID, BOT_NAME, POWERED_BY
from database import (
    add_userbot, remove_userbot, get_all_userbots,
    get_userbot_count, get_userbot, get_setting, set_setting,
)
from userbot_manager import start_client, stop_client, get_all_clients
from helpers import bq, esc

# Track users waiting to submit their session string manually
_pending_add: set[int] = set()


def _is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def register(bot: telebot.TeleBot):

    # ── /add  (manual session string entry for advanced users) ────
    @bot.message_handler(commands=["add"])
    def add_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        _pending_add.add(uid)
        bot.send_message(
            msg.chat.id,
            bq(
                "🔐 ꜱᴇɴᴅ ʏᴏᴜʀ ᴩʏʀᴏɢʀᴀᴍ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ɴᴏᴡ.\n\n"
                "ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ? ᴜꜱᴇ /gen ᴛᴏ ʟᴏɢɪɴ ᴅɪʀᴇᴄᴛʟʏ.\n\n"
                "⚠️ ᴛʏᴩᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ."
            ),
            parse_mode="HTML",
        )

    @bot.message_handler(func=lambda m: m.from_user.id in _pending_add and m.text and not m.text.startswith("/"))
    def receive_session(msg: telebot.types.Message):
        uid = msg.from_user.id
        session_str = msg.text.strip()
        _pending_add.discard(uid)

        wait_msg = bot.send_message(msg.chat.id, bq("⏳ ᴄᴏɴɴᴇᴄᴛɪɴɢ ɴᴏᴅᴇ…"), parse_mode="HTML")

        async def _connect():
            client = await start_client(uid, session_str)
            if client is None:
                return None
            me = await client.get_me()
            return me

        loop = asyncio.new_event_loop()
        try:
            me = loop.run_until_complete(_connect())
        except Exception:
            me = None
        finally:
            loop.close()

        if me is None:
            bot.edit_message_text(
                bq("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ. ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ."),
                wait_msg.chat.id, wait_msg.message_id, parse_mode="HTML",
            )
            return

        username = getattr(me, "username", "") or ""
        first_name = getattr(me, "first_name", "") or ""
        add_userbot(uid, session_str, username, first_name)

        bot.edit_message_text(
            bq(
                f"✅ ɴᴏᴅᴇ ᴅᴇᴩʟᴏʏᴇᴅ!\n\n"
                f"👤 ɴᴀᴍᴇ: {esc(first_name)}\n"
                f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{esc(username)}\n"
                f"🔗 ᴜɪᴅ: {me.id}\n\n"
                f"💎 {POWERED_BY}"
            ),
            wait_msg.chat.id, wait_msg.message_id, parse_mode="HTML",
        )

    # ── /remove ───────────────────────────────────────────────────
    @bot.message_handler(commands=["remove"])
    def remove_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        parts = msg.text.split()

        if len(parts) > 1 and _is_owner(uid):
            try:
                target_uid = int(parts[1])
            except ValueError:
                bot.send_message(msg.chat.id, bq("❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ."), parse_mode="HTML")
                return
        else:
            target_uid = uid

        row = get_userbot(target_uid)
        if row is None:
            bot.send_message(msg.chat.id, bq("⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ɪᴅ."), parse_mode="HTML")
            return

        async def _stop():
            await stop_client(target_uid)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(_stop())
        loop.close()

        remove_userbot(target_uid)
        bot.send_message(
            msg.chat.id,
            bq(f"💀 ɴᴏᴅᴇ {target_uid} ᴋɪʟʟᴇᴅ.\n\n💎 {POWERED_BY}"),
            parse_mode="HTML",
        )

    # ── /nodes ────────────────────────────────────────────────────
    @bot.message_handler(commands=["nodes"])
    def nodes_cmd(msg: telebot.types.Message):
        rows = get_all_userbots()
        clients = get_all_clients()
        if not rows:
            bot.send_message(msg.chat.id, bq("📭 ɴᴏ ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇꜱ."), parse_mode="HTML")
            return

        lines = [f"📋 ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇꜱ [{len(rows)}]\n━━━━━━━━━━━━━━━━━━"]
        for i, (user_id, username, first_name, _, added_at) in enumerate(rows, 1):
            status = "🟢" if user_id in clients else "🔴"
            uname = f"@{esc(username)}" if username else "—"
            lines.append(f"{status} [{i}] {esc(first_name)} ({uname})\n    🆔 {user_id}")

        lines.append(f"\n💎 {POWERED_BY}")
        bot.send_message(msg.chat.id, bq("\n".join(lines)), parse_mode="HTML")

    # ── /activebot ────────────────────────────────────────────────
    @bot.message_handler(commands=["activebot"])
    def activebot_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        row = get_userbot(uid)
        clients = get_all_clients()
        if row is None:
            bot.send_message(msg.chat.id, bq("⚠️ ʏᴏᴜ ʜᴀᴠᴇ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /gen ꜰɪʀꜱᴛ."), parse_mode="HTML")
            return

        user_id, username, first_name, _ = row
        status = "🟢 ᴏɴʟɪɴᴇ" if user_id in clients else "🔴 ᴏꜰꜰʟɪɴᴇ"
        bot.send_message(
            msg.chat.id,
            bq(
                "🚀 ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇ ɪɴꜰᴏ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 ɴᴀᴍᴇ: {esc(first_name)}\n"
                f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{esc(username)}\n"
                f"🔗 ᴜɪᴅ: {user_id}\n"
                f"📡 ꜱᴛᴀᴛᴜꜱ: {status}\n\n"
                f"💎 {POWERED_BY}"
            ),
            parse_mode="HTML",
        )

    # ── /ping ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["ping"])
    def ping_cmd(msg: telebot.types.Message):
        t0 = time.time()
        video_id = get_setting("ping_video")
        latency = round((time.time() - t0) * 1000, 2)

        text = bq(f"⚡️ ᴩᴏɴɢ!\n━━━━━━━━━━━━━━━━━━\n🏓 ʟᴀᴛᴇɴᴄʏ: {latency} ᴍꜱ\n\n💎 {POWERED_BY}")

        if video_id:
            bot.send_video(msg.chat.id, video_id, caption=text, parse_mode="HTML")
        else:
            bot.send_message(msg.chat.id, text, parse_mode="HTML")

    # ── /stats ────────────────────────────────────────────────────
    @bot.message_handler(commands=["stats"])
    def stats_cmd(msg: telebot.types.Message):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        nodes = get_userbot_count()

        def bar(pct, size=10):
            f = int(pct / 100 * size)
            return "▰" * f + "▱" * (size - f)

        text = bq(
            f"📊 {BOT_NAME} ꜱᴛᴀᴛꜱ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"⚡️ ᴄᴩᴜ  : [{bar(cpu)}] {cpu}%\n"
            f"🧠 ʀᴀᴍ  : [{bar(ram.percent)}] {ram.percent}%\n"
            f"💾 ᴅɪꜱᴋ : [{bar(disk.percent)}] {disk.percent}%\n"
            f"🤖 ɴᴏᴅᴇꜱ: {nodes} ᴀᴄᴛɪᴠᴇ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💎 {POWERED_BY}"
        )
        bot.send_message(msg.chat.id, text, parse_mode="HTML")

    # ── /broadcast (owner) ────────────────────────────────────────
    @bot.message_handler(commands=["broadcast"])
    def broadcast_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return
        text = msg.text.partition(" ")[2].strip()
        if not text:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /broadcast ‹ᴍᴇꜱꜱᴀɢᴇ›"), parse_mode="HTML")
            return
        rows = get_all_userbots()
        ok = 0
        for (user_id, *_) in rows:
            try:
                bot.send_message(user_id, bq(f"📣 {BOT_NAME} ʙʀᴏᴀᴅᴄᴀꜱᴛ:\n\n{esc(text)}"), parse_mode="HTML")
                ok += 1
            except Exception:
                pass
        bot.send_message(msg.chat.id, bq(f"✅ ꜱᴇɴᴛ ᴛᴏ {ok}/{len(rows)} ᴜꜱᴇʀꜱ."), parse_mode="HTML")

    # ── /setvideo (owner) ─────────────────────────────────────────
    @bot.message_handler(commands=["setvideo"])
    def setvideo_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return

        parts = msg.text.split()
        if len(parts) < 2 or parts[1] not in ("start", "ping"):
            bot.send_message(
                msg.chat.id,
                bq(
                    "ᴜꜱᴀɢᴇ: ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴠɪᴅᴇᴏ ᴀɴᴅ ꜱᴇɴᴅ:\n\n"
                    "  /setvideo start — ꜱᴇᴛ /start ᴠɪᴅᴇᴏ\n"
                    "  /setvideo ping  — ꜱᴇᴛ /ping ᴠɪᴅᴇᴏ\n\n"
                    "ᴛᴏ ᴄʟᴇᴀʀ ᴀ ᴠɪᴅᴇᴏ:\n"
                    "  /setvideo start clear\n"
                    "  /setvideo ping clear"
                ),
                parse_mode="HTML",
            )
            return

        slot = parts[1]  # "start" or "ping"
        key = f"{slot}_video"

        # Clear mode
        if len(parts) >= 3 and parts[2] == "clear":
            set_setting(key, "")
            bot.send_message(msg.chat.id, bq(f"🗑️ {slot} ᴠɪᴅᴇᴏ ᴄʟᴇᴀʀᴇᴅ."), parse_mode="HTML")
            return

        # Must reply to a video/animation
        reply = msg.reply_to_message
        if reply is None:
            bot.send_message(
                msg.chat.id,
                bq("⚠️ ʀᴇᴩʟʏ ᴛᴏ ᴀ ᴠɪᴅᴇᴏ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ."),
                parse_mode="HTML",
            )
            return

        file_id = None
        if reply.video:
            file_id = reply.video.file_id
        elif reply.animation:
            file_id = reply.animation.file_id
        elif reply.document and reply.document.mime_type and reply.document.mime_type.startswith("video"):
            file_id = reply.document.file_id

        if not file_id:
            bot.send_message(
                msg.chat.id,
                bq("❌ ɴᴏ ᴠɪᴅᴇᴏ ꜰᴏᴜɴᴅ ɪɴ ᴛʜᴇ ʀᴇᴩʟɪᴇᴅ ᴍᴇꜱꜱᴀɢᴇ."),
                parse_mode="HTML",
            )
            return

        set_setting(key, file_id)
        bot.send_message(
            msg.chat.id,
            bq(f"✅ /{slot} ᴠɪᴅᴇᴏ ꜱᴀᴠᴇᴅ!\n\nᴛʀʏ /{slot} ᴛᴏ ꜱᴇᴇ ɪᴛ."),
            parse_mode="HTML",
        )

    # ── Callbacks ─────────────────────────────────────────────────
    @bot.callback_query_handler(func=lambda c: c.data == "add_ub")
    def add_ub_cb(call: telebot.types.CallbackQuery):
        bot.answer_callback_query(call.id)
        # Redirect to /gen flow (in-bot login)
        from plugins.gen_session import _start_gen_flow
        uid = call.from_user.id
        existing = get_userbot(uid)
        from userbot_manager import get_client
        client = get_client(uid)
        if existing and client:
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(
                telebot.types.InlineKeyboardButton("✅ ᴋᴇᴇᴩ", callback_data="gen_keep"),
                telebot.types.InlineKeyboardButton("🔄 ʀᴇᴩʟᴀᴄᴇ", callback_data="gen_replace"),
            )
            bot.send_message(
                call.message.chat.id,
                bq("⚠️ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴜꜱᴇʀʙᴏᴛ.\nᴅᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ʀᴇᴩʟᴀᴄᴇ ɪᴛ?"),
                parse_mode="HTML",
                reply_markup=kb,
            )
        else:
            _start_gen_flow(bot, call.message.chat.id, uid)

    @bot.callback_query_handler(func=lambda c: c.data == "nodes")
    def nodes_cb(call: telebot.types.CallbackQuery):
        bot.answer_callback_query(call.id)
        nodes_cmd(call.message)
