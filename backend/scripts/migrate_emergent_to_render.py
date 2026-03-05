"""
MongoDB Migration: Emergent → Render
Copies all collections from Emergent's DB to Render's DB.

Usage:
    cd /Users/sharadharjai/niro-ai-experts/backend
    python scripts/migrate_emergent_to_render.py

Requirements:
    pip install pymongo
"""

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

# ── Source (Emergent) ──────────────────────────────────────────────────────────
SOURCE_URL = (
    "mongodb+srv://repo-launch-8:d54cc9klqs2c7391hm8g"
    "@customer-apps.pcz98l.mongodb.net/"
    "?appName=embedded-booking&maxPoolSize=5&retryWrites=true&timeoutMS=10000&w=majority"
)
SOURCE_DB = "repo-launch-8-astro_trust_db"

# ── Destination (Render / your MongoDB Atlas) ──────────────────────────────────
DEST_URL = (
    "mongodb+srv://niro-app:NewMongo123a"
    "@cluster0.sqdcfli.mongodb.net/"
    "?appName=Cluster0"
)
DEST_DB = "niro"

# ── Collections to skip (system / transient data) ─────────────────────────────
SKIP_COLLECTIONS = set()   # add collection names here to exclude them


def migrate():
    print("Connecting to source (Emergent)...")
    src_client = MongoClient(SOURCE_URL, serverSelectionTimeoutMS=15000)
    src_db = src_client[SOURCE_DB]

    print("Connecting to destination (Render/Atlas)...")
    dst_client = MongoClient(DEST_URL, serverSelectionTimeoutMS=15000)
    dst_db = dst_client[DEST_DB]

    collections = src_db.list_collection_names()
    print(f"\nFound {len(collections)} collections in source DB: {collections}\n")

    total_copied = 0
    total_skipped = 0

    for col_name in collections:
        if col_name in SKIP_COLLECTIONS:
            print(f"  [SKIP] {col_name}")
            continue

        src_col = src_db[col_name]
        dst_col = dst_db[col_name]

        docs = list(src_col.find({}))
        if not docs:
            print(f"  [EMPTY] {col_name} — nothing to copy")
            continue

        # Upsert by _id so re-running the script is safe
        operations = [
            UpdateOne({"_id": doc["_id"]}, {"$setOnInsert": doc}, upsert=True)
            for doc in docs
        ]

        try:
            result = dst_col.bulk_write(operations, ordered=False)
            inserted = result.upserted_count
            matched = result.matched_count
            print(f"  [OK] {col_name}: {inserted} inserted, {matched} already existed ({len(docs)} total)")
            total_copied += inserted
        except BulkWriteError as e:
            print(f"  [WARN] {col_name}: partial write — {e.details.get('nInserted', 0)} inserted, errors: {len(e.details.get('writeErrors', []))}")
            total_copied += e.details.get("nInserted", 0)

    print(f"\n✅ Migration complete: {total_copied} documents inserted, {total_skipped} skipped.")
    print(f"   Destination: {DEST_DB} @ cluster0.sqdcfli.mongodb.net")

    src_client.close()
    dst_client.close()


if __name__ == "__main__":
    migrate()
