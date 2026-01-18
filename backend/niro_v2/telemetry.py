"""NIRO V2 Telemetry Service

Event logging for growth + quality tracking.
All events include version tracking for auditability.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import json

logger = logging.getLogger(__name__)


class TelemetryEvent(BaseModel):
    """Standard telemetry event structure"""
    event_name: str
    user_id: Optional[str] = None
    properties: Dict[str, Any] = {}
    timestamp: datetime
    
    # Version tracking for audit
    prompt_version: Optional[str] = None
    catalog_version: Optional[str] = None


class TelemetryService:
    """
    Centralized telemetry service for event logging.
    In production, this would send to analytics backend.
    """
    
    def __init__(self, db=None):
        self.db = db
        self.events_buffer: List[TelemetryEvent] = []
        self.buffer_size = 100  # Flush after this many events
    
    async def log_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        prompt_version: Optional[str] = None,
        catalog_version: Optional[str] = None
    ) -> None:
        """
        Log a telemetry event.
        """
        event = TelemetryEvent(
            event_name=event_name,
            user_id=user_id,
            properties=properties or {},
            timestamp=datetime.utcnow(),
            prompt_version=prompt_version,
            catalog_version=catalog_version
        )
        
        # Log to console for debugging
        logger.info(f"TELEMETRY: {event_name} | user={user_id} | props={properties}")
        
        # Buffer event
        self.events_buffer.append(event)
        
        # Flush if buffer is full
        if len(self.events_buffer) >= self.buffer_size:
            await self._flush_events()
        
        # Also store in DB if available
        if self.db:
            await self._store_event(event)
    
    async def _store_event(self, event: TelemetryEvent) -> None:
        """Store event in database"""
        try:
            if self.db:
                await self.db.telemetry_events.insert_one(event.model_dump())
        except Exception as e:
            logger.error(f"Failed to store telemetry event: {e}")
    
    async def _flush_events(self) -> None:
        """Flush buffered events to storage"""
        if not self.events_buffer:
            return
        
        try:
            if self.db:
                events_data = [e.model_dump() for e in self.events_buffer]
                await self.db.telemetry_events.insert_many(events_data)
            self.events_buffer = []
        except Exception as e:
            logger.error(f"Failed to flush telemetry events: {e}")
    
    # =========================================================================
    # ONBOARDING EVENTS
    # =========================================================================
    
    async def track_onboarding_started(
        self,
        user_id: str,
        entry_point: str = "organic",
        device_type: str = "web"
    ) -> None:
        await self.log_event(
            "onboarding_started",
            user_id=user_id,
            properties={
                "entry_point": entry_point,
                "device_type": device_type
            }
        )
    
    async def track_birth_details_completed(
        self,
        user_id: str,
        has_exact_time: bool,
        birth_year: int,
        time_to_complete_seconds: int
    ) -> None:
        await self.log_event(
            "birth_details_completed",
            user_id=user_id,
            properties={
                "has_exact_time": has_exact_time,
                "birth_year": birth_year,
                "time_to_complete_seconds": time_to_complete_seconds
            }
        )
    
    async def track_intake_completed(
        self,
        user_id: str,
        topic: str,
        urgency: str,
        decision_ownership: str,
        time_to_complete_seconds: int
    ) -> None:
        await self.log_event(
            "intake_completed",
            user_id=user_id,
            properties={
                "topic": topic,
                "urgency": urgency,
                "decision_ownership": decision_ownership,
                "time_to_complete_seconds": time_to_complete_seconds
            }
        )
    
    # =========================================================================
    # CHAT EVENTS
    # =========================================================================
    
    async def track_chat_session_started(
        self,
        user_id: str,
        session_id: str,
        topic: str,
        urgency: str,
        prompt_version: str,
        catalog_version: str
    ) -> None:
        await self.log_event(
            "chat_session_started",
            user_id=user_id,
            properties={
                "session_id": session_id,
                "topic": topic,
                "urgency": urgency
            },
            prompt_version=prompt_version,
            catalog_version=catalog_version
        )
    
    async def track_situation_extracted(
        self,
        user_id: str,
        session_id: str,
        topic_confirmed: str,
        urgency_level: str,
        concerns_count: int,
        wants_consultation: bool,
        chat_turns: int
    ) -> None:
        await self.log_event(
            "situation_extracted",
            user_id=user_id,
            properties={
                "session_id": session_id,
                "topic_confirmed": topic_confirmed,
                "urgency_level": urgency_level,
                "concerns_count": concerns_count,
                "wants_consultation": wants_consultation,
                "chat_turns": chat_turns
            }
        )
    
    async def track_recommendations_validated(
        self,
        user_id: str,
        session_id: str,
        recommendation_id: str,
        branch: str,
        primary_package_id: str,
        alt_packages_count: int,
        suggested_remedies_count: int,
        retry_count: int,
        prompt_version: str,
        catalog_version: str
    ) -> None:
        await self.log_event(
            "recommendations_validated",
            user_id=user_id,
            properties={
                "session_id": session_id,
                "recommendation_id": recommendation_id,
                "branch": branch,
                "primary_package_id": primary_package_id,
                "alt_packages_count": alt_packages_count,
                "suggested_remedies_count": suggested_remedies_count,
                "retry_count": retry_count
            },
            prompt_version=prompt_version,
            catalog_version=catalog_version
        )
    
    async def track_recommendation_validation_failed(
        self,
        user_id: str,
        session_id: str,
        error_codes: List[str],
        retry_count: int,
        prompt_version: str,
        catalog_version: str
    ) -> None:
        await self.log_event(
            "recommendation_validation_failed",
            user_id=user_id,
            properties={
                "session_id": session_id,
                "error_codes": error_codes,
                "retry_count": retry_count
            },
            prompt_version=prompt_version,
            catalog_version=catalog_version
        )
    
    # =========================================================================
    # PACKAGE & RECOMMENDATION EVENTS
    # =========================================================================
    
    async def track_trust_step_viewed(
        self,
        user_id: str,
        session_id: str,
        recommendation_id: str,
        chart_insights_count: int
    ) -> None:
        await self.log_event(
            "trust_step_viewed",
            user_id=user_id,
            properties={
                "session_id": session_id,
                "recommendation_id": recommendation_id,
                "chart_insights_count": chart_insights_count
            }
        )
    
    async def track_recommendations_list_viewed(
        self,
        user_id: str,
        recommendation_id: str,
        primary_package_id: str,
        packages_shown_count: int
    ) -> None:
        await self.log_event(
            "recommendations_list_viewed",
            user_id=user_id,
            properties={
                "recommendation_id": recommendation_id,
                "primary_package_id": primary_package_id,
                "packages_shown_count": packages_shown_count
            }
        )
    
    async def track_package_landing_viewed(
        self,
        user_id: str,
        package_id: str,
        package_topic: str,
        package_branch: str,
        package_price_inr: int,
        source: str,
        recommendation_id: Optional[str] = None
    ) -> None:
        await self.log_event(
            "package_landing_viewed",
            user_id=user_id,
            properties={
                "package_id": package_id,
                "package_topic": package_topic,
                "package_branch": package_branch,
                "package_price_inr": package_price_inr,
                "source": source,
                "recommendation_id": recommendation_id
            }
        )
    
    # =========================================================================
    # REMEDY EVENTS
    # =========================================================================
    
    async def track_remedy_addon_viewed(
        self,
        user_id: str,
        remedy_id: str,
        remedy_category: str,
        remedy_price_inr: int,
        source: str
    ) -> None:
        await self.log_event(
            "remedy_addon_viewed",
            user_id=user_id,
            properties={
                "remedy_id": remedy_id,
                "remedy_category": remedy_category,
                "remedy_price_inr": remedy_price_inr,
                "source": source
            }
        )
    
    async def track_remedy_addon_added(
        self,
        user_id: str,
        remedy_id: str,
        remedy_category: str,
        remedy_price_inr: int,
        context_package_id: Optional[str] = None,
        context_plan_id: Optional[str] = None
    ) -> None:
        await self.log_event(
            "remedy_addon_added",
            user_id=user_id,
            properties={
                "remedy_id": remedy_id,
                "remedy_category": remedy_category,
                "remedy_price_inr": remedy_price_inr,
                "context_package_id": context_package_id,
                "context_plan_id": context_plan_id
            }
        )
    
    # =========================================================================
    # CHECKOUT & PURCHASE EVENTS
    # =========================================================================
    
    async def track_checkout_started(
        self,
        user_id: str,
        package_id: str,
        package_price_inr: int,
        remedy_addon_ids: List[str],
        remedy_addons_total_inr: int,
        total_amount_inr: int,
        recommendation_id: Optional[str] = None
    ) -> None:
        await self.log_event(
            "checkout_started",
            user_id=user_id,
            properties={
                "package_id": package_id,
                "package_price_inr": package_price_inr,
                "remedy_addon_ids": remedy_addon_ids,
                "remedy_addons_total_inr": remedy_addons_total_inr,
                "total_amount_inr": total_amount_inr,
                "recommendation_id": recommendation_id
            }
        )
    
    async def track_purchase_completed(
        self,
        user_id: str,
        order_id: str,
        plan_id: str,
        package_id: str,
        package_topic: str,
        package_branch: str,
        package_price_inr: int,
        remedy_addon_ids: List[str],
        remedy_addons_count: int,
        remedy_addons_total_inr: int,
        total_amount_inr: int,
        payment_method: str,
        recommendation_id: Optional[str] = None
    ) -> None:
        await self.log_event(
            "purchase_completed",
            user_id=user_id,
            properties={
                "order_id": order_id,
                "plan_id": plan_id,
                "package_id": package_id,
                "package_topic": package_topic,
                "package_branch": package_branch,
                "package_price_inr": package_price_inr,
                "remedy_addon_ids": remedy_addon_ids,
                "remedy_addons_count": remedy_addons_count,
                "remedy_addons_total_inr": remedy_addons_total_inr,
                "total_amount_inr": total_amount_inr,
                "payment_method": payment_method,
                "recommendation_id": recommendation_id
            }
        )
    
    async def track_purchase_failed(
        self,
        user_id: str,
        order_id: str,
        total_amount_inr: int,
        failure_reason: str,
        payment_method: str
    ) -> None:
        await self.log_event(
            "purchase_failed",
            user_id=user_id,
            properties={
                "order_id": order_id,
                "total_amount_inr": total_amount_inr,
                "failure_reason": failure_reason,
                "payment_method": payment_method
            }
        )
    
    # =========================================================================
    # PLAN ENGAGEMENT EVENTS
    # =========================================================================
    
    async def track_plan_started(
        self,
        user_id: str,
        plan_id: str,
        package_id: str,
        package_topic: str,
        package_duration_weeks: int
    ) -> None:
        await self.log_event(
            "plan_started",
            user_id=user_id,
            properties={
                "plan_id": plan_id,
                "package_id": package_id,
                "package_topic": package_topic,
                "package_duration_weeks": package_duration_weeks
            }
        )
    
    async def track_task_completed(
        self,
        user_id: str,
        plan_id: str,
        task_id: str,
        task_type: str,
        task_day: int,
        time_spent_seconds: Optional[int] = None
    ) -> None:
        await self.log_event(
            "task_completed",
            user_id=user_id,
            properties={
                "plan_id": plan_id,
                "task_id": task_id,
                "task_type": task_type,
                "task_day": task_day,
                "time_spent_seconds": time_spent_seconds
            }
        )
    
    async def track_consult_session_booked(
        self,
        user_id: str,
        plan_id: str,
        booking_id: str,
        session_number: int,
        scheduled_datetime: datetime
    ) -> None:
        await self.log_event(
            "consult_session_booked",
            user_id=user_id,
            properties={
                "plan_id": plan_id,
                "booking_id": booking_id,
                "session_number": session_number,
                "scheduled_datetime": scheduled_datetime.isoformat()
            }
        )
    
    async def track_plan_completed(
        self,
        user_id: str,
        plan_id: str,
        package_id: str,
        package_topic: str,
        duration_actual_days: int,
        tasks_completed: int,
        tasks_total: int,
        completion_percent: int,
        consult_sessions_used: int,
        remedy_addons_purchased: int
    ) -> None:
        await self.log_event(
            "plan_completed",
            user_id=user_id,
            properties={
                "plan_id": plan_id,
                "package_id": package_id,
                "package_topic": package_topic,
                "duration_actual_days": duration_actual_days,
                "tasks_completed": tasks_completed,
                "tasks_total": tasks_total,
                "completion_percent": completion_percent,
                "consult_sessions_used": consult_sessions_used,
                "remedy_addons_purchased": remedy_addons_purchased
            }
        )
    
    async def track_remedy_addon_purchased(
        self,
        user_id: str,
        plan_id: str,
        remedy_id: str,
        remedy_category: str,
        remedy_price_inr: int,
        plan_week: int
    ) -> None:
        await self.log_event(
            "remedy_addon_purchased",
            user_id=user_id,
            properties={
                "plan_id": plan_id,
                "remedy_id": remedy_id,
                "remedy_category": remedy_category,
                "remedy_price_inr": remedy_price_inr,
                "plan_week": plan_week
            }
        )


# Singleton instance
_telemetry_service: Optional[TelemetryService] = None


def get_telemetry_service(db=None) -> TelemetryService:
    """Get or create telemetry service singleton"""
    global _telemetry_service
    if _telemetry_service is None:
        _telemetry_service = TelemetryService(db)
    return _telemetry_service
