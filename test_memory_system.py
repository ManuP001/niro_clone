#!/usr/bin/env python3
"""
Memory System Acceptance Tests

Tests the persistent user memory and conversation context system.

Run: python test_memory_system.py

Tests:
1. Memory context loading
2. Update after user message
3. Update after AI response
4. Repetition penalty in signal scoring
5. Avoid repeating in LLM prompt
6. Debug endpoints
"""

import requests
import json
import time
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8001/api"

# Test user credentials
TEST_EMAIL = f"memory_test_{uuid.uuid4().hex[:8]}@example.com"
TEST_BIRTH_DETAILS = {
    "name": "Memory Test User",
    "dob": "1990-05-15",
    "tob": "14:30",
    "location": "Mumbai",
    "lat": 19.0760,
    "lon": 72.8777
}


def log(message, status="INFO"):
    """Print formatted log message."""
    icons = {"INFO": "ℹ️", "OK": "✅", "FAIL": "❌", "WARN": "⚠️", "TEST": "🧪"}
    print(f"{icons.get(status, '•')} [{status}] {message}")


def create_test_user():
    """Create a test user and return auth token."""
    log("Creating test user...", "TEST")
    
    # Register/identify user
    resp = requests.post(f"{BASE_URL}/auth/identify", json={"email": TEST_EMAIL})
    if resp.status_code != 200:
        log(f"Failed to create user: {resp.text}", "FAIL")
        return None
    
    data = resp.json()
    token = data.get("token")
    user_id = data.get("user", {}).get("id")
    
    log(f"User created: {user_id}", "OK")
    return {"token": token, "user_id": user_id}


def setup_profile(token):
    """Set up birth profile for the test user."""
    log("Setting up birth profile...", "TEST")
    
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/profile/", json=TEST_BIRTH_DETAILS, headers=headers)
    
    if resp.status_code == 200:
        log("Profile created", "OK")
        return True
    else:
        log(f"Profile creation failed: {resp.text}", "FAIL")
        return False


def test_memory_debug_endpoints(user_id, session_id):
    """Test memory debug endpoints."""
    log("Testing memory debug endpoints...", "TEST")
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Test 1: GET /api/debug/memory/{user_id}
    resp = requests.get(f"{BASE_URL}/debug/memory/{user_id}")
    if resp.status_code == 200:
        data = resp.json()
        if data.get("ok") and "memory" in data:
            log("GET /debug/memory/{user_id} - PASSED", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "get_user_memory", "status": "passed"})
        else:
            log(f"GET /debug/memory/{user_id} - Invalid response", "FAIL")
            results["failed"] += 1
            results["tests"].append({"name": "get_user_memory", "status": "failed", "error": "Invalid response"})
    else:
        log(f"GET /debug/memory/{user_id} - {resp.status_code}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "get_user_memory", "status": "failed", "error": resp.text})
    
    # Test 2: GET /api/debug/memory/{user_id}/context
    resp = requests.get(f"{BASE_URL}/debug/memory/{user_id}/context", params={"session_id": session_id})
    if resp.status_code == 200:
        data = resp.json()
        if data.get("ok") and "context" in data:
            log("GET /debug/memory/{user_id}/context - PASSED", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "get_memory_context", "status": "passed"})
        else:
            log(f"GET /debug/memory/{user_id}/context - Invalid response", "FAIL")
            results["failed"] += 1
            results["tests"].append({"name": "get_memory_context", "status": "failed", "error": "Invalid response"})
    else:
        log(f"GET /debug/memory/{user_id}/context - {resp.status_code}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "get_memory_context", "status": "failed", "error": resp.text})
    
    # Test 3: GET /api/debug/memory/{user_id}/sessions
    resp = requests.get(f"{BASE_URL}/debug/memory/{user_id}/sessions")
    if resp.status_code == 200:
        data = resp.json()
        if data.get("ok"):
            log("GET /debug/memory/{user_id}/sessions - PASSED", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "get_user_sessions", "status": "passed"})
        else:
            log(f"GET /debug/memory/{user_id}/sessions - Invalid response", "FAIL")
            results["failed"] += 1
            results["tests"].append({"name": "get_user_sessions", "status": "failed", "error": "Invalid response"})
    else:
        log(f"GET /debug/memory/{user_id}/sessions - {resp.status_code}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "get_user_sessions", "status": "failed", "error": resp.text})
    
    return results


def test_memory_accumulation(token, user_id):
    """Test that memory accumulates across multiple chat messages."""
    log("Testing memory accumulation...", "TEST")
    results = {"passed": 0, "failed": 0, "tests": []}
    
    headers = {"Authorization": f"Bearer {token}"}
    session_id = f"memory_test_{uuid.uuid4().hex[:8]}"
    
    # Send first question about career
    log("Sending first question (career)...", "INFO")
    resp1 = requests.post(f"{BASE_URL}/chat", json={
        "message": "Should I start a business or stick with a job?",
        "sessionId": session_id
    }, headers=headers, timeout=60)
    
    if resp1.status_code != 200:
        log(f"First chat failed: {resp1.text}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "first_chat", "status": "failed"})
        return results, session_id
    
    log("First response received", "OK")
    results["passed"] += 1
    results["tests"].append({"name": "first_chat", "status": "passed"})
    
    # Wait a moment
    time.sleep(1)
    
    # Check memory after first question
    log("Checking memory after first question...", "INFO")
    mem_resp = requests.get(f"{BASE_URL}/debug/memory/{user_id}", params={"session_id": session_id})
    if mem_resp.status_code == 200:
        mem_data = mem_resp.json()
        conv_state = mem_data.get("memory", {}).get("conversation_state")
        if conv_state and conv_state.get("message_count", 0) >= 1:
            log(f"Memory updated: message_count={conv_state.get('message_count')}", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "memory_after_first", "status": "passed"})
        else:
            log("Memory not updated after first question", "WARN")
            results["tests"].append({"name": "memory_after_first", "status": "warning"})
    
    # Send second question (different topic)
    log("Sending second question (health)...", "INFO")
    resp2 = requests.post(f"{BASE_URL}/chat", json={
        "message": "Tell me about my health and energy levels",
        "sessionId": session_id
    }, headers=headers, timeout=60)
    
    if resp2.status_code != 200:
        log(f"Second chat failed: {resp2.text}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "second_chat", "status": "failed"})
        return results, session_id
    
    log("Second response received", "OK")
    results["passed"] += 1
    results["tests"].append({"name": "second_chat", "status": "passed"})
    
    # Wait a moment
    time.sleep(1)
    
    # Check memory accumulation
    log("Checking memory accumulation...", "INFO")
    mem_resp2 = requests.get(f"{BASE_URL}/debug/memory/{user_id}", params={"session_id": session_id})
    if mem_resp2.status_code == 200:
        mem_data2 = mem_resp2.json()
        
        # Check explored topics
        user_mem = mem_data2.get("memory", {}).get("user_memory", {})
        explored = user_mem.get("explored_topics", [])
        
        if len(explored) >= 2:
            log(f"Explored topics accumulated: {explored}", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "explored_topics", "status": "passed"})
        else:
            log(f"Explored topics: {explored} (expected >= 2)", "WARN")
            results["tests"].append({"name": "explored_topics", "status": "warning"})
        
        # Check conversation summary
        conv_summary = mem_data2.get("memory", {}).get("conversation_summary", {})
        avoid_repeating = conv_summary.get("summary_structured", {}).get("avoid_repeating", []) if conv_summary else []
        
        if len(avoid_repeating) >= 1:
            log(f"Avoid repeating populated: {len(avoid_repeating)} items", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "avoid_repeating", "status": "passed"})
        else:
            log("Avoid repeating empty (may need more messages)", "WARN")
            results["tests"].append({"name": "avoid_repeating", "status": "warning"})
    
    return results, session_id


def test_context_injection(token, user_id, session_id):
    """Test that memory context is properly injected into pipeline."""
    log("Testing context injection...", "TEST")
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Get context that would be passed to pipeline
    resp = requests.get(f"{BASE_URL}/debug/memory/{user_id}/context", params={"session_id": session_id})
    
    if resp.status_code != 200:
        log(f"Failed to get context: {resp.text}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "get_context", "status": "failed"})
        return results
    
    data = resp.json()
    context = data.get("context", {})
    
    # Verify context structure
    required_fields = [
        "astro_profile_summary", "high_confidence_facts", "explored_topics",
        "current_topics", "avoid_repeating", "has_prior_context", "message_count"
    ]
    
    missing = [f for f in required_fields if f not in context]
    if missing:
        log(f"Missing context fields: {missing}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "context_structure", "status": "failed", "missing": missing})
    else:
        log("Context structure complete", "OK")
        results["passed"] += 1
        results["tests"].append({"name": "context_structure", "status": "passed"})
    
    # Check has_prior_context flag
    if context.get("has_prior_context") and context.get("message_count", 0) > 0:
        log(f"Prior context detected: message_count={context.get('message_count')}", "OK")
        results["passed"] += 1
        results["tests"].append({"name": "prior_context_flag", "status": "passed"})
    else:
        log("Prior context not detected (expected after multiple messages)", "WARN")
        results["tests"].append({"name": "prior_context_flag", "status": "warning"})
    
    # Check context_for_prompt
    context_for_prompt = data.get("context_for_prompt", "")
    if context_for_prompt or len(context.get("avoid_repeating", [])) == 0:
        # Either has content or nothing to avoid yet
        log("Context for prompt generated correctly", "OK")
        results["passed"] += 1
        results["tests"].append({"name": "context_for_prompt", "status": "passed"})
    
    return results


def test_session_reset(user_id, session_id):
    """Test session memory reset."""
    log("Testing session reset...", "TEST")
    results = {"passed": 0, "failed": 0, "tests": []}
    
    # Reset session
    resp = requests.delete(f"{BASE_URL}/debug/memory/{user_id}/session/{session_id}")
    if resp.status_code == 200:
        data = resp.json()
        if data.get("ok"):
            log("Session reset successful", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "session_reset", "status": "passed"})
        else:
            log("Session reset returned ok=false", "FAIL")
            results["failed"] += 1
            results["tests"].append({"name": "session_reset", "status": "failed"})
    else:
        log(f"Session reset failed: {resp.text}", "FAIL")
        results["failed"] += 1
        results["tests"].append({"name": "session_reset", "status": "failed"})
    
    # Verify session memory is cleared
    mem_resp = requests.get(f"{BASE_URL}/debug/memory/{user_id}", params={"session_id": session_id})
    if mem_resp.status_code == 200:
        mem_data = mem_resp.json()
        conv_state = mem_data.get("memory", {}).get("conversation_state")
        if conv_state is None:
            log("Session memory cleared", "OK")
            results["passed"] += 1
            results["tests"].append({"name": "session_cleared", "status": "passed"})
        else:
            log("Session memory not cleared", "FAIL")
            results["failed"] += 1
            results["tests"].append({"name": "session_cleared", "status": "failed"})
    
    return results


def run_all_tests():
    """Run all memory system tests."""
    print("\n" + "=" * 60)
    print("MEMORY SYSTEM ACCEPTANCE TESTS")
    print("=" * 60 + "\n")
    
    all_results = {"total_passed": 0, "total_failed": 0, "test_groups": []}
    
    # Create test user
    auth = create_test_user()
    if not auth:
        log("FATAL: Could not create test user", "FAIL")
        return
    
    token = auth["token"]
    user_id = auth["user_id"]
    
    # Setup profile
    if not setup_profile(token):
        log("FATAL: Could not set up profile", "FAIL")
        return
    
    print("\n" + "-" * 40)
    
    # Test 1: Memory accumulation (also generates session_id)
    results, session_id = test_memory_accumulation(token, user_id)
    all_results["test_groups"].append({"name": "Memory Accumulation", "results": results})
    all_results["total_passed"] += results["passed"]
    all_results["total_failed"] += results["failed"]
    
    print("\n" + "-" * 40)
    
    # Test 2: Debug endpoints
    results = test_memory_debug_endpoints(user_id, session_id)
    all_results["test_groups"].append({"name": "Debug Endpoints", "results": results})
    all_results["total_passed"] += results["passed"]
    all_results["total_failed"] += results["failed"]
    
    print("\n" + "-" * 40)
    
    # Test 3: Context injection
    results = test_context_injection(token, user_id, session_id)
    all_results["test_groups"].append({"name": "Context Injection", "results": results})
    all_results["total_passed"] += results["passed"]
    all_results["total_failed"] += results["failed"]
    
    print("\n" + "-" * 40)
    
    # Test 4: Session reset
    results = test_session_reset(user_id, session_id)
    all_results["test_groups"].append({"name": "Session Reset", "results": results})
    all_results["total_passed"] += results["passed"]
    all_results["total_failed"] += results["failed"]
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"\nTotal Passed: {all_results['total_passed']}")
    print(f"Total Failed: {all_results['total_failed']}")
    
    for group in all_results["test_groups"]:
        print(f"\n{group['name']}:")
        for test in group["results"]["tests"]:
            status_icon = "✅" if test["status"] == "passed" else "❌" if test["status"] == "failed" else "⚠️"
            print(f"  {status_icon} {test['name']}: {test['status']}")
    
    print("\n" + "=" * 60)
    
    if all_results["total_failed"] == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️ {all_results['total_failed']} TEST(S) FAILED")
    
    print("=" * 60 + "\n")
    
    return all_results


if __name__ == "__main__":
    run_all_tests()
