#!/bin/bash
# Database backup script

set -e

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="crawler_db"

mkdir -p $BACKUP_DIR

echo "================================"
echo "Database Backup"
echo "================================"

# PostgreSQL backup
if docker ps | grep -q crawler_postgres; then
    echo "Backing up PostgreSQL database..."
    docker exec crawler_postgres pg_dump -U crawler_user $DB_NAME > "$BACKUP_DIR/${DB_NAME}_${DATE}.sql"
    
    # Compress backup file
    gzip "$BACKUP_DIR/${DB_NAME}_${DATE}.sql"
    
    echo "✓ Backup complete: $BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"
else
    echo "Warning: PostgreSQL container is not running"
fi

# Clean up old backups (keep last 7 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
echo "✓ Cleaned up backups older than 7 days"
