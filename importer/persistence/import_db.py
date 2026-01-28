import pandas as pd

from app import app, db
from models import Book, Quote
from importer.config import EXCEL_FILE
from importer.persistence.cache import load_cache, save_cache


DEFAULT_QUOTE_TYPE = 2  # 🟡 Amarelo (tipo padrão do domínio)


def import_from_excel(ratings_detected):
    with app.app_context():
        df = pd.read_excel(EXCEL_FILE)
        cache = load_cache()
        quotes_committed = set()

        inserted = 0
        updated = 0
        skipped = 0

        CUTOFF_BOOK_ID = 63

        existing_books = {
            b.title.lower(): b
            for b in Book.query.all()
        }

        # ⭐ Apply ratings
        for item in ratings_detected:
            book = existing_books.get(item['book'].lower())
            if not book or book.id < CUTOFF_BOOK_ID:
                continue

            rating = item['rating']

            if book.rating is None:
                book.rating = rating
                print(f"🟢 Rating set | {book.title} = {rating}")
            elif abs(book.rating - rating) >= 0.1:
                old = book.rating
                book.rating = rating
                print(f"🟡 Rating updated | {book.title}: {old} → {rating}")
            else:
                print(f"⚪ Rating ignored | {book.title}")

        for _, row in df.iterrows():
            if pd.isna(row['Book']) or pd.isna(row['Quote']):
                continue

            book_title = row['Book'].strip()
            book_key = book_title.lower()

            book = existing_books.get(book_key)
            if not book:
                book = Book(
                    title=book_title,
                    author=row['Author'].strip() if pd.notna(row['Author']) else 'Unknown'
                )
                db.session.add(book)
                db.session.flush()
                existing_books[book_key] = book

            if book.id < CUTOFF_BOOK_ID:
                skipped += 1
                continue

            quote_text = row['Quote'].strip()
            note_text = row['Note'].strip() if isinstance(row['Note'], str) else ''

            quote_type = int(row['Type']) if not pd.isna(row['Type']) else 0
            if quote_type == 0:
                skipped += 1
                continue

            loc_start = int(row['LocationStart']) if not pd.isna(row['LocationStart']) else None
            loc_end = int(row['LocationEnd']) if not pd.isna(row['LocationEnd']) else None
            page = row['Page']

            if loc_start is None:
                skipped += 1
                continue

            cache_key = f"{book.id}|{loc_start}"

            # ✅ Cache check
            if cache.get(cache_key) is True:
                skipped += 1
                continue

            existing_quote = Quote.query.filter(
                Quote.book_id == book.id,
                Quote.location_start == loc_start
            ).first()

            if existing_quote:
                changed = False

                if len(quote_text) > len(existing_quote.text):
                    existing_quote.text = quote_text
                    changed = True

                if note_text and (not existing_quote.notes or existing_quote.notes.strip() == ''):
                    existing_quote.notes = note_text
                    changed = True

                if existing_quote.type != quote_type:
                    existing_quote.type = quote_type
                    changed = True

                if changed:
                    updated += 1

                quotes_committed.add(cache_key)
                skipped += 1
                continue

            print(
                f"🟢 Inserted | {book.title} | "
                f"loc={loc_start}-{loc_end} | "
                f"type={quote_type}"
            )

            new_quote = Quote(
                book_id=book.id,
                text=quote_text,
                notes=note_text,
                type=quote_type,
                page=page if not pd.isna(page) else None,
                location_start=loc_start,
                location_end=loc_end,
                is_active=True
            )

            db.session.add(new_quote)
            quotes_committed.add(cache_key)
            inserted += 1

        db.session.commit()

        for key in quotes_committed:
            cache[key] = True

        save_cache(cache)

        print("✅ Commit completed successfully.")
        print(f"🟢 Inserted: {inserted}")
        print(f"🟡 Updated: {updated}")
        print(f"⚪ Skipped: {skipped}")
