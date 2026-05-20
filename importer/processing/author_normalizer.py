# importer/processing/author_normalizer.py

from __future__ import annotations


AUTHOR_ALIASES = {
    # =========================
    # Fyodor Dostoevsky
    # =========================
    "fyodor dostoyevsky": "Fyodor Dostoevsky",
    "fyodor dostoevsky": "Fyodor Dostoevsky",
    "fiódor dostoiévski": "Fyodor Dostoevsky",
    "fiodor dostoievski": "Fyodor Dostoevsky",
    "fiodor dostoiévski": "Fyodor Dostoevsky",
    "dostoevsky": "Fyodor Dostoevsky",
    "dostoyevsky": "Fyodor Dostoevsky",

    # =========================
    # Leo Tolstoy
    # =========================
    "leo tolstoy": "Leo Tolstoy",
    "lev tolstoy": "Leo Tolstoy",
    "lev tolstoi": "Leo Tolstoy",
    "leo tolstoi": "Leo Tolstoy",
    "liév tolstói": "Leo Tolstoy",
    "lev nikolayevich tolstoy": "Leo Tolstoy",
    "tolstoy": "Leo Tolstoy",

    # =========================
    # Anton Chekhov
    # =========================
    "anton chekhov": "Anton Chekhov",
    "anton chekov": "Anton Chekhov",
    "antón tchékhov": "Anton Chekhov",
    "anton tchekhov": "Anton Chekhov",
    "chekhov": "Anton Chekhov",

    # =========================
    # Ivan Turgenev
    # =========================
    "ivan turgenev": "Ivan Turgenev",
    "ivan turgueniev": "Ivan Turgenev",
    "ivan turgeniev": "Ivan Turgenev",
    "iván turguénev": "Ivan Turgenev",
    "turgenev": "Ivan Turgenev",

    # =========================
    # Nikolai Gogol
    # =========================
    "nikolai gogol": "Nikolai Gogol",
    "nikolay gogol": "Nikolai Gogol",
    "nicolai gogol": "Nikolai Gogol",
    "nikolai gógol": "Nikolai Gogol",
    "gogol": "Nikolai Gogol",

    # =========================
    # Alexander Pushkin
    # =========================
    "alexander pushkin": "Alexander Pushkin",
    "alexandr pushkin": "Alexander Pushkin",
    "alexandre pushkin": "Alexander Pushkin",
    "alexander púshkin": "Alexander Pushkin",
    "pushkin": "Alexander Pushkin",

    # =========================
    # Vladimir Nabokov
    # =========================
    "vladimir nabokov": "Vladimir Nabokov",
    "vladímir nabókov": "Vladimir Nabokov",
    "nabokov": "Vladimir Nabokov",

    # =========================
    # Mikhail Bulgakov
    # =========================
    "mikhail bulgakov": "Mikhail Bulgakov",
    "mikhail bulhakov": "Mikhail Bulgakov",
    "mikhail bulgákov": "Mikhail Bulgakov",
    "bulgakov": "Mikhail Bulgakov",

    # =========================
    # Aleksandr Solzhenitsyn
    # =========================
    "aleksandr solzhenitsyn": "Aleksandr Solzhenitsyn",
    "alexander solzhenitsyn": "Aleksandr Solzhenitsyn",
    "alexandr solzhenitsyn": "Aleksandr Solzhenitsyn",
    "solzhenitsyn": "Aleksandr Solzhenitsyn",

    # =========================
    # Boris Pasternak
    # =========================
    "boris pasternak": "Boris Pasternak",
    "borís pasternak": "Boris Pasternak",
    "pasternak": "Boris Pasternak",

    # =========================
    # Ivan Goncharov
    # =========================
    "ivan goncharov": "Ivan Goncharov",
    "ivan goncharóv": "Ivan Goncharov",
    "goncharov": "Ivan Goncharov",

    # =========================
    # Maxim Gorky
    # =========================
    "maxim gorky": "Maxim Gorky",
    "maksim gorky": "Maxim Gorky",
    "máximo górki": "Maxim Gorky",
    "gorky": "Maxim Gorky",

    # =========================
    # Isaac Babel
    # =========================
    "isaac babel": "Isaac Babel",
    "isaak babel": "Isaac Babel",
    "babel": "Isaac Babel",
}


def normalize_author(author: str) -> str:
    raw = (author or "").strip()

    if not raw:
        return "Unknown"

    key = raw.lower()

    return AUTHOR_ALIASES.get(key, raw)