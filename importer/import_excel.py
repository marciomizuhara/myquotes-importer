import time

from importer.kindle.kindle_copy import copy_from_kindle
from importer.processing.clippings import process_clippings
from importer.persistence.import_db import import_from_excel
from importer.persistence.import_vocabulary import import_vocabulary
from importer.backup.backup_supabase import backup_db
from importer.config import INPUT_FILE, EXCEL_FILE


def main():
    print("🔄 Starting MyQuotes import pipeline...")

    if not copy_from_kindle():
        print("❌ Operation cancelled — Kindle not found.")
        return

    print("📖 Processing My Clippings...")
    ratings_detected, vocabularies_detected = process_clippings(
        input_file=INPUT_FILE,
        output_excel=EXCEL_FILE
    )

    time.sleep(1)

    print("📥 Importing quotes into database...")
    import_from_excel(ratings_detected)

    time.sleep(1)

    print("📘 Importing vocabulary into database...")
    import_vocabulary(vocabularies_detected)

    time.sleep(1)

    print("💾 Creating Supabase SQL backup...")
    backup_db()

    print("✅ Import pipeline finished successfully.")


if __name__ == "__main__":
    main()
