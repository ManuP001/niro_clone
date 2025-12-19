# Getting Your VEDIC_API_KEY and Testing Kundli

## Step 1: Get Your API Key

### Option A: Free Plan (Recommended for Testing)
1. Visit: https://api.vedicastroapi.com/
2. Click "Sign Up" or "Get Started"
3. Create a free account
4. Go to Dashboard → API Keys
5. Copy your API key

### Option B: Get a Trial Key
- Contact: support@vedicastroapi.com
- Request a trial/test key

---

## Step 2: Set Environment Variable

### For Current Terminal Session Only
```bash
export VEDIC_API_KEY="your-actual-api-key-here"
```

**Then verify it's set:**
```bash
echo $VEDIC_API_KEY
```

You should see your API key printed.

### For Permanent (Add to ~/.zshrc)
```bash
# Add this line to ~/.zshrc
echo 'export VEDIC_API_KEY="your-api-key"' >> ~/.zshrc

# Then reload
source ~/.zshrc
```

---

## Step 3: Run the Test Script

```bash
# Make sure you're in the project root
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch

# Run the test
/usr/bin/python3 test_api_calls.py
```

**Expected Output:**
```
╔════════════════════════════════════════════════════════════╗
║              API AND COMPONENT TESTING                    ║
╚════════════════════════════════════════════════════════════╝

TESTING VEDIC API CLIENT
Test Birth Details:
  DOB: 1990-01-15
  TOB: 14:30
  Location: Mumbai
  Lat/Lon: 19.076/72.8777

Test 1: Missing API Key
❌ (This will still work - tests error handling)

Test 2: With API Key (Real API Call)
✅ Successfully fetched profile:
   Ascendant: Capricorn (19.2°)
   Planets: 9 total
   Houses: 12
   Yogas: ... (number depends on chart)

TESTING KUNDLI SVG FETCH
✅ Successfully fetched SVG:
   Size: 45000 characters
   Contains <svg>: <svg xmlns='...'
   Chart Type: kundli
   Vendor: VedicAstroAPI
```

---

## Step 4: Start the Backend Server

Once API key is working, start the backend:

```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch/backend

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the server
python3 -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 5: Start the Frontend

In a new terminal:

```bash
cd /Users/sharadharjai/Documents/GitHub/niro-ai-launch/frontend

# Install dependencies (if needed)
npm install

# Start development server
npm start
```

You should see:
```
On Your Network: http://localhost:3000
```

---

## Step 6: Test the Kundli Screen

1. Open http://localhost:3000 in your browser
2. Login with test credentials
3. Complete onboarding with birth details:
   - **Date of Birth:** January 15, 1990
   - **Time of Birth:** 14:30
   - **Place:** Mumbai, India
4. Go to Home screen
5. **Tap the "Kundli" button** in the bottom navigation
6. You should see:
   - Birth chart SVG (visual representation)
   - Ascendant details
   - Planets list
   - Houses list

---

## Troubleshooting

### "VEDIC_API_KEY is not set"
```bash
# Check if it's set
echo $VEDIC_API_KEY

# If empty, set it
export VEDIC_API_KEY="your-key-here"
```

### "API key is invalid"
- Double-check you copied the full key (no extra spaces)
- Make sure it's from vedicastroapi.com (not another provider)
- Check that your account is active

### "Connection refused"
- Make sure backend server is running on port 8000
- Check firewall settings
- Try `curl http://localhost:8000/api/health`

### "Kundli button not appearing"
- Make sure you're logged in
- Make sure you completed onboarding (profile_complete = true)
- Check browser console for errors (F12)

### "SVG not rendering"
- Check Network tab in browser DevTools
- Make sure `/api/kundli` returns 200 status
- Check that SVG is properly formatted

---

## Quick Test Commands

```bash
# Test 1: Check API key is set
echo $VEDIC_API_KEY

# Test 2: Run the test script
/usr/bin/python3 test_api_calls.py

# Test 3: Test API endpoint (requires running backend + valid JWT)
curl -H "Authorization: Bearer $JWT_TOKEN" \
     http://localhost:8000/api/kundli

# Test 4: Check backend is running
curl http://localhost:8000/api/health
```

---

## API Key Sources

| Provider | URL | Free Tier | Speed |
|----------|-----|-----------|-------|
| **VedicAstroAPI** (Used) | https://api.vedicastroapi.com/ | ✅ Yes | Fast |
| AstroSage | https://www.astrosage.com/ | Limited | Medium |
| IndicSoft | https://www.indicsoft.com/ | ✅ Yes | Slow |

---

## Next Steps

1. **Get API Key** → Sign up at vedicastroapi.com
2. **Set Environment Variable** → `export VEDIC_API_KEY="..."`
3. **Run Test** → `/usr/bin/python3 test_api_calls.py`
4. **Start Backend** → `python3 -m uvicorn server:app --reload`
5. **Start Frontend** → `npm start`
6. **Open App** → http://localhost:3000
7. **Login & Complete Onboarding**
8. **Tap Kundli Button** → See your birth chart!

---

**Need Help?**
- Check the API test results: `cat API_TEST_RESULTS.md`
- Check Kundli implementation: `cat KUNDLI_SVG_IMPLEMENTATION.md`
- Review backend logs: `tail -f logs/niro_pipeline.log`
