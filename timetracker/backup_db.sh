#!/bin/bash
# Backup script for PostgreSQL 16
# Run this BEFORE applying changes to docker-compose.yml

echo "Starting backup of existing database..."

# Load environment variables if .env exists
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Ensure backup directory exists
mkdir -p backups

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/dump_v16_${TIMESTAMP}.sql"

echo "Creating dump to $BACKUP_FILE..."

# Execute pg_dumpall inside the container
docker-compose exec -T db pg_dumpall -c -U ${POSTGRES_USER} > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Backup successful! File saved to: $BACKUP_FILE"
  echo "You can now verify the file size:"
  ls -lh "$BACKUP_FILE"
else
  echo "❌ Backup failed. Please check logs and try again."
  exit 1
fi
