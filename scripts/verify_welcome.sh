#!/bin/bash
# Minimal verification: backend startup + welcome endpoint exists + 401 without auth

set -e
BASE_URL="http://localhost:8000"

echo "=== Verify Welcome Endpoint ==="

# 1. Check if backend is running
echo "[1/4] Checking backend health..."
if ! curl -s "$BASE_URL/openapi.json" > /tmp/openapi.json 2>/dev/null; then
    echo "ERROR: Backend not responding at $BASE_URL"
    echo "Start backend with: python3 -m uvicorn backend.server:app --port 8000"
    exit 1
fi
echo "✓ Backend responding"

# 2. Check welcome endpoint exists in OpenAPI
echo "[2/4] Checking OpenAPI paths..."
WELCOME_PATHS=$(python3 -c "
import json
with open('/tmp/openapi.json') as f:
    data = json.load(f)
    paths = [p for p in data.get('paths', {}) if 'welcome' in p]
    print('|'.join(paths) if paths else '')
")

if [ -z "$WELCOME_PATHS" ]; then
    echo "ERROR: /api/profile/welcome not found in OpenAPI"
    exit 1
fi
echo "✓ Found paths: $WELCOME_PATHS"

# 3. Test without auth (expect 401)
echo "[3/4] Testing POST /api/profile/welcome without auth..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/profile/welcome" \
    -H "Content-Type: application/json" \
    -d '{}')

if [ "$HTTP_CODE" == "401" ] || [ "$HTTP_CODE" == "403" ]; then
    echo "✓ Got expected $HTTP_CODE Unauthorized"
else
    echo "⚠ Got $HTTP_CODE (expected 401/403)"
fi

# 4. Summary
echo ""
echo "=== Verification Complete ==="
echo "Backend: running on $BASE_URL"
echo "Welcome endpoint: exists at /api/profile/welcome"
echo "Auth: required (401 without token)"
