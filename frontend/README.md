# 爬虫管理平台 - 前端

基于 React + TypeScript + Vite 的现代化前端应用。

## 🚀 快速开始

### 安装依赖

```bash
npm install
# 或
yarn install
# 或
pnpm install
```

### 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:3000 启动。

### 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 预览生产版本

```bash
npm run preview
```

## 📁 项目结构

```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── TaskCard.tsx     # 任务卡片
│   │   └── CrawlerPanel.tsx # 爬虫控制面板
│   │
│   ├── pages/               # 页面组件
│   │   ├── Login.tsx        # 登录页
│   │   ├── Register.tsx     # 注册页
│   │   ├── Dashboard.tsx    # 主仪表板
│   │   └── History.tsx      # 任务历史
│   │
│   ├── hooks/               # 自定义 Hooks
│   │   └── useWebSocket.ts  # WebSocket Hook
│   │
│   ├── services/            # API 服务
│   │   └── api.ts           # 后端 API 封装
│   │
│   ├── store/               # 状态管理
│   │   └── authStore.ts     # 认证状态
│   │
│   ├── types/               # TypeScript 类型
│   │   └── index.ts
│   │
│   ├── App.tsx              # 根组件
│   ├── main.tsx             # 入口文件
│   └── index.css            # 全局样式
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🎨 技术栈

- **框架**: React 18
- **语言**: TypeScript 5
- **构建工具**: Vite 5
- **路由**: React Router 6
- **状态管理**: Zustand
- **HTTP 客户端**: Axios
- **样式**: Tailwind CSS
- **图标**: Lucide React
- **图表**: Recharts
- **日期处理**: date-fns

## 🌟 主要功能

### 1. 用户认证
- 登录 / 注册
- JWT Token 管理
- 受保护的路由

### 2. 爬虫管理
- 选择爬虫类型
- 设置参数
- 启动任务

### 3. 实时进度
- WebSocket 连接
- 实时进度更新
- 自动重连

### 4. 任务管理
- 任务列表查看
- 状态过滤
- 删除任务
- 下载结果

### 5. 数据可视化
- 任务统计图表
- 成功率显示
- 任务状态分布

## 🔧 开发指南

### 代码规范

- 使用 TypeScript 严格模式
- 所有组件必须有类型定义
- 使用函数式组件 + Hooks
- 遵循 React 最佳实践

### 添加新页面

1. 在 `src/pages/` 创建新组件
2. 在 `App.tsx` 添加路由
3. 如需保护，使用 `<ProtectedRoute>`

### 添加新 API

1. 在 `src/services/api.ts` 添加 API 函数
2. 定义相关类型在 `src/types/index.ts`
3. 在组件中使用

## 🐛 调试

### 查看网络请求

打开浏览器开发者工具 → Network 标签

### 查看 WebSocket 连接

开发者工具 → Network → WS 标签

### React DevTools

安装 React DevTools 浏览器扩展以调试组件状态。

## 📦 构建和部署

### 环境变量

创建 `.env` 文件：

```bash
VITE_API_URL=http://localhost:8000
```

### 构建

```bash
npm run build
```

### 部署到 Nginx

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /var/www/crawler-frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🎯 待办事项

- [ ] 添加单元测试
- [ ] 添加 E2E 测试
- [ ] 优化性能（React.memo, lazy loading）
- [ ] 添加暗黑模式
- [ ] 移动端适配
- [ ] PWA 支持

---

**Phase 3 前端已完成！** 🎉
