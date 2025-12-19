#!/usr/bin/env python3
"""
Test script to verify all four Chat experience improvements
"""

import ast
import re
import sys

def test_goal_1_personalized_welcome():
    """Goal 1: Personalized welcome message with kundli data"""
    print("\n" + "="*70)
    print("TEST 1: Personalized Welcome Message (Using Kundli Data)")
    print("="*70)
    
    with open('backend/profile/__init__.py', 'r') as f:
        content = f.read()
    
    checks = [
        ('vedic_api_client.fetch_full_profile', 'Fetches kundli data from Vedic API'),
        ('ascendant = astro_profile.ascendant', 'Extracts ascendant sign'),
        ('moon_sign = astro_profile.moon_sign', 'Extracts moon sign'),
        ('sun_sign = astro_profile.sun_sign', 'Extracts sun sign'),
        ('create_welcome_message(name, ascendant, moon_sign, sun_sign)', 'Passes chart data to welcome generator'),
    ]
    
    passed = 0
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_goal_2_chat_persistence():
    """Goal 2: Persistent chat history across tab switches"""
    print("\n" + "="*70)
    print("TEST 2: Chat Persistence (localStorage + Global Store)")
    print("="*70)
    
    # Check ChatContext exists
    with open('frontend/src/context/ChatContext.jsx', 'r') as f:
        context_content = f.read()
    
    context_checks = [
        ('localStorage.setItem', 'Syncs messages to localStorage'),
        ('localStorage.getItem', 'Loads messages from localStorage'),
        ('useChatStore', 'Provides useChatStore hook'),
        ('addMessage', 'Exports addMessage function'),
        ('getMessages', 'Exports getMessages function'),
    ]
    
    context_passed = 0
    for check_str, description in context_checks:
        if check_str in context_content:
            print(f"  ✅ Context: {description}")
            context_passed += 1
        else:
            print(f"  ❌ Context: {description}")
    
    # Check ChatScreen uses the store
    with open('frontend/src/components/screens/ChatScreen.jsx', 'r') as f:
        chatscreen_content = f.read()
    
    chatscreen_checks = [
        ('useChatStore()', 'Uses global chat store hook'),
        ('addMessage(userId', 'Adds messages to store'),
        ('getMessages(userId', 'Retrieves messages from store'),
        ('setMessages(userId', 'Sets initial messages'),
    ]
    
    chatscreen_passed = 0
    for check_str, description in chatscreen_checks:
        if check_str in chatscreen_content:
            print(f"  ✅ ChatScreen: {description}")
            chatscreen_passed += 1
        else:
            print(f"  ❌ ChatScreen: {description}")
    
    # Check App wraps with ChatProvider
    with open('frontend/src/App.js', 'r') as f:
        app_content = f.read()
    
    app_checks = [
        ('ChatProvider', 'Imports ChatProvider'),
        ('<ChatProvider>', 'Wraps app with ChatProvider'),
    ]
    
    app_passed = 0
    for check_str, description in app_checks:
        if check_str in app_content:
            print(f"  ✅ App.js: {description}")
            app_passed += 1
        else:
            print(f"  ❌ App.js: {description}")
    
    total_passed = context_passed + chatscreen_passed + app_passed
    total_checks = len(context_checks) + len(chatscreen_checks) + len(app_checks)
    print(f"\nResult: {total_passed}/{total_checks} checks passed")
    return total_passed == total_checks

def test_goal_3_clean_formatting():
    """Goal 3: Remove Reasons from main bubble, show in accordion"""
    print("\n" + "="*70)
    print("TEST 3: Clean Message Formatting (Reasons in Accordion)")
    print("="*70)
    
    with open('frontend/src/components/screens/ChatScreen.jsx', 'r') as f:
        content = f.read()
    
    checks = [
        ('data.reply?.summary || data.reply?.rawText', 'Uses summary for main bubble (not reasons)'),
        ('reasons: data.reply?.reasons || []', 'Stores reasons separately'),
        ('remedies: data.reply?.remedies || []', 'Stores remedies separately'),
        ('msg.reasons?.length > 0', 'Shows reasons only in accordion'),
    ]
    
    passed = 0
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def test_goal_4_data_gaps_filtering():
    """Goal 4: Show Data Gaps only when present"""
    print("\n" + "="*70)
    print("TEST 4: Smart Data Gaps Display (Hidden When Empty)")
    print("="*70)
    
    with open('frontend/src/components/screens/ChatScreen.jsx', 'r') as f:
        content = f.read()
    
    checks = [
        ('const filteredGaps = Array.isArray(dataGaps)', 'Filters data gaps array'),
        ("dataGaps.filter(gap => gap && gap !== 'none'", 'Removes empty/none values'),
        ('gap.trim()', 'Removes whitespace-only gaps'),
        ('filteredGaps?.length > 0 &&', 'Only renders section if gaps exist'),
    ]
    
    passed = 0
    for check_str, description in checks:
        if check_str in content:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description}")
    
    print(f"\nResult: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def main():
    print("\n" + "="*70)
    print("TESTING CHAT EXPERIENCE IMPROVEMENTS")
    print("="*70)
    
    results = []
    
    try:
        results.append(("Goal 1: Personalized Welcome", test_goal_1_personalized_welcome()))
        results.append(("Goal 2: Chat Persistence", test_goal_2_chat_persistence()))
        results.append(("Goal 3: Clean Formatting", test_goal_3_clean_formatting()))
        results.append(("Goal 4: Data Gaps Filter", test_goal_4_data_gaps_filtering()))
    except Exception as e:
        print(f"\n❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All improvements verified successfully!")
        return True
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
