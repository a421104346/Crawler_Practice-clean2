# 2个月FastAPI+React全栈学习计划（生产级爬虫系统）

## 核心决策与理由

### 为什么选FastAPI？

**关键数据（2025年）：**
- FastAPI采用率增长40%（从29% → 38%）[来源：最新行业数据]
- 性能：15,000-20,000 req/s vs Flask的2,000-3,000 req/s
- 你的爬虫项目是I/O密集型 → FastAPI完美适配
- 一次学习，职业生涯受用

**避免的陷阱：**
- ❌ 先学Flask，3个月后发现性能/功能不足，重新学FastAPI
- ✅ 直接学FastAPI，不用回头

### 架构最终方案

```
┌─────────────────────────────────────┐
│   React 前端                        │  (TypeScript)
│   ├─ 爬虫控制面板                   │
│   ├─ 实时进度/统计                  │
│   ├─ 结果展示和下载                 │
│   └─ 任务历史管理                   │
└──────────────┬──────────────────────┘
               │ HTTP + WebSocket
               ▼
┌─────────────────────────────────────┐
│   FastAPI 后端 (Async)              │
│   ├─ RESTful API                    │
│   ├─ WebSocket 实时推送             │
│   ├─ JWT 认证                       │
│   ├─ 后台任务管理                   │
│   └─ 数据验证 (Pydantic)            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   核心爬虫库（你现有的）             │
│   ├─ BaseCrawler                    │
│   ├─ YahooCrawler                   │
│   ├─ MoviesCrawler                  │
│   ├─ JobsCrawler                    │
│   └─ ...                            │
└─────────────────────────────────────┘
       │ 异步调用
       ▼
  Celery + Redis (可选第三阶段升级)
```

---

## 第1阶段：FastAPI + 异步编程基础（2周）

### Week 1：Python异步编程 + FastAPI入门

**Day 1-2：Python Async/Await 深度理解**

核心概念学习（不只是表面学习）：
```python
# 1. 理解事件循环
import asyncio

async def task_1():
    print("Task 1 start")
    await asyncio.sleep(2)  # 模拟I/O等待
    print("Task 1 done")
    return "Result 1"

async def task_2():
    print("Task 2 start")
    await asyncio.sleep(1)
    print("Task 2 done")
    return "Result 2"

# 并发执行（不是并行！）
async def main():
    # 两个任务并发运行（交替执行）
    result1, result2 = await asyncio.gather(task_1(), task_2())
    print(f"Results: {result1}, {result2}")
    # 总耗时 ~2秒（而非3秒）

asyncio.run(main())

# 关键点：Task 1和Task 2交替执行，当Task 1等待时Task 2运行
```

学习材料：
- 官方文档：https://docs.python.org/3/library/asyncio.html
- 重点：事件循环、await、gather、create_task、as_completed

练习1：写一个能同时爬5个股票的异步函数
```python
import asyncio
import httpx  # 异步HTTP库

async def fetch_stock(symbol: str):
    """异步爬取单个股票"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/stock/{symbol}")
        return response.json()

async def fetch_multiple_stocks(symbols: list):
    """并发爬取多个股票"""
    tasks = [fetch_stock(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    return results

# 测试
asyncio.run(fetch_multiple_stocks(['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']))
```

**Day 3-4：FastAPI基础**

安装和快速开始：
```bash
pip install fastapi uvicorn pydantic httpx
```

第一个FastAPI应用：
```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import asyncio

app = FastAPI(title="爬虫API")

# 1. 定义数据模型（自动验证和文档）
class CrawlerRequest(BaseModel):
    crawler_type: str
    symbol: Optional[str] = None
    page: Optional[int] = 1
    
    class Config:
        example = {
            "crawler_type": "yahoo",
            "symbol": "AAPL"
        }

class CrawlerResponse(BaseModel):
    task_id: str
    status: str
    message: str

# 2. 定义路由
@app.get("/")
async def root():
    """根路由"""
    return {"message": "爬虫管理系统"}

@app.get("/crawlers")
async def list_crawlers():
    """列出所有爬虫"""
    return {
        "crawlers": ["yahoo", "movies", "jobs", "douban", "weather", "news"]
    }

@app.post("/api/crawlers/{crawler_type}/run")
async def run_crawler(crawler_type: str, request: CrawlerRequest):
    """启动爬虫任务"""
    if crawler_type not in ["yahoo", "movies", "jobs"]:
        return {"error": "Unknown crawler"}, 404
    
    return CrawlerResponse(
        task_id="uuid-123",
        status="started",
        message=f"Started {crawler_type} crawler"
    )

@app.get("/docs")  # 自动生成的API文档

# 运行：uvicorn main:app --reload
```

关键特性理解：
- ✅ **自动验证** - Pydantic模型自动验证输入
- ✅ **自动文档** - 访问 http://localhost:8000/docs
- ✅ **类型提示** - IDE自动补全，类型检查
- ✅ **异步原生** - 所有路由天生支持async

练习2：创建一个能接收股票代码的FastAPI端点
```python
from fastapi import HTTPException

@app.post("/api/analyze/{symbol}")
async def analyze_stock(symbol: str, days: int = 30):
    """分析股票"""
    if not symbol or len(symbol) > 5:
        raise HTTPException(status_code=400, detail="Invalid symbol")
    
    # 模拟异步分析
    await asyncio.sleep(0.5)
    
    return {
        "symbol": symbol,
        "days": days,
        "trend": "up",
        "volatility": 0.15
    }
```

**Day 5-6：FastAPI + 你的爬虫整合**

创建爬虫包装器：
```python
# backend/app.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
from typing import Dict
import uuid
from datetime import datetime

# 导入你现有的爬虫
import sys
sys.path.insert(0, '../')
from core.base_crawler import BaseCrawler
from crawlers.yahoo import YahooCrawler
from crawlers.movies import MoviesCrawler

app = FastAPI(title="爬虫管理系统")

# 任务存储（第二阶段升级到数据库）
tasks_db: Dict = {}

@app.post("/api/crawlers/{crawler_type}/run")
async def run_crawler(
    crawler_type: str,
    background_tasks: BackgroundTasks,
    request: dict
):
    """启动爬虫（后台运行）"""
    
    task_id = str(uuid.uuid4())
    
    # 后台任务
    background_tasks.add_task(
        execute_crawler,
        task_id=task_id,
        crawler_type=crawler_type,
        params=request
    )
    
    tasks_db[task_id] = {
        "status": "pending",
        "crawler": crawler_type,
        "created_at": datetime.now().isoformat()
    }
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_db[task_id]

async def execute_crawler(task_id: str, crawler_type: str, params: dict):
    """后台爬虫执行"""
    try:
        tasks_db[task_id]["status"] = "running"
        
        if crawler_type == "yahoo":
            crawler = YahooCrawler(**params)
        elif crawler_type == "movies":
            crawler = MoviesCrawler(**params)
        else:
            raise ValueError("Unknown crawler")
        
        # 运行爬虫（同步转异步）
        result = await asyncio.to_thread(crawler.run)
        
        tasks_db[task_id] = {
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat()
        }
    except Exception as e:
        tasks_db[task_id] = {
            "status": "failed",
            "error": str(e)
        }

# 运行
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Day 7-14：巩固 + 项目整合**

- 创建FastAPI项目目录结构
- 集成所有6个爬虫
- 添加错误处理、日志
- 编写单元测试

---

### Week 2：WebSocket实时通信 + 认证

**Day 8-9：WebSocket实时进度推送**

为什么需要WebSocket？
- HTTP轮询：每500ms发一次请求，浪费带宽
- WebSocket：建立持久连接，实时推送进度

```python
from fastapi import WebSocket

# 存储活跃连接
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """广播进度到所有连接"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

@app.websocket("/ws/crawler/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket端点：实时推送爬虫进度"""
    await manager.connect(websocket)
    try:
        while True:
            # 接收前端消息（例如暂停/取消）
            data = await websocket.receive_text()
            
            if task_id in tasks_db:
                # 推送当前状态
                await websocket.send_json(tasks_db[task_id])
            
            await asyncio.sleep(0.2)
    except:
        manager.disconnect(websocket)

# 爬虫执行时，实时广播进度
async def execute_crawler_with_progress(task_id: str, crawler_type: str):
    """改进的爬虫执行（带进度推送）"""
    try:
        crawler = get_crawler(crawler_type)
        
        # 假设爬虫支持进度回调
        def progress_callback(current, total, message=""):
            progress = int((current / total) * 100)
            
            # 广播进度
            asyncio.create_task(
                broadcast_to_clients(task_id, {
                    "status": "running",
                    "progress": progress,
                    "message": message
                })
            )
        
        crawler.set_progress_callback(progress_callback)
        result = await asyncio.to_thread(crawler.run)
        
        await broadcast_to_clients(task_id, {
            "status": "completed",
            "result": result,
            "progress": 100
        })
    except Exception as e:
        await broadcast_to_clients(task_id, {
            "status": "failed",
            "error": str(e)
        })

async def broadcast_to_clients(task_id: str, message: dict):
    """广播进度给订阅该任务的所有客户端"""
    for connection in manager.active_connections:
        await connection.send_json({
            "task_id": task_id,
            **message
        })
```

**Day 10-11：JWT认证与授权**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from datetime import datetime, timedelta
import jwt

# 配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    """生成JWT token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)):
    """验证JWT token"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# 登录端点
@app.post("/api/login")
async def login(username: str, password: str):
    """登录获取token"""
    # 简单验证（实际应用应使用数据库）
    if username == "admin" and password == "password":
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# 保护的端点
@app.get("/api/my-tasks")
async def get_my_tasks(user_id: str = Depends(get_current_user)):
    """只有认证用户才能访问"""
    # 返回该用户的任务
    return {"user_id": user_id, "tasks": []}
```

**Day 12-14：集成和测试**

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_crawlers():
    response = client.get("/crawlers")
    assert response.status_code == 200
    assert "yahoo" in response.json()["crawlers"]

def test_run_crawler():
    response = client.post(
        "/api/crawlers/yahoo/run",
        json={"symbol": "AAPL"}
    )
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_get_task_status():
    # 先启动任务
    run_response = client.post("/api/crawlers/yahoo/run", json={})
    task_id = run_response.json()["task_id"]
    
    # 获取状态
    status_response = client.get(f"/api/tasks/{task_id}")
    assert status_response.status_code == 200

def test_invalid_crawler():
    response = client.post(
        "/api/crawlers/invalid/run",
        json={}
    )
    assert response.status_code == 404

# 运行测试
# pytest tests/test_api.py -v
```

---

## 第2阶段：生产级部署 + 数据库集成（2周）

### Week 3：数据库 + 任务队列

**Day 15-16：SQLAlchemy + SQLite**

```python
# backend/database.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./crawler_tasks.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class TaskModel(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    crawler_type = Column(String)
    status = Column(String)  # pending, running, completed, failed
    progress = Column(Integer, default=0)
    result = Column(Text)
    error = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

Base.metadata.create_all(bind=engine)

# 使用示例
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 在路由中使用
from fastapi import Depends
from sqlalchemy.orm import Session

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404)
    return {
        "task_id": task.id,
        "status": task.status,
        "progress": task.progress
    }
```

**Day 17-18：Celery + Redis（可选但推荐）**

为什么需要任务队列？
- 处理长时间运行的任务
- 支持分布式处理
- 任务持久化和重试

```python
# backend/celery_app.py
from celery import Celery
import time

celery_app = Celery(
    "crawler_system",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def run_crawler_task(task_id: str, crawler_type: str, params: dict):
    """Celery任务：后台运行爬虫"""
    try:
        # 更新任务状态为运行中
        update_task_status(task_id, "running", 0)
        
        crawler = get_crawler(crawler_type)
        
        # 模拟进度
        for i in range(1, 101):
            time.sleep(0.1)  # 模拟工作
            update_task_status(task_id, "running", i)
        
        result = crawler.run()
        update_task_status(task_id, "completed", 100, result=result)
    except Exception as e:
        update_task_status(task_id, "failed", error=str(e))

# 在FastAPI中使用
@app.post("/api/crawlers/{crawler_type}/run")
async def run_crawler(crawler_type: str, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    
    # 创建数据库记录
    task = TaskModel(id=task_id, crawler_type=crawler_type, status="pending")
    db.add(task)
    db.commit()
    
    # 提交到Celery队列
    run_crawler_task.delay(task_id, crawler_type, {})
    
    return {"task_id": task_id}

# 启动Celery worker
# celery -A backend.celery_app worker --loglevel=info
```

安装：
```bash
pip install celery redis sqlalchemy
```

**Day 19-21：生产部署配置**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 生产部署命令
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
```

```bash
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
celery==5.3.4
redis==5.0.1
gunicorn==21.2.0
pytest==7.4.3
python-jose==3.3.0
httpx==0.25.2
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - postgres
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/crawler_db
      REDIS_URL: redis://redis:6379/0
  
  celery:
    build: ./backend
    command: celery -A celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/crawler_db
      REDIS_URL: redis://redis:6379/0
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: crawler_db
    ports:
      - "5432:5432"
```

---

### Week 4：React前端开发

**Day 22-23：React + TypeScript基础**

```tsx
// frontend/src/App.tsx
import React, { useState, useEffect } from 'react';
import './App.css';

interface Task {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  crawler: string;
}

const App: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedCrawler, setSelectedCrawler] = useState('yahoo');
  const [loading, setLoading] = useState(false);

  // 启动爬虫
  const handleRunCrawler = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/crawlers/yahoo/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: 'AAPL' })
      });
      const data = await response.json();
      
      // 连接WebSocket
      connectWebSocket(data.task_id);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  // WebSocket连接
  const connectWebSocket = (taskId: string) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/crawler/${taskId}`);
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setTasks(prev => {
        const existing = prev.find(t => t.task_id === taskId);
        if (existing) {
          return prev.map(t => 
            t.task_id === taskId ? { ...t, ...message } : t
          );
        }
        return [...prev, { task_id: taskId, ...message }];
      });
    };
  };

  return (
    <div className="app">
      <h1>🕷️ 爬虫管理系统</h1>
      
      <div className="control-panel">
        <select 
          value={selectedCrawler}
          onChange={(e) => setSelectedCrawler(e.target.value)}
        >
          <option>yahoo</option>
          <option>movies</option>
          <option>jobs</option>
        </select>
        
        <button onClick={handleRunCrawler} disabled={loading}>
          {loading ? '启动中...' : '▶️ 开始爬取'}
        </button>
      </div>

      <div className="tasks-container">
        {tasks.map(task => (
          <TaskCard key={task.task_id} task={task} />
        ))}
      </div>
    </div>
  );
};

interface TaskCardProps {
  task: Task;
}

const TaskCard: React.FC<TaskCardProps> = ({ task }) => {
  return (
    <div className={`task-card task-${task.status}`}>
      <h3>{task.crawler} - {task.task_id.substring(0, 8)}</h3>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${task.progress}%` }}></div>
      </div>
      <p>{task.progress}% - {task.status}</p>
    </div>
  );
};

export default App;
```

```css
/* frontend/src/App.css */
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, sans-serif;
}

.control-panel {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.control-panel select,
.control-panel button {
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.control-panel button {
  background: #007bff;
  color: white;
  cursor: pointer;
  transition: background 0.3s;
}

.control-panel button:hover {
  background: #0056b3;
}

.tasks-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.task-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.task-card.task-completed {
  border-color: #28a745;
  background: #f0fff4;
}

.task-card.task-failed {
  border-color: #dc3545;
  background: #fff5f5;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  margin: 10px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #007bff, #0056b3);
  transition: width 0.3s;
}
```

**Day 24-25：React高级功能**

```tsx
// frontend/src/hooks/useCrawler.ts
import { useState, useCallback } from 'react';

export const useCrawler = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);

  const runCrawler = useCallback(async (crawlerType: string, params: any) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/crawlers/${crawlerType}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      const data = await response.json();
      const taskId = data.task_id;

      // 订阅WebSocket
      subscribeToTask(taskId);

      return taskId;
    } finally {
      setLoading(false);
    }
  }, []);

  const subscribeToTask = (taskId: string) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/crawler/${taskId}`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTasks(prev => {
        const existing = prev.find((t: any) => t.task_id === taskId);
        if (existing) {
          return prev.map((t: any) => 
            t.task_id === taskId ? { ...t, ...data } : t
          );
        }
        return [...prev, { task_id: taskId, ...data }];
      });
    };
  };

  return { tasks, loading, runCrawler };
};

// frontend/src/components/CrawlerForm.tsx
import React, { useState } from 'react';
import { useCrawler } from '../hooks/useCrawler';

interface CrawlerFormProps {
  crawlerType: string;
}

const CrawlerForm: React.FC<CrawlerFormProps> = ({ crawlerType }) => {
  const { runCrawler, loading } = useCrawler();
  const [params, setParams] = useState({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await runCrawler(crawlerType, params);
  };

  return (
    <form onSubmit={handleSubmit}>
      {crawlerType === 'yahoo' && (
        <input
          type="text"
          placeholder="输入股票代码"
          onChange={(e) => setParams({ ...params, symbol: e.target.value })}
        />
      )}
      
      <button type="submit" disabled={loading}>
        {loading ? '启动中...' : '启动爬虫'}
      </button>
    </form>
  );
};

export default CrawlerForm;
```

**Day 26-28：集成和优化**

- Redux / Zustand 状态管理
- 错误处理和重试逻辑
- 结果导出功能
- 深色模式支持

---

## 第3阶段：爬虫项目集成（1周）

**Day 29-32：完整集成**

```
Crawler_Practice/
├── backend/                     # FastAPI后端
│   ├── main.py
│   ├── celery_app.py
│   ├── database.py
│   ├── models/
│   │   ├── crawler.py
│   │   └── task.py
│   ├── routes/
│   │   ├── crawlers.py
│   │   ├── tasks.py
│   │   └── auth.py
│   ├── services/
│   │   └── crawler_service.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                    # React前端
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── core/                        # 你现有的爬虫核心库
│   ├── __init__.py
│   ├── base_crawler.py
│   └── utils.py
│
├── crawlers/                    # 你现有的所有爬虫
│   ├── __init__.py
│   ├── yahoo.py
│   ├── movies.py
│   ├── jobs.py
│   └── ...
│
├── outputs/                     # 数据输出
├── docker-compose.yml
├── README.md
└── .gitignore
```

整合示例：
```python
# backend/services/crawler_service.py
from typing import Dict, Any
import sys
sys.path.insert(0, '../../')

from crawlers.yahoo import YahooCrawler
from crawlers.movies import MoviesCrawler
from crawlers.jobs import JobsCrawler
from core.base_crawler import BaseCrawler

CRAWLER_MAP = {
    'yahoo': YahooCrawler,
    'movies': MoviesCrawler,
    'jobs': JobsCrawler,
}

class CrawlerService:
    @staticmethod
    def get_crawler(crawler_type: str, params: Dict[str, Any]) -> BaseCrawler:
        """根据类型获取爬虫实例"""
        if crawler_type not in CRAWLER_MAP:
            raise ValueError(f"Unknown crawler: {crawler_type}")
        
        Crawler = CRAWLER_MAP[crawler_type]
        return Crawler(**params)
    
    @staticmethod
    async def run_crawler_async(crawler_type: str, params: Dict[str, Any]):
        """异步运行爬虫"""
        import asyncio
        crawler = CrawlerService.get_crawler(crawler_type, params)
        
        # 在线程池中运行爬虫（爬虫本身是同步的）
        result = await asyncio.to_thread(crawler.run)
        return result
```

---

## 第4阶段：优化、测试、部署（2周）

**Day 33-38：测试和优化**

```python
# tests/integration_test.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestCrawlerAPI:
    def test_list_crawlers(self):
        response = client.get("/api/crawlers")
        assert response.status_code == 200
        crawlers = response.json()["crawlers"]
        assert "yahoo" in crawlers

    def test_run_yahoo_crawler(self):
        response = client.post(
            "/api/crawlers/yahoo/run",
            json={"symbol": "AAPL", "days": 30}
        )
        assert response.status_code == 200
        assert "task_id" in response.json()

    def test_get_task_status(self):
        # 启动任务
        run_response = client.post(
            "/api/crawlers/yahoo/run",
            json={"symbol": "MSFT"}
        )
        task_id = run_response.json()["task_id"]
        
        # 获取状态
        status_response = client.get(f"/api/tasks/{task_id}")
        assert status_response.status_code == 200
        assert status_response.json()["task_id"] == task_id

    @pytest.mark.asyncio
    async def test_concurrent_crawlers(self):
        """并发运行多个爬虫"""
        import asyncio
        
        tasks = []
        for symbol in ["AAPL", "MSFT", "GOOGL"]:
            response = client.post(
                "/api/crawlers/yahoo/run",
                json={"symbol": symbol}
            )
            tasks.append(response.json()["task_id"])
        
        # 验证所有任务都启动了
        assert len(tasks) == 3
```

性能优化：
```python
# backend/performance_tips.py

# 1. 缓存爬虫实例
from functools import lru_cache

@lru_cache(maxsize=10)
def get_cached_crawler(crawler_type: str):
    return CRAWLER_MAP[crawler_type]

# 2. 使用连接池
from httpx import AsyncClient, Limits

# 配置限制
limits = Limits(max_connections=100, max_keepalive_connections=20)
async_client = AsyncClient(limits=limits)

# 3. 异步批处理
async def batch_crawl_stocks(symbols: list):
    """并发爬取多个股票"""
    import asyncio
    tasks = [
        asyncio.create_task(fetch_stock(symbol))
        for symbol in symbols
    ]
    return await asyncio.gather(*tasks)
```

**Day 39-42：文档和部署**

```markdown
# 爬虫管理系统 - 完整指南

## 快速启动

### 本地开发
```bash
# 1. 启动后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 2. 启动前端（新终端）
cd frontend
npm install
npm start

# 3. (可选) 启动Celery worker
celery -A celery_app worker --loglevel=info
```

### Docker部署
```bash
docker-compose up
```

## API文档
访问 http://localhost:8000/docs

## 架构说明
[详细的架构设计文档]

## 贡献指南
[如何添加新爬虫]
```

部署到云服务（例如Render、Heroku）：
```yaml
# render.yaml
services:
  - type: web
    name: crawler-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app"
    
  - type: background_worker
    name: crawler-worker
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "celery -A celery_app worker"
```

---

## 学习资源清单

### FastAPI
- 官方文档：https://fastapi.tiangolo.com/
- 推荐教程：https://www.freecodecamp.org/news/fastapi-quick-start/
- 深度异步：https://realpython.com/async-io-python/

### React + TypeScript
- 官方文档：https://react.dev/
- TypeScript指南：https://www.typescriptlang.org/docs/
- React Pattern：https://patterns.dev/posts/

### DevOps
- Docker：https://docs.docker.com/
- Docker Compose：https://docs.docker.com/compose/
- Gunicorn/Uvicorn：https://gunicorn.org/

---

## 预期学习成果

✅ 掌握现代异步Python开发（FastAPI）
✅ 理解前后端分离架构
✅ 能够构建生产级REST API
✅ 熟悉WebSocket实时通信
✅ 掌握JWT认证和授权
✅ 了解Docker容器化和部署
✅ 基础React + TypeScript开发
✅ 实现了一个完整的项目（简历亮点）

## 职业价值

- **460 Media面试**：展示现代全栈技能
- **技术面**：能深入讨论异步、性能优化、系统设计
- **GitHub**：有一个完整项目作为作品集
- **未来升级**：可轻松扩展到Kubernetes、微服务等

---

## 常见问题

**Q: 2个月够不够？**
A: 完全够。第1周掌握基础，第2周集成爬虫，第3-4周优化和部署。如果需要加快，可跳过部分React高级特性。

**Q: 需要先学会React吗？**
A: 不需要。可以用简单的HTML+JavaScript替代React，或参考我提供的代码。

**Q: 部署很难吗？**
A: 不难。Docker-Compose一键启动，部署到Render/AWS只需改几个配置。

**Q: 爬虫的改造成本高吗？**
A: 低。只需在爬虫外包装一个异步接口，爬虫本身不需改动。

---

## 时间表总结

| 周 | 任务 | 时间投入 |
|----|------|--------|
| 1-2 | FastAPI + 异步 + 爬虫集成 | 60小时 |
| 3-4 | 生产级部署 + 数据库 | 50小时 |
| 5 | React前端开发 | 40小时 |
| 6 | 集成 + 优化 | 35小时 |
| 7-8 | 测试 + 文档 + 部署 | 35小时 |
| **总计** | | **220小时** |

**按每天8小时学习计算 = 27.5天 = ~4周**

所以2个月足够有余，还能打磨细节。

---

**现在就开始吧！** 🚀
