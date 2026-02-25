#!/bin/bash
# Database restore script

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore-db.sh <backup-file>"
    echo "Example: ./restore-db.sh backups/crawler_db_20260108_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "================================"
echo "Database Restore"
echo "================================"
echo "Backup file: $BACKUP_FILE"
echo ""
echo "Warning: This will overwrite the current database!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

# Decompress backup file
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "Decompressing backup file..."
    gunzip -c $BACKUP_FILE > /tmp/restore.sql
    SQL_FILE="/tmp/restore.sql"
else
    SQL_FILE=$BACKUP_FILE
fi

# Restore database
echo "Restoring database..."
docker exec -i crawler_postgres psql -U crawler_user crawler_db < $SQL_FILE

# Clean up temp files
rm -f /tmp/restore.sql

echo "✓ Database restore complete"
