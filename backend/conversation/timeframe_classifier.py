"""
Timeframe Classifier for NIRO
Detects time horizons from user questions to provide context-relevant readings.
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def classify_timeframe(user_question: str) -> Dict[str, any]:
    """
    Classify the timeframe from user question.
    
    Detects phrases like:
    - "this month", "next month", "next few months"
    - "this year", "next year", "next 2 years"
    - "long term", "immediate", "near future"
    
    Args:
        user_question: User's question text
        
    Returns:
        Dict with:
        - type: "days", "weeks", "months", "years", "default"
        - value: numeric value (e.g., 3 for "next 3 months")
        - horizon_months: normalized to months for easy filtering (default: 12)
        - description: human-readable description
    """
    question_lower = user_question.lower()
    
    # PAST timeframe patterns - check these first!
    past_patterns = [
        # Past months
        (r'(last|past|previous)\s+(\d+)(-|\s+to\s+)?(\d+)?\s+months?', {"type": "past_months", "pattern": True}),
        (r'(last|past|previous)\s+month', {"type": "past_months", "value": 1, "horizon_months": -1}),
        (r'(last|past|previous)\s+few\s+months', {"type": "past_months", "value": 3, "horizon_months": -3}),
        (r'(last|past|previous)\s+several\s+months', {"type": "past_months", "value": 6, "horizon_months": -6}),
        # Past years
        (r'(last|past|previous)\s+(\d+)(-|\s+to\s+)?(\d+)?\s+years?', {"type": "past_years", "pattern": True}),
        (r'(last|past|previous)\s+year', {"type": "past_years", "value": 1, "horizon_months": -12}),
        (r'(last|past|previous)\s+few\s+years', {"type": "past_years", "value": 2, "horizon_months": -24}),
        # Generic past indicators
        (r'(what happened|what has happened|how did|why did)', {"type": "past", "value": 12, "horizon_months": -12}),
        (r'(in the past|historically|recently)', {"type": "past", "value": 6, "horizon_months": -6}),
        (r'(ago|back when|since then)', {"type": "past", "value": 12, "horizon_months": -12}),
    ]
    
    for pattern, result_template in past_patterns:
        match = re.search(pattern, question_lower)
        if match:
            if result_template.get("pattern"):
                # Extract numeric values from pattern
                groups = match.groups()
                value = None
                for g in groups:
                    if g and g.isdigit():
                        value = int(g)
                        break
                
                if value:
                    result_type = result_template["type"]
                    if result_type == "past_months":
                        horizon_months = -value
                    elif result_type == "past_years":
                        horizon_months = -value * 12
                    else:
                        horizon_months = -12
                    
                    return {
                        "type": result_type,
                        "value": value,
                        "horizon_months": horizon_months,
                        "description": f"Past {value} {'months' if 'month' in result_type else 'years'}",
                        "time_direction": "past"
                    }
            else:
                result = result_template.copy()
                result["description"] = f"Past timeframe"
                result["time_direction"] = "past"
                return result
    
    # FUTURE timeframe patterns (most specific first)
    patterns = [
        # Days
        (r'(this|next)\s+week', {"type": "weeks", "value": 1, "horizon_months": 0.25}),
        (r'(next|coming)\s+(\d+)\s+days?', {"type": "days", "pattern": True}),
        (r'(today|now|immediate|urgent)', {"type": "days", "value": 7, "horizon_months": 0.25}),
        
        # Months
        (r'(this|current)\s+month', {"type": "months", "value": 1, "horizon_months": 1}),
        (r'(next|coming)\s+month', {"type": "months", "value": 1, "horizon_months": 1}),
        (r'(next|coming)\s+(\d+)\s+months?', {"type": "months", "pattern": True}),
        (r'(next\s+)?few\s+months', {"type": "months", "value": 3, "horizon_months": 3}),
        (r'(next\s+)?several\s+months', {"type": "months", "value": 6, "horizon_months": 6}),
        
        # Years
        (r'(this|current)\s+year', {"type": "years", "value": 1, "horizon_months": 12}),
        (r'(next|coming)\s+year', {"type": "years", "value": 1, "horizon_months": 12}),
        (r'(next|coming)\s+(\d+)(-|\s+to\s+)?(\d+)?\s+years?', {"type": "years", "pattern": True}),
        (r'(next\s+)?few\s+years', {"type": "years", "value": 2, "horizon_months": 24}),
        (r'long\s+term', {"type": "years", "value": 5, "horizon_months": 60}),
    ]
    
    for pattern, result_template in patterns:
        match = re.search(pattern, question_lower)
        if match:
            if result_template.get("pattern"):
                # Extract numeric value from pattern
                groups = match.groups()
                value = None
                
                # Find the numeric group
                for g in groups:
                    if g and g.isdigit():
                        value = int(g)
                        break
                
                if value:
                    result_type = result_template["type"]
                    
                    # Calculate horizon_months
                    if result_type == "days":
                        horizon_months = round(value / 30, 1)
                    elif result_type == "months":
                        horizon_months = value
                    elif result_type == "years":
                        horizon_months = value * 12
                    else:
                        horizon_months = 12
                    
                    result = {
                        "type": result_type,
                        "value": value,
                        "horizon_months": horizon_months,
                        "description": f"Next {value} {result_type}"
                    }
                    logger.info(f"Detected timeframe: {result['description']} ({horizon_months} months)")
                    return result
            else:
                # Use template directly
                result = {
                    "type": result_template["type"],
                    "value": result_template["value"],
                    "horizon_months": result_template["horizon_months"],
                    "description": f"Next {result_template['value']} {result_template['type']}"
                }
                logger.info(f"Detected timeframe: {result['description']} ({result['horizon_months']} months)")
                return result
    
    # Default: 12-month horizon
    logger.info("No specific timeframe detected -> using default 12-month horizon")
    return {
        "type": "default",
        "value": 12,
        "horizon_months": 12,
        "description": "Next 12 months (default)"
    }


def get_timeframe_filter_date(timeframe: Dict[str, any], now) -> any:
    """
    Get the end date for filtering based on timeframe.
    
    Args:
        timeframe: Result from classify_timeframe
        now: Current datetime
        
    Returns:
        datetime representing the end of the timeframe window
    """
    from datetime import timedelta
    
    horizon_months = timeframe.get("horizon_months", 12)
    
    # Approximate months as 30 days
    horizon_days = int(horizon_months * 30)
    
    end_date = now + timedelta(days=horizon_days)
    
    logger.debug(f"Timeframe filter: now -> {end_date} ({horizon_months} months)")
    return end_date
