from __future__ import annotations

import requests


class TranslationService:
    _endpoint = "https://translate.googleapis.com/translate_a/single"

    @staticmethod
    def translate_to_pt_br(text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""

        params = {
            "client": "gtx",
            "sl": "en",
            "tl": "pt",
            "dt": "t",
            "q": t,
        }

        res = requests.get(TranslationService._endpoint, params=params, timeout=15)
        res.raise_for_status()

        data = res.json()

        if not isinstance(data, list) or not data or not isinstance(data[0], list):
            raise ValueError("Unexpected translation response")

        translated_parts = []
        for part in data[0]:
            if isinstance(part, list) and part and isinstance(part[0], str):
                translated_parts.append(part[0])

        translated = "".join(translated_parts).strip()
        if not translated:
            raise ValueError("Empty translation")

        return translated
