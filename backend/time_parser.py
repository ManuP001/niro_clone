"""
Smart Time Parser
Handles flexible time input formats and normalizes to 24-hour format
"""
import re
from typing import Tuple, Optional

class TimeParser:
    """Parse and normalize various time input formats"""
    
    def parse_time(self, time_input: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Parse flexible time input and return normalized 24-hour format
        
        Args:
            time_input: User's time input (various formats)
        
        Returns:
            Tuple of (success, normalized_time_24h, error_message)
            - success: True if parsing succeeded
            - normalized_time_24h: Time in HH:MM format (24-hour)
            - error_message: Helpful error or suggestion if parsing failed
        
        Examples:
            "2:35 PM" -> (True, "14:35", None)
            "1435" -> (True, "14:35", None)
            "2pm" -> (True, "14:00", None)
            "0235" -> (True, "02:35", None)
            "830" -> (False, None, "Ambiguous: Did you mean 08:30 AM or 08:30 PM?")
        """
        
        if not time_input:
            return False, None, "Time is required"
        
        time_input = time_input.strip()
        
        # Pattern 1: 12-hour with AM/PM (e.g., "2:35 PM", "2.35pm", "2 35 PM")
        pattern_12h = r'^(\d{1,2})[\s:.\-,]*(\d{2})?\s*(am|pm|a\.m\.|p\.m\.)?\s*$'
        match_12h = re.match(pattern_12h, time_input, re.IGNORECASE)
        
        if match_12h:
            hour = int(match_12h.group(1))
            minute = int(match_12h.group(2)) if match_12h.group(2) else 0
            meridiem = match_12h.group(3).lower() if match_12h.group(3) else None
            
            # Validate minutes
            if minute > 59:
                return False, None, f"Invalid minutes: {minute}. Minutes must be 0-59."
            
            # Handle meridiem (AM/PM)
            if meridiem:
                meridiem = meridiem.replace('.', '').replace(' ', '')
                
                if hour < 1 or hour > 12:
                    return False, None, f"Invalid hour for 12-hour format: {hour}. Must be 1-12."
                
                # Convert to 24-hour
                if meridiem in ['am', 'a']:
                    if hour == 12:
                        hour = 0  # 12 AM = 00:00
                else:  # PM
                    if hour != 12:
                        hour += 12  # Add 12 for PM (except 12 PM stays 12)
                
                return True, f"{hour:02d}:{minute:02d}", None
            else:
                # No AM/PM specified
                if hour >= 0 and hour <= 23:
                    # Could be 24-hour format
                    return True, f"{hour:02d}:{minute:02d}", None
                elif hour >= 1 and hour <= 12:
                    # Ambiguous - could be AM or PM
                    return False, None, f"Ambiguous time: {time_input}. Did you mean {hour:02d}:{minute:02d} AM or {hour:02d}:{minute:02d} PM? Please add AM/PM."
                else:
                    return False, None, f"Invalid hour: {hour}. Must be 0-23 (24-hour) or 1-12 with AM/PM."
        
        # Pattern 2: 4-digit format (e.g., "1435", "0235")
        pattern_4digit = r'^(\d{4})$'
        match_4digit = re.match(pattern_4digit, time_input)
        
        if match_4digit:
            digits = match_4digit.group(1)
            hour = int(digits[:2])
            minute = int(digits[2:])
            
            if hour > 23:
                return False, None, f"Invalid hour: {hour}. Must be 0-23 for 24-hour format."
            if minute > 59:
                return False, None, f"Invalid minutes: {minute}. Must be 0-59."
            
            return True, f"{hour:02d}:{minute:02d}", None
        
        # Pattern 3: 3-digit format (e.g., "830", "235")
        pattern_3digit = r'^(\d{3})$'
        match_3digit = re.match(pattern_3digit, time_input)
        
        if match_3digit:
            digits = match_3digit.group(1)
            hour = int(digits[0])
            minute = int(digits[1:])
            
            if minute > 59:
                return False, None, f"Invalid minutes: {minute}. Must be 0-59."
            
            # Ambiguous - could be AM or PM
            return False, None, f"Ambiguous time: {time_input}. Did you mean {hour:02d}:{minute:02d} AM or {hour:02d}:{minute:02d} PM? Please add AM/PM or use 4-digit format (0{digits})."
        
        # Pattern 4: Hour only (e.g., "2pm", "14", "2 PM")
        pattern_hour = r'^(\d{1,2})\s*(am|pm|a\.m\.|p\.m\.)?$'
        match_hour = re.match(pattern_hour, time_input, re.IGNORECASE)
        
        if match_hour:
            hour = int(match_hour.group(1))
            meridiem = match_hour.group(2).lower() if match_hour.group(2) else None
            
            if meridiem:
                meridiem = meridiem.replace('.', '').replace(' ', '')
                
                if hour < 1 or hour > 12:
                    return False, None, f"Invalid hour for 12-hour format: {hour}. Must be 1-12."
                
                # Convert to 24-hour
                if meridiem in ['am', 'a']:
                    if hour == 12:
                        hour = 0
                else:  # PM
                    if hour != 12:
                        hour += 12
                
                return True, f"{hour:02d}:00", None
            else:
                # No AM/PM
                if 0 <= hour <= 23:
                    return True, f"{hour:02d}:00", None
                elif 1 <= hour <= 12:
                    return False, None, f"Ambiguous time: {hour}:00. Did you mean {hour:02d}:00 AM or {hour:02d}:00 PM? Please add AM/PM."
                else:
                    return False, None, f"Invalid hour: {hour}."
        
        # No pattern matched
        return False, None, f"Invalid time format: '{time_input}'. Try formats like '2:35 PM', '14:35', or '1435'."
    
    def convert_to_display_format(self, time_24h: str) -> str:
        """
        Convert 24-hour format to friendly 12-hour display
        
        Args:
            time_24h: Time in HH:MM format
        
        Returns:
            Time in 12-hour format with AM/PM
        """
        try:
            hour, minute = map(int, time_24h.split(':'))
            
            meridiem = 'AM' if hour < 12 else 'PM'
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            
            return f"{display_hour}:{minute:02d} {meridiem}"
        except:
            return time_24h
