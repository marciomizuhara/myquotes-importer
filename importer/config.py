from pathlib import Path

# -------------------------------
# Base directories
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# -------------------------------
# Files
# -------------------------------
INPUT_FILE = INPUT_DIR / "My Clippings.txt"
EXCEL_FILE = OUTPUT_DIR / "quotes.xlsx"
CACHE_FILE = DATA_DIR / "quote_cache.json"

# -------------------------------
# Backup (Kindle)
# -------------------------------
BACKUP_DIR = Path(r"C:\Users\marci\Desktop\myclippings_backup")

# -------------------------------
# Import rules
# -------------------------------
CUTOFF_BOOK_ID = 63
