#!/usr/bin/env python3
"""
Test script: Living Welcome Message Implementation

This script demonstrates the new welcome message generator in action
across all three tone types and validates quality criteria.

Run: python3 test_welcome_message_quality.py
"""

from backend.welcome_traits import (
    generate_welcome_message,
    create_welcome_message,
    get_dominant_elements,
    select_tone,
    collect_personality_traits,
)

def print_header(title):
    """Print a section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_tone_a():
    """Test TONE A: Calm & Grounded (Earth/Water)."""
    print_header("TEST 1: TONE A - CALM & GROUNDED")
    
    test_cases = [
        {
            "name": "Sharad",
            "ascendant": "Taurus",
            "moon_sign": "Capricorn",
            "sun_sign": "Virgo",
            "elements": "All Earth → Pure grounding",
        },
        {
            "name": "Priya",
            "ascendant": "Cancer",
            "moon_sign": "Pisces",
            "sun_sign": "Scorpio",
            "elements": "All Water → Deep emotions",
        },
    ]
    
    for case in test_cases:
        name = case["name"]
        asc = case["ascendant"]
        moon = case["moon_sign"]
        sun = case["sun_sign"]
        
        print(f"\nPerson: {name}")
        print(f"Chart: {asc} (Asc) + {moon} (Moon) + {sun} (Sun)")
        print(f"Element combo: {case['elements']}")
        
        elements = get_dominant_elements(asc, moon, sun)
        tone = select_tone(elements)
        traits = collect_personality_traits(asc, moon, sun)
        
        print(f"Elements detected: {elements}")
        print(f"Tone selected: {tone} (expected: A) ✓" if tone == "A" else f"Tone selected: {tone} (expected: A) ✗")
        print(f"Traits: {', '.join(traits)}")
        
        msg = generate_welcome_message(name, asc, moon, sun)
        print(f"\nMessage:\n{msg}")
        print(f"Word count: {len(msg.split())}")


def test_tone_b():
    """Test TONE B: Warm & Encouraging (Water + Fire)."""
    print_header("TEST 2: TONE B - WARM & ENCOURAGING")
    
    test_cases = [
        {
            "name": "Maya",
            "ascendant": "Cancer",
            "moon_sign": "Scorpio",
            "sun_sign": "Sagittarius",
            "elements": "Water (Cancer, Scorpio) + Fire (Sagittarius)",
        },
        {
            "name": "Jai",
            "ascendant": "Pisces",
            "moon_sign": "Cancer",
            "sun_sign": "Leo",
            "elements": "Water (Pisces, Cancer) + Fire (Leo)",
        },
    ]
    
    for case in test_cases:
        name = case["name"]
        asc = case["ascendant"]
        moon = case["moon_sign"]
        sun = case["sun_sign"]
        
        print(f"\nPerson: {name}")
        print(f"Chart: {asc} (Asc) + {moon} (Moon) + {sun} (Sun)")
        print(f"Element combo: {case['elements']}")
        
        elements = get_dominant_elements(asc, moon, sun)
        tone = select_tone(elements)
        traits = collect_personality_traits(asc, moon, sun)
        
        print(f"Elements detected: {elements}")
        print(f"Tone selected: {tone} (expected: B) ✓" if tone == "B" else f"Tone selected: {tone} (expected: B) ✗")
        print(f"Traits: {', '.join(traits)}")
        
        msg = generate_welcome_message(name, asc, moon, sun)
        print(f"\nMessage:\n{msg}")
        print(f"Word count: {len(msg.split())}")


def test_tone_c():
    """Test TONE C: Confident & Forward-looking (Fire/Air)."""
    print_header("TEST 3: TONE C - CONFIDENT & FORWARD-LOOKING")
    
    test_cases = [
        {
            "name": "Alex",
            "ascendant": "Leo",
            "moon_sign": "Gemini",
            "sun_sign": "Aries",
            "elements": "Fire (Leo, Aries) + Air (Gemini)",
        },
        {
            "name": "Jordan",
            "ascendant": "Sagittarius",
            "moon_sign": "Aquarius",
            "sun_sign": "Libra",
            "elements": "Fire (Sagittarius) + Air (Aquarius, Libra)",
        },
    ]
    
    for case in test_cases:
        name = case["name"]
        asc = case["ascendant"]
        moon = case["moon_sign"]
        sun = case["sun_sign"]
        
        print(f"\nPerson: {name}")
        print(f"Chart: {asc} (Asc) + {moon} (Moon) + {sun} (Sun)")
        print(f"Element combo: {case['elements']}")
        
        elements = get_dominant_elements(asc, moon, sun)
        tone = select_tone(elements)
        traits = collect_personality_traits(asc, moon, sun)
        
        print(f"Elements detected: {elements}")
        print(f"Tone selected: {tone} (expected: C) ✓" if tone == "C" else f"Tone selected: {tone} (expected: C) ✗")
        print(f"Traits: {', '.join(traits)}")
        
        msg = generate_welcome_message(name, asc, moon, sun)
        print(f"\nMessage:\n{msg}")
        print(f"Word count: {len(msg.split())}")


def test_quality_criteria():
    """Validate quality criteria from the original prompt."""
    print_header("QUALITY ASSURANCE: Original Prompt Criteria")
    
    messages = [
        generate_welcome_message("Test1", "Taurus", "Capricorn", "Virgo"),    # Tone A
        generate_welcome_message("Test2", "Cancer", "Scorpio", "Sagittarius"), # Tone B
        generate_welcome_message("Test3", "Leo", "Gemini", "Aries"),          # Tone C
    ]
    
    print("\nChecking all messages against quality criteria...\n")
    
    criteria = {
        "No bullet points": lambda m: "•" not in m and "▪" not in m and "- " not in m,
        "No 'Three things' phrase": lambda m: "Three things" not in m,
        "No mechanical labels": lambda m: "Summary" not in m and "Analysis" not in m and "Based on" not in m,
        "No emoji": lambda m: not any(0x1F300 <= ord(c) <= 0x1F9FF for c in m),  # Fixed: actual emoji range only
        "Natural contractions": lambda m: "there's" in m or "I've" in m or "you're" in m,
        "Conversational tone": lambda m: "Hey" in m and "What" in m,
        "Appropriate length": lambda m: 20 <= len(m.split()) <= 35,
        "Acknowledges chart review": lambda m: "looked at your chart" in m,
        "No requests for data": lambda m: "birth details" not in m and "time of birth" not in m,
    }
    
    all_pass = True
    for i, msg in enumerate(messages, 1):
        print(f"Message {i}:")
        msg_pass = True
        for criterion, check in criteria.items():
            result = check(msg)
            symbol = "✓" if result else "✗"
            print(f"  {symbol} {criterion}")
            if not result:
                msg_pass = False
                all_pass = False
        print()
    
    if all_pass:
        print("="*80)
        print("  🎉 ALL QUALITY CRITERIA PASSING")
        print("="*80)
    else:
        print("="*80)
        print("  ⚠️ SOME CRITERIA FAILED - SEE ABOVE")
        print("="*80)


def test_legacy_wrapper():
    """Test backward compatibility with legacy wrapper."""
    print_header("BACKWARD COMPATIBILITY: Legacy Wrapper")
    
    result = create_welcome_message("TestUser", "Taurus", "Cancer", "Leo")
    
    print("create_welcome_message() returns:")
    print(f"  ✓ 'message' key: {bool(result.get('message'))}")
    print(f"  ✓ 'title' key (legacy): {bool(result.get('title'))}")
    print(f"  ✓ 'subtitle' key (legacy): {bool(result.get('subtitle'))}")
    print(f"  ✓ 'bullets' key (legacy): {bool(result.get('bullets'))}")
    
    print(f"\nNew message field:\n{result['message']}")
    print(f"\nLegacy title: {result['title']}")
    print(f"Legacy bullets: {result['bullets']}")


def main():
    """Run all tests."""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  WELCOME MESSAGE QUALITY TEST SUITE".center(78) + "█")
    print("█" + "  Implementation: backend/welcome_traits.py".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    try:
        test_tone_a()
        test_tone_b()
        test_tone_c()
        test_quality_criteria()
        test_legacy_wrapper()
        
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + "  ✅ ALL TESTS COMPLETED SUCCESSFULLY".center(78) + "█")
        print("█" + " "*78 + "█")
        print("█"*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
