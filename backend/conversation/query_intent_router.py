"""
QueryIntentRouter - Lightweight Multi-Topic Intent Detection

Heuristic-based router that detects:
- primary_topic (career/health/relationships/finance/family/etc.)
- secondary_topics[] (0-2 extra topics for tradeoff/impact/compare questions)
- time_context (past/present/future/none)
- question_type (advice/explanation/prediction/compare/planning)
- is_astro (whether question needs astrology signals)

No LLM calls - pure keyword + pattern matching for speed.
"""

import re
import logging
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class QuestionType(str, Enum):
    """Types of questions users ask"""
    ADVICE = "advice"           # "Should I...", "What should I..."
    EXPLANATION = "explanation" # "Why did...", "What caused..."
    PREDICTION = "prediction"   # "Will I...", "When will..."
    COMPARE = "compare"         # "Which is better...", "X vs Y"
    PLANNING = "planning"       # "When should I...", "Best time to..."
    GENERAL = "general"         # Generic questions


class TimeContext(str, Enum):
    """Time context of the question"""
    PAST = "past"
    PRESENT = "present"
    FUTURE = "future"
    NONE = "none"


@dataclass
class QueryIntent:
    """Result of query intent routing"""
    primary_topic: str
    secondary_topics: List[str] = field(default_factory=list)
    time_context: str = "present"
    question_type: str = "general"
    is_astro: bool = True
    is_multi_topic: bool = False
    is_unclear: bool = False  # NEW: Flag for vague/unclear questions
    needs_clarification: bool = False  # NEW: Should ask clarifying question
    confidence: float = 0.8
    debug_info: Dict = field(default_factory=dict)


# ============================================================================
# TOPIC KEYWORDS
# ============================================================================

TOPIC_KEYWORDS: Dict[str, Set[str]] = {
    "career": {
        "job", "career", "work", "office", "boss", "promotion", "startup",
        "company", "profession", "employment", "colleague", "interview",
        "resign", "fired", "hired", "workplace", "business", "venture",
        "entrepreneur", "corporate", "salary", "appraisal", "project",
        "profession", "occupation", "switch jobs", "new job", "quit"
    },
    "health_energy": {
        "health", "tired", "energy", "fitness", "diet", "stress",
        "sleep", "illness", "disease", "doctor", "hospital", "medicine",
        "surgery", "mental", "anxiety", "depression", "wellness",
        "fatigue", "chronic", "recovery", "sick", "weight", "exercise",
        "burnout", "exhaustion", "physical"
    },
    "romantic_relationships": {
        "love", "crush", "dating", "boyfriend", "girlfriend", "romantic",
        "attraction", "relationship", "romance", "flirt", "breakup",
        "ex", "feelings", "chemistry", "soulmate", "partner"
    },
    "marriage_partnership": {
        "marriage", "husband", "wife", "spouse", "wedding", "married",
        "divorce", "engagement", "matrimony", "compatibility"
    },
    "money": {
        "money", "income", "salary", "finance", "investment", "debt",
        "loan", "wealth", "rich", "savings", "stock", "trading",
        "real estate", "property", "inheritance", "financial", "profit",
        "loss", "expense", "budget", "crypto"
    },
    "family_home": {
        "family", "mother", "father", "parents", "home", "house",
        "children", "kids", "son", "daughter", "sibling", "brother",
        "sister", "relatives", "in-laws", "domestic", "household"
    },
    "learning_education": {
        "study", "exam", "college", "university", "course", "degree",
        "learning", "skill", "education", "school", "student",
        "training", "certification", "academic", "research"
    },
    "travel_relocation": {
        "travel", "trip", "abroad", "relocate", "move", "foreign",
        "immigration", "visa", "overseas", "settle", "migration",
        "shifting", "transfer"
    },
    "spirituality": {
        "spiritual", "meditation", "karma", "purpose", "soul", "inner",
        "enlightenment", "prayer", "consciousness", "awakening"
    },
    "self_psychology": {
        "personality", "character", "myself", "identity",
        "confidence", "self-esteem", "who am i", "life path",
        "strengths", "weaknesses", "potential"
    },
}


# ============================================================================
# MULTI-TOPIC DETECTION PATTERNS
# ============================================================================

# Patterns that indicate user is asking about impact/tradeoff between topics
MULTI_TOPIC_PATTERNS = [
    r'\b(impact|affect|influence|effect)\b.*\b(health|career|family|relationship|money|finance)\b',
    r'\b(health|career|family|relationship|money|finance)\b.*\b(impact|affect|influence|effect)\b',
    r'\bif i\b.*\b(will|would)\b.*\b(health|career|family|relationship|money|work)\b',
    r'\b(balance|juggle|manage)\b.*\b(work|career|family|health|relationship)\b',
    r'\b(versus|vs\.?|or)\b',
    r'\b(tradeoff|trade-off|sacrifice|cost)\b',
    r'\b(at the cost of|at expense of)\b',
    r'\bshould i.*\bor\b',
    r'\bwhich is better\b',
    r'\bchoose between\b',
]

# Compile patterns for efficiency
MULTI_TOPIC_COMPILED = [re.compile(p, re.IGNORECASE) for p in MULTI_TOPIC_PATTERNS]


# ============================================================================
# TIME CONTEXT PATTERNS
# ============================================================================

PAST_PATTERNS = [
    r'\b(last year|last month|last week|yesterday)\b',
    r'\b(in 20[01][0-9]|in 202[0-4])\b',  # Years clearly in past
    r'\b(past|previous|earlier|before|ago)\b',
    r'\b(happened|occurred|was|were|did|had)\b.*\?',
    r'\b(why did|what happened|what caused)\b',
    r'\b(between 20[01][0-9]|during 20[01][0-9])\b',
]

FUTURE_PATTERNS = [
    r'\b(next year|next month|next week|tomorrow)\b',
    r'\b(in 202[5-9]|in 203[0-9])\b',  # Years clearly in future
    r'\b(future|upcoming|coming|ahead|soon)\b',
    r'\b(will|going to|shall|plan to)\b',
    r'\b(when will|when should|when can)\b',
    r'\b(best time to|good time for|right time)\b',
]

PRESENT_PATTERNS = [
    r'\b(currently|right now|at the moment|these days)\b',
    r'\b(this year|this month|this week|today)\b',
    r'\b(am i|are you|is my|is it)\b',
    r'\b(ongoing|happening now|present)\b',
]


# ============================================================================
# QUESTION TYPE PATTERNS
# ============================================================================

QUESTION_TYPE_PATTERNS = {
    QuestionType.ADVICE: [
        r'\bshould i\b',
        r'\bwhat should\b',
        r'\bdo you think\b',
        r'\bwould you recommend\b',
        r'\bis it wise\b',
        r'\bis it good idea\b',
        r'\badvice\b',
    ],
    QuestionType.EXPLANATION: [
        r'\bwhy\b.*\?',
        r'\bwhat caused\b',
        r'\bwhat happened\b',
        r'\breason for\b',
        r'\bexplain\b',
        r'\bhow come\b',
    ],
    QuestionType.PREDICTION: [
        r'\bwill i\b',
        r'\bwill my\b',
        r'\bwill there\b',
        r'\bwhat will\b',
        r'\bgoing to happen\b',
        r'\bpredict\b',
    ],
    QuestionType.COMPARE: [
        r'\bwhich is better\b',
        r'\bvs\b',
        r'\bversus\b',
        r'\bcompare\b',
        r'\bchoose between\b',
        r'\b(this|that) or\b',
    ],
    QuestionType.PLANNING: [
        r'\bwhen should i\b',
        r'\bwhen is.*good time\b',
        r'\bbest time to\b',
        r'\bwhen to\b',
        r'\btiming for\b',
        r'\bplan\b',
    ],
}


# ============================================================================
# NON-ASTRO PATTERNS
# ============================================================================

NON_ASTRO_PATTERNS = [
    r'\b(recipe|cook|cooking|ingredient|food|meal)\b',
    r'\b(protein|vitamin|calorie|nutrient|diet plan)\b',
    r'\b(weather|temperature|rain|sunny)\b',
    r'\b(movie|film|song|music|book|show)\b',
    r'\b(code|programming|software|app|website)\b',
    r'\b(how to make|how to cook|how to build)\b',
    r'\b(best \w+ to buy|where to buy)\b',
    r'\b(price of|cost of|how much does)\b.*\b(product|item|thing)\b',
]


# ============================================================================
# MAIN ROUTER CLASS
# ============================================================================

class QueryIntentRouter:
    """
    Lightweight heuristic-based router for detecting query intent.
    
    No LLM calls - uses keyword matching and regex patterns.
    """
    
    def __init__(self):
        # Pre-compile all patterns
        self.past_patterns = [re.compile(p, re.IGNORECASE) for p in PAST_PATTERNS]
        self.future_patterns = [re.compile(p, re.IGNORECASE) for p in FUTURE_PATTERNS]
        self.present_patterns = [re.compile(p, re.IGNORECASE) for p in PRESENT_PATTERNS]
        self.non_astro_patterns = [re.compile(p, re.IGNORECASE) for p in NON_ASTRO_PATTERNS]
        
        self.question_type_patterns = {
            qtype: [re.compile(p, re.IGNORECASE) for p in patterns]
            for qtype, patterns in QUESTION_TYPE_PATTERNS.items()
        }
        
        logger.info("[QUERY_ROUTER] Initialized")
    
    def route(self, user_message: str) -> QueryIntent:
        """
        Route a user query to detect topics, time context, and question type.
        
        Args:
            user_message: The user's question
            
        Returns:
            QueryIntent with all detected attributes
        """
        msg_lower = user_message.lower().strip()
        debug_info = {}
        
        # Step 0: Check if question is unclear/vague
        is_unclear, needs_clarification = self._check_unclear_question(msg_lower)
        debug_info['is_unclear'] = is_unclear
        debug_info['needs_clarification'] = needs_clarification
        
        # Step 1: Check if non-astro query
        is_astro = self._check_is_astro(msg_lower)
        debug_info['is_astro_check'] = is_astro
        
        if not is_astro:
            return QueryIntent(
                primary_topic="general",
                secondary_topics=[],
                time_context="none",
                question_type="general",
                is_astro=False,
                is_multi_topic=False,
                is_unclear=is_unclear,
                needs_clarification=needs_clarification,
                confidence=0.9,
                debug_info=debug_info
            )
        
        # Step 2: Detect topics
        primary_topic, secondary_topics, topic_scores = self._detect_topics(msg_lower)
        debug_info['topic_scores'] = topic_scores
        debug_info['primary_topic'] = primary_topic
        debug_info['secondary_topics_raw'] = secondary_topics
        
        # If topic detection failed and question is short, mark as needing clarification
        if primary_topic == 'general' and len(msg_lower.split()) <= 3:
            needs_clarification = True
            is_unclear = True
        
        # Step 3: Check for multi-topic intent
        is_multi_topic = self._check_multi_topic_intent(msg_lower, secondary_topics)
        debug_info['multi_topic_detected'] = is_multi_topic
        
        # If not multi-topic intent, clear secondary topics
        if not is_multi_topic:
            secondary_topics = []
        
        # Step 4: Detect time context
        time_context = self._detect_time_context(msg_lower)
        debug_info['time_context'] = time_context
        
        # Step 5: Detect question type
        question_type = self._detect_question_type(msg_lower)
        debug_info['question_type'] = question_type
        
        # Calculate confidence
        confidence = self._calculate_confidence(topic_scores, primary_topic)
        
        result = QueryIntent(
            primary_topic=primary_topic,
            secondary_topics=secondary_topics[:2],  # Max 2 secondary
            time_context=time_context,
            question_type=question_type,
            is_astro=True,
            is_multi_topic=len(secondary_topics) > 0,
            is_unclear=is_unclear,
            needs_clarification=needs_clarification,
            confidence=confidence,
            debug_info=debug_info
        )
        
        logger.info(
            f"[QUERY_ROUTER] primary={primary_topic}, secondary={secondary_topics}, "
            f"time={time_context}, type={question_type}, multi={is_multi_topic}, "
            f"unclear={is_unclear}, needs_clarification={needs_clarification}"
        )
        
        return result
    
    def _check_unclear_question(self, msg: str) -> tuple:
        """
        Check if question is unclear/vague and needs clarification.
        
        Returns:
            (is_unclear, needs_clarification)
        """
        # Very short messages without clear topic
        words = msg.split()
        if len(words) <= 2:
            # Check if it's just a single word or two-word question
            vague_starters = ['what', 'how', 'why', 'tell', 'explain', 'help', 'it', 'this', 'that']
            if any(msg.startswith(v) for v in vague_starters):
                return True, True
        
        # Pattern-based unclear detection
        unclear_patterns = [
            r'^(what|how|why|can you)\s*\??$',  # Single interrogative
            r'^tell me\s*$',
            r'^explain\s*$',
            r'^help\s*$',
            r'^(yes|no|ok|okay|sure|maybe)\s*$',  # Single word responses
            r'^(it|this|that)\s+\w{0,3}\s*$',  # "it is", "that one"
        ]
        
        for pattern in unclear_patterns:
            if re.match(pattern, msg, re.IGNORECASE):
                return True, True
        
        return False, False
    
    def _check_is_astro(self, msg: str) -> bool:
        """Check if query needs astrology signals."""
        for pattern in self.non_astro_patterns:
            if pattern.search(msg):
                logger.debug(f"[QUERY_ROUTER] Non-astro pattern matched: {pattern.pattern}")
                return False
        return True
    
    def _detect_topics(self, msg: str) -> Tuple[str, List[str], Dict[str, int]]:
        """
        Detect primary and secondary topics from message.
        
        Returns:
            (primary_topic, secondary_topics, topic_scores)
        """
        words = set(re.findall(r'\b\w+\b', msg))
        topic_scores: Dict[str, int] = {}
        
        for topic, keywords in TOPIC_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Single word match
                if ' ' not in keyword and keyword in words:
                    score += 1
                # Multi-word phrase match (higher weight)
                elif ' ' in keyword and keyword in msg:
                    score += 2
            
            if score > 0:
                topic_scores[topic] = score
        
        # Sort by score descending
        sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_topics:
            return "general", [], {}
        
        primary = sorted_topics[0][0]
        secondary = [t for t, _ in sorted_topics[1:3] if t != primary]
        
        return primary, secondary, topic_scores
    
    def _check_multi_topic_intent(self, msg: str, detected_topics: List[str]) -> bool:
        """
        Check if user is asking about impact/tradeoff between topics.
        
        Multi-topic is detected if:
        1. A multi-topic pattern matches, OR
        2. 2+ topics detected with significant scores
        """
        # Check explicit multi-topic patterns
        for pattern in MULTI_TOPIC_COMPILED:
            if pattern.search(msg):
                logger.debug(f"[QUERY_ROUTER] Multi-topic pattern matched: {pattern.pattern}")
                return True
        
        # Check if 2+ topics with meaningful scores
        if len(detected_topics) >= 1:
            # At least one secondary topic detected
            return True
        
        return False
    
    def _detect_time_context(self, msg: str) -> str:
        """Detect time context from message."""
        # Check past
        for pattern in self.past_patterns:
            if pattern.search(msg):
                return TimeContext.PAST.value
        
        # Check future
        for pattern in self.future_patterns:
            if pattern.search(msg):
                return TimeContext.FUTURE.value
        
        # Check present
        for pattern in self.present_patterns:
            if pattern.search(msg):
                return TimeContext.PRESENT.value
        
        # Default to present for astro queries
        return TimeContext.PRESENT.value
    
    def _detect_question_type(self, msg: str) -> str:
        """Detect the type of question being asked."""
        for qtype, patterns in self.question_type_patterns.items():
            for pattern in patterns:
                if pattern.search(msg):
                    return qtype.value
        
        return QuestionType.GENERAL.value
    
    def _calculate_confidence(self, topic_scores: Dict[str, int], primary: str) -> float:
        """Calculate confidence in topic detection."""
        if not topic_scores:
            return 0.5
        
        primary_score = topic_scores.get(primary, 0)
        total_score = sum(topic_scores.values())
        
        if total_score == 0:
            return 0.5
        
        # Confidence based on how dominant primary topic is
        dominance = primary_score / total_score
        
        if dominance >= 0.7:
            return 0.9
        elif dominance >= 0.5:
            return 0.8
        elif dominance >= 0.3:
            return 0.7
        else:
            return 0.6


# ============================================================================
# MODULE INTERFACE
# ============================================================================

_router: Optional[QueryIntentRouter] = None


def get_query_router() -> QueryIntentRouter:
    """Get or create the QueryIntentRouter singleton."""
    global _router
    if _router is None:
        _router = QueryIntentRouter()
    return _router


def route_query(user_message: str) -> QueryIntent:
    """
    Main entry point for query routing.
    
    Args:
        user_message: The user's question
        
    Returns:
        QueryIntent with primary_topic, secondary_topics, time_context, etc.
    """
    router = get_query_router()
    return router.route(user_message)


# ============================================================================
# TOPIC DISPLAY LABELS
# ============================================================================

TOPIC_DISPLAY_LABELS = {
    "career": "Career",
    "health_energy": "Health",
    "romantic_relationships": "Relationships",
    "marriage_partnership": "Marriage",
    "money": "Finance",
    "family_home": "Family",
    "learning_education": "Education",
    "travel_relocation": "Travel",
    "spirituality": "Spirituality",
    "self_psychology": "Self",
    "general": "General",
}


def get_topic_label(topic: str) -> str:
    """Get display label for a topic."""
    return TOPIC_DISPLAY_LABELS.get(topic, topic.replace('_', ' ').title())
