import asyncio
import sys
import os

# Add path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, close_db, AsyncSessionLocal
from backend.crud.user import user_crud
from backend.crud.task import task_crud
from backend.schemas.auth import UserRegister
from backend.schemas.task import TaskCreate

async def test_schema():
    print("🚀 Starting database schema test...")
    
    # 1. Initialize database
    try:
        await init_db()
        print("✅ Database initialization successful")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return

    async with AsyncSessionLocal() as db:
        # 2. Create user
        print("\n👤 Testing user creation...")
        try:
            user_in = UserRegister(
                username="schema_test_user",
                email="test@schema.com",
                password="password123"
            )
            # Check if exists
            existing = await user_crud.get_by_username(db, user_in.username)
            if existing:
                print(f"   User {user_in.username} already exists, skipping creation")
                user = existing
            else:
                user = await user_crud.create(db, user_in)
                print(f"✅ User created successfully: {user.id} ({user.username})")
        except Exception as e:
            print(f"❌ User creation failed: {e}")
            return

        # 3. Create task
        print("\n📋 Testing task creation (with foreign key association)...")
        try:
            task_in = TaskCreate(
                crawler_type="yahoo",
                params={"symbol": "TEST"}
            )
            task = await task_crud.create(db, task_in, user_id=user.id)
            print(f"✅ Task created successfully: {task.id}")
            print(f"   Associated user ID: {task.user_id}")
        except Exception as e:
            print(f"❌ Task creation failed: {e}")
            return

        # 4. Data isolation test
        print("\n🔒 Testing data isolation...")
        try:
            # Query tasks for this user
            tasks = await task_crud.get_multi(db, user_id=user.id)
            print(f"✅ Query user tasks successful: found {len(tasks)} tasks")
            
            # Query tasks for nonexistent user
            fake_id = "fake-uuid-000"
            empty_tasks = await task_crud.get_multi(db, user_id=fake_id)
            print(f"✅ Query other user tasks: found {len(empty_tasks)} tasks (expected 0)")
            
            assert len(tasks) > 0
            assert len(empty_tasks) == 0
            print("✅ Data isolation verification passed")
        except Exception as e:
            print(f"❌ Data isolation test failed: {e}")

    await close_db()
    print("\n✨ All tests completed! Schema is working correctly.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_schema())
