"""Time context detection for chat messages

Infers whether user is asking about past, present, or future
using cheap heuristics (no LLM needed).
"""

import re
from typing import Literal

TimeContext = Literal["past", "present", "future", "unknown"]


def infer_time_context(user_message: str) -> TimeContext:
    """
    Infer time context from user message using heuristics.
    
    Returns one of: "past", "present", "future", "unknown"
    
    Args:
        user_message: The user's chat message
        
    Returns:
        Time context string
    """
    if not user_message:
        return "unknown"
    
    msg_lower = user_message.lower()
    
    # Future indicators (higher priority)
    future_patterns = [
        r"\bwill\b",
        r"\bshould i\b",
        r"\bshould we\b",
        r"\bcoming\b",
        r"\bnext\s+(?:year|month|week|day)",
        r"\bin\s+20[0-9]{2}",  # in 2025, 2026, etc.
        r"\bstart\b.*\bnow\b",
        r"\bbegin\b.*\bnow\b",
        r"\bjob\s+search\s+now\b",
        r"\bchange.*now\b",
        r"\bstart\s+a\s+(?:business|company|venture)",
        r"\bwhen\s+(?:will|should)",
        r"\btiming\b",
        r"\bwhen\s+is\s+(?:best|good)",
        r"\bin\s+the\s+future\b",
        r"\bforecas[t|e]",
        r"\bpredic[t|ion]",
        r"\blooking\s+ahead\b",
        r"\bgood\s+time\s+(?:to|for)",  # More specific
    ]
    
    for pattern in future_patterns:
        if re.search(pattern, msg_lower):
            return "future"
    
    # Past indicators
    past_patterns = [
        r"\blast\s+(?:year|month|week|day)",
        r"\bin\s+20[0-1][0-9]",  # in 2000-2019
        r"\bwhat\s+happened\b",
        r"\bwhy\s+did\b",
        r"\bhow\s+did\b",
        r"\bwas\b.*\s+reason",
        r"\bpast\b",
        r"\bhistory\b",
        r"\bretrospective\b",
        r"\blooking\s+back\b",
    ]
    
    for pattern in past_patterns:
        if re.search(pattern, msg_lower):
            return "past"
    
    # Present indicators
    present_patterns = [
        r"\bright\s+now\b",
        r"\bcurrently\b",
        r"\btoday\b",
        r"\bnow\b",
        r"\bpresent\b",
        r"\bam\s+i\b",
        r"\bis\s+(?:this|that)\b",
        r"\bdoing\b.*\bnow\b",
    ]
    
    for pattern in present_patterns:
        if re.search(pattern, msg_lower):
            return "present"
    
    return "unknown"
