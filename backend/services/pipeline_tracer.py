"""
Pipeline tracer utility.

Tracks execution of astro computation pipeline.
Attach to request context via middleware.
"""

import uuid
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
from backend.models.pipeline_models import (
    PipelineTrace, PipelineStep, StepStatus, QualityFlag
)

logger = logging.getLogger(__name__)


class PipelineTracer:
    """
    Track pipeline execution step by step.
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.run_id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.steps: Dict[str, PipelineStep] = {}
        self.step_order: List[str] = []
        self.step_timers: Dict[str, float] = {}
        
        logger.info(f"🔍 PipelineTracer created: run_id={self.run_id[:8]}, user_id={user_id}")
    
    def start_step(
        self,
        step_id: str,
        display_name: str,
        inputs: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Mark a step as started.
        """
        if step_id not in self.steps:
            self.step_order.append(step_id)
            self.steps[step_id] = PipelineStep(
                step_id=step_id,
                display_name=display_name,
                status=StepStatus.STARTED,
                started_at=datetime.utcnow(),
                inputs=inputs or {}
            )
            self.step_timers[step_id] = time.time()
            logger.info(f"  ▶️  [{step_id}] {display_name} started")
        else:
            logger.warning(f"  ⚠️  [{step_id}] already tracked, skipping start")
    
    def end_step_success(
        self,
        step_id: str,
        outputs: Optional[Dict[str, Any]] = None,
        artifact_ids: Optional[List[str]] = None,
        quality_flags: Optional[List[QualityFlag]] = None
    ) -> None:
        """
        Mark step as successful.
        """
        if step_id not in self.steps:
            logger.error(f"  ❌ [{step_id}] not found in tracer")
            return
        
        step = self.steps[step_id]
        step.status = StepStatus.SUCCESS
        step.ended_at = datetime.utcnow()
        step.duration_ms = int((time.time() - self.step_timers.get(step_id, time.time())) * 1000)
        step.outputs = outputs or {}
        step.artifact_ids = artifact_ids or []
        step.quality_flags = quality_flags or []
        
        flag_str = f" (flags: {', '.join(f.value for f in quality_flags)})" if quality_flags else ""
        logger.info(f"  ✅ [{step_id}] success ({step.duration_ms}ms){flag_str}")
    
    def end_step_fail(
        self,
        step_id: str,
        error_code: str,
        message: str,
        details: Optional[str] = None
    ) -> None:
        """
        Mark step as failed.
        """
        if step_id not in self.steps:
            logger.error(f"  ❌ [{step_id}] not found in tracer")
            return
        
        step = self.steps[step_id]
        step.status = StepStatus.FAILED
        step.ended_at = datetime.utcnow()
        step.duration_ms = int((time.time() - self.step_timers.get(step_id, time.time())) * 1000)
        step.error = {
            "code": error_code,
            "message": message,
            "details": details
        }
        
        logger.error(f"  ❌ [{step_id}] failed: {error_code} - {message}")
    
    def skip_step(self, step_id: str, display_name: str, reason: str) -> None:
        """Mark step as skipped."""
        if step_id not in self.steps:
            self.step_order.append(step_id)
            self.steps[step_id] = PipelineStep(
                step_id=step_id,
                display_name=display_name,
                status=StepStatus.SKIPPED,
                started_at=datetime.utcnow(),
                ended_at=datetime.utcnow(),
                duration_ms=0,
                outputs={"reason": reason}
            )
            logger.info(f"  ⏭️  [{step_id}] skipped: {reason}")
    
    def build_trace(
        self,
        overall_status: StepStatus = StepStatus.SUCCESS,
        overall_quality_flags: Optional[List[QualityFlag]] = None,
        final_astro_profile_id: Optional[str] = None
    ) -> PipelineTrace:
        """
        Build complete trace from tracked steps.
        """
        # Calculate total duration
        start_time = min(
            (s.started_at for s in self.steps.values() if s.started_at),
            default=self.created_at
        )
        end_time = max(
            (s.ended_at for s in self.steps.values() if s.ended_at),
            default=datetime.utcnow()
        )
        total_ms = int((end_time - start_time).total_seconds() * 1000)
        
        # Determine success/degraded
        failed_steps = [s for s in self.steps.values() if s.status == StepStatus.FAILED]
        success = len(failed_steps) == 0
        degraded = len([f for s in self.steps.values() for f in s.quality_flags]) > 0
        
        trace = PipelineTrace(
            run_id=self.run_id,
            user_id=self.user_id,
            created_at=self.created_at,
            steps=[self.steps[sid] for sid in self.step_order],
            overall_status=overall_status,
            overall_quality_flags=overall_quality_flags or [],
            total_duration_ms=total_ms,
            success=success,
            degraded=degraded,
            final_astro_profile_id=final_astro_profile_id
        )
        
        logger.info(
            f"🏁 Pipeline trace complete: run_id={self.run_id[:8]}, "
            f"success={success}, degraded={degraded}, duration={total_ms}ms"
        )
        
        return trace


# Thread-local/request-scoped tracer (will be set by middleware)
_current_tracer: Optional[PipelineTracer] = None


def get_current_tracer() -> Optional[PipelineTracer]:
    """Get tracer for current request."""
    return _current_tracer


def set_current_tracer(tracer: Optional[PipelineTracer]) -> None:
    """Set tracer for current request."""
    global _current_tracer
    _current_tracer = tracer
