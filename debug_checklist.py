#!/usr/bin/env python3
"""Debug test to check if birth details are being passed to checklist"""

import requests
import json
import time

BACKEND_URL = "http://localhost:8000"

# Authenticate
auth_resp = requests.post(
    f"{BACKEND_URL}/api/auth/identify",
    json={"identifier": f"debug-{int(time.time())}@example.com"}
)
token = auth_resp.json().get("token")
print(f"Token: {token}")

# Save profile
profile_data = {
    "name": "Debug User",
    "dob": "1985-03-20",
    "tob": "10:15",
    "location": "Mumbai, Maharashtra, India",
    "birth_place_lat": 19.0760,
    "birth_place_lon": 72.8777,
    "birth_place_tz": 5.5
}

prof_resp = requests.post(
    f"{BACKEND_URL}/api/profile/",
    headers={"Authorization": f"Bearer {token}"},
    json=profile_data
)
print(f"Profile saved: {prof_resp.json()}")

# Send chat without birth details
chat_req = {
    "sessionId": f"debug-{int(time.time())}",
    "message": "Tell me about my health",
    "subjectData": None
}

chat_resp = requests.post(
    f"{BACKEND_URL}/api/chat",
    headers={"Authorization": f"Bearer {token}"},
    json=chat_req
)

request_id = chat_resp.json().get("requestId")
print(f"\nChat response request_id: {request_id}")
print(f"Chat mode: {chat_resp.json().get('mode')}")

# Get checklist
checklist_resp = requests.get(f"{BACKEND_URL}/api/debug/checklist/{request_id}")
html = checklist_resp.text

# Extract birth details section
import re
match = re.search(r'Birth Details</div>.*?</div>\s*</div>', html, re.DOTALL)
if match:
    section = match.group(0)
    print(f"\nBirth Details section from HTML:\n{section}")
    
    # Check if values are populated
    if "DOB: 1985-03-20" in section:
        print("\n✅ DOB is populated!")
    else:
        print("\n❌ DOB is NOT populated (shows ?)")
        
    if "19.0760" in section or "72.8777" in section:
        print("✅ Coordinates are populated!")
    else:
        print("❌ Coordinates are NOT populated")
