import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env if exists
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Supabase Credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://dtrqnzbbcolnkcufjbhh.supabase.co")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_DSKxUg8AvzTKABaRxjlPFw_-dGOwClE")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY", "")
SUPABASE_PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF", "dtrqnzbbcolnkcufjbhh")

# Direct PostgreSQL Pooler Connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.dtrqnzbbcolnkcufjbhh:1033693601JK@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
)

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
