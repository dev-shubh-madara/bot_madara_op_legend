"""
Manages live Pyrogram userbot client instances.
Each connected user's session runs as a separate Pyrogram client.
"""
import asyncio
import logging
from pyrogram import Client
from config import API_ID, API_HASH, SESSION_DIR
import os

logger = logging.getLogger(__name__)
os.makedirs(SESSION_DIR, exist_ok=True)

# uid -> pyrogram Client
_clients: dict[int, Client] = {}


async def start_client(user_id: int, session_string: str) -> Client | None:
    """Start a Pyrogram client from a session string."""
    try:
        client = Client(
            name=str(user_id),
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            no_updates=True,
        )
        await client.start()
        _clients[user_id] = client
        logger.info(f"[UB] Started client for user {user_id}")
        return client
    except Exception as e:
        logger.error(f"[UB] Failed to start client for {user_id}: {e}")
        return None


async def stop_client(user_id: int):
    client = _clients.pop(user_id, None)
    if client:
        try:
            await client.stop()
        except Exception:
            pass


def get_client(user_id: int) -> Client | None:
    return _clients.get(user_id)


def get_all_clients() -> dict[int, Client]:
    return _clients


def active_count() -> int:
    return len(_clients)


async def load_all_from_db():
    """Load all userbots from DB on startup."""
    from database import get_all_userbots
    rows = get_all_userbots()
    tasks = [start_client(row[0], row[3]) for row in rows]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    ok = sum(1 for r in results if isinstance(r, Client))
    logger.info(f"[UB] Loaded {ok}/{len(rows)} userbots from database")
    return ok
