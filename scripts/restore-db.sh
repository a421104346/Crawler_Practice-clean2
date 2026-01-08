#!/bin/bash
# 数据库恢复脚本

set -e

if [ -z "$1" ]; then
    echo "用法: ./restore-db.sh <备份文件>"
    echo "示例: ./restore-db.sh backups/crawler_db_20260108_120000.sql.gz"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

echo "================================"
echo "数据库恢复"
echo "================================"
echo "备份文件: $BACKUP_FILE"
echo ""
echo "警告: 这将覆盖当前数据库！"
read -p "是否继续？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "取消恢复"
    exit 0
fi

# 解压备份文件
if [[ $BACKUP_FILE == *.gz ]]; then
    echo "解压备份文件..."
    gunzip -c $BACKUP_FILE > /tmp/restore.sql
    SQL_FILE="/tmp/restore.sql"
else
    SQL_FILE=$BACKUP_FILE
fi

# 恢复数据库
echo "恢复数据库..."
docker exec -i crawler_postgres psql -U crawler_user crawler_db < $SQL_FILE

# 清理临时文件
rm -f /tmp/restore.sql

echo "✓ 数据库恢复完成"
