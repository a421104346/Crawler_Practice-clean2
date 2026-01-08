#!/bin/bash
# 数据库备份脚本

set -e

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="crawler_db"

mkdir -p $BACKUP_DIR

echo "================================"
echo "数据库备份"
echo "================================"

# PostgreSQL 备份
if docker ps | grep -q crawler_postgres; then
    echo "备份 PostgreSQL 数据库..."
    docker exec crawler_postgres pg_dump -U crawler_user $DB_NAME > "$BACKUP_DIR/${DB_NAME}_${DATE}.sql"
    
    # 压缩备份文件
    gzip "$BACKUP_DIR/${DB_NAME}_${DATE}.sql"
    
    echo "✓ 备份完成: $BACKUP_DIR/${DB_NAME}_${DATE}.sql.gz"
else
    echo "警告: PostgreSQL 容器未运行"
fi

# 清理旧备份（保留最近 7 天）
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete
echo "✓ 已清理 7 天前的备份"
