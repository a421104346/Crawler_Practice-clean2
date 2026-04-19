import type {
  CrawlerInfo,
  FirecrawlScrapeRequest,
  FirecrawlScrapeResponse,
  FirecrawlWeiboHotRankRequest,
  FirecrawlWeiboHotRankResponse,
  RunCrawlerRequest,
  StatsResponse,
  Task,
  User
} from '@/types';

interface DemoUserRecord extends User {
  password: string;
}

interface DemoState {
  users: DemoUserRecord[];
  tasks: Task[];
}

const DEMO_STATE_KEY = 'crawler_demo_state_v1';
const DEFAULT_ADMIN_USERNAME = 'admin';
const DEFAULT_ADMIN_PASSWORD = 'admin123';

const demoCrawlers: CrawlerInfo[] = [
  {
    name: 'yahoo',
    display_name: 'Yahoo Finance',
    description: 'Fetches stock quote data (demo mode uses mock output).',
    parameters: ['symbol'],
    optional_parameters: [],
    status: 'active'
  },
  {
    name: 'movies',
    display_name: 'Douban Movies',
    description: 'Fetches movie list data (demo mode uses mock output).',
    parameters: [],
    optional_parameters: ['max_pages'],
    status: 'active'
  },
  {
    name: 'jobs',
    display_name: 'Remotive Jobs',
    description: 'Fetches remote job listings (demo mode uses mock output).',
    parameters: [],
    optional_parameters: ['search', 'category'],
    status: 'active'
  },
  {
    name: 'weibo',
    display_name: 'Weibo Hot Search',
    description: 'Playwright crawler example (demo mode uses mock output).',
    parameters: [],
    optional_parameters: [],
    status: 'active'
  },
  {
    name: 'rednote',
    display_name: 'Xiaohongshu Discovery',
    description: 'Playwright crawler example (demo mode uses mock output).',
    parameters: [],
    optional_parameters: [],
    status: 'active'
  },
  {
    name: 'prosettings',
    display_name: 'ProSettings',
    description: 'Fetches player settings (demo mode uses mock output).',
    parameters: [],
    optional_parameters: [],
    status: 'active'
  }
];

const makeId = (): string => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return `demo-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

const nowIso = (): string => new Date().toISOString();

const makeBase64 = (value: string): string => {
  if (typeof btoa === 'function') {
    return btoa(value);
  }
  return value;
};

const parseBase64 = (value: string): string => {
  if (typeof atob === 'function') {
    return atob(value);
  }
  return value;
};

const toPublicUser = (record: DemoUserRecord): User => ({
  id: record.id,
  username: record.username,
  email: record.email,
  is_active: record.is_active,
  is_admin: record.is_admin,
  created_at: record.created_at,
  updated_at: record.updated_at,
  last_login: record.last_login
});

const makeDefaultState = (): DemoState => {
  const admin: DemoUserRecord = {
    id: 'demo-admin',
    username: DEFAULT_ADMIN_USERNAME,
    email: 'admin@example.com',
    password: DEFAULT_ADMIN_PASSWORD,
    is_active: true,
    is_admin: true,
    created_at: nowIso(),
    updated_at: nowIso()
  };
  return { users: [admin], tasks: [] };
};

let memoryState: DemoState = makeDefaultState();

const loadDemoState = (): DemoState => {
  if (typeof window === 'undefined') {
    return memoryState;
  }
  try {
    const raw = localStorage.getItem(DEMO_STATE_KEY);
    if (!raw) {
      localStorage.setItem(DEMO_STATE_KEY, JSON.stringify(memoryState));
      return memoryState;
    }
    const parsed = JSON.parse(raw) as DemoState;
    if (!Array.isArray(parsed.users) || !Array.isArray(parsed.tasks)) {
      return memoryState;
    }
    memoryState = parsed;
    return parsed;
  } catch {
    return memoryState;
  }
};

const saveDemoState = (state: DemoState): void => {
  memoryState = state;
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.setItem(DEMO_STATE_KEY, JSON.stringify(state));
};

const createToken = (username: string): string => {
  const expiresAt = Math.floor(Date.now() / 1000) + 60 * 60 * 24 * 7;
  const payload = makeBase64(JSON.stringify({ sub: username, exp: expiresAt }));
  return `demo.${payload}.signature`;
};

const parseTokenUsername = (): string | null => {
  if (typeof window === 'undefined') {
    return null;
  }
  const token = localStorage.getItem('access_token');
  if (!token) {
    return null;
  }
  try {
    const [, payload] = token.split('.');
    if (!payload) {
      return null;
    }
    const parsed = JSON.parse(parseBase64(payload)) as { sub?: string };
    return parsed.sub ?? null;
  } catch {
    return null;
  }
};

const buildTaskResult = (crawlerType: string, params: RunCrawlerRequest): Record<string, unknown> => ({
  crawler: crawlerType,
  summary: `Demo result generated for ${crawlerType}`,
  params,
  generated_at: nowIso(),
  items: [
    { title: 'Demo item 1', score: 98 },
    { title: 'Demo item 2', score: 93 },
    { title: 'Demo item 3', score: 89 }
  ]
});

const createDemoTask = (crawlerType: string, params: RunCrawlerRequest): Task => {
  const username = parseTokenUsername();
  const state = loadDemoState();
  const user = state.users.find((item) => item.username === username);
  const createdAt = nowIso();
  return {
    id: makeId(),
    crawler_type: crawlerType,
    status: 'completed',
    progress: 100,
    params: params ?? {},
    result: buildTaskResult(crawlerType, params),
    error: null,
    created_at: createdAt,
    started_at: createdAt,
    completed_at: createdAt,
    duration: 0.4,
    user_id: user?.id ?? null
  };
};

export const demoAuthApi = {
  login: async (username: string, password: string) => {
    const state = loadDemoState();
    const found = state.users.find((user) => user.username === username && user.password === password);
    if (!found) {
      throw new Error('Invalid username or password');
    }
    return {
      access_token: createToken(found.username),
      token_type: 'bearer',
      expires_in: 60 * 60 * 24 * 7
    };
  },

  register: async (username: string, email: string | null, password: string) => {
    const state = loadDemoState();
    if (state.users.some((user) => user.username === username)) {
      throw new Error('Username already exists');
    }
    const newUser: DemoUserRecord = {
      id: makeId(),
      username,
      email,
      password,
      is_active: true,
      is_admin: false,
      created_at: nowIso(),
      updated_at: nowIso()
    };
    saveDemoState({ ...state, users: [newUser, ...state.users] });
    return { ok: true };
  },

  getCurrentUser: async (): Promise<User> => {
    const state = loadDemoState();
    const username = parseTokenUsername();
    const user = state.users.find((item) => item.username === username);
    if (!user) {
      throw new Error('User not found');
    }
    return toPublicUser(user);
  },

  logout: async () => ({ ok: true })
};

export const demoTaskApi = {
  createTask: async (crawlerType: string, params: RunCrawlerRequest) => {
    const task = createDemoTask(crawlerType, params);
    const state = loadDemoState();
    saveDemoState({ ...state, tasks: [task, ...state.tasks] });
    return { task_id: task.id };
  },

  getTasks: async (page = 1, pageSize = 20) => {
    const state = loadDemoState();
    const start = (page - 1) * pageSize;
    const tasks = state.tasks.slice(start, start + pageSize);
    return {
      total: state.tasks.length,
      tasks,
      page,
      page_size: pageSize
    };
  },

  list: async (params: { page: number; page_size: number }) => {
    return demoTaskApi.getTasks(params.page, params.page_size);
  },

  get: async (taskId: string) => {
    const state = loadDemoState();
    const task = state.tasks.find((item) => item.id === taskId);
    if (!task) {
      throw new Error('Task not found');
    }
    return task;
  },

  getTask: async (taskId: string) => demoTaskApi.get(taskId),

  cancelTask: async (taskId: string) => {
    const state = loadDemoState();
    const nextTasks = state.tasks.map((task) =>
      task.id === taskId ? { ...task, status: 'cancelled' as const, progress: task.progress ?? 0 } : task
    );
    saveDemoState({ ...state, tasks: nextTasks });
    return { ok: true };
  },

  delete: async (taskId: string) => {
    const state = loadDemoState();
    saveDemoState({ ...state, tasks: state.tasks.filter((task) => task.id !== taskId) });
    return { ok: true };
  },

  deleteTask: async (taskId: string) => demoTaskApi.delete(taskId)
};

export const demoCrawlerApi = {
  list: async () => demoCrawlers,
  getCrawlers: async () => demoCrawlers,
  getCrawlerInfo: async (crawlerType: string) => {
    const crawler = demoCrawlers.find((item) => item.name === crawlerType);
    if (!crawler) {
      throw new Error('Crawler not found');
    }
    return crawler;
  },
  run: async (crawlerType: string, params: RunCrawlerRequest) => {
    const created = await demoTaskApi.createTask(crawlerType, params);
    return { ...created, status: 'completed' };
  }
};

export const demoAdminApi = {
  getUsers: async () => {
    const state = loadDemoState();
    return state.users.map(toPublicUser);
  },

  deleteUser: async (userId: string) => {
    const state = loadDemoState();
    const nextUsers = state.users.filter((user) => user.id !== userId);
    const nextTasks = state.tasks.filter((task) => task.user_id !== userId);
    saveDemoState({ users: nextUsers, tasks: nextTasks });
    return { ok: true };
  },

  getAllTasks: async (page = 1, pageSize = 20) => {
    const state = loadDemoState();
    const start = (page - 1) * pageSize;
    const tasks = state.tasks.slice(start, start + pageSize);
    const totalPages = Math.max(1, Math.ceil(state.tasks.length / pageSize));
    return {
      tasks,
      total: state.tasks.length,
      page,
      page_size: pageSize,
      total_pages: totalPages
    };
  },

  deleteTask: async (taskId: string) => demoTaskApi.delete(taskId)
};

export const demoMonitoringApi = {
  stats: async (): Promise<StatsResponse> => {
    const state = loadDemoState();
    const total = state.tasks.length;
    const completed = state.tasks.filter((task) => task.status === 'completed').length;
    const failed = state.tasks.filter((task) => task.status === 'failed').length;
    const running = state.tasks.filter((task) => task.status === 'running').length;
    const successRate = total > 0 ? completed / total : 0;
    return {
      tasks: {
        total,
        completed,
        failed,
        running,
        success_rate: successRate
      },
      uptime: 'Demo mode'
    };
  },

  health: async () => ({ status: 'healthy', mode: 'demo' }),
  detailedHealth: async () => ({ status: 'healthy', mode: 'demo' }),
  metrics: async () => ({ mode: 'demo' })
};

const demoScreenshot =
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sL6r8EAAAAASUVORK5CYII=';

export const demoFirecrawlApi = {
  scrape: async (payload: FirecrawlScrapeRequest): Promise<FirecrawlScrapeResponse> => {
    const format = payload.formats?.[0] ?? 'markdown';
    const data: Record<string, unknown> = {
      metadata: {
        title: 'Demo Firecrawl Result',
        sourceURL: payload.url,
        statusCode: 200
      }
    };

    if (format === 'screenshot') {
      data.screenshot = demoScreenshot;
    } else if (format === 'html' || format === 'rawHtml') {
      data[format] = `<html><body><h1>Demo scrape for ${payload.url}</h1><p>Generated in demo mode.</p></body></html>`;
    } else {
      data[format] = `# Demo Firecrawl Output\n\n- URL: ${payload.url}\n- Mode: demo\n- Time: ${nowIso()}`;
    }

    return { success: true, data };
  },

  weiboHotRank1: async (_payload: FirecrawlWeiboHotRankRequest): Promise<FirecrawlWeiboHotRankResponse> => ({
    success: true,
    data: {
      topic_title: 'Demo Hot Topic',
      topic_url: 'https://s.weibo.com/top/summary?cate=realtimehot',
      pages: 1,
      total_posts: 3,
      posts: [
        {
          username: 'demo_user_1',
          user_link: 'https://weibo.com',
          content: 'Demo post content 1'
        },
        {
          username: 'demo_user_2',
          user_link: 'https://weibo.com',
          content: 'Demo post content 2'
        },
        {
          username: 'demo_user_3',
          user_link: 'https://weibo.com',
          content: 'Demo post content 3'
        }
      ]
    }
  })
};
