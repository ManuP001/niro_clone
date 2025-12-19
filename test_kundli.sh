#!/bin/bash
# Kundli Testing Setup Script

# Check if VEDIC_API_KEY is set
if [ -z "$VEDIC_API_KEY" ]; then
    echo "❌ VEDIC_API_KEY is not set"
    echo ""
    echo "To get an API key:"
    echo "1. Visit: https://api.vedicastroapi.com/"
    echo "2. Sign up for a free account"
    echo "3. Get your API key from the dashboard"
    echo ""
    echo "To set the API key:"
    echo "  export VEDIC_API_KEY='your-api-key-here'"
    echo ""
    echo "Then run:"
    echo "  ./test_kundli.sh"
    exit 1
fi

echo "✅ VEDIC_API_KEY is set: ${VEDIC_API_KEY:0:20}..."
echo ""
echo "Testing Vedic API connectivity..."
echo ""

# Run the test script
/usr/bin/python3 test_api_calls.py
