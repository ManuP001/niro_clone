# NIRO AI Astrology App - Complete Development Summary

## Overview
NIRO is an AI-powered Vedic astrology application that provides personalized astrological readings, birth chart (Kundli) generation, and intelligent conversation-based guidance.

---

## Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: React with Tailwind CSS
- **Database**: MongoDB
- **LLM**: OpenAI GPT-4o-mini (primary), Gemini (fallback)
- **External API**: Vedic API for astronomical calculations

---

## Core Features Implemented

### 1. Authentication & User Management
- Email-based identification system
- JWT token authentication
- User profile storage with birth details (name, DOB, time, location)
- Gender and marital status collection during onboarding

### 2. Birth Chart (Kundli) System
**File**: `/app/backend/astro_client/vedic_api.py`

- **Vedic API Integration**: Fetches real astronomical data (planets, houses, degrees, signs)
- **SVG Chart Generation**: Custom North Indian style Kundli chart
- **Correct Layout**: Houses arranged CLOCKWISE from Lagna (Ascendant)
- **Sign Numbers**: Displays Rashi numbers (1-12) based on Ascendant, not house numbers
- **Planet Placement**: 9 planets (Su, Mo, Ma, Me, Ju, Ve, Sa, Ra, Ke) correctly positioned
- **Structured Data**: Returns houses, planets with degrees, signs, retrograde status

### 3. Chat System Architecture

#### Ultra-Thin LLM Architecture
**Files**: `/app/backend/astro_client/niro_llm.py`, `/app/backend/conversation/enhanced_orchestrator.py`

- Single LLM call per message (no regeneration loops)
- Optimized prompts (~150 words system prompt)
- Fast greeting handling (0.01s preset responses)
- Clean output without signal IDs [S1], [S2], [S3]

#### Topic Classification
**File**: `/app/backend/astro_client/topics.py`

- 14 topics: career, money, health_energy, romantic_relationships, family, education, travel, property, spirituality, life_purpose, timing, compatibility, children, legal_matters
- Keyword-based detection with ActionId override support
- Topic-to-house mapping (e.g., CAREER→10/6/2)

#### Multi-Topic Answer-First System
**Files**: 
- `/app/backend/conversation/query_intent_router.py`
- `/app/backend/astro_client/reading_pack.py`

- **QueryIntentRouter**: Detects primary_topic, secondary_topics, time_context, question_type
- **MultiTopicReadingPack**: Handles questions spanning multiple topics (e.g., "career and health")
- **Answer-First Format**: Direct Answer → Why → What to do next

### 4. Signal Pipeline & Trust Widget

#### Rule-Based Signal Selection
**File**: `/app/backend/astro_client/reading_pack.py`

- Gate → Score → Select process
- Base score 0.40 with bonuses/penalties
- Global score-based driver selection (not role-quota)
- Max 3 diverse drivers per response
- Planet diversity constraint

#### Trust Widget
**File**: `/app/backend/conversation/ux_utils.py`

- Human-readable drivers (no signal IDs)
- Topic tags per driver (Career, Health, etc.)
- Time window display
- No confidence scores shown

### 5. Time Layer Differentiation
**File**: `/app/backend/astro_client/reading_pack.py`

- Distinguishes past vs future queries
- Mahadasha/Dasha period integration
- Time relevance boost (+0.35 for exact year match)
- Static natal vs time-layer signal classification

### 6. Welcome Message Builder
**File**: `/app/backend/conversation/welcome_builder.py`

- Dedicated builder (not chat flow reuse)
- Structure: Introduction → Personality Insight → Current Phase → Closing
- Confidence guardrails (HIGH/MEDIUM/LOW)
- ≤180 words, mobile-friendly paragraphs
- No spiritual language, no predictions

### 7. Persistent User Memory System
**Files**: `/app/backend/memory/`

#### Data Models
- **UserProfileMemory**: Per-user stable traits, facts, explored topics
- **ConversationState**: Per-session context, message count, current topics
- **ConversationSummary**: Rolling summary with avoid_repeating list

#### Features
- Memory loaded before signal scoring
- 15% repetition penalty for signals matching avoid_repeating
- AVOID_REPEATING section injected into LLM prompt
- Update after user message and AI response
- Summary regeneration every 4 turns

#### Debug Endpoints
- `GET /api/debug/memory/{user_id}` - Get user memory
- `GET /api/debug/memory/{user_id}/context` - Get pipeline context
- `GET /api/debug/memory/{user_id}/sessions` - List sessions
- `DELETE /api/debug/memory/{user_id}` - Reset all memory
- `DELETE /api/debug/memory/{user_id}/session/{session_id}` - Reset session

### 8. Chat Quality Enhancements

- **Timeframe Enforcement**: Past questions don't reference "current dasha", future questions use upcoming periods
- **Explicit Intent Override**: Short messages with clear intent process directly
- **Unclear Question Detection**: Vague inputs prompt clarification
- **Exploratory Questions**: No forced "Yes" answers for What/Which/Where/How questions
- **Follow-up Invitations**: Phrased as offers, not interrogation

---

## API Endpoints

### Authentication
- `POST /api/auth/identify` - Register/login user

### Profile
- `POST /api/profile/` - Create/update birth profile
- `POST /api/profile/welcome` - Get personalized welcome message

### Chat
- `POST /api/chat` - Send message, get AI response
- `GET /api/chat/topics` - Get all 14 topics
- `POST /api/chat/feedback` - Submit response feedback

### Kundli
- `GET /api/kundli` - Get birth chart (SVG + structured data)

### Debug
- `GET /api/debug/candidate-signals/latest` - View signal pipeline
- `GET /api/debug/checklist/{request_id}` - Processing checklist
- `GET /api/debug/memory/{user_id}` - Memory state

---

## Frontend Components

### Screens
- **LoginScreen**: Email entry
- **OnboardingScreen**: Birth details collection (name, DOB, time, location, gender, marital status)
- **ChatScreen**: Main conversation interface
- **KundliScreen**: Birth chart display
- **CandidateSignalsScreen**: Signal debugging view

### UI Features
- Bottom navigation bar (Chat, Kundli, Signals, Profile)
- Trust widget display in chat
- Next step chips for quick actions
- Mobile-responsive design

---

## Key Bug Fixes

1. **Kundli Chart Layout**: Fixed house position mapping (CLOCKWISE from Lagna)
2. **Sign Numbers**: Changed from house numbers to Rashi/sign numbers
3. **Planet Positions**: Corrected SVG coordinates to match house regions
4. **OpenAI Model**: Fixed invalid model 'gpt-5.1' to 'gpt-4o-mini'
5. **Welcome Message Duplication**: Prevented refresh/duplicate fetches
6. **Bottom Nav Static**: Fixed positioning with `fixed bottom-0`

---

## File Structure

```
/app/backend/
├── astro_client/
│   ├── models.py           # Data models
│   ├── vedic_api.py        # Vedic API + SVG generation
│   ├── reading_pack.py     # Signal pipeline
│   ├── niro_llm.py         # LLM integration
│   ├── topics.py           # Topic classification
│   └── interpreter.py      # Astro feature extraction
├── conversation/
│   ├── enhanced_orchestrator.py  # Main chat flow
│   ├── query_intent_router.py    # Intent detection
│   ├── welcome_builder.py        # Welcome messages
│   └── ux_utils.py               # Trust widget
├── memory/
│   ├── models.py           # Memory data models
│   ├── memory_store.py     # MongoDB storage
│   ├── memory_service.py   # High-level service
│   └── README.md           # Documentation
├── routes/
│   └── debug_routes.py     # Debug endpoints
├── auth/
│   ├── models.py           # User models
│   └── auth_service.py     # Authentication
└── server.py               # Main FastAPI app

/app/frontend/src/
├── components/
│   ├── screens/
│   │   ├── ChatScreen.jsx
│   │   ├── KundliScreen.jsx
│   │   ├── OnboardingScreen.jsx
│   │   └── CandidateSignalsScreen.jsx
│   └── BottomNav.jsx
└── App.js
```

---

## Configuration

### Environment Variables (backend/.env)
- `MONGO_URL` - MongoDB connection
- `OPENAI_API_KEY` - OpenAI API key
- `GEMINI_API_KEY` - Google Gemini API key
- `VEDICASTRO_API_KEY` - Vedic API key
- `DB_NAME` - Database name

### Environment Variables (frontend/.env)
- `REACT_APP_BACKEND_URL` - Backend API URL

---

## Testing

### Backend Testing
- Use `deep_testing_backend_v2` agent
- Test file: `/app/test_memory_system.py`

### Debug Tools
- Signal pipeline: `/api/debug/candidate-signals/latest`
- Memory state: `/api/debug/memory/{user_id}`
- Processing trace: `/api/debug/checklist/{request_id}`

---

## Deployment

The application is deployment-ready with:
- ✅ All URLs from environment variables
- ✅ No hardcoded secrets
- ✅ Proper CORS configuration
- ✅ Supervisor configuration for services
- ✅ MongoDB connection via MONGO_URL

---

## Session History

### Features Added This Session:
1. **Memory System Completion**: Debug endpoints, update after AI response, test script, documentation
2. **Kundli Chart Fix**: Corrected house layout from anti-clockwise to CLOCKWISE
3. **Sign Number Display**: Changed from house numbers to Rashi/sign numbers

### Previous Sessions:
- Welcome Message Builder
- Multi-Topic Answer-First Chat System
- Chat Response Quality Fixes
- UI Fixes (Bottom Nav, Welcome Message, Onboarding)
- Persistent User Memory System (initial implementation)
- Time Layer Differentiation
- Ultra-Thin LLM Architecture
- Trust Widget Simplification
- And many more (see test_result.md for complete history)
