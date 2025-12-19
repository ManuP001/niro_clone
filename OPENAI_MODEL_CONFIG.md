# OpenAI Model Configuration

## Updated Model Settings

The NIRO AI system now uses environment variables to configure OpenAI models instead of hard-coded values. This allows you to easily switch to the latest OpenAI models without code changes.

---

## Environment Variables

### `OPENAI_EXTRACTION_MODEL`
- **Purpose**: Model used for structured birth details extraction
- **Default**: `gpt-4o` (latest OpenAI model)
- **Previous**: `gpt-4-turbo` (hard-coded)
- **File**: `backend/conversation/birth_extractor.py`
- **Use Case**: Precise extraction with temperature=0

**Example:**
```bash
export OPENAI_EXTRACTION_MODEL="gpt-4o"
# or use default with: python3 backend/server.py
```

### `OPENAI_API_MODEL`
- **Purpose**: Model used for chat responses and general LLM tasks
- **Default**: `gpt-4o` (latest OpenAI model)
- **Previous**: `gpt-4o-mini` (hard-coded)
- **File**: `backend/niro_agent.py`
- **Use Case**: Natural chat responses with temperature=0.7

**Example:**
```bash
export OPENAI_API_MODEL="gpt-4o"
# or use default with: python3 backend/server.py
```

---

## Quick Start

### Option 1: Use Defaults (Recommended)
```bash
# Uses gpt-4o for both extraction and chat
python3 backend/server.py
```

### Option 2: Custom Models
```bash
# Use specific models
export OPENAI_EXTRACTION_MODEL="gpt-4-turbo"
export OPENAI_API_MODEL="gpt-4-turbo"
python3 backend/server.py
```

### Option 3: Shell One-liner
```bash
OPENAI_API_MODEL="gpt-4o" OPENAI_EXTRACTION_MODEL="gpt-4o" python3 backend/server.py
```

---

## Latest OpenAI Models

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| `gpt-4o` | General purpose, latest | $$$ | Medium |
| `gpt-4o-mini` | Fast, budget-friendly | $ | Fast |
| `gpt-4-turbo` | Previous generation | $$$ | Medium |
| `o1` (preview) | Complex reasoning | $$$$ | Slow |

---

## Changes Made

### File: `backend/conversation/birth_extractor.py`
**Before:**
```python
EXTRACTION_MODEL_NAME = "gpt-4-turbo"
```

**After:**
```python
EXTRACTION_MODEL_NAME = os.environ.get('OPENAI_EXTRACTION_MODEL', 'gpt-4o')
```

### File: `backend/niro_agent.py`
**Before:**
```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    temperature=0.7
)
```

**After:**
```python
model_name = os.environ.get('OPENAI_API_MODEL', 'gpt-4o')
response = client.chat.completions.create(
    model=model_name,
    messages=messages,
    temperature=0.7
)
```

---

## Testing

### Verify Environment Variables are Being Used

```bash
# Start server with custom model
OPENAI_API_MODEL="gpt-4o" python3 backend/server.py &

# Check logs for model name in API calls
tail -f logs/niro_pipeline.log | grep -i "gpt-4o"
```

### Run Tests
```bash
# Tests will use the env var settings
VEDIC_API_KEY="..." python3 test_api_calls.py
```

---

## Benefits

✅ **Flexibility**: Change models without code changes  
✅ **Latest Models**: Easy to upgrade to new OpenAI models  
✅ **Cost Control**: Switch between expensive/cheap models  
✅ **Environment-Specific**: Different models for dev/prod  
✅ **Backward Compatible**: Default to latest model (gpt-4o)  

---

## Notes

- **Extraction Model** uses `temperature=0` for deterministic, structured output
- **Chat Model** uses `temperature=0.7` for natural, creative responses
- Both models fall back to Gemini API if available (primary), then OpenAI (fallback)
- Environment variables are read at server startup

---

**Updated**: December 16, 2025  
**Status**: ✅ Configuration updated to use latest OpenAI models
