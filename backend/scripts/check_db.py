"""
Quick check: list all collections and document counts in Render's MongoDB.
Run: python3 scripts/check_db.py
"""
from pymongo import MongoClient

MONGO_URL = "mongodb+srv://niro-app:fhd5vvNU0VzZebcc@cluster0.sqdcfli.mongodb.net/?appName=Cluster0"
DB_NAME = "astro_trust_db"

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=15000)
db = client[DB_NAME]

collections = db.list_collection_names()
print(f"\nDatabase: {DB_NAME}")
print(f"Collections found: {len(collections)}\n")

for col in sorted(collections):
    count = db[col].count_documents({})
    print(f"  {col}: {count} documents")

client.close()
