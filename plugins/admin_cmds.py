"""
Admin commands executed via the user's connected userbot Pyrogram client.
Commands: /ban /unban /mute /unmute /promote /demote /purge /adminlist /botlist /owns /userinfo /id
"""
import asyncio
import telebot
from pyrogram.errors import ChatAdminRequired
from userbot_manager import get_client
from database import get_userbot
from config import POWERED_BY
from helpers import bq, esc


def _get_ub(uid: int):
    row = get_userbot(uid)
    if row is None:
        return None, None
    client = get_client(uid)
    return client, row


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _extract_target(msg: telebot.types.Message):
    if msg.reply_to_message:
        return msg.reply_to_message.from_user.id
    parts = msg.text.split()
    if len(parts) > 1:
        t = parts[1]
        if t.startswith("@"):
            return t
        try:
            return int(t)
        except ValueError:
            return t
    return None


def _no_ub(bot, chat_id):
    bot.send_message(chat_id, bq("⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /gen ꜰɪʀꜱᴛ."), parse_mode="HTML")


def register(bot: telebot.TeleBot):

    # ── /ban ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["ban"])
    def ban_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /ban @user | ʀᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ"), parse_mode="HTML")
            return
        parts = msg.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "ɴᴏ ʀᴇᴀꜱᴏɴ"
        try:
            _run(client.ban_chat_member(msg.chat.id, target))
            bot.send_message(msg.chat.id, bq(f"🔨 ʙᴀɴɴᴇᴅ {esc(str(target))}\n📝 ʀᴇᴀꜱᴏɴ: {esc(reason)}\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except ChatAdminRequired:
            bot.send_message(msg.chat.id, bq("❌ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ."), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ ᴇʀʀᴏʀ: {esc(str(e))}"), parse_mode="HTML")

    # ── /unban ────────────────────────────────────────────────────
    @bot.message_handler(commands=["unban"])
    def unban_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /unban @user"), parse_mode="HTML")
            return
        try:
            _run(client.unban_chat_member(msg.chat.id, target))
            bot.send_message(msg.chat.id, bq(f"✅ ᴜɴʙᴀɴɴᴇᴅ {esc(str(target))}\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /mute ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["mute"])
    def mute_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /mute @user"), parse_mode="HTML")
            return
        from pyrogram.types import ChatPermissions
        try:
            _run(client.restrict_chat_member(msg.chat.id, target, ChatPermissions()))
            bot.send_message(msg.chat.id, bq(f"🔇 ᴍᴜᴛᴇᴅ {esc(str(target))}\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /unmute ────────────────────────────────────────────────────
    @bot.message_handler(commands=["unmute"])
    def unmute_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /unmute @user"), parse_mode="HTML")
            return
        from pyrogram.types import ChatPermissions
        try:
            _run(client.restrict_chat_member(
                msg.chat.id, target,
                ChatPermissions(can_send_messages=True, can_send_media_messages=True,
                                can_send_other_messages=True, can_add_web_page_previews=True),
            ))
            bot.send_message(msg.chat.id, bq(f"🔊 ᴜɴᴍᴜᴛᴇᴅ {esc(str(target))}\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /promote ───────────────────────────────────────────────────
    @bot.message_handler(commands=["promote"])
    def promote_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /promote @user"), parse_mode="HTML")
            return
        try:
            _run(client.promote_chat_member(msg.chat.id, target,
                can_delete_messages=True, can_restrict_members=True,
                can_invite_users=True, can_pin_messages=True))
            bot.send_message(msg.chat.id, bq(f"⬆️ ᴩʀᴏᴍᴏᴛᴇᴅ {esc(str(target))}\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /demote ────────────────────────────────────────────────────
    @bot.message_handler(commands=["demote"])
    def demote_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, bq("ᴜꜱᴀɢᴇ: /demote @user"), parse_mode="HTML")
            return
        try:
            _run(client.promote_chat_member(msg.chat.id, target,
                can_delete_messages=False, can_restrict_members=False,
                can_invite_users=False, can_pin_messages=False))
            bot.send_message(msg.chat.id, bq(f"⬇️ ᴅᴇᴍᴏᴛᴇᴅ {esc(str(target))}\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /purge ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["purge"])
    def purge_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        if not msg.reply_to_message:
            bot.send_message(msg.chat.id, bq("ʀᴇᴩʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴛᴀʀᴛ ᴩᴜʀɢᴇ ꜰʀᴏᴍ."), parse_mode="HTML")
            return
        from_id = msg.reply_to_message.message_id
        to_id = msg.message_id
        chat_id = msg.chat.id

        async def _purge():
            ids = list(range(from_id, to_id + 1))
            for i in range(0, len(ids), 100):
                await client.delete_messages(chat_id, ids[i:i + 100])

        try:
            _run(_purge())
            count = to_id - from_id + 1
            bot.send_message(msg.chat.id, bq(f"🗑️ ᴩᴜʀɢᴇᴅ {count} ᴍꜱɢꜱ\n\n💎 {POWERED_BY}"), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /adminlist ─────────────────────────────────────────────────
    @bot.message_handler(commands=["adminlist"])
    def adminlist_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)

        async def _get():
            admins = []
            async for m in client.get_chat_members(msg.chat.id, filter="administrators"):
                name = m.user.first_name or "?"
                uname = f"@{m.user.username}" if m.user.username else str(m.user.id)
                admins.append(f"  👑 {esc(name)} ({esc(uname)})")
            return admins

        try:
            admins = _run(_get())
            text = f"🩸 ᴀᴅᴍɪɴ ʟɪꜱᴛ [{len(admins)}]\n━━━━━━━━━━━━━━━━━━\n"
            text += "\n".join(admins) or "ɴᴏɴᴇ"
            text += f"\n━━━━━━━━━━━━━━━━━━\n💎 {POWERED_BY}"
            bot.send_message(msg.chat.id, bq(text), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /botlist ───────────────────────────────────────────────────
    @bot.message_handler(commands=["botlist"])
    def botlist_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)

        async def _get():
            bots = []
            async for m in client.get_chat_members(msg.chat.id):
                if m.user.is_bot:
                    uname = f"@{m.user.username}" if m.user.username else str(m.user.id)
                    bots.append(f"  🤖 {esc(m.user.first_name)} ({esc(uname)})")
            return bots

        try:
            bots_list = _run(_get())
            text = f"🤖 ʙᴏᴛ ʟɪꜱᴛ [{len(bots_list)}]\n━━━━━━━━━━━━━━━━━━\n"
            text += "\n".join(bots_list) or "ɴᴏ ʙᴏᴛꜱ"
            text += f"\n━━━━━━━━━━━━━━━━━━\n💎 {POWERED_BY}"
            bot.send_message(msg.chat.id, bq(text), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /owns ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["owns"])
    def owns_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)

        async def _get():
            groups = []
            me = await client.get_me()
            async for dialog in client.get_dialogs():
                chat = dialog.chat
                if chat.type in ("group", "supergroup", "channel"):
                    try:
                        member = await client.get_chat_member(chat.id, me.id)
                        if member.status == "creator":
                            groups.append(f"  🌐 {esc(chat.title or str(chat.id))}")
                    except Exception:
                        pass
            return groups

        wait = bot.send_message(msg.chat.id, bq("⏳ ꜱᴄᴀɴɴɪɴɢ ᴅɪᴀʟᴏɢꜱ…"), parse_mode="HTML")
        try:
            groups = _run(_get())
            text = f"🪐 ɢʀᴏᴜᴩꜱ ᴏᴡɴᴇᴅ [{len(groups)}]\n━━━━━━━━━━━━━━━━━━\n"
            text += "\n".join(groups) or "ɴᴏɴᴇ"
            text += f"\n━━━━━━━━━━━━━━━━━━\n💎 {POWERED_BY}"
            bot.edit_message_text(bq(text), wait.chat.id, wait.message_id, parse_mode="HTML")
        except Exception as e:
            bot.edit_message_text(bq(f"❌ {esc(str(e))}"), wait.chat.id, wait.message_id, parse_mode="HTML")

    # ── /userinfo ──────────────────────────────────────────────────
    @bot.message_handler(commands=["userinfo", "info"])
    def userinfo_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            return _no_ub(bot, msg.chat.id)
        target = _extract_target(msg)

        async def _get():
            return await client.get_users(target) if target else await client.get_me()

        try:
            user = _run(_get())
            uname = f"@{user.username}" if user.username else "—"
            text = (
                "🌐 ᴜꜱᴇʀ ɪɴꜰᴏ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 ɴᴀᴍᴇ     : {esc(user.first_name)} {esc(user.last_name or '')}\n"
                f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ : {esc(uname)}\n"
                f"🔗 ɪᴅ       : {user.id}\n"
                f"🤖 ʙᴏᴛ      : {'ʏᴇꜱ' if user.is_bot else 'ɴᴏ'}\n"
                f"✅ ᴠᴇʀɪꜰɪᴇᴅ  : {'ʏᴇꜱ' if user.is_verified else 'ɴᴏ'}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"💎 {POWERED_BY}"
            )
            bot.send_message(msg.chat.id, bq(text), parse_mode="HTML")
        except Exception as e:
            bot.send_message(msg.chat.id, bq(f"❌ {esc(str(e))}"), parse_mode="HTML")

    # ── /id ────────────────────────────────────────────────────────
    @bot.message_handler(commands=["id"])
    def id_cmd(msg: telebot.types.Message):
        bot.send_message(
            msg.chat.id,
            bq(
                "🆔 ɪᴅ ɪɴꜰᴏ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 ʏᴏᴜʀ ɪᴅ : {msg.from_user.id}\n"
                f"💬 ᴄʜᴀᴛ ɪᴅ : {msg.chat.id}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"💎 {POWERED_BY}"
            ),
            parse_mode="HTML",
        )
