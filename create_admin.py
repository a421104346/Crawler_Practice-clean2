import asyncio
import sys
import os
from passlib.context import CryptContext

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import AsyncSessionLocal
from backend.models.user import UserModel
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    print("Creating admin user...")
    
    # 从环境变量读取，避免硬编码默认口令
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not username or not email or not password:
        print("Missing admin credentials. Please set:")
        print("  ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD")
        return

    print(f"Using credentials for: {username}")
    
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(select(UserModel).where(UserModel.username == username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User {username} already exists.")
            
            # Reset password
            existing_user.hashed_password = pwd_context.hash(password)
            print("Password reset completed.")
            
            if not existing_user.is_admin:
                existing_user.is_admin = True
                await db.commit()
                print(f"User {username} promoted to admin.")
            else:
                await db.commit()
                print(f"User {username} is already an admin.")
            return

        # Create new admin user
        hashed_password = pwd_context.hash(password)
        new_user = UserModel(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True
        )
        
        db.add(new_user)
        await db.commit()
        print(f"Admin user {username} created successfully!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_admin())
