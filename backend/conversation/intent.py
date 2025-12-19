"""Intent detection for chat messages

Infers user intent (timing, compare, advice, etc.) and time context
using lightweight regex/keyword heuristics (no LLM needed).
"""

import re
from typing import Literal, Dict, Any

TimeContext = Literal["past", "present", "future", "timeless"]
Intent = Literal["compare", "timing", "explain", "advice", "predict", "reflect"]


def detect_time_context(text: str) -> TimeContext:
    """
    Infer time context from text using keyword patterns.
    
    Returns one of: "past", "present", "future", "timeless"
    
    Args:
        text: User message or question
        
    Returns:
        Time context string
    """
    if not text:
        return "timeless"
    
    msg_lower = text.lower()
    
    # Future indicators (higher priority)
    future_patterns = [
        r"\bwill\b",
        r"\bshould i\b",
        r"\bshould we\b",
        r"\bcoming\b",
        r"\bnext\s+(?:year|month|week|day)",
        r"\bin\s+20[2-9][0-9]",  # in 2020+
        r"\bstart\b.*\bnow\b",
        r"\bbegin\b.*\bnow\b",
        r"\bwhen\s+(?:will|should|can|would)",
        r"\btiming\b",
        r"\bwhen\s+is\s+(?:best|good|favorable|suitable)",
        r"\bin\s+the\s+future\b",
        r"\bforecas[t|e]",
        r"\bpredic[t|ion]",
        r"\blooking\s+ahead\b",
        r"\bgood\s+time\s+(?:to|for)",
        r"\bauspicious\b",
        r"\bop(?:port|tim)unit",
        r"\bchallenge\s+ahead\b",
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
        r"\bwas\b.*\s+(?:reason|cause)",
        r"\bpast\b",
        r"\bhistory\b",
        r"\bretrospective\b",
        r"\blooking\s+back\b",
        r"\brecent\b",
        r"\blast\s+(?:few|several)\s+(?:months|years)",
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
        r"\bright\s+now\b",
        r"\bthese\s+days\b",
    ]
    
    for pattern in present_patterns:
        if re.search(pattern, msg_lower):
            return "present"
    
    return "timeless"


def detect_intent(text: str) -> Intent:
    """
    Detect user intent from message text.
    
    Returns one of: "compare", "timing", "explain", "advice", "predict", "reflect"
    
    Args:
        text: User message or question
        
    Returns:
        Intent string
    """
    if not text:
        return "reflect"
    
    msg_lower = text.lower()
    
    # Comparison/choice: "vs", "which is better", "should I pick"
    compare_patterns = [
        r"\bvs\.?\b",
        r"\bversus\b",
        r"\bwhich\s+(?:is|would|should)\s+(?:be|i)",
        r"\bwhich\s+(?:path|option|choice)",
        r"\bshould\s+i\s+(?:choose|pick|go\s+with)",
        r"\bbetter.*(?:or|between)",
        r"\bcompare\b",
        r"\bdifferent\s+(?:between|from)",
        r"\bpros\s+and\s+cons\b",
    ]
    
    for pattern in compare_patterns:
        if re.search(pattern, msg_lower):
            return "compare"
    
    # Timing/when: "when", "best time", "timing", "good time"
    timing_patterns = [
        r"\bwhen\s+(?:should|will|is)\b",
        r"\bwhen\s+is\s+(?:best|good|favorable|suitable)",
        r"\btiming\b",
        r"\bauspicious\s+(?:time|window|period|date)",
        r"\bgood\s+time\s+(?:to|for)",
        r"\bbest\s+(?:time|period|window)",
        r"\bshould\s+i\s+(?:start|begin|launch|wait)",
        r"\bwait\b",
        r"\bdelay\b",
    ]
    
    for pattern in timing_patterns:
        if re.search(pattern, msg_lower):
            return "timing"
    
    # Prediction/forecast: "predict", "forecast", "what will"
    predict_patterns = [
        r"\bpredict\b",
        r"\bforecast\b",
        r"\bwill\s+(?:i|we)\b",
        r"\bwhat\s+will\s+(?:happen|occur)",
        r"\bchances\b",
        r"\blikelihood\b",
        r"\bsuccess\b.*\bchance",
    ]
    
    for pattern in predict_patterns:
        if re.search(pattern, msg_lower):
            return "predict"
    
    # Explain/understand: "why", "how", "what does", "explain"
    explain_patterns = [
        r"\bwhy\b",
        r"\bhow\b(?!\s+(?:did|will))",  # "how did" is past, not explain
        r"\bwhat\s+(?:does|is)\b",
        r"\bexplain\b",
        r"\bmeaning\s+of\b",
        r"\binterpret\b",
        r"\bsignificance\b",
        r"\bunderstand\b",
    ]
    
    for pattern in explain_patterns:
        if re.search(pattern, msg_lower):
            return "explain"
    
    # Advice/guidance: "advise", "suggest", "recommend", "should I"
    advice_patterns = [
        r"\badvise\b",
        r"\bsuggest\b",
        r"\brecommend\b",
        r"\bshould\s+i\b",
        r"\bshould\s+we\b",
        r"\bremedy\b",
        r"\bhow\s+can\s+i\b",
        r"\bwhat\s+can\s+i\b",
        r"\bactions?\s+(?:i|we|should)",
        r"\bguidance\b",
        r"\bhelp\b",
    ]
    
    for pattern in advice_patterns:
        if re.search(pattern, msg_lower):
            return "advice"
    
    # Default to reflect (general inquiry/reflection)
    return "reflect"


def detect_intent_and_context(text: str) -> Dict[str, str]:
    """
    Detect both intent and time context in one call.
    
    Args:
        text: User message or question
        
    Returns:
        Dict with 'time_context' and 'intent' keys
    """
    return {
        'time_context': detect_time_context(text),
        'intent': detect_intent(text)
    }
