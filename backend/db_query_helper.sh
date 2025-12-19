#!/bin/bash
# MongoDB Query Helper Script
# Usage: ./db_query_helper.sh [command]

DB_NAME="astro_trust_db"
MONGO_URL="mongodb://localhost:27017"

case "$1" in
  "stats")
    echo "=== Database Statistics ==="
    mongosh $DB_NAME --quiet --eval "
      var collections = db.getCollectionNames();
      collections.forEach(function(col) {
        var count = db[col].countDocuments();
        print(col + ': ' + count + ' documents');
      });
    "
    ;;
  
  "users")
    echo "=== All Users ==="
    mongosh $DB_NAME --quiet --eval "
      db.users.find({}, {_id:0, user_id:1, name:1, email:1, gender:1, occupation:1, relationship_status:1}).forEach(u => printjson(u))
    "
    ;;
  
  "user")
    if [ -z "$2" ]; then
      echo "Usage: ./db_query_helper.sh user <user_id>"
      exit 1
    fi
    echo "=== User Details: $2 ==="
    mongosh $DB_NAME --quiet --eval "
      var user = db.users.findOne({user_id: '$2'}, {_id:0});
      printjson(user);
    "
    ;;
  
  "reports")
    echo "=== All Reports ==="
    mongosh $DB_NAME --quiet --eval "
      db.reports.find({}, {_id:0, report_id:1, user_id:1, report_type:1, status:1, processing_time_seconds:1}).sort({created_at:-1}).forEach(r => printjson(r))
    "
    ;;
  
  "report")
    if [ -z "$2" ]; then
      echo "Usage: ./db_query_helper.sh report <report_id>"
      exit 1
    fi
    echo "=== Report Details: $2 ==="
    mongosh $DB_NAME --quiet --eval "
      var report = db.reports.findOne({report_id: '$2'}, {_id:0});
      printjson(report);
    "
    ;;
  
  "transactions")
    echo "=== All Transactions ==="
    mongosh $DB_NAME --quiet --eval "
      db.transactions.find({}, {_id:0, transaction_id:1, user_id:1, report_type:1, amount:1, payment_status:1}).sort({created_at:-1}).forEach(t => printjson(t))
    "
    ;;
  
  "pricing")
    echo "=== Current Pricing ==="
    mongosh $DB_NAME --quiet --eval "
      db.pricing.find({}, {_id:0}).forEach(p => printjson(p))
    "
    ;;
  
  "count")
    if [ -z "$2" ]; then
      echo "Usage: ./db_query_helper.sh count <collection_name>"
      exit 1
    fi
    COUNT=$(mongosh $DB_NAME --quiet --eval "db.$2.countDocuments()")
    echo "$2: $COUNT documents"
    ;;
  
  "query")
    if [ -z "$2" ] || [ -z "$3" ]; then
      echo "Usage: ./db_query_helper.sh query <collection> '<query>'"
      echo "Example: ./db_query_helper.sh query users '{\"gender\": \"male\"}'"
      exit 1
    fi
    mongosh $DB_NAME --quiet --eval "db.$2.find($3, {_id:0}).forEach(doc => printjson(doc))"
    ;;
  
  "clear")
    if [ -z "$2" ]; then
      echo "Usage: ./db_query_helper.sh clear <collection_name>"
      echo "WARNING: This will delete all documents in the collection!"
      exit 1
    fi
    read -p "Are you sure you want to delete all documents from '$2'? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
      mongosh $DB_NAME --quiet --eval "db.$2.deleteMany({})"
      echo "Collection '$2' cleared."
    else
      echo "Operation cancelled."
    fi
    ;;
  
  "shell")
    echo "Opening MongoDB shell for database: $DB_NAME"
    mongosh $DB_NAME
    ;;
  
  *)
    echo "MongoDB Query Helper - astro_trust_db"
    echo
    echo "Database: $DB_NAME"
    echo "URL: $MONGO_URL"
    echo
    echo "Available commands:"
    echo "  stats                           - Show database statistics"
    echo "  users                           - List all users"
    echo "  user <user_id>                  - Show specific user details"
    echo "  reports                         - List all reports"
    echo "  report <report_id>              - Show specific report details"
    echo "  transactions                    - List all transactions"
    echo "  pricing                         - Show current pricing"
    echo "  count <collection>              - Count documents in collection"
    echo "  query <collection> '<query>'    - Custom query"
    echo "  clear <collection>              - Delete all documents (with confirmation)"
    echo "  shell                           - Open MongoDB shell"
    echo
    echo "Examples:"
    echo "  ./db_query_helper.sh stats"
    echo "  ./db_query_helper.sh user a5bd7ba0-cb1f-4285-ae7f-e5bccad4a12a"
    echo "  ./db_query_helper.sh query users '{\"gender\": \"male\"}'"
    ;;
esac
