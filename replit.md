# MADARA_X_AURA — Userbot Manager Bot

## Overview
A Telegram userbot manager bot. Users connect their Telegram accounts via Pyrogram session strings, and the bot executes commands on their behalf. The owner has full control over all connected accounts.

**Branding:** MADARA_X_AURA | POWERED BY MADARA | GMS X USER

## Stack
- Python 3.11
- `pyTelegramBotAPI` — main bot framework
- `pyrogram` + `TgCrypto` — userbot (MTProto) client sessions
- `psutil` — CPU/RAM stats
- `sqlite3` — local database for sessions
- `aiohttp` — async HTTP

## How to Run
```
python main.py
```

## Required Secrets / Environment Variables
| Key | Type | Description |
|-----|------|-------------|
| `BOT_TOKEN` | Secret | BotFather token for the main bot |
| `API_ID` | Secret | Telegram API ID from my.telegram.org |
| `API_HASH` | Secret | Telegram API hash from my.telegram.org |
| `OWNER_ID` | Env var | Your Telegram numeric user ID |

## Project Structure
```
main.py              — Entry point, bot startup
config.py            — All config/branding constants
database.py          — SQLite helpers (store userbot sessions)
userbot_manager.py   — Pyrogram client lifecycle (start/stop/get)
plugins/
  start.py           — /start command with live stats
  help.py            — /help with 16-page paginated menu
  node_mgmt.py       — /add /gen /remove /nodes /ping /stats /broadcast
  admin_cmds.py      — /ban /unban /mute /unmute /promote /demote /purge
                       /adminlist /botlist /owns /userinfo /id
  aesthetic.py       — /hug /slap /kiss /dice /fvn /spotify
  owner_cmds.py      — /eval /sh /restart (owner only)
data/                — SQLite DB and session files (auto-created)
```

## User Preferences
- Branding: MADARA_X_AURA, POWERED BY MADARA, GMS X USER
- Fancy Unicode small-caps style text for all UI (matching original bot aesthetic)
- Owner has master control over all connected accounts
