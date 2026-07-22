"""
Admin commands executed via the user's connected userbot Pyrogram client.
Commands: /ban /unban /mute /unmute /promote /demote /purge /adminlist /botlist /owns /pin /unpin
"""
import asyncio
import telebot
from pyrogram.errors import ChatAdminRequired, UserAdminInvalid, FloodWait
from userbot_manager import get_client
from database import get_userbot
from config import POWERED_BY


def _get_ub(uid: int):
    """Return (client, row) or (None, None) if no userbot."""
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
    """Return target username/id from reply or command arg."""
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


def register(bot: telebot.TeleBot):

    def ub_required(fn):
        """Decorator: ensures user has an active userbot."""
        def wrapper(msg: telebot.types.Message):
            client, _ = _get_ub(msg.from_user.id)
            if client is None:
                bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
                return
            fn(msg, client)
        return wrapper

    # ── /ban ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["ban"])
    def ban_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /ban @user | ʀᴇᴘʟʏ ᴛᴏ ᴜꜱᴇʀ")
            return

        parts = msg.text.split(None, 2)
        reason = parts[2] if len(parts) > 2 else "ɴᴏ ʀᴇᴀꜱᴏɴ"

        chat_id = msg.chat.id

        async def _ban():
            await client.ban_chat_member(chat_id, target)

        try:
            _run(_ban())
            bot.send_message(msg.chat.id, f"🔨 ʙᴀɴɴᴇᴅ {target}\n📝 ʀᴇᴀꜱᴏɴ: {reason}\n\n💎 {POWERED_BY}")
        except ChatAdminRequired:
            bot.send_message(msg.chat.id, "❌ ᴜꜱᴇʀʙᴏᴛ ɪꜱ ɴᴏᴛ ᴀᴅᴍɪɴ ʜᴇʀᴇ.")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ ᴇʀʀᴏʀ: {e}")

    # ── /unban ────────────────────────────────────────────────────
    @bot.message_handler(commands=["unban"])
    def unban_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /unban @user")
            return

        async def _unban():
            await client.unban_chat_member(msg.chat.id, target)

        try:
            _run(_unban())
            bot.send_message(msg.chat.id, f"✅ ᴜɴʙᴀɴɴᴇᴅ {target}\n\n💎 {POWERED_BY}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /mute ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["mute"])
    def mute_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /mute @user")
            return

        from pyrogram.types import ChatPermissions

        async def _mute():
            await client.restrict_chat_member(msg.chat.id, target, ChatPermissions())

        try:
            _run(_mute())
            bot.send_message(msg.chat.id, f"🔇 ᴍᴜᴛᴇᴅ {target}\n\n💎 {POWERED_BY}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /unmute ────────────────────────────────────────────────────
    @bot.message_handler(commands=["unmute"])
    def unmute_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /unmute @user")
            return

        from pyrogram.types import ChatPermissions

        async def _unmute():
            await client.restrict_chat_member(
                msg.chat.id, target,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                ),
            )

        try:
            _run(_unmute())
            bot.send_message(msg.chat.id, f"🔊 ᴜɴᴍᴜᴛᴇᴅ {target}\n\n💎 {POWERED_BY}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /promote ───────────────────────────────────────────────────
    @bot.message_handler(commands=["promote"])
    def promote_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /promote @user")
            return

        async def _promote():
            await client.promote_chat_member(
                msg.chat.id, target,
                can_delete_messages=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
            )

        try:
            _run(_promote())
            bot.send_message(msg.chat.id, f"⬆️ ᴩʀᴏᴍᴏᴛᴇᴅ {target}\n\n💎 {POWERED_BY}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /demote ────────────────────────────────────────────────────
    @bot.message_handler(commands=["demote"])
    def demote_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        target = _extract_target(msg)
        if not target:
            bot.send_message(msg.chat.id, "ᴜꜱᴀɢᴇ: /demote @user")
            return

        async def _demote():
            await client.promote_chat_member(
                msg.chat.id, target,
                can_delete_messages=False,
                can_restrict_members=False,
                can_invite_users=False,
                can_pin_messages=False,
            )

        try:
            _run(_demote())
            bot.send_message(msg.chat.id, f"⬇️ ᴅᴇᴍᴏᴛᴇᴅ {target}\n\n💎 {POWERED_BY}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /purge ─────────────────────────────────────────────────────
    @bot.message_handler(commands=["purge"])
    def purge_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return
        if not msg.reply_to_message:
            bot.send_message(msg.chat.id, "ʀᴇᴩʟʏ ᴛᴏ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴛᴀʀᴛ ᴩᴜʀɢᴇ ꜰʀᴏᴍ.")
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
            sent = bot.send_message(msg.chat.id, f"🗑️ ᴩᴜʀɢᴇᴅ {count} ᴍꜱɢꜱ\n\n💎 {POWERED_BY}")
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /adminlist ─────────────────────────────────────────────────
    @bot.message_handler(commands=["adminlist"])
    def adminlist_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return

        async def _get_admins():
            admins = []
            async for m in client.get_chat_members(msg.chat.id, filter="administrators"):
                name = m.user.first_name or "?"
                uname = f"@{m.user.username}" if m.user.username else str(m.user.id)
                admins.append(f"  👑 {name} ({uname})")
            return admins

        try:
            admins = _run(_get_admins())
            text = f"🩸 ᴀᴅᴍɪɴ ʟɪꜱᴛ [{len(admins)}]\n━━━━━━━━━━━━━━━━━━\n"
            text += "\n".join(admins) or "ɴᴏɴᴇ"
            text += f"\n━━━━━━━━━━━━━━━━━━\n💎 {POWERED_BY}"
            bot.send_message(msg.chat.id, text)
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /botlist ───────────────────────────────────────────────────
    @bot.message_handler(commands=["botlist"])
    def botlist_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return

        async def _get_bots():
            bots = []
            async for m in client.get_chat_members(msg.chat.id):
                if m.user.is_bot:
                    uname = f"@{m.user.username}" if m.user.username else str(m.user.id)
                    bots.append(f"  🤖 {m.user.first_name} ({uname})")
            return bots

        try:
            bots = _run(_get_bots())
            text = f"🤖 ʙᴏᴛ ʟɪꜱᴛ [{len(bots)}]\n━━━━━━━━━━━━━━━━━━\n"
            text += "\n".join(bots) or "ɴᴏ ʙᴏᴛꜱ"
            text += f"\n━━━━━━━━━━━━━━━━━━\n💎 {POWERED_BY}"
            bot.send_message(msg.chat.id, text)
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /owns ──────────────────────────────────────────────────────
    @bot.message_handler(commands=["owns"])
    def owns_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return

        async def _get_owns():
            groups = []
            async for dialog in client.get_dialogs():
                chat = dialog.chat
                if chat.type in ("group", "supergroup", "channel"):
                    me = await client.get_me()
                    try:
                        member = await client.get_chat_member(chat.id, me.id)
                        if member.status == "creator":
                            title = chat.title or str(chat.id)
                            groups.append(f"  🌐 {title}")
                    except Exception:
                        pass
            return groups

        wait = bot.send_message(msg.chat.id, "⏳ ꜱᴄᴀɴɴɪɴɢ ᴅɪᴀʟᴏɢꜱ…")
        try:
            groups = _run(_get_owns())
            text = f"🪐 ɢʀᴏᴜᴩꜱ ᴏᴡɴᴇᴅ [{len(groups)}]\n━━━━━━━━━━━━━━━━━━\n"
            text += "\n".join(groups) or "ɴᴏɴᴇ"
            text += f"\n━━━━━━━━━━━━━━━━━━\n💎 {POWERED_BY}"
            bot.edit_message_text(text, wait.chat.id, wait.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ {e}", wait.chat.id, wait.message_id)

    # ── /userinfo ──────────────────────────────────────────────────
    @bot.message_handler(commands=["userinfo", "info"])
    def userinfo_cmd(msg: telebot.types.Message):
        client, _ = _get_ub(msg.from_user.id)
        if not client:
            bot.send_message(msg.chat.id, "⚠️ ɴᴏ ᴜꜱᴇʀʙᴏᴛ. ᴜꜱᴇ /add ꜰɪʀꜱᴛ.")
            return

        target = _extract_target(msg)

        async def _get_info():
            if target:
                user = await client.get_users(target)
            else:
                user = await client.get_me()
            return user

        try:
            user = _run(_get_info())
            uname = f"@{user.username}" if user.username else "—"
            text = (
                f"🌐 ᴜꜱᴇʀ ɪɴꜰᴏ\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"👤 ɴᴀᴍᴇ  : {user.first_name} {user.last_name or ''}\n"
                f"🆔 ᴜꜱᴇʀɴᴀᴍᴇ: {uname}\n"
                f"🔗 ɪᴅ   : {user.id}\n"
                f"🤖 ʙᴏᴛ   : {'ʏᴇꜱ' if user.is_bot else 'ɴᴏ'}\n"
                f"✅ ᴠᴇʀɪꜰɪᴇᴅ: {'ʏᴇꜱ' if user.is_verified else 'ɴᴏ'}\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"💎 {POWERED_BY}"
            )
            bot.send_message(msg.chat.id, text)
        except Exception as e:
            bot.send_message(msg.chat.id, f"❌ {e}")

    # ── /id ────────────────────────────────────────────────────────
    @bot.message_handler(commands=["id"])
    def id_cmd(msg: telebot.types.Message):
        chat_id = msg.chat.id
        user_id = msg.from_user.id
        bot.send_message(
            msg.chat.id,
            f"🆔 ɪᴅ ɪɴꜰᴏ\n"
            "━━━━━━━━━━━━━━━━━━\n"
            f"👤 ʏᴏᴜʀ ɪᴅ : {user_id}\n"
            f"💬 ᴄʜᴀᴛ ɪᴅ : {chat_id}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💎 {POWERED_BY}"
        )
