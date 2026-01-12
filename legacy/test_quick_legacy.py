"""
快速测试脚本：验证应用是否能正常启动
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试所有导入是否正常"""
    print("Testing imports...")
    
    try:
        from backend.config import settings
        print("[OK] Config import OK")
        
        from backend.database import Base, get_db, init_db
        print("[OK] Database import OK")
        
        from backend.models.task import TaskModel
        print("[OK] Models import OK")
        
        from backend.schemas.task import TaskResponse
        print("[OK] Schemas import OK")
        
        from backend.services.crawler_service import crawler_service
        print("[OK] Services import OK")
        
        from backend.crud.task import task_crud
        print("[OK] CRUD import OK")
        
        from backend.routers import crawlers, tasks, websocket, auth
        print("[OK] Routers import OK")
        
        from backend.main import app
        print("[OK] Main app import OK")
        
        print("\n[OK] All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crawler_service():
    """测试爬虫服务"""
    print("\n\nTesting crawler service...")
    
    try:
        from backend.services.crawler_service import crawler_service
        
        # 列出所有爬虫
        crawlers = crawler_service.list_crawlers()
        print(f"[OK] Found {len(crawlers)} crawlers:")
        for crawler in crawlers:
            print(f"  - {crawler.name}: {crawler.display_name}")
        
        # 测试获取爬虫信息
        yahoo_info = crawler_service.get_crawler_info("yahoo")
        if yahoo_info:
            print(f"[OK] Yahoo crawler info: {yahoo_info.name}")
        
        # 测试创建爬虫实例
        yahoo_crawler = crawler_service.get_crawler_instance("yahoo")
        print(f"[OK] Yahoo crawler instance created: {type(yahoo_crawler).__name__}")
        
        print("\n[OK] Crawler service test passed!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] Crawler service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """测试 API 路由"""
    print("\n\nTesting API routes...")
    
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        client = TestClient(app)
        
        # 测试根路径
        response = client.get("/")
        assert response.status_code == 200
        print(f"[OK] Root endpoint: {response.json()['message']}")
        
        # 测试健康检查
        response = client.get("/health")
        assert response.status_code == 200
        print(f"[OK] Health check: {response.json()['status']}")
        
        # 测试获取爬虫列表
        response = client.get("/api/crawlers")
        assert response.status_code == 200
        crawlers = response.json()
        print(f"[OK] Crawlers list: {len(crawlers)} crawlers available")
        
        # 测试登录
        response = client.post(
            "/api/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        print(f"[OK] Login successful: token received")
        
        # 测试获取任务列表
        response = client.get("/api/tasks")
        assert response.status_code == 200
        print(f"[OK] Tasks list: {response.json()['total']} tasks")
        
        print("\n[OK] API routes test passed!")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] API routes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*60)
    print("Phase 1 Quick Test")
    print("="*60)
    
    # 运行测试
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Crawler Service", test_crawler_service()))
    results.append(("API Routes", test_api_routes()))
    
    # 打印总结
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\nAll tests passed! Application is ready.")
        print("\nTo start the application:")
        print("  cd backend")
        print("  python main.py")
        print("\nOr:")
        print("  uvicorn backend.main:app --reload")
    else:
        print("\nSome tests failed. Please check the error messages.")
    
    sys.exit(0 if all_passed else 1)
