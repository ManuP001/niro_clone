"""
NIRO Chat Agent
AI-powered Vedic Astrology chat agent for NIRO
"""

import os
import logging
from typing import List, Optional, Tuple
from datetime import datetime

from niro_models import NiroReply, SuggestedAction, NiroChatResponse

logger = logging.getLogger(__name__)


class NiroChatAgent:
    """
    NIRO AI Chat Agent for Vedic Astrology readings
    
    Handles conversation flow, birth detail extraction, and generates
    structured responses with Summary, Reasons, and Remedies.
    """
    
    def __init__(self):
        """Initialize NIRO chat agent with LLM integration"""
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Conversation context storage (in production, use Redis/DB)
        self.sessions = {}
        
        # Action mappings
        self.action_configs = {
            'focus_career': {
                'focus': 'career',
                'mode': 'FOCUS_READING',
                'prompt_hint': 'career, profession, work life, and professional growth'
            },
            'focus_relationship': {
                'focus': 'relationship',
                'mode': 'FOCUS_READING',
                'prompt_hint': 'relationships, love, marriage, and partnerships'
            },
            'focus_health': {
                'focus': 'health',
                'mode': 'FOCUS_READING',
                'prompt_hint': 'health, wellness, and physical well-being'
            },
            'past_themes': {
                'focus': None,
                'mode': 'PAST_THEMES',
                'prompt_hint': 'patterns and themes from the past 2 years'
            },
            'daily_guidance': {
                'focus': None,
                'mode': 'DAILY_GUIDANCE',
                'prompt_hint': "today's cosmic influences and guidance"
            }
        }
    
    def _get_llm_response(self, prompt: str, system_prompt: str = None) -> str:
        """Get response from LLM (Gemini with OpenAI fallback)"""
        
        # Try Gemini first
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
                
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                logger.warning(f"Gemini failed: {e}, trying OpenAI fallback")
        
        # OpenAI fallback
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_key)
                
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI also failed: {e}")
        
        # Fallback to template response
        return None
    
    def _parse_structured_response(self, llm_response: str) -> Tuple[str, List[str], List[str]]:
        """Parse LLM response into summary, reasons, and remedies"""
        
        if not llm_response:
            return (
                "I'm analyzing the cosmic patterns...",
                ["The stars are aligning for your reading"],
                []
            )
        
        summary = ""
        reasons = []
        remedies = []
        
        current_section = None
        lines = llm_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            lower_line = line.lower()
            
            # Detect section headers
            if 'summary' in lower_line and ':' in line:
                current_section = 'summary'
                # Extract content after colon if on same line
                after_colon = line.split(':', 1)[1].strip()
                if after_colon:
                    summary = after_colon
                continue
            elif 'reason' in lower_line and ':' in line:
                current_section = 'reasons'
                continue
            elif 'remed' in lower_line and ':' in line:
                current_section = 'remedies'
                continue
            
            # Add content to appropriate section
            if current_section == 'summary':
                if summary:
                    summary += ' ' + line
                else:
                    summary = line
            elif current_section == 'reasons':
                # Clean up bullet points
                clean_line = line.lstrip('- •*0123456789.)')
                if clean_line.strip():
                    reasons.append(clean_line.strip())
            elif current_section == 'remedies':
                clean_line = line.lstrip('- •*0123456789.)')
                if clean_line.strip():
                    remedies.append(clean_line.strip())
            elif not current_section and line:
                # Default to summary if no section detected yet
                if summary:
                    summary += ' ' + line
                else:
                    summary = line
        
        # Ensure we have at least summary
        if not summary:
            summary = llm_response[:500]
        
        return summary, reasons, remedies
    
    def _get_follow_up_actions(self, mode: str, focus: Optional[str]) -> List[SuggestedAction]:
        """Get suggested follow-up actions based on context"""
        
        actions = []
        
        if mode == 'WELCOME' or mode == 'GENERAL':
            actions = [
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='past_themes', label='Past 2 years'),
                SuggestedAction(id='daily_guidance', label='Daily guidance')
            ]
        elif mode == 'FOCUS_READING':
            # Suggest other focus areas
            other_focuses = {
                'career': [
                    SuggestedAction(id='focus_relationship', label='Relationships'),
                    SuggestedAction(id='ask_timing', label='Best timing for changes'),
                    SuggestedAction(id='deep_dive', label='Go deeper on this')
                ],
                'relationship': [
                    SuggestedAction(id='focus_career', label='Career'),
                    SuggestedAction(id='compatibility', label='Compatibility insights'),
                    SuggestedAction(id='deep_dive', label='Go deeper on this')
                ],
                'health': [
                    SuggestedAction(id='focus_career', label='Career'),
                    SuggestedAction(id='wellness_tips', label='Wellness recommendations'),
                    SuggestedAction(id='deep_dive', label='Go deeper on this')
                ]
            }
            actions = other_focuses.get(focus, [
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='daily_guidance', label='Daily guidance')
            ])
        elif mode == 'PAST_THEMES':
            actions = [
                SuggestedAction(id='future_outlook', label='Future 6 months'),
                SuggestedAction(id='focus_career', label='Career insights'),
                SuggestedAction(id='focus_relationship', label='Relationships')
            ]
        elif mode == 'DAILY_GUIDANCE':
            actions = [
                SuggestedAction(id='weekly_outlook', label='This week'),
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships')
            ]
        else:
            actions = [
                SuggestedAction(id='focus_career', label='Career'),
                SuggestedAction(id='focus_relationship', label='Relationships'),
                SuggestedAction(id='daily_guidance', label='Daily guidance')
            ]
        
        return actions
    
    def process_message(
        self,
        session_id: str,
        message: str,
        action_id: Optional[str] = None
    ) -> NiroChatResponse:
        """
        Process a user message and generate NIRO response
        
        Args:
            session_id: Unique session identifier
            message: User message text
            action_id: Optional action ID if user clicked a chip
            
        Returns:
            NiroChatResponse with structured reply and suggested actions
        """
        
        # Determine mode and focus from action or message
        mode = 'GENERAL'
        focus = None
        prompt_hint = 'general life guidance'
        
        if action_id and action_id in self.action_configs:
            config = self.action_configs[action_id]
            mode = config['mode']
            focus = config['focus']
            prompt_hint = config['prompt_hint']
        else:
            # Detect intent from message
            message_lower = message.lower()
            if any(word in message_lower for word in ['career', 'job', 'work', 'profession', 'business']):
                mode = 'FOCUS_READING'
                focus = 'career'
                prompt_hint = 'career and professional life'
            elif any(word in message_lower for word in ['love', 'relationship', 'marriage', 'partner', 'dating']):
                mode = 'FOCUS_READING'
                focus = 'relationship'
                prompt_hint = 'love and relationships'
            elif any(word in message_lower for word in ['health', 'wellness', 'body', 'fitness']):
                mode = 'FOCUS_READING'
                focus = 'health'
                prompt_hint = 'health and wellness'
            elif any(word in message_lower for word in ['past', 'previous', 'years ago', 'history']):
                mode = 'PAST_THEMES'
                prompt_hint = 'past patterns and themes'
            elif any(word in message_lower for word in ['today', 'daily', 'guidance', 'now']):
                mode = 'DAILY_GUIDANCE'
                prompt_hint = "today's guidance"
        
        # Generate structured response using LLM
        system_prompt = """You are NIRO, a wise and compassionate Vedic astrology guide. 
You provide insights using traditional Jyotish wisdom in a warm, accessible way.

IMPORTANT: Structure your response in exactly this format:

SUMMARY:
[Write a 2-3 sentence overview of the main insight]

REASONS:
- [First astrological reason or influence]
- [Second astrological reason or influence]
- [Third astrological reason or influence]

REMEDIES:
- [First practical remedy or suggestion]
- [Second practical remedy or suggestion]

Keep your language warm and encouraging. Reference planets, houses, and nakshatras where appropriate.
If the user hasn't shared birth details, gently ask for them while still providing general guidance."""
        
        user_prompt = f"""User message: "{message}"

Focus area: {prompt_hint}
Reading mode: {mode}

Provide a structured Vedic astrology response with Summary, Reasons, and Remedies.
If this is about {prompt_hint}, provide specific insights for that area.
Keep the response concise but meaningful."""
        
        # Get LLM response
        llm_response = self._get_llm_response(user_prompt, system_prompt)
        
        # Parse into structured format
        summary, reasons, remedies = self._parse_structured_response(llm_response)
        
        # Build reply
        reply = NiroReply(
            rawText=llm_response,
            summary=summary,
            reasons=reasons if reasons else [
                "The cosmic energies are currently in flux",
                "Your personal planetary period is showing interesting patterns",
                "The current transits suggest a time of growth"
            ],
            remedies=remedies
        )
        
        # Get suggested follow-up actions
        suggested_actions = self._get_follow_up_actions(mode, focus)
        
        return NiroChatResponse(
            reply=reply,
            mode=mode,
            focus=focus,
            suggestedActions=suggested_actions
        )


# Singleton instance
niro_agent = NiroChatAgent()
