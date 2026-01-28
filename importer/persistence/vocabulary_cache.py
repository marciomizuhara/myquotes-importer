from pathlib import Path
import json

CACHE_FILE = Path("vocabulary_cache.json")


class VocabularyCache:
    def __init__(self, path: Path = CACHE_FILE):
        self.path = path
        self._data = self._load()
        self._dirty = False

    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def save(self):
        if not self._dirty and self.path.exists():
            return

        self.path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self._dirty = False

    @staticmethod
    def make_key(book: str, location_start: int) -> str:
        return f"{book.lower()}|{location_start}"

    def exists(self, book: str, location_start: int) -> bool:
        return self.make_key(book, location_start) in self._data

    def mark(self, book: str, location_start: int):
        key = self.make_key(book, location_start)
        if key not in self._data:
            self._data[key] = True
            self._dirty = True

