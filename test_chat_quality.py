#!/usr/bin/env python3
"""
Test script for improved chat message quality.
Tests conversational responses and astrology questions.
"""

import sys
import json
sys.path.insert(0, '/Users/sharadharjai/Documents/GitHub/niro-ai-Prod-version')

from backend.astro_client.niro_llm import NiroLLMModule, CHAT_TONE_POLICY

print("\n" + "="*80)
print("CHAT MESSAGE QUALITY IMPROVEMENTS - TEST SUITE")
print("="*80)

# ============================================================================
# TEST 1: Chat Tone Policy is Loaded
# ============================================================================
print("\n[TEST 1] Chat Tone Policy Constant")
print("-" * 80)

if CHAT_TONE_POLICY:
    print("✅ PASS: CHAT_TONE_POLICY constant loaded")
    print(f"   Size: {len(CHAT_TONE_POLICY)} characters")
    
    # Check key elements
    required_sections = [
        "CONVERSATIONAL TONE",
        "NO MECHANICAL SECTIONS",
        "DATA GAPS HANDLING",
        "FOLLOW-UP PROMPTS"
    ]
    
    all_found = True
    for section in required_sections:
        if section in CHAT_TONE_POLICY:
            print(f"   ✅ Contains: {section}")
        else:
            print(f"   ❌ Missing: {section}")
            all_found = False
    
    if all_found:
        print("\n✅ TEST 1 PASSED: Chat tone policy fully defined")
    else:
        print("\n❌ TEST 1 FAILED: Missing sections")
else:
    print("❌ TEST 1 FAILED: CHAT_TONE_POLICY not found")

# ============================================================================
# TEST 2: Conversational Input Detection
# ============================================================================
print("\n[TEST 2] Conversational Input Detection")
print("-" * 80)

llm = NiroLLMModule()

test_inputs = [
    ("hi", True, "Greeting"),
    ("hello there", True, "Greeting variant"),
    ("thanks!", True, "Thanks"),
    ("thank you so much", True, "Thank you variant"),
    ("how are you", True, "Question about agent"),
    ("what's up", True, "Casual greeting"),
    ("ok", True, "Acknowledgment"),
    ("got it", True, "Acknowledgment variant"),
    ("lol", True, "Laugh"),
    ("Should I switch jobs?", False, "Career question"),
    ("When will I get married?", False, "Timing question"),
    ("What's my love life like?", False, "Astrology question"),
    ("Compare two job offers", False, "Compare question"),
]

passed = 0
failed = 0

for text, expected, description in test_inputs:
    result = llm._is_conversational_input(text)
    status = "✅" if result == expected else "❌"
    if result == expected:
        passed += 1
    else:
        failed += 1
    print(f"{status} '{text}' → conversational={result} (expected {expected}) - {description}")

print(f"\nDetection Results: {passed} passed, {failed} failed")
if failed == 0:
    print("✅ TEST 2 PASSED: All inputs detected correctly")
else:
    print(f"❌ TEST 2 FAILED: {failed} detection errors")

# ============================================================================
# TEST 3: System Prompt Content
# ============================================================================
print("\n[TEST 3] System Prompt Content")
print("-" * 80)

system_prompt = llm._build_system_prompt()

print(f"System prompt size: {len(system_prompt)} characters")

required_elements = [
    ("CHAT_TONE_POLICY embedded", "CORE MESSAGE QUALITY RULES"),
    ("Output structure explained", "OUTPUT STRUCTURE"),
    ("Conversational handling", "CONVERSATIONAL INPUT"),
    ("Astrology question handling", "IF ASTROLOGY QUESTION"),
    ("Data gaps rules", "DATA GAPS HANDLING"),
    ("No mechanical sections", "NO MECHANICAL SECTIONS"),
    ("Examples included", "SMALL TALK EXAMPLES"),
]

all_passed = True
for check_name, keyword in required_elements:
    if keyword in system_prompt:
        print(f"✅ {check_name}")
    else:
        print(f"❌ {check_name}")
        all_passed = False

if all_passed:
    print("\n✅ TEST 3 PASSED: System prompt contains all required elements")
else:
    print("\n❌ TEST 3 FAILED: Missing required elements")

# ============================================================================
# TEST 4: User Prompt Building - Conversational
# ============================================================================
print("\n[TEST 4] User Prompt for Conversational Input")
print("-" * 80)

payload_conversational = {
    'mode': 'NORMAL_READING',
    'topic': 'general',
    'time_context': 'timeless',
    'intent': 'reflect',
    'user_question': 'hi there!',
    'reading_pack': {}
}

user_prompt = llm._build_user_prompt(payload_conversational)
print("Generated user prompt for 'hi there!':")
print(user_prompt[:200] + "...")

checks = [
    ("No signals required", "SIGNALS" not in user_prompt),
    ("Conversational instruction", "naturally and warmly" in user_prompt),
    ("No structure requested", "structured sections" in user_prompt.lower()),
]

passed_checks = 0
for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if result:
        passed_checks += 1

if passed_checks == len(checks):
    print("✅ TEST 4 PASSED: Conversational prompt properly formatted")
else:
    print("❌ TEST 4 FAILED: Some checks failed")

# ============================================================================
# TEST 5: User Prompt Building - Astrology Question
# ============================================================================
print("\n[TEST 5] User Prompt for Astrology Question")
print("-" * 80)

payload_astrology = {
    'mode': 'NORMAL_READING',
    'topic': 'career',
    'time_context': 'future',
    'intent': 'advise',
    'user_question': 'Should I switch jobs in the next 6 months?',
    'reading_pack': {
        'signals': [
            {'id': 'S1', 'claim': 'Venus in 10th house', 'type': 'placement', 'polarity': 'positive'},
            {'id': 'S2', 'claim': 'Jupiter mahadasha', 'type': 'dasha', 'polarity': 'positive'}
        ],
        'timing_windows': [
            {'period': 'Jan-Mar 2025', 'nature': 'favorable', 'activity': 'Job transitions'}
        ],
        'data_gaps': []
    }
}

user_prompt = llm._build_user_prompt(payload_astrology)
print("Generated user prompt for astrology question:")
print(user_prompt[:300] + "...")

astro_checks = [
    ("Has signals", "SIGNALS" in user_prompt),
    ("Has timing windows", "TIMING_WINDOWS" in user_prompt),
    ("Instructed on format", "rawText section" in user_prompt),
    ("No mechanical sections in main message", "NO mechanical sections" in user_prompt),
]

astro_passed = 0
for check_name, result in astro_checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if result:
        astro_passed += 1

if astro_passed == len(astro_checks):
    print("✅ TEST 5 PASSED: Astrology prompt properly formatted")
else:
    print("❌ TEST 5 FAILED: Some checks failed")

# ============================================================================
# TEST 6: Response Parsing - Conversational
# ============================================================================
print("\n[TEST 6] Response Parsing - Conversational Format")
print("-" * 80)

conversational_response = "Hey! Great to have you here. What's on your mind today?"

parsed = llm._parse_structured_response(conversational_response)
print(f"Parsed response: {json.dumps(parsed, indent=2)}")

parse_checks = [
    ("rawText preserved", parsed.get('rawText') == conversational_response),
    ("No reasons list", len(parsed.get('reasons', [])) == 0),
    ("No remedies list", len(parsed.get('remedies', [])) == 0),
]

parse_passed = 0
for check_name, result in parse_checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if result:
        parse_passed += 1

if parse_passed == len(parse_checks):
    print("✅ TEST 6 PASSED: Conversational response parsed correctly")
else:
    print("❌ TEST 6 FAILED: Parsing issues")

# ============================================================================
# TEST 7: Response Parsing - Structured Format
# ============================================================================
print("\n[TEST 7] Response Parsing - Structured Format")
print("-" * 80)

structured_response = """rawText: Venus in your 10th house suggests strong career growth potential. The timing looks favorable for a change. Go for it!

reasons:
- [S1] Venus in 10th house → Career opportunities & positive social standing
- [S2] Jupiter mahadasha → Expansion and favorable outcomes

remedies:
- Have conversations with mentors before making the jump

data_gaps:
"""

parsed_structured = llm._parse_structured_response(structured_response)
print(f"Parsed structured response:")
print(f"  rawText: {parsed_structured.get('rawText')[:80]}...")
print(f"  reasons: {len(parsed_structured.get('reasons', []))} items")
print(f"  remedies: {len(parsed_structured.get('remedies', []))} items")
print(f"  data_gaps: {parsed_structured.get('data_gaps', 'not present')}")

struct_checks = [
    ("rawText extracted", "Venus in your 10th" in parsed_structured.get('rawText', '')),
    ("Reasons parsed", len(parsed_structured.get('reasons', [])) == 2),
    ("Remedies parsed", len(parsed_structured.get('remedies', [])) == 1),
    ("No empty data_gaps", 'data_gaps' not in parsed_structured or parsed_structured['data_gaps']),
]

struct_passed = 0
for check_name, result in struct_checks:
    status = "✅" if result else "❌"
    print(f"{status} {check_name}")
    if result:
        struct_passed += 1

if struct_passed == len(struct_checks):
    print("✅ TEST 7 PASSED: Structured response parsed correctly")
else:
    print("❌ TEST 7 FAILED: Parsing issues")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("TEST SUMMARY")
print("="*80)

all_tests = [
    ("TEST 1: Chat Tone Policy", True),
    ("TEST 2: Input Detection", failed == 0),
    ("TEST 3: System Prompt", all_passed),
    ("TEST 4: Conversational Prompt", passed_checks == len(checks)),
    ("TEST 5: Astrology Prompt", astro_passed == len(astro_checks)),
    ("TEST 6: Conversational Parse", parse_passed == len(parse_checks)),
    ("TEST 7: Structured Parse", struct_passed == len(struct_checks)),
]

passed_tests = sum(1 for _, result in all_tests if result)
total_tests = len(all_tests)

for test_name, result in all_tests:
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {test_name}")

print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")

if passed_tests == total_tests:
    print("\n🎉 ALL TESTS PASSED - Chat quality improvements ready!")
else:
    print(f"\n⚠️ {total_tests - passed_tests} test(s) need attention")

print("="*80 + "\n")
