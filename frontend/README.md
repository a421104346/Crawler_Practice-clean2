# Crawler Management Platform - Frontend

A modern frontend application built with React + TypeScript + Vite.

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### Start Development Server

```bash
npm run dev
```

The app will start at http://localhost:3000.

### Build for Production

```bash
npm run build
```

Build output is in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── TaskCard.tsx     # Task card
│   │   └── CrawlerPanel.tsx # Crawler control panel
│   │
│   ├── pages/               # Page components
│   │   ├── Login.tsx        # Login page
│   │   ├── Register.tsx     # Registration page
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   └── History.tsx      # Task history
│   │
│   ├── hooks/               # Custom Hooks
│   │   └── useWebSocket.ts  # WebSocket Hook
│   │
│   ├── services/            # API services
│   │   └── api.ts           # Backend API wrapper
│   │
│   ├── store/               # State management
│   │   └── authStore.ts     # Auth state
│   │
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   │
│   ├── App.tsx              # Root component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
│
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## 🎨 Tech Stack

- **Framework**: React 18
- **Language**: TypeScript 5
- **Build Tool**: Vite 5
- **Routing**: React Router 6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Charts**: Recharts
- **Date Handling**: date-fns

## 🌟 Key Features

### 1. User Authentication
- Login / Registration
- JWT Token Management
- Protected routes

### 2. Crawler Management
- Select crawler type
- Configure parameters
- Start tasks

### 3. Real-time Progress
- WebSocket connection
- Real-time progress updates
- Auto reconnect

### 4. Task Management
- View task list
- Status filtering
- Delete tasks
- Download results

### 5. Data Visualization
- Task statistics charts
- Success rate display
- Task status distribution

## 🔧 Development Guide

### Code Standards

- Use TypeScript strict mode
- All components must have type definitions
- Use functional components + Hooks
- Follow React best practices

### Adding New Pages

1. Create new component in `src/pages/`
2. Add route in `App.tsx`
3. If protection needed, use `<ProtectedRoute>`

### Adding New APIs

1. Add API function in `src/services/api.ts`
2. Define related types in `src/types/index.ts`
3. Use in components

## 🐛 Debugging

### View Network Requests

Open browser DevTools → Network tab

### View WebSocket Connections

DevTools → Network → WS tab

### React DevTools

Install the React DevTools browser extension to debug component state.

## 📦 Build and Deploy

### Environment Variables

Create `.env` file:

```bash
VITE_API_URL=http://localhost:8000
```

### Build

```bash
npm run build
```

### Deploy to Nginx

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

## 🎯 Todo

- [ ] Add unit tests
- [ ] Add E2E tests
- [ ] Optimize performance (React.memo, lazy loading)
- [ ] Add dark mode
- [ ] Mobile responsive
- [ ] PWA support

---

**Phase 3 Frontend Complete!** 🎉
