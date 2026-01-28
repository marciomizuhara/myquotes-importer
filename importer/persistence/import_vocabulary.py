# importer/persistence/import_vocabulary_db.py

from __future__ import annotations

from importer.persistence.vocabulary_cache import VocabularyCache

from app import app, db
from models import Book, Vocabulary


def import_vocabulary(vocabularies_detected: list[dict]):
    """
    Persiste Vocabulary no DB e atualiza o VocabularyCache
    SOMENTE após commit bem-sucedido.
    """
    if not vocabularies_detected:
        print("📘 Vocabulary | nothing to import.")
        return

    vocab_cache = VocabularyCache()

    inserted = 0
    skipped = 0

    with app.app_context():
        # cache de livros por título (case-insensitive)
        existing_books = {
            b.title.lower(): b
            for b in Book.query.all()
        }

        for v in vocabularies_detected:
            book_title = (v.get("book") or "").strip()
            if not book_title:
                skipped += 1
                continue

            loc_start = v.get("location_start")
            if loc_start is None:
                skipped += 1
                continue

            # ✅ Cache check (idempotência)
            if vocab_cache.exists(book_title, int(loc_start)):
                skipped += 1
                continue

            book = existing_books.get(book_title.lower())
            if not book:
                # tenta encontrar no DB por ilike (fallback)
                book = Book.query.filter(Book.title.ilike(book_title)).first()
                if book:
                    existing_books[book_title.lower()] = book

            if not book:
                print(f"⚠️ Vocabulary skipped (book not found): {book_title}")
                skipped += 1
                continue

            word = (v.get("word") or "").strip()
            if not word:
                skipped += 1
                continue

            # ✅ evita duplicata no DB também (mesma chave lógica)
            existing_vocab = Vocabulary.query.filter(
                Vocabulary.book_id == book.id,
                Vocabulary.location_start == int(loc_start)
            ).first()
            if existing_vocab:
                vocab_cache.mark(book_title, int(loc_start))
                skipped += 1
                continue

            vocab = Vocabulary(
                book_id=book.id,
                location_start=int(loc_start),
                location_end=int(v.get("location_end") or loc_start),
                text=(v.get("text") or "").strip(),
                word=word,
                notes=None,
                page=v.get("page"),
                is_active=1,
            )

            db.session.add(vocab)
            inserted += 1

            print(
                f"📘 Vocabulary queued | "
                f"Book: {book.title} | "
                f"Word: {word} | "
                f"Location: {vocab.location_start}-{vocab.location_end}"
            )

        db.session.commit()

        # ✅ só marca cache depois do commit
        for v in vocabularies_detected:
            book_title = (v.get("book") or "").strip()
            loc_start = v.get("location_start")
            if book_title and loc_start is not None:
                vocab_cache.mark(book_title, int(loc_start))

        # ✅ AGORA SIM persiste o cache
        vocab_cache.save()

    print("✅ Vocabulary commit completed successfully.")
    print(f"🟢 Inserted: {inserted}")
    print(f"⚪ Skipped: {skipped}")
