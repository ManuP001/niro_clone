"""
UX Utilities for NIRO Chat
Handles conversation state, short-reply detection, chip generation, and trust widget building.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Short reply patterns
SHORT_REPLY_TOKENS = {"yes", "ok", "okay", "continue", "sure", "go", "go on", "next", "more", 
                       "tell me", "yes please", "yep", "yeah", "alright", "right", "got it",
                       "understood", "i see", "hmm", "interesting", "cool", "great", "thanks",
                       "thank you", "no", "nope", "not really", "maybe"}

# Single-word topic keywords
TOPIC_KEYWORDS = {
    "career": ["career", "job", "work", "profession", "business", "employment"],
    "relationship": ["relationship", "love", "marriage", "partner", "spouse", "dating"],
    "health": ["health", "wellness", "fitness", "medical", "disease", "body"],
    "finance": ["finance", "money", "wealth", "income", "investment", "savings"],
    "spirituality": ["spirituality", "spiritual", "meditation", "karma", "dharma", "soul"],
    "education": ["education", "study", "learning", "exam", "college", "university"],
    "family": ["family", "parents", "children", "siblings", "home"],
    "travel": ["travel", "foreign", "abroad", "relocation", "moving"]
}


def is_short_reply(message: str, max_tokens: int = 5) -> bool:
    """
    Detect if a message is a short reply that needs context resolution.
    
    Args:
        message: User message
        max_tokens: Maximum token count to consider as short
        
    Returns:
        True if message is a short reply
    """
    clean_msg = message.strip().lower()
    
    # Check if it's a known short reply pattern
    if clean_msg in SHORT_REPLY_TOKENS:
        return True
    
    # Check token count
    tokens = clean_msg.split()
    if len(tokens) <= max_tokens:
        # Check if it's a single-word topic
        for topic, keywords in TOPIC_KEYWORDS.items():
            if clean_msg in keywords:
                return True
        
        # Check if it looks like a continuation
        if len(tokens) <= 2:
            return True
    
    return False


def resolve_short_reply(
    message: str,
    last_ai_question: Optional[str],
    current_topic: Optional[str],
    last_user_intent: Optional[str]
) -> Tuple[str, float, Optional[str]]:
    """
    Resolve a short reply against conversation context.
    
    Args:
        message: Short user message
        last_ai_question: Last question asked by AI
        current_topic: Current conversation topic
        last_user_intent: Last detected user intent
        
    Returns:
        Tuple of (resolved_message, confidence, clarifying_question)
        - resolved_message: Expanded message with context
        - confidence: 0.0-1.0 confidence in resolution
        - clarifying_question: Question to ask if confidence is low (or None)
    """
    clean_msg = message.strip().lower()
    confidence = 0.5
    clarifying_question = None
    resolved_message = message
    
    # Affirmative replies
    if clean_msg in {"yes", "ok", "okay", "sure", "yep", "yeah", "alright", "go", "go on", "continue", "next", "more", "tell me", "yes please"}:
        if last_ai_question:
            resolved_message = f"Yes, please continue with: {last_ai_question}"
            confidence = 0.8
        elif current_topic:
            resolved_message = f"Tell me more about {current_topic}"
            confidence = 0.7
        else:
            clarifying_question = "What would you like to know more about?"
            confidence = 0.3
            
    # Negative replies
    elif clean_msg in {"no", "nope", "not really"}:
        if last_ai_question:
            resolved_message = f"No, I don't want to continue with {last_ai_question}. What else can you tell me?"
            confidence = 0.6
        else:
            clarifying_question = "What would you prefer to explore instead?"
            confidence = 0.3
            
    # Single-word topic detection
    else:
        detected_topic = None
        for topic, keywords in TOPIC_KEYWORDS.items():
            if clean_msg in keywords:
                detected_topic = topic
                break
        
        if detected_topic:
            resolved_message = f"Tell me about my {detected_topic} prospects based on my chart"
            confidence = 0.85
        elif len(clean_msg.split()) <= 2:
            # Very short but not recognized - ask for clarification
            clarifying_question = f"I'd love to help! Could you tell me a bit more about what aspect of '{message}' you'd like to explore?"
            confidence = 0.3
    
    return resolved_message, confidence, clarifying_question


def generate_clarifying_options(
    current_topic: Optional[str],
    last_ai_question: Optional[str]
) -> List[Dict[str, str]]:
    """
    Generate 2-3 clarifying options for ambiguous replies.
    
    Returns:
        List of options with id and label
    """
    options = []
    
    if current_topic:
        topic_options = {
            "career": [
                {"id": "career_timing", "label": "When is the best time for career moves?"},
                {"id": "career_change", "label": "Should I change my job?"},
                {"id": "career_growth", "label": "How can I grow in my current role?"}
            ],
            "relationship": [
                {"id": "rel_timing", "label": "When will I find love?"},
                {"id": "rel_compatibility", "label": "Am I compatible with my partner?"},
                {"id": "rel_advice", "label": "How can I improve my relationships?"}
            ],
            "health": [
                {"id": "health_concerns", "label": "Any health concerns I should watch?"},
                {"id": "health_timing", "label": "When is a good time for medical procedures?"},
                {"id": "health_wellness", "label": "How can I improve my wellbeing?"}
            ],
            "finance": [
                {"id": "fin_investment", "label": "Is this a good time to invest?"},
                {"id": "fin_income", "label": "When will my income improve?"},
                {"id": "fin_savings", "label": "How can I manage my finances better?"}
            ]
        }
        options = topic_options.get(current_topic, [])[:3]
    
    if not options:
        options = [
            {"id": "explore_career", "label": "Explore my career"},
            {"id": "explore_relationships", "label": "Explore relationships"},
            {"id": "explore_general", "label": "General life guidance"}
        ]
    
    return options


def generate_next_step_chips(
    current_topic: Optional[str],
    last_ai_question: Optional[str],
    mode: str,
    reply_text: str
) -> List[Dict[str, str]]:
    """
    Generate 3-5 context-aware next-step chips.
    
    Args:
        current_topic: Current conversation topic
        last_ai_question: Last question from AI
        mode: Current conversation mode
        reply_text: AI's reply text
        
    Returns:
        List of chip objects with id and label
    """
    chips = []
    
    # Topic-specific chips
    topic_chips = {
        "career": [
            {"id": "career_timing", "label": "🕐 Timing"},
            {"id": "career_action", "label": "📋 What should I do?"},
            {"id": "career_vs_business", "label": "🤔 Job vs Business"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "relationship": [
            {"id": "rel_timing", "label": "🕐 Timing"},
            {"id": "rel_compatibility", "label": "💕 Compatibility"},
            {"id": "rel_action", "label": "📋 What should I do?"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "health": [
            {"id": "health_timing", "label": "🕐 Timing"},
            {"id": "health_precautions", "label": "⚠️ Precautions"},
            {"id": "health_wellness", "label": "🧘 Wellness tips"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "finance": [
            {"id": "fin_timing", "label": "🕐 Best time to invest"},
            {"id": "fin_action", "label": "📋 What should I do?"},
            {"id": "fin_sources", "label": "💰 Income sources"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ],
        "spirituality": [
            {"id": "spirit_practices", "label": "🧘 Practices for me"},
            {"id": "spirit_guidance", "label": "✨ Spiritual guidance"},
            {"id": "spirit_karma", "label": "☯️ Karmic insights"},
            {"id": "switch_topic", "label": "🔄 Ask about something else"}
        ]
    }
    
    if current_topic and current_topic in topic_chips:
        chips = topic_chips[current_topic][:4]
    else:
        # Default chips for general conversation
        chips = [
            {"id": "explore_career", "label": "💼 Career"},
            {"id": "explore_relationship", "label": "💕 Relationships"},
            {"id": "explore_finance", "label": "💰 Finance"},
            {"id": "explore_health", "label": "🏥 Health"},
            {"id": "explore_timing", "label": "🕐 Timing"}
        ]
    
    # Add "Tell me more" if the response seems to have more to offer
    if "?" in reply_text and len(chips) < 5:
        chips.append({"id": "continue", "label": "📖 Tell me more"})
    
    return chips[:5]


def build_trust_widget(
    reasons: List[str],
    timing_windows: List[Dict[str, Any]],
    signal_scores: List[float],
    time_context: str = "timeless"
) -> Dict[str, Any]:
    """
    Build Trust Widget data from raw reasons.
    
    Args:
        reasons: Raw reasons list (may contain S1, S2 labels)
        timing_windows: Timing window data
        signal_scores: Signal confidence scores
        time_context: Time context ("past", "present", "future", "timeless")
        
    Returns:
        Trust Widget dict with drivers, confidence, and time_window
    """
    # Clean reasons - remove S1, S2 labels and make human-readable
    drivers = []
    for reason in reasons[:3]:  # Top 3 only
        # Remove signal IDs like [S1], [S2]
        clean_reason = re.sub(r'\[S\d+\]\s*', '', reason).strip()
        
        # Split on → to get label and impact
        if '→' in clean_reason:
            parts = clean_reason.split('→', 1)
            label = parts[0].strip()
            impact = parts[1].strip() if len(parts) > 1 else None
        else:
            label = clean_reason
            impact = None
        
        # Make more human-readable
        label = humanize_astrological_term(label)
        
        if label:
            drivers.append({
                "label": label,
                "impact": impact
            })
    
    # Calculate confidence based on signal scores
    if signal_scores:
        avg_score = sum(signal_scores) / len(signal_scores)
        if avg_score >= 0.75:
            confidence = "High"
        elif avg_score >= 0.5:
            confidence = "Medium"
        else:
            confidence = "Low"
    else:
        confidence = "Medium"  # Default
    
    # Extract time window based on time_context
    time_window = None
    
    # For PAST context, don't show "current" or "ongoing" timing - it's not relevant
    if time_context == "past":
        # For past questions, timing windows are less relevant
        # Only show if specifically about the past period
        time_window = None  # Don't show current dasha for past questions
        
    # For PRESENT/TIMELESS context, show current timing
    elif time_context in ("present", "timeless"):
        if timing_windows:
            first_window = timing_windows[0]
            period = first_window.get('period', '')
            nature = first_window.get('nature', '')
            # Skip if it says "ongoing" - that's not helpful
            if period and 'ongoing' not in period.lower():
                time_window = f"{period}" + (f" ({nature})" if nature else "")
                
    # For FUTURE context, show the relevant future window
    elif time_context == "future":
        if timing_windows:
            first_window = timing_windows[0]
            period = first_window.get('period', '')
            nature = first_window.get('nature', '')
            if period:
                time_window = f"{period}" + (f" ({nature})" if nature else "")
    
    return {
        "drivers": drivers,
        "confidence": confidence,
        "time_window": time_window
    }


def humanize_astrological_term(term: str) -> str:
    """
    Convert astrological jargon to human-readable terms.
    """
    replacements = {
        "Mahadasha": "Major planetary period",
        "Antardasha": "Sub-period",
        "mahadasha": "major period",
        "antardasha": "sub-period",
        "dasha": "planetary period",
        "Rahu": "North Node (Rahu)",
        "Ketu": "South Node (Ketu)",
        "Saturn": "Saturn's influence",
        "Jupiter": "Jupiter's blessing",
        "Mars": "Mars energy",
        "Venus": "Venus influence",
        "Mercury": "Mercury's effect",
        "Sun": "Solar influence",
        "Moon": "Lunar influence",
        "house": "life area",
        "1st house": "self & identity",
        "2nd house": "wealth & family",
        "3rd house": "communication & siblings",
        "4th house": "home & mother",
        "5th house": "creativity & children",
        "6th house": "health & daily work",
        "7th house": "partnerships & marriage",
        "8th house": "transformation & hidden matters",
        "9th house": "luck & higher learning",
        "10th house": "career & public image",
        "11th house": "gains & aspirations",
        "12th house": "spirituality & endings"
    }
    
    result = term
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result


def should_show_feedback(
    reply_text: str,
    is_welcome: bool = False,
    has_emotional_insight: bool = False
) -> bool:
    """
    Determine if we should show micro-feedback buttons.
    
    Shows feedback for:
    - Welcome messages
    - Emotional insights
    - Strong personality-based statements
    """
    if is_welcome:
        return True
    
    if has_emotional_insight:
        return True
    
    # Check for emotional/personality language
    emotional_keywords = [
        "you are", "you're", "your nature", "your personality",
        "you tend to", "you feel", "emotionally", "your strengths",
        "your weaknesses", "naturally", "innately"
    ]
    
    lower_text = reply_text.lower()
    for keyword in emotional_keywords:
        if keyword in lower_text:
            return True
    
    return False


def extract_ai_question(reply_text: str) -> Optional[str]:
    """
    Extract the question from AI's reply (usually at the end).
    """
    # Find the last question in the reply
    sentences = re.split(r'[.!]\s+', reply_text)
    for sentence in reversed(sentences):
        if '?' in sentence:
            return sentence.strip()
    return None
