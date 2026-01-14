import sqlite3
import os

db_path = r"A:\workspace\To-do\Crawler_Practice\backend\data\crawler_tasks.db"

def check_users():
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Table 'users' does not exist.")
            conn.close()
            return

        cursor.execute("SELECT id, username, email, is_admin, is_active FROM users")
        users = cursor.fetchall()
        
        print(f"\nTotal Users: {len(users)}")
        print("-" * 60)
        print(f"{'ID':<38} | {'Username':<15} | {'Email':<25} | {'Admin':<5}")
        print("-" * 60)
        
        for user in users:
            uid, username, email, is_admin, is_active = user
            print(f"{uid:<38} | {username:<15} | {email if email else 'N/A':<25} | {str(bool(is_admin)):<5}")
            
        conn.close()
        
    except Exception as e:
        print(f"Error querying database: {e}")

if __name__ == "__main__":
    check_users()
