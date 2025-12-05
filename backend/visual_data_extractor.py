"""
Visual Data Extractor
Extracts structured data from astrological interpretations and raw data
for frontend visualization (charts, timelines, heatmaps)
"""
import re
from typing import Dict, List, Any
from datetime import datetime, timedelta
from models import VisualData

class VisualDataExtractor:
    """Extract visual data from reports for chart generation"""
    
    def extract_visual_data(self, raw_json: Dict[str, Any], interpreted_text: str, report_type: str) -> VisualData:
        """
        Extract structured visual data from report
        
        Args:
            raw_json: Raw VedicAstroAPI data
            interpreted_text: AI-interpreted report text
            report_type: Type of report
        
        Returns:
            VisualData object with timeline, intensity, risk/opportunity windows
        """
        
        visual_data = VisualData()
        
        # Extract timeline events
        visual_data.timeline_events = self._extract_timeline_events(interpreted_text)
        
        # Calculate monthly intensity scores
        visual_data.monthly_intensity = self._calculate_monthly_intensity(interpreted_text)
        
        # Extract risk and opportunity windows
        visual_data.risk_windows = self._extract_risk_windows(interpreted_text)
        visual_data.opportunity_windows = self._extract_opportunity_windows(interpreted_text)
        
        # Extract planetary positions
        visual_data.planetary_positions = self._extract_planetary_positions(raw_json)
        
        return visual_data
    
    def _extract_timeline_events(self, text: str) -> List[Dict[str, Any]]:
        """Extract date-specific events from interpretation"""
        
        events = []
        
        # Pattern: Date Range: month day - month day, year
        # Example: "April 15 - May 30, 2026"
        date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*[-–]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*\d{1,2}(?:,?\s*\d{4})?'
        
        # Find all date mentions
        date_matches = re.finditer(date_pattern, text, re.IGNORECASE)
        
        for match in date_matches:
            date_str = match.group()
            # Get context around the date (50 chars before and after)
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 200)
            context = text[start:end]
            
            # Extract event type from context
            event_type = self._classify_event_type(context)
            
            # Extract severity/probability if present
            severity_match = re.search(r'(\d+)%', context)
            probability = int(severity_match.group(1)) if severity_match else None
            
            events.append({
                'date_range': date_str,
                'event_type': event_type,
                'description': context.strip(),
                'probability': probability,
                'severity': self._calculate_severity(context)
            })
        
        return events[:20]  # Limit to top 20 events
    
    def _classify_event_type(self, context: str) -> str:
        """Classify event type from context"""
        
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['promotion', 'career', 'job', 'professional', 'advancement']):
            return 'career'
        elif any(word in context_lower for word in ['health', 'illness', 'stress', 'vitality', 'medical']):
            return 'health'
        elif any(word in context_lower for word in ['love', 'relationship', 'marriage', 'partner', 'romance']):
            return 'relationship'
        elif any(word in context_lower for word in ['finance', 'wealth', 'money', 'income', 'debt']):
            return 'finance'
        elif any(word in context_lower for word in ['family', 'home', 'parent', 'relocation']):
            return 'family'
        else:
            return 'general'
    
    def _calculate_severity(self, context: str) -> str:
        """Calculate severity level from context"""
        
        context_lower = context.lower()
        
        # High severity indicators
        if any(word in context_lower for word in ['critical', 'severe', 'crisis', 'danger', 'accident', 'major risk']):
            return 'high'
        # Medium severity indicators
        elif any(word in context_lower for word in ['moderate', 'challenge', 'stress', 'conflict', 'difficulty']):
            return 'medium'
        # Positive indicators
        elif any(word in context_lower for word in ['opportunity', 'growth', 'success', 'favorable', 'auspicious']):
            return 'positive'
        else:
            return 'low'
    
    def _calculate_monthly_intensity(self, text: str) -> Dict[str, float]:
        """Calculate intensity score for each month (0-10 scale)"""
        
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        
        intensity_scores = {}
        
        for month in months:
            # Count mentions of the month
            mentions = len(re.findall(month, text, re.IGNORECASE))
            
            # Count risk/challenge words near month
            month_sections = re.finditer(f'{month}.*?(?={"|".join(months)}|$)', text, re.IGNORECASE | re.DOTALL)
            
            risk_score = 0
            positive_score = 0
            
            for section in month_sections:
                section_text = section.group().lower()
                
                # Risk indicators
                risk_score += len(re.findall(r'risk|stress|challenge|conflict|difficulty|crisis', section_text))
                
                # Positive indicators
                positive_score += len(re.findall(r'opportunity|growth|success|favorable|positive|breakthrough', section_text))
            
            # Calculate intensity (0-10 scale)
            # High risk = high intensity, high positive = medium-high intensity
            base_intensity = min(mentions * 2, 5)
            risk_intensity = min(risk_score * 0.8, 3)
            positive_intensity = min(positive_score * 0.5, 2)
            
            total_intensity = min(base_intensity + risk_intensity + positive_intensity, 10)
            
            intensity_scores[month] = round(total_intensity, 1)
        
        return intensity_scores
    
    def _extract_risk_windows(self, text: str) -> List[Dict[str, Any]]:
        """Extract identified risk windows"""
        
        risk_windows = []
        
        # Pattern for risk sections
        risk_patterns = [
            r'Risk Window.*?(?=###|$)',
            r'Caution.*?(?=###|$)',
            r'Danger.*?(?=###|$)',
            r'Alert.*?(?=###|$)',
            r'Warning.*?(?=###|$)'
        ]
        
        for pattern in risk_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                section = match.group()
                
                # Extract date range
                date_match = re.search(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*[-–]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*\d{1,2}', section)
                
                if date_match:
                    risk_windows.append({
                        'date_range': date_match.group(),
                        'type': self._classify_event_type(section),
                        'description': section[:200],
                        'severity': self._calculate_severity(section)
                    })
        
        return risk_windows[:10]  # Top 10 risks
    
    def _extract_opportunity_windows(self, text: str) -> List[Dict[str, Any]]:
        """Extract identified opportunity windows"""
        
        opportunity_windows = []
        
        # Pattern for opportunity sections
        opp_patterns = [
            r'Opportunity.*?(?=###|$)',
            r'Growth.*?(?=###|$)',
            r'Success.*?(?=###|$)',
            r'Breakthrough.*?(?=###|$)',
            r'Favorable.*?(?=###|$)'
        ]
        
        for pattern in opp_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            
            for match in matches:
                section = match.group()
                
                # Extract date range
                date_match = re.search(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}\s*[-–]\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)?\s*\d{1,2}', section)
                
                if date_match:
                    # Extract probability if present
                    prob_match = re.search(r'(\d+)%', section)
                    probability = int(prob_match.group(1)) if prob_match else None
                    
                    opportunity_windows.append({
                        'date_range': date_match.group(),
                        'type': self._classify_event_type(section),
                        'description': section[:200],
                        'probability': probability
                    })
        
        return opportunity_windows[:10]  # Top 10 opportunities
    
    def _extract_planetary_positions(self, raw_json: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key planetary positions for visualization"""
        
        if not raw_json or 'data' not in raw_json:
            return {}
        
        data = raw_json.get('data', {})
        
        # This structure depends on VedicAstroAPI response format
        # Extract relevant planetary data for charts
        planetary_data = {
            'chart_type': 'natal',
            'positions': []
        }
        
        # Add more extraction logic based on actual API response structure
        
        return planetary_data
