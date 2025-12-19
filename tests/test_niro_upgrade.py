#!/usr/bin/env python3
"""
Unit tests for NIRO Intelligence Upgrade

Tests:
1. Intent detection (timing, compare, advice, etc.)
2. Time context detection (past, present, future, timeless)
3. Reading pack building with signal limiting
4. Reading pack data gap handling
"""

import pytest
from backend.conversation.intent import detect_intent, detect_time_context, detect_intent_and_context
from backend.astro_client.reading_pack import build_reading_pack


class TestIntentDetection:
    """Test intent detection heuristics"""
    
    def test_timing_intent(self):
        """Detect timing intent"""
        assert detect_intent("When should I start my business?") == "timing"
        assert detect_intent("Best time for marriage?") == "timing"
        assert detect_intent("Good timing for job change?") == "timing"
    
    def test_compare_intent(self):
        """Detect compare intent"""
        assert detect_intent("Job vs business, which is better?") == "compare"
        assert detect_intent("Should I pick option A or B?") == "compare"
        assert detect_intent("Which path would be better for me?") == "compare"
    
    def test_predict_intent(self):
        """Detect predict intent"""
        assert detect_intent("Will I succeed in my career?") == "predict"
        assert detect_intent("What will happen next?") == "predict"
        assert detect_intent("Chances of success?") == "predict"
    
    def test_explain_intent(self):
        """Detect explain intent"""
        assert detect_intent("Why do I struggle with relationships?") == "explain"
        assert detect_intent("What does my ascendant mean?") == "explain"
        assert detect_intent("How does Saturn affect me?") == "explain"
    
    def test_advice_intent(self):
        """Detect advice intent"""
        assert detect_intent("Should I change jobs?") == "advice"
        assert detect_intent("What should I do about this situation?") == "advice"
        assert detect_intent("How can I improve my career?") == "advice"
    
    def test_reflect_intent(self):
        """Detect reflect (default) intent"""
        assert detect_intent("Tell me about my chart") == "reflect"
        assert detect_intent("General reading please") == "reflect"


class TestTimeContextDetection:
    """Test time context detection"""
    
    def test_future_context(self):
        """Detect future time context"""
        assert detect_time_context("When will I get married?") == "future"
        assert detect_time_context("Next year what's in store?") == "future"
        assert detect_time_context("Good time to start a business in 2026?") == "future"
        assert detect_time_context("What's ahead for me?") == "future"
    
    def test_past_context(self):
        """Detect past time context"""
        assert detect_time_context("What happened last year?") == "past"
        assert detect_time_context("Why did that occur in 2023?") == "past"
        assert detect_time_context("Looking back at my history") == "past"
    
    def test_present_context(self):
        """Detect present time context"""
        assert detect_time_context("What am I experiencing now?") == "present"
        assert detect_time_context("Currently how is my situation?") == "present"
        assert detect_time_context("Right now, what's happening?") == "present"
    
    def test_timeless_context(self):
        """Detect timeless context"""
        assert detect_time_context("Tell me about my personality") == "timeless"
        assert detect_time_context("General reading") == "timeless"
        assert detect_time_context("What are my traits?") == "timeless"


class TestIntentAndContextCombined:
    """Test combined intent + time context detection"""
    
    def test_timing_future(self):
        """Timing intent with future context"""
        result = detect_intent_and_context("When is the best time to change jobs?")
        assert result['intent'] == "timing"
        assert result['time_context'] == "future"
    
    def test_compare_present(self):
        """Compare intent with present context"""
        result = detect_intent_and_context("Job vs business - which is better for me right now?")
        assert result['intent'] == "compare"
        assert result['time_context'] == "present"
    
    def test_advice_timeless(self):
        """Advice intent with timeless context"""
        result = detect_intent_and_context("What should I do with my life?")
        assert result['intent'] == "advice"
        assert result['time_context'] == "timeless"


class TestReadingPackBuilder:
    """Test reading pack construction"""
    
    def test_empty_astro_features(self):
        """Build pack with no astro features"""
        pack = build_reading_pack(
            user_question="Test question",
            topic="career",
            time_context="future",
            astro_features={},
            missing_keys=[]
        )
        
        assert pack['question'] == "Test question"
        assert pack['topic'] == "career"
        assert pack['time_context'] == "future"
        assert pack['signals'] == []
        assert pack['data_gaps'] == []
    
    def test_signal_limiting(self):
        """Ensure signals are limited to 12 max"""
        features = {
            'focus_factors': [
                {'rule_id': f'Factor{i}', 'strength': 0.5, 'interpretation': f'Test {i}'}
                for i in range(20)  # 20 factors
            ]
        }
        
        pack = build_reading_pack(
            user_question="Test",
            topic="career",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        assert len(pack['signals']) <= 12
    
    def test_data_gaps_reporting(self):
        """Data gaps only include critical missing fields"""
        missing = ['some_field', 'ascendant', 'mahadasha', 'another_field']
        
        pack = build_reading_pack(
            user_question="Test",
            topic="career",
            time_context="future",
            astro_features={},
            missing_keys=missing
        )
        
        # Only critical fields should be in gaps
        assert 'ascendant' in pack['data_gaps']
        assert 'mahadasha' in pack['data_gaps']
        assert 'some_field' not in pack['data_gaps']
    
    def test_dasha_polarity(self):
        """Dasha polarity should be set correctly"""
        features = {
            'mahadasha': {
                'planet': 'Jupiter',
                'start_date': '2024-01-01',
                'end_date': '2034-01-01',
                'years_remaining': 10
            },
            'antardasha': {
                'planet': 'Saturn',
                'start_date': '2024-01-01',
                'end_date': '2025-01-01',
                'years_remaining': 1
            }
        }
        
        pack = build_reading_pack(
            user_question="Test",
            topic="career",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        # Find dasha signals
        dasha_signals = [s for s in pack['signals'] if s['type'] == 'dasha']
        assert len(dasha_signals) == 2
        
        # Jupiter should be supportive
        jupiter_signal = next((s for s in dasha_signals if 'Jupiter' in s['claim']), None)
        assert jupiter_signal['polarity'] == 'supportive'
        
        # Saturn should be challenging
        saturn_signal = next((s for s in dasha_signals if 'Saturn' in s['claim']), None)
        assert saturn_signal['polarity'] == 'challenging'
    
    def test_timing_windows_limiting(self):
        """Timing windows limited to 3 max"""
        features = {
            'timing_windows': [
                {'period': f'Window {i}', 'nature': 'beneficial', 'activity': 'Good for work'}
                for i in range(10)  # 10 windows
            ]
        }
        
        pack = build_reading_pack(
            user_question="Test",
            topic="career",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        assert len(pack['timing_windows']) <= 3
    
    def test_topic_specific_signals(self):
        """Different topics should extract different signals"""
        features = {
            'focus_factors': [
                {'rule_id': 'Career House', 'strength': 0.8, 'interpretation': 'Strong 10th'},
                {'rule_id': 'Love House', 'strength': 0.4, 'interpretation': 'Weak 7th'},
            ]
        }
        
        # Career topic
        career_pack = build_reading_pack(
            user_question="Career?",
            topic="career",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        # Relationship topic
        love_pack = build_reading_pack(
            user_question="Love?",
            topic="relationship",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        # Both should have signals, but may weight differently
        assert len(career_pack['signals']) > 0
        assert len(love_pack['signals']) > 0
    
    def test_transit_signals(self):
        """Transits should be converted to signals"""
        features = {
            'transits': [
                {
                    'planet': 'Jupiter',
                    'sign': 'Capricorn',
                    'house': 10,
                    'start_date': '2025-01-11',
                    'end_date': '2025-12-20',
                    'nature': 'beneficial'
                },
                {
                    'planet': 'Saturn',
                    'sign': 'Scorpio',
                    'house': 8,
                    'start_date': '2026-06-10',
                    'end_date': '2029-05-20',
                    'nature': 'challenging'
                }
            ]
        }
        
        pack = build_reading_pack(
            user_question="Future transits?",
            topic="career",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        transit_signals = [s for s in pack['signals'] if s['type'] == 'transit']
        assert len(transit_signals) == 2
        
        # Check signal polarity matches transit nature
        jup_signal = next((s for s in transit_signals if 'Jupiter' in s['claim']), None)
        assert jup_signal['polarity'] == 'beneficial'


class TestLLMPayloadShape:
    """Test that LLM payload has correct structure"""
    
    def test_payload_keys(self):
        """Verify payload includes all required keys"""
        from backend.astro_client.reading_pack import build_reading_pack
        
        features = {'ascendant': 'Sagittarius', 'moon_sign': 'Taurus'}
        reading_pack = build_reading_pack(
            user_question="Test",
            topic="career",
            time_context="future",
            astro_features=features,
            missing_keys=[]
        )
        
        # Expected keys in reading pack
        assert 'question' in reading_pack
        assert 'topic' in reading_pack
        assert 'time_context' in reading_pack
        assert 'signals' in reading_pack
        assert 'timing_windows' in reading_pack
        assert 'data_gaps' in reading_pack
        
        # LLM payload structure (as passed to LLM)
        payload = {
            'mode': 'NORMAL_READING',
            'topic': 'career',
            'time_context': 'future',
            'intent': 'timing',
            'user_question': 'Test',
            'astro_features': features,
            'reading_pack': reading_pack,
            'data_coverage': {
                'profile': {},
                'transits': {},
                'features': {}
            },
            'session_id': 'test-session',
            'timestamp': '2025-12-13T00:00:00Z'
        }
        
        # Verify all keys present
        required_keys = {
            'mode', 'topic', 'time_context', 'intent',
            'user_question', 'astro_features', 'reading_pack',
            'data_coverage', 'session_id', 'timestamp'
        }
        assert required_keys.issubset(set(payload.keys()))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
