"""NIRO V2 MongoDB Storage Layer

Persistent storage for intakes, recommendations, orders, plans, and tasks.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import uuid

logger = logging.getLogger(__name__)


class NiroV2Storage:
    """MongoDB storage for NIRO V2 data"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Collections
        self.intakes = db.niro_v2_intakes
        self.recommendations = db.niro_v2_recommendations
        self.orders = db.niro_v2_orders
        self.plans = db.niro_v2_plans
        self.tasks = db.niro_v2_tasks
        self.remedy_addons = db.niro_v2_remedy_addons
        self.telemetry_events = db.niro_v2_telemetry
        
        logger.info("NiroV2Storage initialized with MongoDB collections")
    
    async def ensure_indexes(self):
        """Create database indexes for performance"""
        try:
            # Intakes indexes
            await self.intakes.create_index("intake_id", unique=True)
            await self.intakes.create_index("user_id")
            await self.intakes.create_index("created_at")
            
            # Recommendations indexes
            await self.recommendations.create_index("recommendation_id", unique=True)
            await self.recommendations.create_index("user_id")
            await self.recommendations.create_index("session_id")
            
            # Orders indexes
            await self.orders.create_index("order_id", unique=True)
            await self.orders.create_index("user_id")
            await self.orders.create_index("razorpay_order_id")
            await self.orders.create_index("status")
            
            # Plans indexes
            await self.plans.create_index("plan_id", unique=True)
            await self.plans.create_index("user_id")
            await self.plans.create_index("status")
            
            # Tasks indexes
            await self.tasks.create_index("task_id", unique=True)
            await self.tasks.create_index("plan_id")
            await self.tasks.create_index([("plan_id", 1), ("scheduled_date", 1)])
            
            # Remedy addons indexes
            await self.remedy_addons.create_index("addon_id", unique=True)
            await self.remedy_addons.create_index("plan_id")
            await self.remedy_addons.create_index("user_id")
            
            # Telemetry indexes
            await self.telemetry_events.create_index("user_id")
            await self.telemetry_events.create_index("event_name")
            await self.telemetry_events.create_index("timestamp")
            
            logger.info("NiroV2Storage indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
    
    # =========================================================================
    # INTAKE OPERATIONS
    # =========================================================================
    
    async def save_intake(self, intake_data: Dict[str, Any]) -> str:
        """Save a situation intake"""
        if "intake_id" not in intake_data:
            intake_data["intake_id"] = str(uuid.uuid4())
        intake_data["created_at"] = datetime.utcnow()
        
        await self.intakes.update_one(
            {"intake_id": intake_data["intake_id"]},
            {"$set": intake_data},
            upsert=True
        )
        return intake_data["intake_id"]
    
    async def get_intake(self, intake_id: str) -> Optional[Dict[str, Any]]:
        """Get intake by ID"""
        return await self.intakes.find_one({"intake_id": intake_id}, {"_id": 0})
    
    async def get_user_intakes(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's intakes"""
        cursor = self.intakes.find(
            {"user_id": user_id}, 
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_latest_user_intake(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's most recent intake"""
        intakes = await self.get_user_intakes(user_id, limit=1)
        return intakes[0] if intakes else None
    
    # =========================================================================
    # RECOMMENDATION OPERATIONS
    # =========================================================================
    
    async def save_recommendation(self, recommendation_data: Dict[str, Any]) -> str:
        """Save a validated recommendation"""
        if "recommendation_id" not in recommendation_data:
            recommendation_data["recommendation_id"] = str(uuid.uuid4())
        recommendation_data["created_at"] = datetime.utcnow()
        
        await self.recommendations.update_one(
            {"recommendation_id": recommendation_data["recommendation_id"]},
            {"$set": recommendation_data},
            upsert=True
        )
        return recommendation_data["recommendation_id"]
    
    async def get_recommendation(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        """Get recommendation by ID"""
        return await self.recommendations.find_one(
            {"recommendation_id": recommendation_id}, 
            {"_id": 0}
        )
    
    async def get_user_recommendations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's recommendations"""
        cursor = self.recommendations.find(
            {"user_id": user_id}, 
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # =========================================================================
    # ORDER OPERATIONS
    # =========================================================================
    
    async def save_order(self, order_data: Dict[str, Any]) -> str:
        """Save an order"""
        if "order_id" not in order_data:
            order_data["order_id"] = f"order_{uuid.uuid4().hex[:12]}"
        order_data["created_at"] = datetime.utcnow()
        order_data["updated_at"] = datetime.utcnow()
        
        await self.orders.update_one(
            {"order_id": order_data["order_id"]},
            {"$set": order_data},
            upsert=True
        )
        return order_data["order_id"]
    
    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID"""
        return await self.orders.find_one({"order_id": order_id}, {"_id": 0})
    
    async def get_order_by_razorpay_id(self, razorpay_order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by Razorpay order ID"""
        return await self.orders.find_one(
            {"razorpay_order_id": razorpay_order_id}, 
            {"_id": 0}
        )
    
    async def update_order_status(
        self, 
        order_id: str, 
        status: str, 
        payment_id: str = None,
        plan_id: str = None
    ) -> bool:
        """Update order status"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if payment_id:
            update_data["razorpay_payment_id"] = payment_id
        if plan_id:
            update_data["plan_id"] = plan_id
        
        result = await self.orders.update_one(
            {"order_id": order_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def get_user_orders(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's orders"""
        cursor = self.orders.find(
            {"user_id": user_id}, 
            {"_id": 0}
        ).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # =========================================================================
    # PLAN OPERATIONS
    # =========================================================================
    
    async def save_plan(self, plan_data: Dict[str, Any]) -> str:
        """Save a user plan"""
        if "plan_id" not in plan_data:
            plan_data["plan_id"] = f"plan_{uuid.uuid4().hex[:12]}"
        plan_data["created_at"] = datetime.utcnow()
        plan_data["updated_at"] = datetime.utcnow()
        
        # Convert date objects to ISO strings for MongoDB
        if isinstance(plan_data.get("start_date"), date):
            plan_data["start_date"] = plan_data["start_date"].isoformat()
        if isinstance(plan_data.get("end_date"), date):
            plan_data["end_date"] = plan_data["end_date"].isoformat()
        
        await self.plans.update_one(
            {"plan_id": plan_data["plan_id"]},
            {"$set": plan_data},
            upsert=True
        )
        return plan_data["plan_id"]
    
    async def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get plan by ID"""
        return await self.plans.find_one({"plan_id": plan_id}, {"_id": 0})
    
    async def get_user_plans(
        self, 
        user_id: str, 
        status: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get user's plans"""
        query = {"user_id": user_id}
        if status:
            query["status"] = status
        
        cursor = self.plans.find(query, {"_id": 0}).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_plan(self, plan_id: str, updates: Dict[str, Any]) -> bool:
        """Update plan fields"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.plans.update_one(
            {"plan_id": plan_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def increment_plan_tasks_completed(self, plan_id: str) -> bool:
        """Increment tasks_completed counter"""
        result = await self.plans.update_one(
            {"plan_id": plan_id},
            {
                "$inc": {"tasks_completed": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    # =========================================================================
    # TASK OPERATIONS
    # =========================================================================
    
    async def save_task(self, task_data: Dict[str, Any]) -> str:
        """Save a task"""
        if "task_id" not in task_data:
            task_data["task_id"] = f"task_{uuid.uuid4().hex[:8]}"
        task_data["created_at"] = datetime.utcnow()
        
        # Convert date objects to ISO strings
        if isinstance(task_data.get("scheduled_date"), date):
            task_data["scheduled_date"] = task_data["scheduled_date"].isoformat()
        
        await self.tasks.update_one(
            {"task_id": task_data["task_id"]},
            {"$set": task_data},
            upsert=True
        )
        return task_data["task_id"]
    
    async def save_tasks_bulk(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Save multiple tasks at once"""
        task_ids = []
        for task in tasks:
            if "task_id" not in task:
                task["task_id"] = f"task_{uuid.uuid4().hex[:8]}"
            task["created_at"] = datetime.utcnow()
            if isinstance(task.get("scheduled_date"), date):
                task["scheduled_date"] = task["scheduled_date"].isoformat()
            task_ids.append(task["task_id"])
        
        if tasks:
            await self.tasks.insert_many(tasks)
        return task_ids
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        return await self.tasks.find_one({"task_id": task_id}, {"_id": 0})
    
    async def get_plan_tasks(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a plan"""
        cursor = self.tasks.find(
            {"plan_id": plan_id}, 
            {"_id": 0}
        ).sort("sequence_order", 1)
        return await cursor.to_list(length=1000)
    
    async def get_plan_tasks_for_date(self, plan_id: str, task_date: date) -> List[Dict[str, Any]]:
        """Get tasks for a specific date"""
        date_str = task_date.isoformat() if isinstance(task_date, date) else task_date
        cursor = self.tasks.find(
            {"plan_id": plan_id, "scheduled_date": date_str},
            {"_id": 0}
        ).sort("sequence_order", 1)
        return await cursor.to_list(length=100)
    
    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update task fields"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def complete_task(self, task_id: str, notes: str = None) -> bool:
        """Mark task as completed"""
        updates = {
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        if notes:
            updates["notes"] = notes
        
        result = await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def skip_task(self, task_id: str) -> bool:
        """Mark task as skipped"""
        result = await self.tasks.update_one(
            {"task_id": task_id},
            {"$set": {
                "status": "skipped",
                "updated_at": datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    # =========================================================================
    # REMEDY ADDON OPERATIONS
    # =========================================================================
    
    async def save_remedy_addon(self, addon_data: Dict[str, Any]) -> str:
        """Save a remedy addon purchase"""
        if "addon_id" not in addon_data:
            addon_data["addon_id"] = f"addon_{uuid.uuid4().hex[:8]}"
        addon_data["created_at"] = datetime.utcnow()
        addon_data["updated_at"] = datetime.utcnow()
        
        await self.remedy_addons.update_one(
            {"addon_id": addon_data["addon_id"]},
            {"$set": addon_data},
            upsert=True
        )
        return addon_data["addon_id"]
    
    async def get_remedy_addon(self, addon_id: str) -> Optional[Dict[str, Any]]:
        """Get remedy addon by ID"""
        return await self.remedy_addons.find_one({"addon_id": addon_id}, {"_id": 0})
    
    async def get_plan_remedy_addons(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get all remedy addons for a plan"""
        cursor = self.remedy_addons.find(
            {"plan_id": plan_id},
            {"_id": 0}
        ).sort("created_at", -1)
        return await cursor.to_list(length=100)
    
    async def get_user_remedy_addons(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all remedy addons for a user"""
        cursor = self.remedy_addons.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1)
        return await cursor.to_list(length=100)
    
    async def update_addon_status(self, addon_id: str, status: str, notes: str = None) -> bool:
        """Update addon fulfillment status"""
        updates = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        if status == "fulfilled":
            updates["fulfilled_at"] = datetime.utcnow()
        if notes:
            updates["fulfillment_notes"] = notes
        
        result = await self.remedy_addons.update_one(
            {"addon_id": addon_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    # =========================================================================
    # TELEMETRY OPERATIONS
    # =========================================================================
    
    async def save_telemetry_event(self, event_data: Dict[str, Any]) -> None:
        """Save a telemetry event"""
        event_data["_timestamp"] = datetime.utcnow()
        await self.telemetry_events.insert_one(event_data)
    
    async def save_telemetry_events_bulk(self, events: List[Dict[str, Any]]) -> None:
        """Save multiple telemetry events"""
        for event in events:
            event["_timestamp"] = datetime.utcnow()
        if events:
            await self.telemetry_events.insert_many(events)
    
    # =========================================================================
    # STATISTICS & ANALYTICS
    # =========================================================================
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        plans = await self.get_user_plans(user_id)
        orders = await self.get_user_orders(user_id)
        
        active_plans = [p for p in plans if p.get("status") == "active"]
        completed_plans = [p for p in plans if p.get("status") == "completed"]
        total_spent = sum(o.get("total_amount", 0) for o in orders if o.get("status") == "completed")
        
        return {
            "total_plans": len(plans),
            "active_plans": len(active_plans),
            "completed_plans": len(completed_plans),
            "total_orders": len(orders),
            "total_spent_inr": total_spent
        }


# Global storage instance
_storage: Optional[NiroV2Storage] = None


def get_niro_v2_storage(db: AsyncIOMotorDatabase = None) -> Optional[NiroV2Storage]:
    """Get or create NiroV2Storage singleton"""
    global _storage
    if _storage is None and db is not None:
        _storage = NiroV2Storage(db)
    return _storage


async def init_niro_v2_storage(db: AsyncIOMotorDatabase) -> NiroV2Storage:
    """Initialize NiroV2Storage with database"""
    global _storage
    _storage = NiroV2Storage(db)
    await _storage.ensure_indexes()
    return _storage
