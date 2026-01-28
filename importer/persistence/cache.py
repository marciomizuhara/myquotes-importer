import json
from pathlib import Path

from importer.config import CACHE_FILE


def load_cache():
    """
    Carrega o cache de quotes já commitadas.
    Estrutura esperada:
        {
            "book_id|location_start": true,
            ...
        }
    """
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            print("⚠️ Cache corrompido — recriando...")
    return {}


def save_cache(cache: dict):
    """
    Persiste o cache no disco.
    """
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
