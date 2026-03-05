"""
Delete all dummy/catalog experts from admin_experts collection.
Run: python3 scripts/clear_dummy_experts.py
"""
from pymongo import MongoClient

MONGO_URL = "mongodb+srv://niro-app:fhd5vvNU0VzZebcc@cluster0.sqdcfli.mongodb.net/?appName=Cluster0"
DB_NAME = "astro_trust_db"

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=15000)
db = client[DB_NAME]

count_before = db.admin_experts.count_documents({})
result = db.admin_experts.delete_many({})
count_after = db.admin_experts.count_documents({})

print(f"Deleted {result.deleted_count} experts.")
print(f"Before: {count_before} | After: {count_after}")

client.close()
