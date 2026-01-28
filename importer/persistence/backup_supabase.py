import subprocess
from datetime import datetime
from pathlib import Path

BACKUP_DIR = Path("db_backups")
BACKUP_DIR.mkdir(exist_ok=True)

SUPABASE_URL = "postgresql://USER:PASSWORD@HOST:5432/postgres"

def backup_db():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"myquotes_{timestamp}.dump"

    cmd = [
        "pg_dump",
        "--dbname", SUPABASE_URL,
        "--format=custom",
        "--file", str(backup_file),
    ]

    subprocess.run(cmd, check=True)
    print(f"💾 DB backup created: {backup_file}")
