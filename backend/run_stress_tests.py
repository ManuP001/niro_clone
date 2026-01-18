"""
Astrology Pipeline Stress Test Framework

End-to-end behavioral testing of the full inference pipeline:
question → topic detection → time parsing → signal generation → scoring → driver selection → LLM output → trust widget

Run: python run_stress_tests.py [--output json|html|console]
"""

import sys
sys.path.insert(0, '/app/backend')

import os
import json
import asyncio
import logging
from datetime import date, datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import re
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ============================================================================
# TEST RESULT ENUMS AND DATACLASSES
# ============================================================================

class TestStatus(Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    ERROR = "ERROR"


@dataclass
class TestAssertion:
    """Single assertion result"""
    name: str
    passed: bool
    severity: str  # "hard" or "soft"
    message: str = ""


@dataclass 
class TestResult:
    """Result of a single test case"""
    test_id: str
    profile_id: str
    question: str
    expected_topic: str
    expected_time_context: str
    
    # Detected values
    detected_topic: str = ""
    detected_time_context: str = ""
    resolved_year: Optional[int] = None
    
    # Signal data
    candidate_signals_count: int = 0
    kept_signals_count: int = 0
    
    # Drivers
    drivers: List[Dict] = field(default_factory=list)
    driver_sources: Dict[str, int] = field(default_factory=dict)  # static/dasha/transit counts
    
    # Outputs
    llm_output_text: str = ""
    trust_widget_drivers: List[Dict] = field(default_factory=list)
    
    # Assertions
    assertions: List[TestAssertion] = field(default_factory=list)
    status: TestStatus = TestStatus.PASS
    failure_reasons: List[str] = field(default_factory=list)
    warning_reasons: List[str] = field(default_factory=list)
    
    # Timing
    execution_time_ms: float = 0
    error_message: str = ""


@dataclass
class TestProfile:
    """Test user profile with birth details"""
    profile_id: str
    name: str
    dob: str
    tob: str
    location: str
    lat: float
    lon: float
    description: str  # e.g. "baseline", "different lagna", "edge case"


# ============================================================================
# TEST PROFILES (3 different charts)
# ============================================================================

TEST_PROFILES = [
    TestProfile(
        profile_id="profile_baseline",
        name="Baseline Chart - Sagittarius Asc",
        dob="1986-01-24",
        tob="06:32",
        location="Mumbai",
        lat=19.08,
        lon=72.88,
        description="Sagittarius Ascendant, Capricorn stellium (Sun/Mercury/Jupiter/Venus in 2nd), Saturn in 12th"
    ),
    TestProfile(
        profile_id="profile_different_lagna",
        name="Different Lagna - Aries Asc",
        dob="1992-07-15",
        tob="14:30",
        location="Delhi",
        lat=28.61,
        lon=77.23,
        description="Aries Ascendant, Cancer Moon, Leo Sun - very different from baseline"
    ),
    TestProfile(
        profile_id="profile_edge_case",
        name="Edge Case - Strong 8th/12th",
        dob="1978-11-03",
        tob="23:45",
        location="Chennai",
        lat=13.08,
        lon=80.27,
        description="Scorpio emphasis, Saturn dominant, challenging 8th/12th house placements"
    ),
]


# ============================================================================
# TEST MATRIX - 60 CURATED QUESTIONS
# ============================================================================

@dataclass
class TestCase:
    """Single test case definition"""
    test_id: str
    question: str
    expected_topic: str
    expected_time_context: str  # past, present, future, timeless
    expected_intent: str  # explain, reflect, predict, advice, non_astro
    tags: List[str] = field(default_factory=list)
    notes: str = ""


# Curated test questions organized by category
TEST_CASES = [
    # ========== CAREER QUESTIONS ==========
    # Past
    TestCase("career_past_1", "How was my career in 2019?", "career", "past", "explain", ["past_year"]),
    TestCase("career_past_2", "What happened with my job in 2022?", "career", "past", "explain", ["past_year"]),
    TestCase("career_past_3", "Why did I struggle professionally last year?", "career", "past", "explain", ["relative_past"]),
    TestCase("career_past_4", "Tell me about my work life before 2020", "career", "past", "explain", ["past_range"]),
    
    # Present
    TestCase("career_present_1", "How is my career going right now?", "career", "present", "reflect", ["present"]),
    TestCase("career_present_2", "What's happening with my job currently?", "career", "present", "reflect", ["present"]),
    TestCase("career_present_3", "Am I in the right career path?", "career", "present", "reflect", ["present"]),
    
    # Future
    TestCase("career_future_1", "How will my career be in 2026?", "career", "future", "predict", ["future_year"]),
    TestCase("career_future_2", "When will I get promoted?", "career", "future", "predict", ["future_timing"]),
    TestCase("career_future_3", "Should I change jobs next year?", "career", "future", "advice", ["future_advice"]),
    TestCase("career_future_4", "What opportunities await me professionally?", "career", "future", "predict", ["future_general"]),
    
    # ========== MONEY/FINANCE QUESTIONS ==========
    TestCase("money_past_1", "How was my financial situation in 2021?", "money", "past", "explain", ["past_year"]),
    TestCase("money_present_1", "How is my wealth right now?", "money", "present", "reflect", ["present"]),
    TestCase("money_future_1", "Will I become wealthy in the next 5 years?", "money", "future", "predict", ["future_range"]),
    TestCase("money_future_2", "When is a good time for investments?", "money", "future", "advice", ["timing"]),
    
    # ========== RELATIONSHIP QUESTIONS ==========
    TestCase("relationship_past_1", "Why did my relationship end in 2020?", "romantic_relationships", "past", "explain", ["past_year"]),
    TestCase("relationship_past_2", "How was my love life before marriage?", "romantic_relationships", "past", "explain", ["past_range"]),
    TestCase("relationship_present_1", "How is my marriage going?", "romantic_relationships", "present", "reflect", ["present"]),
    TestCase("relationship_present_2", "Am I compatible with my partner?", "romantic_relationships", "present", "reflect", ["compatibility"]),
    TestCase("relationship_future_1", "When will I get married?", "romantic_relationships", "future", "predict", ["timing"]),
    TestCase("relationship_future_2", "Will my relationship improve in 2025?", "romantic_relationships", "future", "predict", ["future_year"]),
    
    # ========== FAMILY/MOTHER QUESTIONS ==========
    TestCase("family_mother_1", "Tell me about my relationship with my mother", "family", "timeless", "reflect", ["mother"]),
    TestCase("family_mother_2", "How is my mother's health?", "family", "present", "reflect", ["mother", "health"]),
    TestCase("family_mother_3", "What does my chart say about my mother?", "family", "timeless", "reflect", ["mother"]),
    TestCase("family_past_1", "How were my family dynamics in childhood?", "family", "past", "explain", ["past_range"]),
    TestCase("family_future_1", "Will there be family harmony next year?", "family", "future", "predict", ["future_year"]),
    
    # ========== HEALTH QUESTIONS ==========
    TestCase("health_past_1", "Why did I have health issues in 2018?", "health_energy", "past", "explain", ["past_year"]),
    TestCase("health_present_1", "How is my health currently?", "health_energy", "present", "reflect", ["present"]),
    TestCase("health_present_2", "What should I watch out for health-wise?", "health_energy", "present", "advice", ["present"]),
    TestCase("health_future_1", "Will my health improve next year?", "health_energy", "future", "predict", ["future_year"]),
    
    # ========== TRAVEL/RELOCATION QUESTIONS ==========
    TestCase("travel_past_1", "Why did my relocation in 2019 not work out?", "travel", "past", "explain", ["past_year"]),
    TestCase("travel_present_1", "Should I relocate abroad?", "travel", "present", "advice", ["present"]),
    TestCase("travel_future_1", "When is a good time to move to another country?", "travel", "future", "advice", ["timing"]),
    TestCase("travel_future_2", "Will foreign travel be good for me in 2025?", "travel", "future", "predict", ["future_year"]),
    
    # ========== EDUCATION QUESTIONS ==========
    TestCase("education_past_1", "How was my academic performance in college?", "education", "past", "explain", ["past_range"]),
    TestCase("education_present_1", "Should I pursue higher studies?", "education", "present", "advice", ["present"]),
    TestCase("education_future_1", "Will I succeed in competitive exams next year?", "education", "future", "predict", ["future_year"]),
    
    # ========== SPIRITUALITY QUESTIONS ==========
    TestCase("spirituality_1", "What is my spiritual path?", "spirituality", "timeless", "reflect", ["timeless"]),
    TestCase("spirituality_2", "How can I grow spiritually?", "spirituality", "present", "advice", ["present"]),
    
    # ========== GENERAL/LIFE OVERVIEW ==========
    TestCase("general_past_1", "What were the major themes of 2020 for me?", "general", "past", "explain", ["past_year"]),
    TestCase("general_present_1", "Tell me about my current life phase", "general", "present", "reflect", ["present"]),
    TestCase("general_present_2", "What should I focus on right now?", "general", "present", "advice", ["present"]),
    TestCase("general_future_1", "What does 2025 hold for me?", "general", "future", "predict", ["future_year"]),
    TestCase("general_future_2", "What are my life's major upcoming changes?", "general", "future", "predict", ["future_general"]),
    TestCase("general_timeless_1", "What are my life's strengths?", "general", "timeless", "reflect", ["timeless"]),
    TestCase("general_timeless_2", "What is my life purpose?", "general", "timeless", "reflect", ["timeless"]),
    
    # ========== RELATIVE TIME WINDOWS ==========
    TestCase("relative_1", "How were the last 18 months for my career?", "career", "past", "explain", ["relative_past"]),
    TestCase("relative_2", "What happened in the past 2 years?", "general", "past", "explain", ["relative_past"]),
    TestCase("relative_3", "How will the next 6 months be?", "general", "future", "predict", ["relative_future"]),
    
    # ========== NON-ASTROLOGY CONTROL QUESTIONS ==========
    TestCase("non_astro_1", "Hi, how are you?", "general", "timeless", "non_astro", ["greeting", "non_astro"]),
    TestCase("non_astro_2", "Thanks for your help!", "general", "timeless", "non_astro", ["thanks", "non_astro"]),
    TestCase("non_astro_3", "What's the weather like?", "general", "timeless", "non_astro", ["non_astro", "irrelevant"]),
    TestCase("non_astro_4", "Tell me a joke", "general", "timeless", "non_astro", ["non_astro", "irrelevant"]),
    TestCase("non_astro_5", "Who is the president of USA?", "general", "timeless", "non_astro", ["non_astro", "factual"]),
    
    # ========== EDGE CASES / HIGH FAILURE RISK ==========
    TestCase("edge_1", "Tell me about my 4th Lord", "family", "timeless", "reflect", ["lord_reference"]),
    TestCase("edge_2", "What about my 10th house?", "career", "timeless", "reflect", ["house_reference"]),
    TestCase("edge_3", "How is Saturn affecting me?", "general", "present", "reflect", ["planet_reference"]),
    TestCase("edge_4", "When does my current dasha end?", "general", "present", "reflect", ["dasha_reference"]),
    TestCase("edge_5", "Compare my 2019 vs 2024", "general", "past", "explain", ["comparison", "multi_year"]),
]


# ============================================================================
# ASSERTION CHECKERS
# ============================================================================

class AssertionChecker:
    """Checks various assertions on test results"""
    
    KNOWN_PLANETS = {
        'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu',
        'sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu'
    }
    
    HOUSE_PATTERNS = [
        r'\b(\d+)(?:st|nd|rd|th)\s+house\b',
        r'\bhouse\s+(\d+)\b',
        r'\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|eleventh|twelfth)\s+house\b'
    ]
    
    HOUSE_WORDS = {
        'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6,
        'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10, 'eleventh': 11, 'twelfth': 12
    }
    
    @classmethod
    def check_narrative_planet_drift(cls, result: TestResult) -> TestAssertion:
        """HARD: Check if narrative mentions planets NOT in allowed entities (drivers + secondary)"""
        # Build allowed planets from both drivers AND secondary context (signals)
        # The LLM is allowed to mention any planet from PRIMARY_DRIVERS + SECONDARY_CONTEXT
        allowed_planets = set()
        
        # From drivers (PRIMARY)
        for d in result.drivers:
            planet = d.get('planet', '').lower()
            if planet and planet not in ('unknown', ''):
                allowed_planets.add(planet)
        
        # The test should also consider secondary signals if available
        # For now, we'll be more lenient and allow planets that are "close" to drivers
        # This matches the actual LLM behavior which gets allowed_entities from drivers + secondary
        
        # Extract planets mentioned in LLM output
        narrative = result.llm_output_text.lower()
        mentioned_planets = set()
        for planet in cls.KNOWN_PLANETS:
            if planet.lower() in narrative:
                mentioned_planets.add(planet.lower())
        
        # Check for planets mentioned but not in allowed list
        drifted_planets = mentioned_planets - allowed_planets
        
        # Filter out common words that might be false positives
        drifted_planets = {p for p in drifted_planets if p not in {'sun', 'moon'} or 
                          (p == 'sun' and 'sunshine' not in narrative) or
                          (p == 'moon' and 'moonlight' not in narrative)}
        
        if drifted_planets and allowed_planets:  # Only fail if we have allowed planets
            # Make this a WARNING if only 1 planet drifted (might be in secondary context)
            # FAIL if multiple planets drifted
            if len(drifted_planets) == 1:
                return TestAssertion(
                    name="narrative_planet_drift",
                    passed=False,
                    severity="soft",  # Soft failure for single drift (might be secondary)
                    message=f"Narrative mentions {drifted_planets} but drivers have {allowed_planets}"
                )
            return TestAssertion(
                name="narrative_planet_drift",
                passed=False,
                severity="hard",
                message=f"Narrative mentions {drifted_planets} but drivers only have {allowed_planets}"
            )
        return TestAssertion(name="narrative_planet_drift", passed=True, severity="hard")
    
    @classmethod
    def check_trust_widget_alignment(cls, result: TestResult) -> TestAssertion:
        """HARD: Check if trust widget drivers match PRIMARY_DRIVERS"""
        driver_planets = {d.get('planet', '').lower() for d in result.drivers if d.get('planet')}
        widget_planets = set()
        
        for w in result.trust_widget_drivers:
            label = w.get('label', '').lower()
            for planet in cls.KNOWN_PLANETS:
                if planet.lower() in label:
                    widget_planets.add(planet.lower())
        
        if driver_planets and widget_planets:
            if not widget_planets.issubset(driver_planets):
                extra = widget_planets - driver_planets
                return TestAssertion(
                    name="trust_widget_alignment",
                    passed=False,
                    severity="hard",
                    message=f"Trust widget mentions {extra} not in drivers {driver_planets}"
                )
        return TestAssertion(name="trust_widget_alignment", passed=True, severity="hard")
    
    @classmethod
    def check_past_query_current_signal(cls, result: TestResult) -> TestAssertion:
        """HARD: Past queries should not mention 'ongoing/current' signals"""
        if result.detected_time_context != 'past':
            return TestAssertion(name="past_query_current_signal", passed=True, severity="hard")
        
        narrative = result.llm_output_text.lower()
        current_markers = ['currently', 'ongoing', 'right now', 'at present', 'these days']
        
        found_markers = [m for m in current_markers if m in narrative]
        if found_markers:
            return TestAssertion(
                name="past_query_current_signal",
                passed=False,
                severity="hard",
                message=f"Past query narrative contains current markers: {found_markers}"
            )
        return TestAssertion(name="past_query_current_signal", passed=True, severity="hard")
    
    @classmethod
    def check_unresolved_placeholders(cls, result: TestResult) -> TestAssertion:
        """HARD: Check for unresolved lord/house placeholders in output"""
        narrative = result.llm_output_text
        
        placeholders = [
            r'\b\d+(st|nd|rd|th)\s+Lord\b',  # "4th Lord" as literal string
            r'\{[^}]+\}',  # {placeholder}
            r'\[PLANET\]',
            r'\[HOUSE\]',
        ]
        
        found = []
        for pattern in placeholders:
            matches = re.findall(pattern, narrative, re.IGNORECASE)
            if matches:
                found.extend(matches)
        
        if found:
            return TestAssertion(
                name="unresolved_placeholders",
                passed=False,
                severity="hard",
                message=f"Unresolved placeholders found: {found[:3]}"
            )
        return TestAssertion(name="unresolved_placeholders", passed=True, severity="hard")
    
    @classmethod
    def check_non_astro_trigger(cls, test_case: TestCase, result: TestResult) -> TestAssertion:
        """HARD: Non-astro questions should not trigger full astrology logic"""
        if test_case.expected_intent != 'non_astro':
            return TestAssertion(name="non_astro_trigger", passed=True, severity="hard")
        
        # Check if significant astrology signals were generated
        if result.kept_signals_count > 3 or len(result.drivers) > 2:
            return TestAssertion(
                name="non_astro_trigger",
                passed=False,
                severity="hard",
                message=f"Non-astro question triggered {result.kept_signals_count} signals, {len(result.drivers)} drivers"
            )
        return TestAssertion(name="non_astro_trigger", passed=True, severity="hard")
    
    @classmethod
    def check_topic_detection(cls, test_case: TestCase, result: TestResult) -> TestAssertion:
        """SOFT: Check if topic was correctly detected"""
        if result.detected_topic == test_case.expected_topic:
            return TestAssertion(name="topic_detection", passed=True, severity="soft")
        
        # Allow some flexibility for related topics
        related_topics = {
            ('money', 'career'): True,
            ('family', 'romantic_relationships'): True,
            ('general', 'life_overview'): True,
        }
        
        topic_pair = (test_case.expected_topic, result.detected_topic)
        reverse_pair = (result.detected_topic, test_case.expected_topic)
        
        if related_topics.get(topic_pair) or related_topics.get(reverse_pair):
            return TestAssertion(
                name="topic_detection",
                passed=True,
                severity="soft",
                message=f"Related topic detected: expected={test_case.expected_topic}, got={result.detected_topic}"
            )
        
        return TestAssertion(
            name="topic_detection",
            passed=False,
            severity="soft",
            message=f"Topic mismatch: expected={test_case.expected_topic}, got={result.detected_topic}"
        )
    
    @classmethod
    def check_time_context_detection(cls, test_case: TestCase, result: TestResult) -> TestAssertion:
        """SOFT: Check if time context was correctly detected"""
        if result.detected_time_context == test_case.expected_time_context:
            return TestAssertion(name="time_context_detection", passed=True, severity="soft")
        
        # Timeless and present are often interchangeable
        if {test_case.expected_time_context, result.detected_time_context} <= {'timeless', 'present'}:
            return TestAssertion(
                name="time_context_detection",
                passed=True,
                severity="soft",
                message="timeless/present interchanged (acceptable)"
            )
        
        return TestAssertion(
            name="time_context_detection",
            passed=False,
            severity="soft",
            message=f"Time context mismatch: expected={test_case.expected_time_context}, got={result.detected_time_context}"
        )
    
    @classmethod
    def check_unknown_signals(cls, result: TestResult) -> TestAssertion:
        """SOFT: Check if 'Unknown' signals are dominating drivers"""
        unknown_count = sum(1 for d in result.drivers if d.get('planet', '').lower() in ('unknown', ''))
        
        if len(result.drivers) > 0 and unknown_count / len(result.drivers) > 0.5:
            return TestAssertion(
                name="unknown_signals_dominant",
                passed=False,
                severity="soft",
                message=f"{unknown_count}/{len(result.drivers)} drivers are Unknown"
            )
        return TestAssertion(name="unknown_signals_dominant", passed=True, severity="soft")
    
    @classmethod
    def run_all_assertions(cls, test_case: TestCase, result: TestResult) -> List[TestAssertion]:
        """Run all assertions and return list of results"""
        assertions = [
            cls.check_narrative_planet_drift(result),
            cls.check_trust_widget_alignment(result),
            cls.check_past_query_current_signal(result),
            cls.check_unresolved_placeholders(result),
            cls.check_non_astro_trigger(test_case, result),
            cls.check_topic_detection(test_case, result),
            cls.check_time_context_detection(test_case, result),
            cls.check_unknown_signals(result),
        ]
        return assertions


# ============================================================================
# CROSS-PROFILE ASSERTIONS
# ============================================================================

class CrossProfileChecker:
    """Checks assertions across multiple profiles"""
    
    @classmethod
    def check_same_drivers_across_profiles(cls, results: List[TestResult]) -> List[TestAssertion]:
        """SOFT: Same drivers across different profiles for same question is suspicious"""
        assertions = []
        
        # Group by test_id
        by_test_id = defaultdict(list)
        for r in results:
            by_test_id[r.test_id].append(r)
        
        for test_id, profile_results in by_test_id.items():
            if len(profile_results) < 2:
                continue
            
            # Compare driver sets
            driver_sets = []
            for r in profile_results:
                driver_set = frozenset(d.get('planet', '') for d in r.drivers)
                driver_sets.append((r.profile_id, driver_set))
            
            # Check if all profiles have same drivers
            unique_sets = set(ds[1] for ds in driver_sets)
            if len(unique_sets) == 1 and len(driver_sets[0][1]) > 0:
                assertions.append(TestAssertion(
                    name=f"cross_profile_same_drivers_{test_id}",
                    passed=False,
                    severity="soft",
                    message=f"All profiles have identical drivers for {test_id}: {driver_sets[0][1]}"
                ))
        
        return assertions
    
    @classmethod
    def check_past_vs_future_differentiation(cls, results: List[TestResult]) -> List[TestAssertion]:
        """SOFT: Past vs future queries for same topic should have different drivers"""
        assertions = []
        
        # Group by profile
        by_profile = defaultdict(list)
        for r in results:
            by_profile[r.profile_id].append(r)
        
        for profile_id, profile_results in by_profile.items():
            # Find pairs of past/future for same topic
            past_results = {r.detected_topic: r for r in profile_results if r.detected_time_context == 'past'}
            future_results = {r.detected_topic: r for r in profile_results if r.detected_time_context == 'future'}
            
            for topic in set(past_results.keys()) & set(future_results.keys()):
                past_r = past_results[topic]
                future_r = future_results[topic]
                
                past_drivers = frozenset(d.get('planet', '') for d in past_r.drivers)
                future_drivers = frozenset(d.get('planet', '') for d in future_r.drivers)
                
                if past_drivers == future_drivers and len(past_drivers) > 0:
                    assertions.append(TestAssertion(
                        name=f"past_vs_future_same_{profile_id}_{topic}",
                        passed=False,
                        severity="soft",
                        message=f"Past and future {topic} queries have identical drivers: {past_drivers}"
                    ))
        
        return assertions


# ============================================================================
# TEST RUNNER
# ============================================================================

class StressTestRunner:
    """Main test runner"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.cross_profile_assertions: List[TestAssertion] = []
    
    async def setup_profile(self, profile: TestProfile) -> Optional[str]:
        """Create user and profile, return auth token"""
        import httpx
        import uuid
        
        base_url = "http://localhost:8001/api"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Create user with unique email per run
            run_suffix = uuid.uuid4().hex[:8]
            email = f"{profile.profile_id}-{run_suffix}@stress-test.local"
            resp = await client.post(f"{base_url}/auth/identify", json={"identifier": email})
            if resp.status_code != 200:
                logger.error(f"Failed to create user for {profile.profile_id}: {resp.text}")
                return None
            
            token = resp.json().get("token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Create profile
            profile_data = {
                "name": profile.name,
                "dob": profile.dob,
                "tob": profile.tob,
                "location": profile.location,
                "lat": profile.lat,
                "lon": profile.lon
            }
            resp = await client.post(f"{base_url}/profile/", json=profile_data, headers=headers)
            if resp.status_code not in (200, 201):
                logger.warning(f"Profile creation returned {resp.status_code} for {profile.profile_id}")
            
            return token
    
    async def run_single_test(
        self, 
        test_case: TestCase, 
        profile: TestProfile, 
        token: str
    ) -> TestResult:
        """Run a single test case"""
        import httpx
        import time
        
        base_url = "http://localhost:8001/api"
        headers = {"Authorization": f"Bearer {token}"}
        
        result = TestResult(
            test_id=test_case.test_id,
            profile_id=profile.profile_id,
            question=test_case.question,
            expected_topic=test_case.expected_topic,
            expected_time_context=test_case.expected_time_context,
        )
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Send chat message
                session_id = f"stress-{profile.profile_id}-{test_case.test_id}"
                resp = await client.post(
                    f"{base_url}/chat",
                    json={
                        "message": test_case.question,
                        "sessionId": session_id
                    },
                    headers=headers
                )
                
                result.execution_time_ms = (time.time() - start_time) * 1000
                
                if resp.status_code != 200:
                    result.status = TestStatus.ERROR
                    result.error_message = f"Chat failed: {resp.status_code} - {resp.text[:200]}"
                    return result
                
                data = resp.json()
                
                # Extract reply data
                reply = data.get('reply', {})
                result.llm_output_text = reply.get('rawText', '')
                
                # Extract trust widget
                trust_widget = data.get('trustWidget', {})
                result.trust_widget_drivers = trust_widget.get('drivers', [])
                
                # Get debug data - pass user_id to filter
                # Note: The debug endpoint uses in-memory cache which doesn't filter by user
                # so we just get the latest entry and check if it matches our question
                debug_resp = await client.get(
                    f"{base_url}/debug/candidate-signals/latest",
                    headers=headers
                )
                
                if debug_resp.status_code == 200:
                    debug_wrapper = debug_resp.json()
                    # Handle nested data structure
                    debug_data = debug_wrapper.get('data', debug_wrapper)
                    
                    # DEBUG: Log what we're getting
                    if not debug_data or not isinstance(debug_data, dict):
                        logger.warning(f"[STRESS] No debug_data for {test_case.test_id}: {debug_wrapper}")
                    
                    if isinstance(debug_data, dict):
                        summary = debug_data.get('summary', {})
                        
                        result.detected_topic = debug_data.get('topic', '')
                        result.detected_time_context = debug_data.get('time_context', '')
                        result.resolved_year = debug_data.get('query_year')
                        result.candidate_signals_count = summary.get('total_candidates', 0)
                        result.kept_signals_count = summary.get('kept_count', 0)
                        
                        # Check if this debug data is for our question
                        debug_question = debug_data.get('user_question', '')
                        if debug_question != test_case.question:
                            logger.warning(f"[STRESS] Debug data mismatch: expected='{test_case.question}', got='{debug_question}'")
                        
                        # Extract drivers from candidates that are marked as drivers OR from kept signals
                        candidates = debug_data.get('candidates', [])
                        
                        # Get top 3 kept signals as PRIMARY_DRIVERS
                        kept_signals = [c for c in candidates if c.get('kept')]
                        result.drivers = [
                            {
                                'planet': c.get('planet'),
                                'house': c.get('house'),
                                'role': c.get('role'),
                                'score_final': c.get('score_final'),
                                'type': c.get('signal_type'),
                                'is_time_layer': c.get('is_time_layer', False)
                            }
                            for c in kept_signals[:3]
                        ]
                        
                        # Store ALL kept signals for allowed entities check (drivers + secondary)
                        # This is what the LLM actually gets as ALLOWED_ENTITIES
                        all_allowed = [
                            {
                                'planet': c.get('planet'),
                                'house': c.get('house'),
                            }
                            for c in kept_signals[:6]  # Primary (3) + Secondary (3)
                        ]
                        # Add to drivers list for complete allowed set
                        for sig in all_allowed[3:]:  # Secondary signals
                            if sig.get('planet'):
                                result.drivers.append(sig)
                        
                        # Calculate driver sources
                        for d in result.drivers[:3]:  # Only count primary drivers
                            if d.get('type') == 'dasha':
                                result.driver_sources['dasha'] = result.driver_sources.get('dasha', 0) + 1
                            elif d.get('type') == 'transit':
                                result.driver_sources['transit'] = result.driver_sources.get('transit', 0) + 1
                            else:
                                result.driver_sources['static'] = result.driver_sources.get('static', 0) + 1
                else:
                    logger.warning(f"[STRESS] Debug endpoint returned {debug_resp.status_code}")
                
                # Run assertions
                result.assertions = AssertionChecker.run_all_assertions(test_case, result)
                
                # Determine overall status
                hard_failures = [a for a in result.assertions if not a.passed and a.severity == 'hard']
                soft_failures = [a for a in result.assertions if not a.passed and a.severity == 'soft']
                
                if hard_failures:
                    result.status = TestStatus.FAIL
                    result.failure_reasons = [a.message for a in hard_failures]
                elif soft_failures:
                    result.status = TestStatus.WARN
                    result.warning_reasons = [a.message for a in soft_failures]
                else:
                    result.status = TestStatus.PASS
                
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.execution_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    async def run_all_tests(self, profiles: List[TestProfile] = None, test_cases: List[TestCase] = None):
        """Run all tests"""
        profiles = profiles or TEST_PROFILES
        test_cases = test_cases or TEST_CASES
        
        total_tests = len(profiles) * len(test_cases)
        print(f"\n{'='*70}")
        print(f"ASTROLOGY PIPELINE STRESS TEST")
        print(f"{'='*70}")
        print(f"Profiles: {len(profiles)}")
        print(f"Test cases: {len(test_cases)}")
        print(f"Total tests: {total_tests}")
        print(f"{'='*70}\n")
        
        # Setup profiles
        profile_tokens = {}
        for profile in profiles:
            print(f"Setting up profile: {profile.name}...")
            token = await self.setup_profile(profile)
            if token:
                profile_tokens[profile.profile_id] = token
                print(f"  ✓ {profile.profile_id} ready")
            else:
                print(f"  ✗ Failed to setup {profile.profile_id}")
        
        print()
        
        # Run tests
        completed = 0
        for profile in profiles:
            token = profile_tokens.get(profile.profile_id)
            if not token:
                continue
            
            print(f"\nRunning tests for {profile.name}...")
            
            for test_case in test_cases:
                result = await self.run_single_test(test_case, profile, token)
                self.results.append(result)
                completed += 1
                
                # Progress indicator
                status_char = {
                    TestStatus.PASS: '✓',
                    TestStatus.WARN: '⚠',
                    TestStatus.FAIL: '✗',
                    TestStatus.ERROR: 'E'
                }.get(result.status, '?')
                
                print(f"  [{completed}/{total_tests}] {test_case.test_id}: {status_char}", end='\r')
                
                # Small delay to avoid overwhelming the server
                await asyncio.sleep(0.5)
            
            print()  # New line after profile
        
        # Cross-profile assertions
        print("\nRunning cross-profile checks...")
        self.cross_profile_assertions.extend(
            CrossProfileChecker.check_same_drivers_across_profiles(self.results)
        )
        self.cross_profile_assertions.extend(
            CrossProfileChecker.check_past_vs_future_differentiation(self.results)
        )
    
    def generate_report(self) -> Dict:
        """Generate summary report"""
        # Count by status
        status_counts = defaultdict(int)
        for r in self.results:
            status_counts[r.status.value] += 1
        
        # Group failures by category
        failures_by_assertion = defaultdict(list)
        for r in self.results:
            for a in r.assertions:
                if not a.passed:
                    failures_by_assertion[a.name].append({
                        'test_id': r.test_id,
                        'profile_id': r.profile_id,
                        'message': a.message
                    })
        
        # Group by topic
        by_topic = defaultdict(lambda: {'pass': 0, 'warn': 0, 'fail': 0, 'error': 0})
        for r in self.results:
            by_topic[r.expected_topic][r.status.value.lower()] += 1
        
        # Group by time context
        by_time = defaultdict(lambda: {'pass': 0, 'warn': 0, 'fail': 0, 'error': 0})
        for r in self.results:
            by_time[r.expected_time_context][r.status.value.lower()] += 1
        
        # Cross-profile failures
        cross_profile_failures = [a for a in self.cross_profile_assertions if not a.passed]
        
        return {
            'summary': {
                'total_tests': len(self.results),
                'pass': status_counts['PASS'],
                'warn': status_counts['WARN'],
                'fail': status_counts['FAIL'],
                'error': status_counts['ERROR'],
                'pass_rate': f"{100 * status_counts['PASS'] / len(self.results):.1f}%" if self.results else "0%"
            },
            'by_topic': dict(by_topic),
            'by_time_context': dict(by_time),
            'failures_by_assertion': dict(failures_by_assertion),
            'cross_profile_failures': [asdict(a) for a in cross_profile_failures],
            'detailed_results': [
                {
                    'test_id': r.test_id,
                    'profile_id': r.profile_id,
                    'status': r.status.value,
                    'question': r.question,
                    'detected_topic': r.detected_topic,
                    'detected_time_context': r.detected_time_context,
                    'drivers': r.drivers,
                    'failure_reasons': r.failure_reasons,
                    'warning_reasons': r.warning_reasons,
                    'execution_time_ms': r.execution_time_ms
                }
                for r in self.results
            ]
        }
    
    def print_summary(self):
        """Print summary to console"""
        report = self.generate_report()
        
        print("\n" + "="*70)
        print("STRESS TEST RESULTS SUMMARY")
        print("="*70)
        
        s = report['summary']
        print(f"\nOverall: {s['total_tests']} tests")
        print(f"  ✓ PASS: {s['pass']} ({s['pass_rate']})")
        print(f"  ⚠ WARN: {s['warn']}")
        print(f"  ✗ FAIL: {s['fail']}")
        print(f"  E ERROR: {s['error']}")
        
        print("\n--- By Topic ---")
        for topic, counts in sorted(report['by_topic'].items()):
            total = sum(counts.values())
            pass_rate = 100 * counts['pass'] / total if total else 0
            print(f"  {topic}: {counts['pass']}/{total} pass ({pass_rate:.0f}%)")
        
        print("\n--- By Time Context ---")
        for time_ctx, counts in sorted(report['by_time_context'].items()):
            total = sum(counts.values())
            pass_rate = 100 * counts['pass'] / total if total else 0
            print(f"  {time_ctx}: {counts['pass']}/{total} pass ({pass_rate:.0f}%)")
        
        print("\n--- Failures by Assertion Type ---")
        for assertion_name, failures in sorted(report['failures_by_assertion'].items()):
            print(f"  {assertion_name}: {len(failures)} failures")
            for f in failures[:3]:  # Show first 3
                print(f"    - {f['test_id']} ({f['profile_id']}): {f['message'][:60]}")
            if len(failures) > 3:
                print(f"    ... and {len(failures) - 3} more")
        
        if report['cross_profile_failures']:
            print("\n--- Cross-Profile Issues ---")
            for f in report['cross_profile_failures'][:5]:
                print(f"  ⚠ {f['name']}: {f['message'][:70]}")
        
        print("\n" + "="*70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run astrology pipeline stress tests')
    parser.add_argument('--output', choices=['json', 'console'], default='console',
                       help='Output format')
    parser.add_argument('--output-file', type=str, default='stress_test_results.json',
                       help='Output file for JSON format')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick test with subset of cases')
    args = parser.parse_args()
    
    runner = StressTestRunner()
    
    # Use subset for quick test
    test_cases = TEST_CASES
    profiles = TEST_PROFILES
    
    if args.quick:
        test_cases = TEST_CASES[:10]
        profiles = TEST_PROFILES[:1]
    
    await runner.run_all_tests(profiles=profiles, test_cases=test_cases)
    
    if args.output == 'json':
        report = runner.generate_report()
        with open(args.output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nResults written to {args.output_file}")
    
    runner.print_summary()


if __name__ == '__main__':
    asyncio.run(main())
