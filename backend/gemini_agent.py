import os
import time
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class GeminiAgent:
    """
    Gemini Agent Wrapper for Astro-Trust Engine
    Handles all interactions with Google Gemini API
    - Model A (gemini-pro): Complex tasks like code generation & interpretation
    - Model B (gemini-flash): Fast tasks like follow-up questions
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Model configurations
        self.pro_model_name = os.environ.get('GEMINI_PRO_MODEL', 'gemini-pro')
        self.flash_model_name = os.environ.get('GEMINI_FLASH_MODEL', 'gemini-flash')
        
        # Initialize models
        self.pro_model = genai.GenerativeModel(self.pro_model_name)
        self.flash_model = genai.GenerativeModel(self.flash_model_name)
        
        logger.info(f"GeminiAgent initialized with Pro: {self.pro_model_name}, Flash: {self.flash_model_name}")
    
    def _call_model(self, model: genai.GenerativeModel, prompt: str, temperature: float = 0.7, allow_fallback: bool = True) -> str:
        """Internal method to call Gemini model with quota fallback"""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8000,
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.candidates:
                return response.text
            else:
                logger.error(f"No candidates in response. Prompt feedback: {response.prompt_feedback}")
                raise Exception("No response generated from Gemini")
                
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a quota error and we can fallback
            if allow_fallback and ("ResourceExhausted" in error_msg or "quota" in error_msg.lower()):
                logger.warning(f"Quota exceeded for {model._model_name}, attempting fallback to Flash model...")
                
                # If Pro failed, try Flash
                if model == self.pro_model:
                    try:
                        logger.info("Falling back to gemini-2.5-flash...")
                        response = self.flash_model.generate_content(
                            prompt,
                            generation_config=generation_config
                        )
                        
                        if response.candidates:
                            logger.info("Successfully used Flash model as fallback")
                            return response.text
                    except Exception as fallback_error:
                        logger.error(f"Fallback to Flash also failed: {str(fallback_error)}")
                        raise
            
            logger.error(f"Error calling Gemini model: {error_msg}")
            raise
    
    
    def extract_json(self, prompt: str) -> Dict[str, Any]:
        """
        Call model and extract JSON from response
        
        Args:
            prompt: Prompt requesting JSON output
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        
        response = self._call_model(self.flash_model, prompt, temperature=0.1)
        
        # Clean response
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        # Parse JSON
        return json.loads(response)
    
    def health_check(self) -> bool:
        """Check if Gemini API is accessible"""
        try:
            # Simple test call
            self.flash_model.generate_content(
                "Hello",
                generation_config=genai.types.GenerationConfig(temperature=0.1, max_output_tokens=10)
            )
            return True
        except Exception:
            return False

    def generate_code(self, user_intent: str, api_docs: str, user_data: Dict[str, Any]) -> str:
        """
        Generate Python code using Gemini 2.5 Pro to fetch astrology data
        
        Args:
            user_intent: What the user wants (e.g., "Generate yearly prediction report")
            api_docs: VedicAstroAPI documentation for relevant endpoints
            user_data: User's birth details (dob, tob, lat, lon, etc.)
        
        Returns:
            str: Executable Python code string
        """
        prompt = f"""You are an expert Python engineer specializing in API integrations.

Your task: Write a complete, executable Python script that fetches astrology data from VedicAstroAPI.

**USER INTENT:**
{user_intent}

**USER DATA:**
- Date of Birth: {user_data.get('dob')}
- Time of Birth: {user_data.get('tob')}
- Latitude: {user_data.get('lat')}
- Longitude: {user_data.get('lon')}
- Timezone: {user_data.get('timezone', 5.5)}

**VEDICASTROAPI DOCUMENTATION:**
{api_docs}

**REQUIREMENTS:**
1. Use the `requests` library for HTTP calls
2. Use the API key from environment: `os.environ['VEDIC_API_KEY']`
3. Return data as a JSON-serializable dictionary assigned to a variable named `result`
4. Handle errors gracefully with try-except blocks
5. The script must be completely self-contained and executable
6. Import all required libraries at the top
7. DO NOT use async/await - use synchronous requests only
8. Store the final output in a variable called `result`

**OUTPUT FORMAT:**
Return ONLY the Python code, no explanations, no markdown formatting, no ```python``` tags.
The code must be ready to execute with exec().

EXAMPLE STRUCTURE:
```
import os
import requests

try:
    api_key = os.environ['VEDIC_API_KEY']
    base_url = os.environ['VEDIC_API_BASE_URL']
    
    # Example API call
    response = requests.get(
        f"{{base_url}}/horoscope/planet-details",
        params={{
            'api_key': api_key,
            'dob': '15/08/1990',  # Use forward slashes
            'tob': '14:30',
            'lat': 28.6139,
            'lon': 77.2090,
            'tz': 5.5
        }},
        timeout=15
    )
    response.raise_for_status()
    data = response.json()
    
    if data.get('status') == 200:
        result = {{"success": True, "data": data.get('response', {{}})}}
    else:
        result = {{"error": f"API returned status {{data.get('status')}}: {{data.get('response', 'Unknown error')}}"}}
        
except Exception as e:
    result = {{"error": str(e)}}
```

Now write the complete Python script:
"""
        
        logger.info(f"Generating code for user intent: {user_intent}")
        code = self._call_model(self.pro_model, prompt, temperature=0.3)
        
        # Clean up the code (remove markdown formatting if present)
        code = code.strip()
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        code = code.strip()
        
        logger.info("Code generation completed")
        return code
    
    def interpret_report(self, raw_json: Dict[str, Any], report_type: str, user_context: str = "") -> str:
        """
        Interpret raw astrology data into human-readable, data-driven report
        Uses Gemini 2.5 Pro with advanced anti-Barnum prompts
        
        Args:
            raw_json: Raw data from VedicAstroAPI
            report_type: Type of report (yearly_prediction, love_marriage, career_job, retro_check)
            user_context: Gender-neutral user context with occupation, relationship status
        
        Returns:
            str: Data-driven, specific interpretation following "Because Rule"
        """
        
        # Import advanced prompts
        from advanced_prompts import (
            get_yearly_prediction_advanced_prompt,
            get_love_marriage_advanced_prompt,
            get_career_job_advanced_prompt,
            get_retro_check_prompt
        )
        
        report_template_map = {
            "yearly_prediction": get_yearly_prediction_advanced_prompt(),
            "love_marriage": get_love_marriage_advanced_prompt(),
            "career_job": get_career_job_advanced_prompt(),
            "retro_check": get_retro_check_prompt()
        }
        
        template = report_template_map.get(report_type, report_template_map["yearly_prediction"])
        
        prompt = f"""You are an expert Vedic astrology analyst who provides DATA-DRIVEN, SPECIFIC interpretations.

{user_context}

{template}

**RAW ASTROLOGICAL DATA:**
```json
{raw_json}
```

**CRITICAL EXECUTION RULES:**
1. **The "Because Rule":** Every prediction MUST explain WHY (reference specific planetary factor)
2. **Date Precision:** Use exact date ranges (e.g., "June 10-July 15, 2026"), NOT vague terms like "mid-year"
3. **Probability Scores:** Include likelihood percentages (e.g., "78% probability")
4. **Anti-Barnum:** No generic statements. Every claim must be specific and verifiable
5. **Gender Neutrality:** Use correct pronouns from user context. No assumptions about family role or occupation
6. **Specific Sub-Headings:** Use data-driven titles (e.g., "The Promotion Window" not just "Career")
7. **Professional Tone:** Direct, honest, empowering but not sugar-coated

**STRUCTURE COMPLIANCE:**
Follow the exact section structure provided in the template above. Do not skip sections.

Write the complete interpretation now:
"""
        
        logger.info(f"Interpreting {report_type} report")
        interpretation = self._call_model(self.pro_model, prompt, temperature=0.7)
        logger.info("Report interpretation completed")
        
        return interpretation
    
    def clarify_question(self, original_report: str, user_question: str) -> str:
        """
        Answer follow-up questions about a generated report
        Uses Gemini Flash for fast, cost-effective responses
        
        Args:
            original_report: The previously generated report text
            user_question: User's clarification question
        
        Returns:
            str: Answer to the question
        """
        prompt = f"""You are a compassionate Vedic astrology expert answering a follow-up question about a report.

**ORIGINAL REPORT:**
{original_report}

**USER'S QUESTION:**
{user_question}

**INSTRUCTIONS:**
- Answer based only on the information in the original report
- If the report doesn't contain the answer, politely explain that additional analysis would be needed
- Be concise but warm and helpful
- Provide specific references to the report where relevant

Your answer:
"""
        
        logger.info(f"Clarifying question: {user_question[:50]}...")
        answer = self._call_model(self.flash_model, prompt, temperature=0.5)
        logger.info("Clarification completed")
        
        return answer
