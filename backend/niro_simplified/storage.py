"""NIRO Simplified V1 - Storage Layer

MongoDB storage for plans, threads, and passes.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)


class SimplifiedStorage:
    """MongoDB storage for NIRO Simplified"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Collections
        self.plans = db.niro_simplified_plans
        self.threads = db.niro_simplified_threads
        self.messages = db.niro_simplified_messages
        self.topic_passes = db.niro_simplified_topic_passes
        self.telemetry = db.niro_simplified_telemetry
        
        logger.info("SimplifiedStorage initialized")
    
    async def ensure_indexes(self):
        """Create database indexes"""
        try:
            # Plans indexes
            await self.plans.create_index("plan_id", unique=True)
            await self.plans.create_index("user_id")
            await self.plans.create_index("status")
            
            # Threads indexes
            await self.threads.create_index("thread_id", unique=True)
            await self.threads.create_index("plan_id")
            await self.threads.create_index("user_id")
            await self.threads.create_index("expert_id")
            
            # Messages indexes
            await self.messages.create_index("thread_id")
            await self.messages.create_index("created_at")
            
            # Topic passes indexes
            await self.topic_passes.create_index("pass_id", unique=True)
            await self.topic_passes.create_index("user_id")
            await self.topic_passes.create_index("parent_plan_id")
            
            # Telemetry indexes
            await self.telemetry.create_index("user_id")
            await self.telemetry.create_index("event_name")
            await self.telemetry.create_index("timestamp")
            
            logger.info("SimplifiedStorage indexes created")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # =========================================================================
    # PLAN OPERATIONS
    # =========================================================================
    
    async def create_plan(self, plan_data: Dict[str, Any]) -> str:
        """Create a new plan"""
        if "plan_id" not in plan_data:
            plan_data["plan_id"] = f"plan_{uuid.uuid4().hex[:12]}"
        plan_data["created_at"] = datetime.utcnow()
        plan_data["updated_at"] = datetime.utcnow()
        
        await self.plans.insert_one(plan_data)
        return plan_data["plan_id"]
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        return await self.plans.find_one({"plan_id": plan_id}, {"_id": 0})
    
    async def get_user_plans(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get user's plans"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        cursor = self.plans.find(query, {"_id": 0}).sort("created_at", -1)
        return await cursor.to_list(length=50)
    
    async def get_user_active_plans(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's active plans"""
        return await self.get_user_plans(user_id, status="active")
    
    async def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Update plan"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.plans.update_one(
            {"plan_id": plan_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def has_user_purchased(self, user_id: str) -> bool:
        """Check if user has ever purchased"""
        count = await self.plans.count_documents({"user_id": user_id})
        return count > 0
    
    # =========================================================================
    # THREAD OPERATIONS
    # =========================================================================
    
    async def create_thread(self, thread_data: Dict[str, Any]) -> str:
        """Create a new expert thread"""
        if "thread_id" not in thread_data:
            thread_data["thread_id"] = str(uuid.uuid4())
        thread_data["created_at"] = datetime.utcnow()
        thread_data["updated_at"] = datetime.utcnow()
        
        await self.threads.insert_one(thread_data)
        return thread_data["thread_id"]
    
    async def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get thread by ID"""
        return await self.threads.find_one({"thread_id": thread_id}, {"_id": 0})
    
    async def get_plan_threads(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get all threads for a plan"""
        cursor = self.threads.find({"plan_id": plan_id}, {"_id": 0}).sort("last_message_at", -1)
        return await cursor.to_list(length=100)
    
    async def get_user_threads(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recent threads"""
        cursor = self.threads.find(
            {"user_id": user_id, "status": "active"}, 
            {"_id": 0}
        ).sort("last_message_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def count_active_threads(self, plan_id: str) -> int:
        """Count active threads for a plan"""
        return await self.threads.count_documents({"plan_id": plan_id, "status": "active"})
    
    async def update_thread(self, thread_id: str, updates: Dict[str, Any]) -> bool:
        """Update thread"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.threads.update_one(
            {"thread_id": thread_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    # =========================================================================
    # MESSAGE OPERATIONS
    # =========================================================================
    
    async def add_message(self, message_data: Dict[str, Any]) -> str:
        """Add a message to a thread"""
        if "message_id" not in message_data:
            message_data["message_id"] = str(uuid.uuid4())
        message_data["created_at"] = datetime.utcnow()
        
        await self.messages.insert_one(message_data)
        
        # Update thread
        await self.threads.update_one(
            {"thread_id": message_data["thread_id"]},
            {
                "$set": {"last_message_at": datetime.utcnow(), "updated_at": datetime.utcnow()},
                "$inc": {"message_count": 1}
            }
        )
        
        return message_data["message_id"]
    
    async def get_thread_messages(self, thread_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages for a thread"""
        cursor = self.messages.find(
            {"thread_id": thread_id}, 
            {"_id": 0}
        ).sort("created_at", 1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # =========================================================================
    # TOPIC PASS OPERATIONS
    # =========================================================================
    
    async def create_topic_pass(self, pass_data: Dict[str, Any]) -> str:
        """Create a topic pass"""
        if "pass_id" not in pass_data:
            pass_data["pass_id"] = str(uuid.uuid4())
        pass_data["created_at"] = datetime.utcnow()
        
        await self.topic_passes.insert_one(pass_data)
        return pass_data["pass_id"]
    
    async def get_user_topic_passes(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's topic passes"""
        cursor = self.topic_passes.find(
            {"user_id": user_id, "status": "active"}, 
            {"_id": 0}
        )
        return await cursor.to_list(length=50)
    
    async def get_user_accessible_topics(self, user_id: str) -> List[str]:
        """Get all topics user can access (from plans + passes)"""
        topic_ids = set()
        
        # From active plans
        plans = await self.get_user_active_plans(user_id)
        for plan in plans:
            topic_ids.add(plan.get("topic_id"))
        
        # From active passes
        passes = await self.get_user_topic_passes(user_id)
        for p in passes:
            topic_ids.add(p.get("topic_id"))
        
        return list(topic_ids)
    
    # =========================================================================
    # TELEMETRY OPERATIONS
    # =========================================================================
    
    async def log_event(self, event_data: Dict[str, Any]) -> None:
        """Log a telemetry event"""
        event_data["timestamp"] = datetime.utcnow()
        event_data["flow_version"] = "simplified_v1"
        await self.telemetry.insert_one(event_data)


# Singleton instance
_storage: Optional[SimplifiedStorage] = None


def get_simplified_storage(db: AsyncIOMotorDatabase = None) -> Optional[SimplifiedStorage]:
    """Get storage singleton"""
    global _storage
    if _storage is None and db is not None:
        _storage = SimplifiedStorage(db)
    return _storage


async def init_simplified_storage(db: AsyncIOMotorDatabase) -> SimplifiedStorage:
    """Initialize storage"""
    global _storage
    _storage = SimplifiedStorage(db)
    await _storage.ensure_indexes()
    return _storage
