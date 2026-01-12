# 快速启动指南

## 环境要求

- Python 3.10+
- pip

## 第一步：安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 第二步：启动应用

### 方法 1: 直接运行（推荐）

```bash
python main.py
```

### 方法 2: 使用 uvicorn

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

应用将在 http://localhost:8000 启动

## 第三步：访问 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 快速测试

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 获取爬虫列表

```bash
curl http://localhost:8000/api/crawlers
```

### 3. 登录获取 token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

默认账号：
- 用户名: `admin` 密码: `admin123`
- 用户名: `demo` 密码: `demo123`

### 4. 运行爬虫

#### Yahoo Finance 爬虫
```bash
curl -X POST "http://localhost:8000/api/crawlers/yahoo/run" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'
```

#### 豆瓣电影爬虫
```bash
curl -X POST "http://localhost:8000/api/crawlers/movies/run" \
  -H "Content-Type: application/json" \
  -d '{"max_pages": 1}'
```

#### 招聘爬虫
```bash
curl -X POST "http://localhost:8000/api/crawlers/jobs/run" \
  -H "Content-Type: application/json" \
  -d '{"search": "python"}'
```

响应会返回一个 `task_id`，用于查询任务状态。

### 5. 查看任务状态

```bash
curl "http://localhost:8000/api/tasks/{task_id}"
```

替换 `{task_id}` 为上一步返回的实际 task_id。

### 6. 获取任务列表

```bash
curl "http://localhost:8000/api/tasks?page=1&page_size=10"
```

## WebSocket 实时进度（前端示例）

```html
<!DOCTYPE html>
<html>
<head>
    <title>Crawler Progress</title>
</head>
<body>
    <h1>实时爬虫进度</h1>
    <div id="progress"></div>
    
    <script>
        // 替换为实际的 task_id
        const taskId = "YOUR_TASK_ID_HERE";
        const ws = new WebSocket(`ws://localhost:8000/ws/tasks/${taskId}`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const div = document.getElementById('progress');
            div.innerHTML = `
                <p>任务状态: ${data.status}</p>
                <p>进度: ${data.progress}%</p>
                <p>消息: ${data.message}</p>
            `;
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
```

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 跳过慢速测试
pytest tests/ -m "not slow" -v

# 运行特定测试
pytest tests/test_api_basic.py -v
```

## 常见问题

### 问题 1: 端口被占用

错误：`Address already in use`

解决方案：
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### 问题 2: 依赖安装失败

解决方案：
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像（中国大陆用户）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题 3: 数据库权限错误

解决方案：
```bash
# 确保当前目录可写
chmod 755 .  # Linux/Mac
```

## 项目结构

```
Crawler_Practice/
├── backend/                # FastAPI 后端
│   ├── main.py            # 主应用入口
│   ├── config.py          # 配置
│   ├── database.py        # 数据库
│   ├── models/            # 数据模型
│   ├── schemas/           # API 模型
│   ├── services/          # 业务逻辑
│   ├── crud/              # CRUD 操作
│   └── routers/           # API 路由
├── core/                  # 爬虫核心
│   └── base_crawler.py    # 基础爬虫类
├── crawlers/              # 具体爬虫
│   ├── yahoo.py           # Yahoo Finance
│   ├── movies.py          # 豆瓣电影
│   └── jobs.py            # 招聘爬虫
├── tests/                 # 测试
└── README.md              # 完整文档
```

## 下一步

- 阅读 [README.md](README.md) 了解完整功能
- 阅读 [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) 查看完成情况
- 访问 http://localhost:8000/docs 探索所有 API

## 获取帮助

- 查看 API 文档: http://localhost:8000/docs
- 查看日志输出了解详细信息
- 检查 `crawler_tasks.db` 数据库文件

---

**Phase 1 完成！开始探索吧！** 🚀
