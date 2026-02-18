"""
Seed packages/tiers into the database.
Run this script to populate the admin_tiers collection with package data.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "niro")

# Package definitions based on V6 content
PACKAGES = [
    # Career topic packages
    {
        "tier_id": "career_clarity_focussed",
        "name": "Career Clarity - Focussed",
        "topic_id": "career_clarity",
        "price": 2999,
        "duration_weeks": 4,
        "calls_included": 1,
        "call_duration_mins": 30,
        "features": [
            "1 × 30-min deep consultation",
            "1 follow-up call",
            "Unlimited chat support",
            "Career timing analysis",
            "Strength assessment"
        ],
        "description": "Quick clarity on your career path and immediate decisions",
        "popular": False,
        "active": True,
        "content": {
            "hero_title": "Career Clarity",
            "hero_subtitle": "Decode what your chart says about your strengths and direction so you can choose your next move with clarity.",
            "outcomes": {
                "clarity": ["Understand your core strengths", "Identify favorable career paths"],
                "timeline": ["Best periods for job changes", "Upcoming opportunities"],
                "support": ["1 follow-up call", "Chat support"]
            },
            "how_unfolds": [
                "Share your birth details and career questions",
                "30-minute deep dive into your chart",
                "Get personalized insights and timing",
                "Follow-up call to clarify any doubts"
            ]
        }
    },
    {
        "tier_id": "career_clarity_supported",
        "name": "Career Clarity - Supported",
        "topic_id": "career_clarity",
        "price": 6999,
        "duration_weeks": 8,
        "calls_included": 1,
        "call_duration_mins": 45,
        "features": [
            "1 × 45-min deep consultation",
            "2 follow-up calls",
            "Unlimited chat support",
            "Full career analysis",
            "Monthly timing guidance",
            "Decision support"
        ],
        "description": "Comprehensive career guidance with ongoing support",
        "popular": True,
        "active": True,
        "content": {
            "hero_title": "Career Clarity",
            "hero_subtitle": "Decode what your chart says about your strengths and direction so you can choose your next move with clarity.",
            "outcomes": {
                "clarity": ["Deep understanding of your career potential", "Identify favorable career paths", "Understand challenges and solutions"],
                "timeline": ["Best periods for job changes", "Upcoming opportunities", "Monthly guidance"],
                "support": ["2 follow-up calls", "Unlimited chat support", "Decision support"]
            },
            "how_unfolds": [
                "Share your birth details and career questions",
                "45-minute comprehensive chart analysis",
                "Get detailed insights, timing, and action plan",
                "Regular follow-ups over 8 weeks",
                "Ongoing chat support for quick questions"
            ]
        }
    },
    {
        "tier_id": "career_clarity_comprehensive",
        "name": "Career Clarity - Comprehensive",
        "topic_id": "career_clarity",
        "price": 14999,
        "duration_weeks": 12,
        "calls_included": 2,
        "call_duration_mins": 60,
        "features": [
            "2 × 60-min consultations",
            "3 follow-up calls",
            "Unlimited chat support",
            "Complete career roadmap",
            "Weekly check-ins",
            "Priority support"
        ],
        "description": "Complete career transformation with intensive support",
        "popular": False,
        "active": True,
        "content": {
            "hero_title": "Career Clarity",
            "hero_subtitle": "Decode what your chart says about your strengths and direction so you can choose your next move with clarity.",
            "outcomes": {
                "clarity": ["Complete career roadmap", "Business vs job guidance", "Long-term planning"],
                "timeline": ["12-week action plan", "Yearly forecast", "Optimal timing windows"],
                "support": ["3 follow-up calls", "Weekly check-ins", "Priority chat support"]
            },
            "how_unfolds": [
                "Initial deep-dive consultation (60 mins)",
                "Comprehensive chart and career analysis",
                "Create personalized action plan",
                "Second consultation for progress review",
                "Regular follow-ups and weekly check-ins",
                "Ongoing priority support"
            ]
        }
    },
    
    # Marriage/Love topic packages
    {
        "tier_id": "marriage_planning_focussed",
        "name": "Marriage Planning - Focussed",
        "topic_id": "marriage_planning",
        "price": 3999,
        "duration_weeks": 4,
        "calls_included": 1,
        "call_duration_mins": 30,
        "features": [
            "1 × 30-min consultation",
            "1 follow-up call",
            "Compatibility check",
            "Timing guidance",
            "Chat support"
        ],
        "description": "Quick clarity on marriage timing and compatibility",
        "popular": False,
        "active": True
    },
    {
        "tier_id": "marriage_planning_supported",
        "name": "Marriage Planning - Supported",
        "topic_id": "marriage_planning",
        "price": 8999,
        "duration_weeks": 8,
        "calls_included": 1,
        "call_duration_mins": 45,
        "features": [
            "1 × 45-min consultation",
            "2 follow-up calls",
            "Full compatibility analysis",
            "Muhurat selection",
            "Family harmony guidance",
            "Unlimited chat support"
        ],
        "description": "Comprehensive marriage guidance and planning",
        "popular": True,
        "active": True
    },
    {
        "tier_id": "marriage_planning_comprehensive",
        "name": "Marriage Planning - Comprehensive",
        "topic_id": "marriage_planning",
        "price": 17999,
        "duration_weeks": 12,
        "calls_included": 2,
        "call_duration_mins": 60,
        "features": [
            "2 × 60-min consultations",
            "3 follow-up calls",
            "Complete kundli matching",
            "Remedies included",
            "Wedding muhurat",
            "Priority support"
        ],
        "description": "Complete marriage guidance package",
        "popular": False,
        "active": True
    },
    
    # Health/Stress topic packages
    {
        "tier_id": "stress_management_focussed",
        "name": "Stress Management - Focussed",
        "topic_id": "stress_management",
        "price": 2999,
        "duration_weeks": 4,
        "calls_included": 1,
        "call_duration_mins": 30,
        "features": [
            "1 × 30-min consultation",
            "1 follow-up call",
            "Stress pattern analysis",
            "Basic remedies",
            "Chat support"
        ],
        "description": "Quick insights into stress patterns and relief",
        "popular": False,
        "active": True
    },
    {
        "tier_id": "stress_management_supported",
        "name": "Stress Management - Supported",
        "topic_id": "stress_management",
        "price": 6999,
        "duration_weeks": 8,
        "calls_included": 1,
        "call_duration_mins": 45,
        "features": [
            "1 × 45-min consultation",
            "2 follow-up calls",
            "Full health chart analysis",
            "Personalized remedies",
            "Lifestyle guidance",
            "Unlimited chat support"
        ],
        "description": "Comprehensive stress management with ongoing support",
        "popular": True,
        "active": True
    },
    {
        "tier_id": "stress_management_comprehensive",
        "name": "Stress Management - Comprehensive",
        "topic_id": "stress_management",
        "price": 14999,
        "duration_weeks": 12,
        "calls_included": 2,
        "call_duration_mins": 60,
        "features": [
            "2 × 60-min consultations",
            "3 follow-up calls",
            "Complete wellness roadmap",
            "Chakra healing sessions",
            "Weekly check-ins",
            "Priority support"
        ],
        "description": "Complete wellness transformation program",
        "popular": False,
        "active": True
    },
    
    # Relationship Healing packages
    {
        "tier_id": "relationship_healing_focussed",
        "name": "Relationship Healing - Focussed",
        "topic_id": "relationship_healing",
        "price": 2999,
        "duration_weeks": 4,
        "calls_included": 1,
        "call_duration_mins": 30,
        "features": [
            "1 × 30-min consultation",
            "1 follow-up call",
            "Relationship pattern analysis",
            "Basic guidance",
            "Chat support"
        ],
        "description": "Quick clarity on relationship challenges",
        "popular": False,
        "active": True
    },
    {
        "tier_id": "relationship_healing_supported",
        "name": "Relationship Healing - Supported",
        "topic_id": "relationship_healing",
        "price": 6999,
        "duration_weeks": 8,
        "calls_included": 1,
        "call_duration_mins": 45,
        "features": [
            "1 × 45-min consultation",
            "2 follow-up calls",
            "Full relationship analysis",
            "Healing remedies",
            "Communication guidance",
            "Unlimited chat support"
        ],
        "description": "Comprehensive relationship healing support",
        "popular": True,
        "active": True
    },
    {
        "tier_id": "relationship_healing_comprehensive",
        "name": "Relationship Healing - Comprehensive",
        "topic_id": "relationship_healing",
        "price": 14999,
        "duration_weeks": 12,
        "calls_included": 2,
        "call_duration_mins": 60,
        "features": [
            "2 × 60-min consultations",
            "3 follow-up calls",
            "Complete relationship roadmap",
            "Healing rituals included",
            "Weekly check-ins",
            "Priority support"
        ],
        "description": "Complete relationship transformation program",
        "popular": False,
        "active": True
    },
]

async def seed_packages():
    """Seed packages into the database"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"Connected to {DB_NAME} database")
    
    inserted = 0
    updated = 0
    
    for pkg in PACKAGES:
        # Check if exists
        existing = await db.admin_tiers.find_one({"tier_id": pkg["tier_id"]})
        
        if existing:
            # Update
            pkg["updated_at"] = datetime.now(timezone.utc)
            await db.admin_tiers.update_one(
                {"tier_id": pkg["tier_id"]},
                {"$set": pkg}
            )
            updated += 1
            print(f"  Updated: {pkg['tier_id']}")
        else:
            # Insert
            pkg["created_at"] = datetime.now(timezone.utc)
            pkg["updated_at"] = datetime.now(timezone.utc)
            await db.admin_tiers.insert_one(pkg)
            inserted += 1
            print(f"  Inserted: {pkg['tier_id']}")
    
    print(f"\nDone! Inserted: {inserted}, Updated: {updated}")
    
    # Verify
    count = await db.admin_tiers.count_documents({})
    print(f"Total packages in database: {count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_packages())
