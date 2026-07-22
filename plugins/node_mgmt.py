"""
Node management: /add /gen /remove /nodes /broadcast /stats /ping
"""
import time
import psutil
import asyncio
import telebot
from config import OWNER_ID, BOT_NAME, POWERED_BY
from database import add_userbot, remove_userbot, get_all_userbots, get_userbot_count, get_userbot
from userbot_manager import start_client, stop_client, get_all_clients, active_count

# Track users waiting to submit their session string
_pending_add: set[int] = set()

GEN_GUIDE = """
🔑 ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ɢᴜɪᴅᴇ
━━━━━━━━━━━━━━━━━━

1️⃣  ɢᴇᴛ ʏᴏᴜʀ API_ID ᴀɴᴅ API_HASH ꜰʀᴏᴍ:
    👉 https://my.telegram.org

2️⃣  ᴜꜱᴇ @StringFatherBot ᴏʀ ʀᴜɴ ᴛʜɪꜱ ʟᴏᴄᴀʟʟʏ:
    pip install pyrogram TgCrypto
    python -c "from pyrogram import Client; Client(':memory:').run()"

3️⃣  ʟᴏɢɪɴ ᴡɪᴛʜ ʏᴏᴜʀ ᴩʜᴏɴᴇ ɴᴜᴍʙᴇʀ + ᴏᴛᴩ

4️⃣  ᴄᴏᴩʏ ᴛʜᴇ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ᴏᴜᴛᴩᴜᴛ

5️⃣  ꜱᴇɴᴅ /add ᴛᴏ ᴛʜɪꜱ ʙᴏᴛ ᴀɴᴅ ᴩᴀꜱᴛᴇ ɪᴛ

⚠️  ɴᴇᴠᴇʀ ꜱʜᴀʀᴇ ʏᴏᴜʀ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ᴡɪᴛʜ ᴀɴʏᴏɴᴇ ᴇʟꜱᴇ!

💎 """ + POWERED_BY


def _is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def register(bot: telebot.TeleBot):

    # ── /gen ────────────────────────────────────────────────────
    @bot.message_handler(commands=["gen"])
    def gen_cmd(msg: telebot.types.Message):
        bot.send_message(msg.chat.id, GEN_GUIDE, disable_web_page_preview=True)

    # ── /add ────────────────────────────────────────────────────
    @bot.message_handler(commands=["add"])
    def add_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        _pending_add.add(uid)
        bot.send_message(
            msg.chat.id,
            "🔐 ꜱᴇɴᴅ ʏᴏᴜʀ ᴩʏʀᴏɢʀᴀᴍ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ɴᴏᴡ.\n\n"
            "ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ? ᴜꜱᴇ /gen ꜰɪʀꜱᴛ.\n\n"
            "⚠️ ᴛʏᴩᴇ /cancel ᴛᴏ ᴀʙᴏʀᴛ."
        )

    @bot.message_handler(commands=["cancel"])
    def cancel_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        _pending_add.discard(uid)
        bot.send_message(msg.chat.id, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ.")

    @bot.message_handler(func=lambda m: m.from_user.id in _pending_add and m.text and not m.text.startswith("/"))
    def receive_session(msg: telebot.types.Message):
        uid = msg.from_user.id
        session_str = msg.text.strip()
        _pending_add.discard(uid)

        wait_msg = bot.send_message(msg.chat.id, "⏳ ᴄᴏɴɴᴇᴄᴛɪɴɢ ɴᴏᴅᴇ…")

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
                "❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ. ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.",
                wait_msg.chat.id, wait_msg.message_id,
            )
            return

        username = getattr(me, "username", "") or ""
        first_name = getattr(me, "first_name", "") or ""
        add_userbot(uid, session_str, username, first_name)

        bot.edit_message_text(
            f"✅ ɴᴏᴅᴇ ᴅᴇᴩʟᴏʏᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!\n\n"
            f"👤 ɴᴀᴍᴇ: {first_name}\n"
            f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{username}\n"
            f"🔗 ᴜɪᴅ: {me.id}\n\n"
            f"💎 {POWERED_BY}",
            wait_msg.chat.id, wait_msg.message_id,
        )

    # ── /remove ─────────────────────────────────────────────────
    @bot.message_handler(commands=["remove"])
    def remove_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        parts = msg.text.split()

        # owner can remove any uid: /remove <uid>
        if len(parts) > 1 and _is_owner(uid):
            try:
                target_uid = int(parts[1])
            except ValueError:
                bot.send_message(msg.chat.id, "❌ ɪɴᴠᴀʟɪᴅ ᴜɪᴅ.")
                return
        else:
            target_uid = uid

        row = get_userbot(target_uid)
        if row is None:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ɪᴅ.")
            return

        async def _stop():
            await stop_client(target_uid)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(_stop())
        loop.close()

        remove_userbot(target_uid)
        bot.send_message(msg.chat.id, f"💀 ɴᴏᴅᴇ {target_uid} ᴋɪʟʟᴇᴅ.\n\n💎 {POWERED_BY}")

    # ── /nodes ───────────────────────────────────────────────────
    @bot.message_handler(commands=["nodes"])
    def nodes_cmd(msg: telebot.types.Message):
        rows = get_all_userbots()
        clients = get_all_clients()
        if not rows:
            bot.send_message(msg.chat.id, "📭 ɴᴏ ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇꜱ.")
            return

        lines = [
            f"📋 ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇꜱ [{len(rows)}]\n━━━━━━━━━━━━━━━━━━"
        ]
        for i, (user_id, username, first_name, _, added_at) in enumerate(rows, 1):
            status = "🟢" if user_id in clients else "🔴"
            uname = f"@{username}" if username else "—"
            lines.append(f"{status} [{i}] {first_name} ({uname})\n    🆔 {user_id}")

        lines.append(f"\n💎 {POWERED_BY}")
        bot.send_message(msg.chat.id, "\n".join(lines))

    # ── /activebot ───────────────────────────────────────────────
    @bot.message_handler(commands=["activebot"])
    def activebot_cmd(msg: telebot.types.Message):
        uid = msg.from_user.id
        row = get_userbot(uid)
        clients = get_all_clients()
        if row is None:
            bot.send_message(msg.chat.id, "⚠️ ʏᴏᴜ ʜᴀᴠᴇ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return

        user_id, username, first_name, _, = row
        status = "🟢 ᴏɴʟɪɴᴇ" if user_id in clients else "🔴 ᴏꜰꜰʟɪɴᴇ"
        bot.send_message(
            msg.chat.id,
            f"🚀 ᴀᴄᴛɪᴠᴇ ɴᴏᴅᴇ ɪɴꜰᴏ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 ɴᴀᴍᴇ: {first_name}\n"
            f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: @{username}\n"
            f"🔗 ᴜɪᴅ: {user_id}\n"
            f"📡 ꜱᴛᴀᴛᴜꜱ: {status}\n\n"
            f"💎 {POWERED_BY}"
        )

    # ── /ping ────────────────────────────────────────────────────
    @bot.message_handler(commands=["ping"])
    def ping_cmd(msg: telebot.types.Message):
        t0 = time.time()
        sent = bot.send_message(msg.chat.id, "⏳ ᴩɪɴɢɪɴɢ…")
        latency = round((time.time() - t0) * 1000, 2)
        bot.edit_message_text(
            f"⚡️ ᴩᴏɴɢ! {latency} ᴍꜱ\n💎 {POWERED_BY}",
            sent.chat.id, sent.message_id,
        )

    # ── /stats ───────────────────────────────────────────────────
    @bot.message_handler(commands=["stats"])
    def stats_cmd(msg: telebot.types.Message):
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        nodes = get_userbot_count()

        def bar(pct, size=10):
            f = int(pct / 100 * size)
            return "▰" * f + "▱" * (size - f)

        text = (
            f"📊 {BOT_NAME} ꜱᴛᴀᴛꜱ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"⚡️ ᴄᴩᴜ  : [{bar(cpu)}] {cpu}%\n"
            f"🧠 ʀᴀᴍ  : [{bar(ram.percent)}] {ram.percent}%\n"
            f"💾 ᴅɪꜱᴋ : [{bar(disk.percent)}] {disk.percent}%\n"
            f"🤖 ɴᴏᴅᴇꜱ: {nodes} ᴀᴄᴛɪᴠᴇ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"💎 {POWERED_BY}"
        )
        bot.send_message(msg.chat.id, text)

    # ── /broadcast (owner) ────────────────────────────────────────
    @bot.message_handler(commands=["broadcast"])
    def broadcast_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ.")
            return
        text = msg.text.partition(" ")[2].strip()
        if not text:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /broadcast <message>")
            return
        rows = get_all_userbots()
        ok = 0
        for (user_id, *_) in rows:
            try:
                bot.send_message(user_id, f"📣 {BOT_NAME} ʙʀᴏᴀᴅᴄᴀꜱᴛ:\n\n{text}")
                ok += 1
            except Exception:
                pass
        bot.send_message(msg.chat.id, f"✅ ꜱᴇɴᴛ ᴛᴏ {ok}/{len(rows)} ᴜꜱᴇʀꜱ.")

    # ── Callback: add_ub ─────────────────────────────────────────
    @bot.callback_query_handler(func=lambda c: c.data == "add_ub")
    def add_ub_cb(call: telebot.types.CallbackQuery):
        _pending_add.add(call.from_user.id)
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🔐 ꜱᴇɴᴅ ʏᴏᴜʀ ᴩʏʀᴏɢʀᴀᴍ ꜱᴇꜱꜱɪᴏɴ ꜱᴛʀɪɴɢ ɴᴏᴡ.\n\n"
            "ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ? ᴜꜱᴇ /gen\n\n"
            "⚠️ /cancel ᴛᴏ ᴀʙᴏʀᴛ."
        )

    # ── Callback: nodes ──────────────────────────────────────────
    @bot.callback_query_handler(func=lambda c: c.data == "nodes")
    def nodes_cb(call: telebot.types.CallbackQuery):
        bot.answer_callback_query(call.id)
        nodes_cmd(call.message)
