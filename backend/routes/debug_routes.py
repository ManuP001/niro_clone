"""
Debug endpoints for pipeline observability.

Powers the Match → Checklist tab.
Shows complete execution trace with no guessing.

Also includes memory debug endpoints for conversation memory system.
"""

import logging
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional
from datetime import datetime

from backend.models.pipeline_models import DebugPipelineTraceResponse
from backend.services.astro_database import get_astro_db
from backend.memory import get_memory_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/pipeline-trace/latest", response_model=DebugPipelineTraceResponse)
async def get_latest_pipeline_trace(
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    Get the latest pipeline trace for a user.
    
    This is what the Match/Checklist tab displays.
    Shows:
    - What steps ran
    - What succeeded/failed
    - What quality issues were detected
    - Complete timing
    """
    # Use from query or JWT
    if not user_id:
        user_id = "test_user"  # TODO: Extract from JWT
    
    db = await get_astro_db()
    trace = await db.get_latest_pipeline_trace(user_id)
    
    if not trace:
        raise HTTPException(
            status_code=404,
            detail="No pipeline trace found for this user"
        )
    
    return DebugPipelineTraceResponse(
        trace=trace,
        rendered_at=datetime.utcnow()
    )


@router.get("/pipeline-trace", response_model=DebugPipelineTraceResponse)
async def get_pipeline_trace(
    run_id: str = Query(...),
    authorization: Optional[str] = Header(None)
):
    """
    Get specific pipeline trace by run_id.
    """
    db = await get_astro_db()
    trace = await db.get_pipeline_trace(run_id)
    
    if not trace:
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline trace {run_id} not found"
        )
    
    return DebugPipelineTraceResponse(
        trace=trace,
        rendered_at=datetime.utcnow()
    )


@router.get("/pipeline-trace/render-html")
async def render_pipeline_trace_html(
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    Return HTML rendering of latest pipeline trace.
    Used for browser display in Match/Checklist tab.
    """
    if not user_id:
        user_id = "test_user"  # TODO: Extract from JWT
    
    db = await get_astro_db()
    trace = await db.get_latest_pipeline_trace(user_id)
    
    if not trace:
        return """
        <div class="error">
            <h2>No pipeline trace found</h2>
            <p>No astro computation has been run for this user yet.</p>
        </div>
        """
    
    # Build HTML table
    html = f"""
    <div class="pipeline-trace">
        <h2>Pipeline Trace: {trace.run_id}</h2>
        <p>User: <code>{trace.user_id}</code></p>
        <p>Created: {trace.created_at.isoformat()}</p>
        <p>Overall Status: <strong>{trace.overall_status.value}</strong></p>
        <p>Success: {trace.success} | Degraded: {trace.degraded}</p>
        <p>Total Duration: {trace.total_duration_ms}ms</p>
        
        <table border="1" cellpadding="8" cellspacing="0" style="margin-top: 20px; width: 100%;">
            <thead>
                <tr style="background-color: #f0f0f0;">
                    <th>Step ID</th>
                    <th>Display Name</th>
                    <th>Status</th>
                    <th>Duration (ms)</th>
                    <th>Quality Flags</th>
                    <th>Error</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for step in trace.steps:
        error_text = ""
        if step.error:
            error_text = f"{step.error.get('code', 'unknown')}: {step.error.get('message', '')}"
        
        flags_text = ", ".join(f.value for f in step.quality_flags) if step.quality_flags else "-"
        
        status_color = {
            "success": "#4CAF50",
            "failed": "#f44336",
            "skipped": "#FFC107",
            "started": "#2196F3"
        }.get(step.status.value, "#999")
        
        html += f"""
                <tr>
                    <td><code>{step.step_id}</code></td>
                    <td>{step.display_name}</td>
                    <td style="background-color: {status_color}; color: white;">
                        <strong>{step.status.value}</strong>
                    </td>
                    <td>{step.duration_ms or "-"}ms</td>
                    <td><small>{flags_text}</small></td>
                    <td><small>{error_text}</small></td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    <style>
        .pipeline-trace {
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        code {
            background-color: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
        }
    </style>
    """
    
    return {"html": html, "content_type": "text/html"}


# === CANDIDATE SIGNALS DEBUG ENDPOINTS ===

@router.get("/candidate-signals/latest")
async def get_latest_candidate_signals(
    user_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    Get the latest candidate signals debug data.
    
    Shows ALL candidate signals considered before filtering,
    useful for understanding why certain signals were kept/dropped.
    
    Checks in-memory cache first, then falls back to database.
    """
    # First try in-memory cache (faster, most recent)
    from backend.astro_client.reading_pack import _candidate_signals_cache
    
    if _candidate_signals_cache:
        # Get the most recent entry from cache
        latest_key = max(_candidate_signals_cache.keys(), 
                        key=lambda k: _candidate_signals_cache[k].get('timestamp', ''))
        cache_data = _candidate_signals_cache[latest_key]
        
        # If user_id specified, filter
        if user_id and cache_data.get('user_id') != user_id:
            # Try database for specific user
            db = await get_astro_db()
            debug_data = await db.get_latest_candidate_signals_debug(user_id)
            if debug_data:
                return {
                    "data": debug_data,
                    "retrieved_at": datetime.utcnow().isoformat(),
                    "source": "database"
                }
        else:
            return {
                "data": cache_data,
                "retrieved_at": datetime.utcnow().isoformat(),
                "source": "cache"
            }
    
    # Fall back to database
    db = await get_astro_db()
    debug_data = await db.get_latest_candidate_signals_debug(user_id)
    
    if not debug_data:
        raise HTTPException(
            status_code=404,
            detail="No candidate signals debug data found. Ask a question in chat first."
        )
    
    return {
        "data": debug_data,
        "retrieved_at": datetime.utcnow().isoformat(),
        "source": "database"
    }


@router.get("/candidate-signals/{run_id}")
async def get_candidate_signals_by_run(
    run_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Get candidate signals debug data for a specific run.
    """
    db = await get_astro_db()
    debug_data = await db.get_candidate_signals_debug(run_id)
    
    if not debug_data:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate signals debug data for run {run_id} not found"
        )
    
    return {
        "data": debug_data,
        "retrieved_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# MEMORY DEBUG ENDPOINTS
# ============================================================================

@router.get("/memory/{user_id}")
async def get_user_memory(
    user_id: str,
    session_id: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None)
):
    """
    Get memory state for a user.
    
    Returns:
    - user_memory: Long-term user profile memory (stable traits, facts)
    - conversation_state: Current session state (if session_id provided)
    - conversation_summary: Rolling summary (if session_id provided)
    
    Use this to debug:
    - What facts/traits the system remembers about a user
    - What's being avoided in responses (avoid_repeating)
    - Current conversation context
    """
    memory_service = get_memory_service()
    debug_info = memory_service.get_debug_info(user_id, session_id)
    
    if not debug_info.get('user_memory'):
        # Create empty memory if not exists
        debug_info['user_memory'] = {
            "user_id": user_id,
            "birth_profile_complete": False,
            "astro_profile_summary": [],
            "high_confidence_facts": [],
            "low_confidence_notes": [],
            "explored_topics": [],
            "created_at": None,
            "last_updated_at": None
        }
    
    return {
        "ok": True,
        "user_id": user_id,
        "session_id": session_id,
        "memory": debug_info,
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.get("/memory/{user_id}/context")
async def get_memory_context(
    user_id: str,
    session_id: str = Query(..., description="Session ID to load context for"),
    authorization: Optional[str] = Header(None)
):
    """
    Get the combined MemoryContext that gets passed to the pipeline.
    
    This shows exactly what context is being injected into:
    1. Signal scoring (for repetition penalty)
    2. LLM prompt (for avoiding repeated conclusions)
    
    Useful for understanding why certain responses were generated.
    """
    memory_service = get_memory_service()
    context = memory_service.load_memory_context(user_id, session_id)
    
    return {
        "ok": True,
        "user_id": user_id,
        "session_id": session_id,
        "context": context.to_dict(),
        "context_for_prompt": context.get_context_for_prompt(),
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.get("/memory/{user_id}/sessions")
async def get_user_sessions(
    user_id: str,
    limit: int = Query(5, ge=1, le=20),
    authorization: Optional[str] = Header(None)
):
    """
    Get recent session IDs for a user.
    
    Useful for finding session_id to query conversation state.
    """
    from backend.memory import get_memory_store
    store = get_memory_store()
    sessions = store.get_recent_sessions(user_id, limit)
    
    return {
        "ok": True,
        "user_id": user_id,
        "sessions": sessions,
        "count": len(sessions),
        "retrieved_at": datetime.utcnow().isoformat()
    }


@router.delete("/memory/{user_id}")
async def reset_user_memory(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Reset ALL memory for a user.
    
    This clears:
    - User profile memory (traits, facts)
    - All conversation states
    - All conversation summaries
    
    Use with caution - this is destructive!
    """
    memory_service = get_memory_service()
    success = memory_service.reset_user_memory(user_id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to reset user memory"
        )
    
    return {
        "ok": True,
        "message": f"All memory reset for user {user_id}",
        "reset_at": datetime.utcnow().isoformat()
    }


@router.delete("/memory/{user_id}/session/{session_id}")
async def reset_session_memory(
    user_id: str,
    session_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Reset memory for a specific session.
    
    This clears:
    - Conversation state for the session
    - Conversation summary for the session
    
    User profile memory is preserved.
    """
    memory_service = get_memory_service()
    success = memory_service.reset_session_memory(session_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to reset session memory"
        )
    
    return {
        "ok": True,
        "message": f"Session memory reset for session {session_id}",
        "reset_at": datetime.utcnow().isoformat()
    }

