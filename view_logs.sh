#!/bin/bash
# NIRO Pipeline Log Viewer

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           NIRO Pipeline Logs - Quick Viewer                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

LOG_FILE="/app/logs/niro_pipeline.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

case "${1:-summary}" in
    summary)
        echo "📊 SUMMARY"
        echo "────────────────────────────────────────────────────────────"
        echo "Total messages: $(wc -l < $LOG_FILE)"
        echo ""
        echo "Topic Classification Sources:"
        cat $LOG_FILE | jq -r '.topic_classification.source' | sort | uniq -c | awk '{printf "  %s: %d\n", $2, $1}'
        echo ""
        echo "Topics Detected:"
        cat $LOG_FILE | jq -r '.topic_classification.topic' | sort | uniq -c | awk '{printf "  %s: %d\n", $2, $1}'
        echo ""
        echo "Average Confidence: $(cat $LOG_FILE | jq -r '.topic_classification.confidence' | awk '{sum+=$1; count++} END {printf "%.2f\n", sum/count}')"
        ;;
    
    recent)
        echo "📋 RECENT MESSAGES (Last ${2:-5})"
        echo "────────────────────────────────────────────────────────────"
        tail -n ${2:-5} $LOG_FILE | jq -r '"\(.timestamp | split("T")[0]) \(.timestamp | split("T")[1] | split(".")[0]) | Session: \(.session_id | split("-")[-1]) | Mode: \(.mode) | Topic: \(.topic_classification.topic) (\(.topic_classification.confidence)) | Message: \(.user_message[:60])"'
        ;;
    
    low-confidence)
        echo "⚠️  LOW CONFIDENCE CLASSIFICATIONS (< 0.7)"
        echo "────────────────────────────────────────────────────────────"
        cat $LOG_FILE | jq -r 'select(.topic_classification.confidence < 0.7) | "\(.timestamp | split("T")[0]) | \(.topic_classification.topic) (\(.topic_classification.confidence)) | \(.user_message[:80])"'
        ;;
    
    by-source)
        SOURCE="${2:-llm}"
        echo "🔍 MESSAGES CLASSIFIED BY: $SOURCE"
        echo "────────────────────────────────────────────────────────────"
        cat $LOG_FILE | jq -r --arg src "$SOURCE" 'select(.topic_classification.source == $src) | "\(.topic_classification.topic) (\(.topic_classification.confidence)) | \(.user_message[:80])"'
        ;;
    
    full)
        echo "📄 FULL LOG (Last ${2:-1} entry)"
        echo "────────────────────────────────────────────────────────────"
        tail -n ${2:-1} $LOG_FILE | jq '.'
        ;;
    
    watch)
        echo "👁️  WATCHING LOG (Ctrl+C to stop)"
        echo "────────────────────────────────────────────────────────────"
        tail -f $LOG_FILE | while read line; do
            echo "$line" | jq -r '"\n[\(.timestamp | split("T")[1] | split(".")[0])] \(.mode) | \(.topic_classification.topic) (\(.topic_classification.source))\nUser: \(.user_message)\nSummary: \(.llm_response_summary.summary_preview)\n"'
        done
        ;;
    
    help|*)
        echo "Usage: $0 [command] [args]"
        echo ""
        echo "Commands:"
        echo "  summary              Show log statistics (default)"
        echo "  recent [N]           Show last N messages (default: 5)"
        echo "  low-confidence       Show classifications with confidence < 0.7"
        echo "  by-source [SOURCE]   Filter by source (llm, chip, fallback)"
        echo "  full [N]             Show full JSON for last N entries (default: 1)"
        echo "  watch                Watch logs in real-time"
        echo "  help                 Show this help"
        ;;
esac
