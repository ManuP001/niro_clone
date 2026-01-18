"""Audit what astro_features structure is actually used in production"""
import sys
sys.path.insert(0, '/app/backend')
import requests
import json

BASE_URL = "http://localhost:8001/api"

# Create test user
email = "audit-time-test@example.com"
resp = requests.post(f"{BASE_URL}/auth/identify", json={"email": email})
token = resp.json().get("token")
headers = {"Authorization": f"Bearer {token}"}
print(f"User created: {resp.status_code}")

# Create profile
profile_data = {
    "name": "Audit User",
    "dob": "1986-01-24",
    "tob": "06:32",
    "location": "Mumbai",
    "lat": 19.08,
    "lon": 72.88
}
resp = requests.post(f"{BASE_URL}/profile/", json=profile_data, headers=headers)
print(f"Profile created: {resp.status_code}")

# Now send TWO chat requests - past and future
print("\n" + "="*80)
print("SENDING PAST QUERY: 'How was my career in 2022?'")
print("="*80)

past_resp = requests.post(f"{BASE_URL}/chat", json={
    "message": "How was my career in 2022?",
    "sessionId": "audit-past-session"
}, headers=headers)
past_data = past_resp.json()

print(f"\nPAST Response Status: {past_resp.status_code}")
print(f"PAST Reply (first 300 chars): {past_data.get('reply', {}).get('rawText', '')[:300]}")
print(f"PAST Reasons: {past_data.get('reply', {}).get('reasons', [])}")
print(f"PAST Trust Widget Drivers: {past_data.get('trustWidget', {}).get('drivers', [])}")

print("\n" + "="*80)
print("SENDING FUTURE QUERY: 'How will my career be in 2026?'")
print("="*80)

future_resp = requests.post(f"{BASE_URL}/chat", json={
    "message": "How will my career be in 2026?",
    "sessionId": "audit-future-session"
}, headers=headers)
future_data = future_resp.json()

print(f"\nFUTURE Response Status: {future_resp.status_code}")
print(f"FUTURE Reply (first 300 chars): {future_data.get('reply', {}).get('rawText', '')[:300]}")
print(f"FUTURE Reasons: {future_data.get('reply', {}).get('reasons', [])}")
print(f"FUTURE Trust Widget Drivers: {future_data.get('trustWidget', {}).get('drivers', [])}")

# Get debug signals
print("\n" + "="*80)
print("CHECKING CANDIDATE SIGNALS DEBUG")
print("="*80)

debug_resp = requests.get(f"{BASE_URL}/debug/candidate-signals/latest", headers=headers)
if debug_resp.status_code == 200:
    debug_data = debug_resp.json()
    candidates = debug_data.get('candidates', [])
    summary = debug_data.get('summary', {})
    
    print(f"\nTotal candidates: {summary.get('total_candidates', 0)}")
    print(f"Kept: {summary.get('kept_count', 0)}, Dropped: {summary.get('dropped_count', 0)}")
    print(f"Counts by time layer: {summary.get('counts_by_time_layer', {})}")
    print(f"Time layer stats: {summary.get('time_layer_stats', {})}")
    
    # Show kept signals
    kept = [c for c in candidates if c.get('kept')]
    print(f"\nKEPT SIGNALS ({len(kept)}):")
    for c in kept[:5]:
        is_time = c.get('is_time_layer', False)
        layer = "TIME" if is_time else "STATIC"
        print(f"  - {c.get('planet')} [{c.get('signal_type')}] {layer} score={c.get('score_final', 0):.3f}")
        print(f"    time_period={c.get('time_period')}")
else:
    print(f"Debug endpoint failed: {debug_resp.status_code}")

# Compare
print("\n" + "="*80)
print("COMPARISON")
print("="*80)
past_reasons = past_data.get('reply', {}).get('reasons', [])
future_reasons = future_data.get('reply', {}).get('reasons', [])
print(f"\nPAST reasons: {past_reasons}")
print(f"FUTURE reasons: {future_reasons}")
print(f"\nAre reasons identical? {past_reasons == future_reasons}")
