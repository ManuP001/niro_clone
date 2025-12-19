# NIRO AI - Quick Reference Card

## 🚀 Quick Start

### Start Services
```bash
# Terminal 1: Backend (port 8000)
VEDIC_API_KEY="325a213f-91fe-5e28-8e89-4308a15075a1" python3 backend/server.py

# Terminal 2: Frontend (port 3000)
cd frontend && npm start
```

### Access Application
- **Web App**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🔑 API Endpoints

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| POST | /api/auth/identify | Login (no OTP) | ✅ |
| GET | /api/kundli | Birth chart | ✅ |
| POST | /api/chat | Chat with AI | ✅ |
| GET | /api/debug/checklist/{id} | Checklist report | ✅ |

---

## 🧪 One-Minute Test

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/identify \
  -H "Content-Type: application/json" \
  -d '{"identifier":"test@example.com"}' | jq -r '.token')

# 2. Test Kundli
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/kundli

# 3. Test Chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"sessionId":"test","message":"Hi","actionId":null}'
```

---

## 📱 User Flow

```
1. Login (no password)
   ↓
2. Complete Birth Details
   ↓
3. View Kundli (SVG chart)
   ↓
4. Chat with AI
   ↓
5. View Checklist Report
```

---

## 🔧 Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| VEDIC_API_KEY | Required | Astrological data |
| BACKEND_URL | http://localhost:8000 | API base URL |
| GEMINI_API_KEY | Optional | AI responses |
| MONGODB_URI | Optional | Data persistence |

---

## 📊 Features

- ✅ No-OTP Login
- ✅ JWT Auth
- ✅ Kundli SVG
- ✅ AI Chat
- ✅ Request Tracking
- ✅ Error Logging
- ✅ Profile Management

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | `pkill -f "python3.*server"` |
| Port 3000 in use | `pkill -f "npm start"` |
| Import errors | Update PYTHONPATH, install deps |
| MongoDB error | Optional - not required for testing |
| No response | Check servers are running |

---

## 📚 Documentation

- **SYSTEM_TEST_REPORT.md** - Full test results
- **TEST_COMMANDS.md** - All test commands
- **QUICK_START.md** - Detailed setup guide
- **TEST_COMPLETE.md** - Completion summary

---

## ✅ Status

**Production Ready** - All systems operational and tested.

Last Updated: December 16, 2025
