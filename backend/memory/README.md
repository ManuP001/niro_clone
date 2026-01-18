# NIRO Memory System

## Overview

The Memory System provides persistent user memory and rolling conversation summaries to reduce generic/repetitive answers and build on established context.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MEMORY SYSTEM                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   │
│  │  UserProfile    │   │ Conversation    │   │ Conversation    │   │
│  │    Memory       │   │    State        │   │   Summary       │   │
│  │  (per user)     │   │  (per session)  │   │ (per session)   │   │
│  └────────┬────────┘   └────────┬────────┘   └────────┬────────┘   │
│           │                     │                     │             │
│           └─────────────────────┼─────────────────────┘             │
│                                 │                                    │
│                                 ▼                                    │
│                    ┌─────────────────────────┐                      │
│                    │    MemoryContext        │                      │
│                    │ (combined, for pipeline)│                      │
│                    └───────────┬─────────────┘                      │
│                                │                                    │
└────────────────────────────────┼────────────────────────────────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                        PIPELINE INJECTION                           │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Signal Scoring: 15% repetition penalty for avoid_repeating     │
│  2. LLM Prompt: AVOID_REPEATING section injected                   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Data Models

### UserProfileMemory (per user, persists across sessions)

```python
{
    "user_id": "uuid",
    "birth_profile_complete": true,
    "astro_profile_summary": [       # 3-6 stable traits
        "Mercury-ruled mind with analytical bent",
        "Career sector activated by Jupiter"
    ],
    "high_confidence_facts": [       # Chart-based facts
        "Strong 10th house - career focused",
        "Venus in 7th indicates partnership emphasis"
    ],
    "low_confidence_notes": [],      # Mentioned but not confirmed
    "explored_topics": [             # Topics user has asked about
        "career", "relationships", "health"
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "last_updated_at": "2025-01-01T00:00:00Z"
}
```

### ConversationState (per session)

```python
{
    "session_id": "uuid",
    "user_id": "uuid",
    "current_topics": ["career"],
    "last_user_question": "Should I start a business?",
    "last_ai_answer_summary": [
        "Career looks favorable in 2025-2026",
        "Mercury period supports business ventures"
    ],
    "open_loops": [],                # Questions not fully addressed
    "last_run_id": "uuid",
    "message_count": 5,
    "created_at": "2025-01-01T00:00:00Z",
    "last_updated_at": "2025-01-01T00:00:00Z"
}
```

### ConversationSummary (rolling, regenerated every 4 turns)

```python
{
    "session_id": "uuid",
    "user_id": "uuid",
    "summary_text": "Confirmed: User interested in career...",
    "summary_structured": {
        "confirmed_facts": ["User interested in career"],
        "assumptions": [],
        "user_preferences": [],
        "unresolved_questions": [],
        "avoid_repeating": [         # KEY: What NOT to repeat
            "Career looks favorable in 2025-2026",
            "Mercury supports communication roles"
        ]
    },
    "turn_count_at_generation": 4,
    "last_regenerated_at": "2025-01-01T00:00:00Z"
}
```

## How It Works

### 1. Before Processing (Load Context)

```python
# In enhanced_orchestrator.py
memory_service = get_memory_service()
memory_context = memory_service.load_memory_context(user_id, session_id)
```

The `MemoryContext` combines data from all three sources:
- User traits from UserProfileMemory
- Current session state from ConversationState
- Avoid-repeating items from ConversationSummary

### 2. After User Message

```python
memory_service.update_after_user_message(
    user_id=user_id,
    session_id=session_id,
    user_question=message,
    detected_topics=topics,
    run_id=request_id
)
```

Updates:
- `last_user_question`
- `current_topics`
- `message_count` (incremented)
- `explored_topics` in UserProfileMemory

### 3. Signal Scoring (Repetition Penalty)

In `reading_pack.py`, signals matching `avoid_repeating` items get a 15% penalty:

```python
# Check repetition penalty
for avoid_item in avoid_repeating:
    if avoid_item.lower() in signal_text.lower():
        repetition_penalty = 0.15
        break
        
score_final = score_final * (1 - repetition_penalty)
```

### 4. LLM Prompt Injection

In `niro_llm.py`, memory context is added to the prompt:

```
=== CONVERSATION MEMORY ===

AVOID REPEATING (already covered in this conversation):
• Career looks favorable in 2025-2026
• Mercury supports communication roles

ESTABLISHED CONTEXT:
• User interested in career
```

### 5. After AI Response

```python
memory_service.update_after_ai_response(
    user_id=user_id,
    session_id=session_id,
    ai_response=response_text,
    drivers=drivers,
    topic=topic
)
```

Updates:
- `last_ai_answer_summary` (extracted from response)
- `avoid_repeating` (conclusions not to repeat)
- `high_confidence_facts` (from driver claims)

## Debug Endpoints

### Get User Memory
```bash
GET /api/debug/memory/{user_id}?session_id={session_id}
```

Returns complete memory state for debugging.

### Get Memory Context (Pipeline Input)
```bash
GET /api/debug/memory/{user_id}/context?session_id={session_id}
```

Returns exactly what gets passed to the pipeline.

### Get User Sessions
```bash
GET /api/debug/memory/{user_id}/sessions?limit=5
```

Lists recent session IDs for a user.

### Reset User Memory
```bash
DELETE /api/debug/memory/{user_id}
```

Clears ALL memory for a user (use with caution).

### Reset Session Memory
```bash
DELETE /api/debug/memory/{user_id}/session/{session_id}
```

Clears memory for a specific session (preserves user profile).

## Testing

Run acceptance tests:

```bash
python test_memory_system.py
```

Tests cover:
- Memory accumulation across messages
- Debug endpoint functionality
- Context injection verification
- Session reset functionality

## Configuration

### Summary Regeneration Interval

In `memory_service.py`:
```python
SUMMARY_REGENERATION_INTERVAL = 4  # Regenerate every 4 turns
```

### Repetition Penalty

In `reading_pack.py`:
```python
repetition_penalty = 0.15  # 15% penalty for repeated signals
```

## Files

| File | Purpose |
|------|---------|
| `backend/memory/models.py` | Pydantic models for memory data |
| `backend/memory/memory_store.py` | MongoDB storage layer |
| `backend/memory/memory_service.py` | High-level service with business logic |
| `backend/memory/__init__.py` | Module exports |
| `backend/routes/debug_routes.py` | Debug endpoints |
| `test_memory_system.py` | Acceptance tests |

## Usage Example

```python
from backend.memory import get_memory_service

# Get service singleton
memory_service = get_memory_service()

# Load context before processing
context = memory_service.load_memory_context(user_id, session_id)

# Check what to avoid
print(f"Avoid: {context.avoid_repeating}")
print(f"Facts: {context.confirmed_facts}")

# After processing, update memory
memory_service.update_after_ai_response(
    user_id=user_id,
    session_id=session_id,
    ai_response="Your career looks favorable...",
    drivers=[{"planet": "Jupiter", "text_human": "Strong career house"}],
    topic="career"
)
```
