"""
Owner-only mass commands: /massjoin /mreport
"""
import asyncio
import time
import threading
import telebot
from pyrogram import raw
from config import OWNER_ID, BOT_NAME, POWERED_BY
from database import get_all_userbots
from userbot_manager import get_all_clients
from helpers import bq, esc

# Pending mreport sessions: owner_uid -> {target, count, chat_id, msg_id}
_report_sessions: dict[int, dict] = {}

REPORT_REASONS = {
    "spam":       ("🗑️ Spam", raw.types.InputReportReasonSpam()),
    "fake":       ("🎭 Fake Account", raw.types.InputReportReasonFake()),
    "violence":   ("⚔️ Violence", raw.types.InputReportReasonViolence()),
    "porn":       ("🔞 Adult Content", raw.types.InputReportReasonPornography()),
    "drugs":      ("💊 Illegal Drugs", raw.types.InputReportReasonIllegalDrugs()),
    "copyright":  ("©️ Copyright", raw.types.InputReportReasonCopyright()),
    "personal":   ("🪪 Personal Details", raw.types.InputReportReasonPersonalDetails()),
    "other":      ("❓ Other", raw.types.InputReportReasonOther()),
}


def _is_owner(uid: int) -> bool:
    return uid == OWNER_ID


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def register(bot: telebot.TeleBot):

    # ── /massjoin ─────────────────────────────────────────────────
    @bot.message_handler(commands=["massjoin"])
    def massjoin_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return

        parts = msg.text.split(None, 1)
        if len(parts) < 2:
            bot.send_message(
                msg.chat.id,
                bq(
                    "ᴜꜱᴀɢᴇ: /massjoin ‹group_link_or_username›\n\n"
                    "ᴇxᴀᴍᴩʟᴇ:\n"
                    "  /massjoin @mygroup\n"
                    "  /massjoin https://t.me/mygroup"
                ),
                parse_mode="HTML",
            )
            return

        target = parts[1].strip()
        clients = get_all_clients()

        if not clients:
            bot.send_message(msg.chat.id, bq("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴜꜱᴇʀʙᴏᴛꜱ ᴄᴏɴɴᴇᴄᴛᴇᴅ."), parse_mode="HTML")
            return

        status_msg = bot.send_message(
            msg.chat.id,
            bq(
                f"🚀 ᴍᴀꜱꜱ ᴊᴏɪɴ ꜱᴛᴀʀᴛɪɴɢ…\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 ᴛᴀʀɢᴇᴛ: {esc(target)}\n"
                f"🤖 ᴀᴄᴄᴏᴜɴᴛꜱ: {len(clients)}\n"
                f"⏳ ᴩʟᴇᴀꜱᴇ ᴡᴀɪᴛ…"
            ),
            parse_mode="HTML",
        )

        def _do_massjoin():
            ok, fail = 0, 0
            details = []

            async def _join_one(uid, client):
                nonlocal ok, fail
                try:
                    await client.join_chat(target)
                    ok += 1
                    details.append(f"  ✅ ᴜɪᴅ {uid}")
                except Exception as e:
                    fail += 1
                    details.append(f"  ❌ ᴜɪᴅ {uid}: {esc(str(e)[:40])}")
                await asyncio.sleep(1.5)  # stagger to avoid flood

            async def _run_all():
                for uid, client in list(clients.items()):
                    await _join_one(uid, client)

            loop = asyncio.new_event_loop()
            loop.run_until_complete(_run_all())
            loop.close()

            summary = "\n".join(details[:20])  # cap display at 20
            result_text = bq(
                f"✅ ᴍᴀꜱꜱ ᴊᴏɪɴ ᴄᴏᴍᴩʟᴇᴛᴇ!\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 ᴛᴀʀɢᴇᴛ: {esc(target)}\n"
                f"✅ ᴊᴏɪɴᴇᴅ: {ok}\n"
                f"❌ ꜰᴀɪʟᴇᴅ: {fail}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{summary}\n\n"
                f"💎 {POWERED_BY}"
            )
            try:
                bot.edit_message_text(result_text, status_msg.chat.id, status_msg.message_id, parse_mode="HTML")
            except Exception:
                bot.send_message(msg.chat.id, result_text, parse_mode="HTML")

        threading.Thread(target=_do_massjoin, daemon=True).start()

    # ── /mreport ──────────────────────────────────────────────────
    @bot.message_handler(commands=["mreport"])
    def mreport_cmd(msg: telebot.types.Message):
        if not _is_owner(msg.from_user.id):
            bot.send_message(msg.chat.id, bq("🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ."), parse_mode="HTML")
            return

        parts = msg.text.split()
        if len(parts) < 3:
            bot.send_message(
                msg.chat.id,
                bq(
                    "ᴜꜱᴀɢᴇ: /mreport ‹count› ‹@username›\n\n"
                    "ᴇxᴀᴍᴩʟᴇ:\n"
                    "  /mreport 10 @scammer\n\n"
                    "ꜱᴩᴇᴇᴅ: 1 ʀᴇᴩᴏʀᴛ / 2ꜱ ᴩᴇʀ ᴀᴄᴄᴏᴜɴᴛ\n"
                    "ᴄᴀᴛᴇɢᴏʀʏ ᴡɪʟʟ ʙᴇ ᴀꜱᴋᴇᴅ ɴᴇxᴛ."
                ),
                parse_mode="HTML",
            )
            return

        try:
            count = int(parts[1])
        except ValueError:
            bot.send_message(msg.chat.id, bq("❌ ‹count› ᴍᴜꜱᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ."), parse_mode="HTML")
            return

        target = parts[2].lstrip("@")
        clients = get_all_clients()

        if not clients:
            bot.send_message(msg.chat.id, bq("⚠️ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴜꜱᴇʀʙᴏᴛꜱ ᴄᴏɴɴᴇᴄᴛᴇᴅ."), parse_mode="HTML")
            return

        # Store pending session
        _report_sessions[msg.from_user.id] = {
            "target": target,
            "count": count,
            "chat_id": msg.chat.id,
        }

        # Build category keyboard
        kb = telebot.types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            telebot.types.InlineKeyboardButton(label, callback_data=f"mreport_{key}")
            for key, (label, _) in REPORT_REASONS.items()
        ]
        kb.add(*buttons)
        kb.row(telebot.types.InlineKeyboardButton("❌ ᴄᴀɴᴄᴇʟ", callback_data="mreport_cancel"))

        bot.send_message(
            msg.chat.id,
            bq(
                f"🎯 ʀᴇᴩᴏʀᴛ ᴛᴀʀɢᴇᴛ: @{esc(target)}\n"
                f"📊 ᴄᴏᴜɴᴛ: {count} ʀᴇᴩᴏʀᴛꜱ ᴩᴇʀ ᴀᴄᴄᴏᴜɴᴛ\n"
                f"🤖 ᴀᴄᴄᴏᴜɴᴛꜱ: {len(clients)}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                "ꜱᴇʟᴇᴄᴛ ʀᴇᴩᴏʀᴛ ᴄᴀᴛᴇɢᴏʀʏ:"
            ),
            parse_mode="HTML",
            reply_markup=kb,
        )

    # ── Callback: category selected ───────────────────────────────
    @bot.callback_query_handler(func=lambda c: c.data.startswith("mreport_"))
    def mreport_category_cb(call: telebot.types.CallbackQuery):
        uid = call.from_user.id
        if not _is_owner(uid):
            bot.answer_callback_query(call.id, "🚫 ᴏᴡɴᴇʀ ᴏɴʟʏ.")
            return

        key = call.data[len("mreport_"):]
        bot.answer_callback_query(call.id)

        if key == "cancel":
            _report_sessions.pop(uid, None)
            bot.edit_message_text(bq("❌ ʀᴇᴩᴏʀᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ."), call.message.chat.id, call.message.message_id, parse_mode="HTML")
            return

        session = _report_sessions.pop(uid, None)
        if not session:
            bot.edit_message_text(bq("⚠️ ꜱᴇꜱꜱɪᴏɴ ᴇxᴩɪʀᴇᴅ. ᴜꜱᴇ /mreport ᴀɢᴀɪɴ."), call.message.chat.id, call.message.message_id, parse_mode="HTML")
            return

        label, reason_type = REPORT_REASONS[key]
        target = session["target"]
        count = session["count"]
        chat_id = session["chat_id"]
        clients = get_all_clients()

        status_msg = bot.edit_message_text(
            bq(
                f"⚡️ ʀᴇᴩᴏʀᴛɪɴɢ ꜱᴛᴀʀᴛᴇᴅ!\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 ᴛᴀʀɢᴇᴛ: @{esc(target)}\n"
                f"📁 ᴄᴀᴛᴇɢᴏʀʏ: {label}\n"
                f"📊 ᴄᴏᴜɴᴛ: {count} × {len(clients)} ᴀᴄᴄᴏᴜɴᴛꜱ\n"
                f"⏱️ ꜱᴩᴇᴇᴅ: 1 ʀᴇᴩᴏʀᴛ / 2ꜱ ᴩᴇʀ ᴀᴄᴄᴏᴜɴᴛ\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                "⏳ ɪɴ ᴩʀᴏɢʀᴇꜱꜱ…"
            ),
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
        )

        def _do_reports():
            total_ok = 0
            total_fail = 0

            async def _report_account(uid_acc, client, reason_obj):
                nonlocal total_ok, total_fail
                acc_ok = 0
                try:
                    peer = await client.resolve_peer(target)
                    for _ in range(count):
                        try:
                            await client.invoke(
                                raw.functions.account.ReportPeer(
                                    peer=peer,
                                    reason=reason_obj,
                                    message="",
                                )
                            )
                            acc_ok += 1
                            total_ok += 1
                        except Exception:
                            total_fail += 1
                        await asyncio.sleep(2)  # 1 report per 2 seconds
                except Exception:
                    total_fail += count

            async def _run_all():
                tasks = [
                    _report_account(uid_acc, client, reason_type)
                    for uid_acc, client in list(clients.items())
                ]
                await asyncio.gather(*tasks)

            loop = asyncio.new_event_loop()
            loop.run_until_complete(_run_all())
            loop.close()

            result = bq(
                f"✅ ʀᴇᴩᴏʀᴛɪɴɢ ᴄᴏᴍᴩʟᴇᴛᴇ!\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 ᴛᴀʀɢᴇᴛ: @{esc(target)}\n"
                f"📁 ᴄᴀᴛᴇɢᴏʀʏ: {label}\n"
                f"✅ ꜱᴇɴᴛ: {total_ok}\n"
                f"❌ ꜰᴀɪʟᴇᴅ: {total_fail}\n"
                f"🤖 ᴀᴄᴄᴏᴜɴᴛꜱ ᴜꜱᴇᴅ: {len(clients)}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"💎 {POWERED_BY}"
            )
            try:
                bot.edit_message_text(result, status_msg.chat.id, status_msg.message_id, parse_mode="HTML")
            except Exception:
                bot.send_message(chat_id, result, parse_mode="HTML")

        threading.Thread(target=_do_reports, daemon=True).start()
