# NIRO Pipeline Logging Guide

## 📊 Overview

Every chat message to `/api/chat` generates **one structured JSON log entry** in `/app/logs/niro_pipeline.log`.

This provides complete observability of:
- Topic classification (source, confidence, secondary topics)
- Astro profile usage (ascendant, moon sign, cached/fresh)
- Astro transit events
- Astro features extracted
- LLM payload summary
- LLM response summary

---

## 📍 Log Location

```bash
/app/logs/niro_pipeline.log
```

- **Format**: JSON lines (one JSON object per line)
- **Rotation**: Manual (no auto-rotation configured yet)
- **Permissions**: Read/write for backend process

---

## 📝 Log Entry Structure

```json
{
  "timestamp": "2025-12-10T08:42:44.792852+00:00Z",
  "session_id": "test-session-001",
  "user_id": "test-session-001",
  "user_message": "What about my love life?",
  "action_id": "focus_relationship",
  "mode": "FOCUS_READING",
  
  "topic_classification": {
    "source": "chip",                    // "llm", "chip", or "fallback"
    "topic": "romantic_relationships",   // Primary topic
    "secondary_topics": [],              // 0-2 secondary topics
    "confidence": 1.0,                   // 0.0-1.0
    "needs_clarification": false         // true if ambiguous
  },
  
  "astro_profile": {
    "used_cached": true,                 // Was profile cached?
    "ascendant": "Cancer",               // Rising sign
    "moon_sign": "Capricorn"            // Moon sign
  },
  
  "astro_transits": {
    "used_cached": true,                 // Were transits cached?
    "events_count": 31                   // Number of transit events
  },
  
  "astro_features_summary": {
    "has_features": true,                // Were features extracted?
    "focus_factors_count": 7,            // Planet/house factors
    "key_rules_ids": [                   // First 5 rule IDs
      "MAHADASHA_JUPITER",
      "TRANSIT_SATURN_INGRESS"
    ],
    "timing_windows_count": 1            // Timing windows
  },
  
  "llm_payload_summary": {
    "mode": "FOCUS_READING",
    "topic": "romantic_relationships",
    "has_astro_features": true           // Were features sent to LLM?
  },
  
  "llm_response_summary": {
    "summary_preview": "Your love life is...",  // First 120 chars
    "reasons_count": 4,                          // Number of reasons
    "remedies_count": 2                          // Number of remedies
  }
}
```

---

## 🔍 Quick Queries

### View Log Statistics
```bash
/app/view_logs.sh summary
```

### Recent Messages
```bash
/app/view_logs.sh recent 10
```

### Low Confidence Classifications
```bash
/app/view_logs.sh low-confidence
```

### Filter by Source
```bash
/app/view_logs.sh by-source llm
/app/view_logs.sh by-source chip
/app/view_logs.sh by-source fallback
```

### Full JSON Entry
```bash
/app/view_logs.sh full 1
```

### Watch in Real-Time
```bash
/app/view_logs.sh watch
```

---

## 🛠️ Advanced Queries with jq

### Find All Career Questions
```bash
cat /app/logs/niro_pipeline.log | jq 'select(.topic_classification.topic == "career")'
```

### Messages with Secondary Topics
```bash
cat /app/logs/niro_pipeline.log | jq 'select(.topic_classification.secondary_topics | length > 0)'
```

### Average Reasons per Response
```bash
cat /app/logs/niro_pipeline.log | jq -r '.llm_response_summary.reasons_count' | awk '{sum+=$1; count++} END {print sum/count}'
```

### Sessions with Cached Profiles
```bash
cat /app/logs/niro_pipeline.log | jq -r 'select(.astro_profile.used_cached == true) | .session_id' | sort -u
```

### Messages Requiring Clarification
```bash
cat /app/logs/niro_pipeline.log | jq 'select(.topic_classification.needs_clarification == true)'
```

### Group by Mode
```bash
cat /app/logs/niro_pipeline.log | jq -r '.mode' | sort | uniq -c
```

### Group by Ascendant
```bash
cat /app/logs/niro_pipeline.log | jq -r '.astro_profile.ascendant' | sort | uniq -c
```

---

## 📈 Analytics Queries

### Confidence Distribution
```bash
cat /app/logs/niro_pipeline.log | jq -r '.topic_classification.confidence' | \
  awk '{
    if($1>=0.9) high++; 
    else if($1>=0.7) medium++; 
    else low++
  } 
  END {
    print "High (≥0.9):", high; 
    print "Medium (0.7-0.9):", medium; 
    print "Low (<0.7):", low
  }'
```

### Topic Classification Accuracy (by source)
```bash
echo "=== LLM Classifications ==="
cat /app/logs/niro_pipeline.log | jq 'select(.topic_classification.source == "llm")' | jq -r '.topic_classification.topic' | sort | uniq -c

echo -e "\n=== Chip Overrides ==="
cat /app/logs/niro_pipeline.log | jq 'select(.topic_classification.source == "chip")' | jq -r '.topic_classification.topic' | sort | uniq -c
```

### Average Response Complexity
```bash
cat /app/logs/niro_pipeline.log | jq '{
  avg_reasons: ([.llm_response_summary.reasons_count] | add / length),
  avg_remedies: ([.llm_response_summary.remedies_count] | add / length),
  avg_features: ([.astro_features_summary.focus_factors_count] | add / length)
}' | jq -s 'add | {
  avg_reasons: (.avg_reasons / length),
  avg_remedies: (.avg_remedies / length),
  avg_features: (.avg_features / length)
}'
```

---

## 🔧 Maintenance

### Check Log Size
```bash
du -h /app/logs/niro_pipeline.log
```

### Count Entries
```bash
wc -l /app/logs/niro_pipeline.log
```

### Rotate Logs Manually
```bash
mv /app/logs/niro_pipeline.log /app/logs/niro_pipeline.$(date +%Y%m%d).log
# Restart backend to create new log file
sudo supervisorctl restart backend
```

### Clear Logs (CAUTION)
```bash
> /app/logs/niro_pipeline.log
```

---

## 🎯 Use Cases

### 1. Debug Classification Issues
Find messages with low confidence or fallback classifications:
```bash
cat /app/logs/niro_pipeline.log | \
  jq 'select(.topic_classification.confidence < 0.6 or .topic_classification.source == "fallback")'
```

### 2. Monitor LLM Performance
Track when LLM fails and falls back to keyword classifier:
```bash
cat /app/logs/niro_pipeline.log | \
  jq -r '.topic_classification.source' | \
  sort | uniq -c
```

### 3. Identify Ambiguous Questions
Find messages that need clarification:
```bash
cat /app/logs/niro_pipeline.log | \
  jq 'select(.topic_classification.needs_clarification == true) | .user_message'
```

### 4. Track Astro Features Usage
See how often different chart features are used:
```bash
cat /app/logs/niro_pipeline.log | \
  jq -r '.astro_features_summary.key_rules_ids[]' | \
  sort | uniq -c | sort -rn
```

### 5. User Session Analysis
Track a specific user's journey:
```bash
cat /app/logs/niro_pipeline.log | \
  jq 'select(.session_id == "test-session-001")'
```

---

## 📊 Exporting for Analysis

### Export to CSV
```bash
cat /app/logs/niro_pipeline.log | \
  jq -r '[
    .timestamp,
    .session_id,
    .mode,
    .topic_classification.topic,
    .topic_classification.confidence,
    .topic_classification.source,
    .astro_features_summary.focus_factors_count,
    .llm_response_summary.reasons_count
  ] | @csv' > /tmp/niro_logs.csv
```

### Export to JSON Array
```bash
cat /app/logs/niro_pipeline.log | jq -s '.' > /tmp/niro_logs_array.json
```

---

## 🚨 Troubleshooting

### No Logs Being Generated?
1. Check if log directory exists:
   ```bash
   ls -la /app/logs/
   ```

2. Check backend logs for errors:
   ```bash
   tail -f /var/log/supervisor/backend.err.log | grep NIRO_PIPELINE
   ```

3. Verify logging is enabled:
   ```bash
   grep -r "log_pipeline_event" /app/backend/
   ```

### Logs Not Formatted Correctly?
Check if jq is installed:
```bash
which jq || echo "jq not installed"
```

### Log File Too Large?
Implement log rotation or archive old logs:
```bash
# Archive logs older than 7 days
find /app/logs/ -name "niro_pipeline.*.log" -mtime +7 -exec gzip {} \;
```

---

## 🎓 Best Practices

1. **Monitor Daily**: Check log summary daily for anomalies
2. **Low Confidence Alert**: Set up alerts for messages with confidence < 0.5
3. **Regular Backups**: Back up logs before rotation
4. **Privacy**: Be cautious with user messages in logs (truncated to 200 chars)
5. **Analysis**: Run weekly analytics to improve classification

---

## 📚 Related Documentation

- **Enhancement Summary**: `/app/ENHANCEMENTS_SUMMARY.md`
- **VedicAPI Metrics**: `/app/VEDIC_API_METRICS.md`
- **Log Viewer Script**: `/app/view_logs.sh`

---

## 💡 Future Enhancements

1. **Auto Log Rotation**: Implement daily/weekly rotation
2. **Dashboard**: Build real-time analytics dashboard
3. **Alerts**: Set up monitoring for low confidence / errors
4. **Anonymization**: Hash user messages for privacy
5. **Export API**: Create endpoint to export logs
