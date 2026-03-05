"""
Peek at admin_experts collection to see what's there.
Run: python3 scripts/peek_experts.py
"""
from pymongo import MongoClient

MONGO_URL = "mongodb+srv://niro-app:fhd5vvNU0VzZebcc@cluster0.sqdcfli.mongodb.net/?appName=Cluster0"
DB_NAME = "astro_trust_db"

client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=15000)
db = client[DB_NAME]

experts = list(db.admin_experts.find({}, {"_id": 0, "expert_id": 1, "name": 1, "active": 1, "topics": 1}))
print(f"\nTotal admin_experts: {len(experts)}\n")
for e in experts:
    print(f"  id={e.get('expert_id')} | name={e.get('name')} | active={e.get('active')} | topics={e.get('topics')}")

client.close()
