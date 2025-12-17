#!/bin/bash
# Restore script for PostgreSQL 18.1
# Run this AFTER the new container is up and running

# Check if a backup file was provided
if [ -z "$1" ]; then
  echo "Usage: $0 backups/dump_v16_TIMESTAMP.sql"
  echo "Please provide the path to the backup file created by backup_db.sh"
  exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ File not found: $BACKUP_FILE"
  exit 1
fi

echo "Starting restore from $BACKUP_FILE..."

# Load environment variables if .env exists
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Execute psql inside the container to restore data
cat "$BACKUP_FILE" | docker-compose exec -T db psql -U ${POSTGRES_USER} -d postgres

if [ $? -eq 0 ]; then
  echo "✅ Restore successful!"
else
  echo "❌ Restore failed. Check logs above."
  exit 1
fi
