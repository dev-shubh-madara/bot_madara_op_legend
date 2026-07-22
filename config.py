import os

# ─── Bot Identity ─────────────────────────────────────────────
BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
OWNER_ID    = int(os.environ.get("OWNER_ID", "0"))
API_ID      = int(os.environ.get("API_ID", "0"))
API_HASH    = os.environ.get("API_HASH", "")

# ─── Branding ─────────────────────────────────────────────────
BOT_NAME    = "MADARA_X_AURA"
POWERED_BY  = "POWERED BY MADARA"
TAG_LINE    = "GMS X USER"
OWNER_NAME  = "Mᴀᴅᴀʀᴀ"

# ─── Misc ─────────────────────────────────────────────────────
DB_PATH     = "data/userbots.db"
SESSION_DIR = "data/sessions"
