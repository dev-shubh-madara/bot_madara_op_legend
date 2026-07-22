import sqlite3
import os
from config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS userbots (
                user_id     INTEGER PRIMARY KEY,
                username    TEXT,
                first_name  TEXT,
                session     TEXT NOT NULL,
                added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active      INTEGER DEFAULT 1
            )
        """)
        conn.commit()


def add_userbot(user_id: int, session: str, username: str = "", first_name: str = ""):
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO userbots (user_id, username, first_name, session, active)
            VALUES (?, ?, ?, ?, 1)
        """, (user_id, username, first_name, session))
        conn.commit()


def remove_userbot(user_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM userbots WHERE user_id = ?", (user_id,))
        conn.commit()


def get_all_userbots():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT user_id, username, first_name, session, added_at FROM userbots WHERE active=1"
        ).fetchall()
    return rows


def get_userbot(user_id: int):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT user_id, username, first_name, session FROM userbots WHERE user_id=? AND active=1",
            (user_id,)
        ).fetchone()
    return row


def get_userbot_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM userbots WHERE active=1").fetchone()[0]
