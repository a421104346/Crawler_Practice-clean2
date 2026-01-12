import asyncio
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, close_db, AsyncSessionLocal
from backend.crud.user import user_crud
from backend.crud.task import task_crud
from backend.schemas.auth import UserRegister
from backend.schemas.task import TaskCreate

async def test_schema():
    print("🚀 开始数据库 Schema 测试...")
    
    # 1. 初始化数据库
    try:
        await init_db()
        print("✅ 数据库初始化成功")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        return

    async with AsyncSessionLocal() as db:
        # 2. 创建用户
        print("\n👤 测试用户创建...")
        try:
            user_in = UserRegister(
                username="schema_test_user",
                email="test@schema.com",
                password="password123"
            )
            # 检查是否存在
            existing = await user_crud.get_by_username(db, user_in.username)
            if existing:
                print(f"   用户 {user_in.username} 已存在，跳过创建")
                user = existing
            else:
                user = await user_crud.create(db, user_in)
                print(f"✅ 用户创建成功: {user.id} ({user.username})")
        except Exception as e:
            print(f"❌ 用户创建失败: {e}")
            return

        # 3. 创建任务
        print("\n📋 测试任务创建 (带外键关联)...")
        try:
            task_in = TaskCreate(
                crawler_type="yahoo",
                params={"symbol": "TEST"}
            )
            task = await task_crud.create(db, task_in, user_id=user.id)
            print(f"✅ 任务创建成功: {task.id}")
            print(f"   关联用户ID: {task.user_id}")
        except Exception as e:
            print(f"❌ 任务创建失败: {e}")
            return

        # 4. 数据隔离测试
        print("\n🔒 测试数据隔离...")
        try:
            # 查该用户的任务
            tasks = await task_crud.get_multi(db, user_id=user.id)
            print(f"✅ 查询用户任务成功: 找到 {len(tasks)} 个任务")
            
            # 查不存在用户的任务
            fake_id = "fake-uuid-000"
            empty_tasks = await task_crud.get_multi(db, user_id=fake_id)
            print(f"✅ 查询其他用户任务: 找到 {len(empty_tasks)} 个任务 (预期为0)")
            
            assert len(tasks) > 0
            assert len(empty_tasks) == 0
            print("✅ 数据隔离验证通过")
        except Exception as e:
            print(f"❌ 数据隔离测试失败: {e}")

    await close_db()
    print("\n✨ 所有测试完成！Schema 正常工作。")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_schema())
