# Phase 6: Next.js Analytics Dashboard (New Project)

## Goal

Create a new Next.js webapp project (`dzzlo_analytics`) that serves as the analytics dashboard. It consumes the Phase 4 query APIs and presents rich visualizations: KPI cards, time-series charts, funnel visualizations, retention grids, live event feeds, and session explorers.

## Prerequisites

- Phase 4 complete (query APIs available)
- Phase 5 recommended (pre-computed data for fast historical queries)

## Deliverables

- New Next.js project (`dzzlo_analytics/`) alongside existing projects
- Authentication via existing JWT (SuperAdmin only)
- 6 dashboard pages with interactive charts
- Responsive layout optimized for desktop use

---

## Step 6.1: Project Setup

**Location:** Create at `/251130_v1_76_100_env/dzzlo_analytics/`

```bash
npx create-next-app@latest dzzlo_analytics --typescript --tailwind --eslint --app --src-dir
```

### Tech Stack

- **Next.js 15** (App Router)
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Recharts** or **Tremor** for charts (Tremor recommended -- built on Recharts + Tailwind, has pre-built dashboard components)
- **Axios** for API calls to dzzlo_oms_api
- **date-fns** for date manipulation
- **JWT decode** for auth token parsing

### Dependencies to Install

```bash
npm install @tremor/react recharts axios date-fns jwt-decode
npm install -D @types/recharts
```

### Project Structure

```
dzzlo_analytics/
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Root layout with sidebar nav
│   │   ├── page.tsx                # Redirect to /dashboard
│   │   ├── login/
│   │   │   └── page.tsx            # Login page
│   │   ├── dashboard/
│   │   │   ├── page.tsx            # Overview KPIs
│   │   │   ├── layout.tsx          # Dashboard layout with sidebar
│   │   │   ├── live/
│   │   │   │   └── page.tsx        # Live event feed
│   │   │   ├── funnels/
│   │   │   │   └── page.tsx        # Funnel analysis
│   │   │   ├── retention/
│   │   │   │   └── page.tsx        # Retention cohort grid
│   │   │   ├── sessions/
│   │   │   │   └── page.tsx        # Session explorer
│   │   │   ├── events/
│   │   │   │   └── page.tsx        # Event explorer
│   │   │   └── users/
│   │   │       ├── page.tsx        # User activity list
│   │   │       └── [userId]/
│   │   │           └── page.tsx    # User timeline
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx         # Navigation sidebar
│   │   │   ├── Header.tsx          # Top header with date picker
│   │   │   └── AuthGuard.tsx       # Auth wrapper component
│   │   ├── charts/
│   │   │   ├── KPICard.tsx         # Metric card with sparkline
│   │   │   ├── TimeSeriesChart.tsx # Line/area chart for trends
│   │   │   ├── FunnelChart.tsx     # Horizontal funnel bars
│   │   │   ├── RetentionGrid.tsx   # Color-coded cohort table
│   │   │   ├── EventTable.tsx      # Sortable event list
│   │   │   └── SessionTimeline.tsx # Session detail timeline
│   │   └── filters/
│   │       ├── DateRangePicker.tsx  # Date range selection
│   │       ├── CompanyFilter.tsx   # Company dropdown
│   │       └── RoleFilter.tsx      # Role filter
│   ├── lib/
│   │   ├── api.ts                  # Axios instance + API helpers
│   │   ├── auth.ts                 # JWT auth utilities
│   │   └── types.ts                # TypeScript interfaces
│   └── hooks/
│       ├── useAnalytics.ts         # Data fetching hooks
│       └── useAuth.ts              # Auth state hook
├── .env.local                      # API URL config
├── .env.production
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

---

## Step 6.2: Environment Configuration

### `.env.local` (development)

```
NEXT_PUBLIC_API_URL=http://localhost:8030
NEXT_PUBLIC_API_VERSION=/api/v3
```

### `.env.production`

```
NEXT_PUBLIC_API_URL=https://doms.vsyst.in
NEXT_PUBLIC_API_VERSION=/api/v3
```

---

## Step 6.3: API Client

### `src/lib/api.ts`

```typescript
import axios from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL
const API_VERSION = process.env.NEXT_PUBLIC_API_VERSION

const api = axios.create({
  baseURL: `${API_URL}${API_VERSION}`,
  timeout: 15000,
})

// Attach JWT token from localStorage
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("analytics_token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // Use the same API key as the mobile app
  config.headers["x-api-key"] = process.env.NEXT_PUBLIC_API_KEY || ""
  return config
})

// Handle 401 — redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("analytics_token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  },
)

// Type imports (defined in types.ts)
import type {
  OverviewParams,
  EventCountParams,
  LiveEventParams,
  FunnelParams,
  RetentionParams,
  SessionParams,
  UserActivityParams,
  TimelineParams,
} from "./types"

// Analytics API methods
export const analyticsAPI = {
  // Auth
  login: (email: string, password: string) => api.post("/auth/loginrx", { email, password }),

  // Query endpoints (from Phase 4)
  getOverview: (params?: OverviewParams) => api.get("/analytics/query/overview", { params }),

  getEventCounts: (params: EventCountParams) =>
    api.get("/analytics/query/events/count", { params }),

  getLiveEvents: (params?: LiveEventParams) => api.get("/analytics/query/events/live", { params }),

  getFunnel: (params: FunnelParams) => api.get("/analytics/query/funnel", { params }),

  getRetention: (params?: RetentionParams) => api.get("/analytics/query/retention", { params }),

  getSessions: (params?: SessionParams) => api.get("/analytics/query/sessions", { params }),

  getUserActivity: (params?: UserActivityParams) =>
    api.get("/analytics/query/users/activity", { params }),

  getUserTimeline: (userId: string, params?: TimelineParams) =>
    api.get(`/analytics/query/users/${userId}/timeline`, { params }),
}

export default api
```

### Key design decisions

1. **Separate Axios instance** -- the dashboard's API client is independent from mobile app logic, with its own interceptors and error handling.
2. **Token key `analytics_token`** -- deliberately different from any key the mobile app might use, avoiding collisions if both run on the same domain during development.
3. **Automatic 401 redirect** -- if the token expires mid-session, the user is sent to the login page without a crash.
4. **15-second timeout** -- generous enough for heavy aggregation queries (retention, funnels) that may run long on first request before Phase 5 caching kicks in.

---

## Step 6.4: TypeScript Types

### `src/lib/types.ts`

```typescript
// ─── API Response Types ────────────────────────────────────

export interface OverviewData {
  dau: number
  wau: number
  mau: number
  events_today: number
  avg_session_duration_ms: number
  top_events: { _id: string; count: number }[]
}

export interface EventCount {
  period: string // ISO date string for the period start
  event_name: string
  count: number
  unique_users: number
}

export interface LiveEvent {
  _id: string
  event_name: string
  event_category: string
  event_properties: Record<string, any>
  screen_name: string
  user_id: string
  user_role: string
  device_os: string
  app_version: string
  server_timestamp: string
  session_id: string
}

export interface FunnelStep {
  step_index: number
  event_name: string
  users: number
  conversion_rate: string // e.g. "84.4%"
  overall_rate: string // e.g. "55.6%" (from step 0)
}

export interface FunnelData {
  steps: FunnelStep[]
  total_users: number
  date_range: { from: string; to: string }
}

export interface RetentionCohort {
  cohort_start: string // ISO date
  cohort_end: string // ISO date
  cohort_size: number
  retention: {
    period_index: number // 0, 1, 2, ...
    active_users: number
    retention_rate: string // e.g. "62.0%"
  }[]
}

export interface Session {
  _id: string
  session_id: string
  user_id: { _id: string; username: string; email: string }
  started_at: string
  ended_at: string
  duration_ms: number
  event_count: number
  screens_visited: string[]
  app_version: string
  device_os: string
  device_brand: string
}

export interface UserActivity {
  _id: string
  user_id: string
  event_count: number
  session_count: number
  first_active: string
  last_active: string
  roles: string[]
  devices: string[]
  user_info: {
    username: string
    email: string
    phone: string
    role: string
  }
}

// ─── API Request Param Types ───────────────────────────────

export interface OverviewParams {
  company_id?: string
  date?: string // ISO date, defaults to today
}

export interface EventCountParams {
  event_name?: string
  group_by: "hour" | "day" | "week" | "month"
  from: string // ISO date
  to: string // ISO date
  company_id?: string
  role?: string
}

export interface LiveEventParams {
  limit?: number // default 50
  event_name?: string
  event_category?: string
  role?: string
  device_os?: string
}

export interface FunnelParams {
  steps: string // comma-separated event names
  from: string
  to: string
  company_id?: string
}

export interface RetentionParams {
  period: "week" | "month"
  cohorts?: number // default 8
  company_id?: string
}

export interface SessionParams {
  from?: string
  to?: string
  user_id?: string
  min_duration_ms?: number
  max_duration_ms?: number
  page?: number
  limit?: number
}

export interface UserActivityParams {
  sort_by?: "event_count" | "last_active" | "session_count"
  order?: "asc" | "desc"
  search?: string // search by email or username
  page?: number
  limit?: number
}

export interface TimelineParams {
  from?: string
  to?: string
  event_category?: string
  page?: number
  limit?: number
}
```

---

## Step 6.5: Authentication

### `src/components/layout/AuthGuard.tsx`

```typescript
'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { jwtDecode } from 'jwt-decode';

interface DecodedToken {
  exp: number;
  role: string;
  userId: string;
  email: string;
}

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('analytics_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const decoded = jwtDecode<DecodedToken>(token);

      // Check expiry
      if (decoded.exp * 1000 < Date.now()) {
        localStorage.removeItem('analytics_token');
        router.push('/login');
        return;
      }

      // Check role — SuperAdmin only
      if (decoded.role !== 'superadmin') {
        localStorage.removeItem('analytics_token');
        router.push('/login');
        return;
      }

      setIsAuthed(true);
    } catch {
      localStorage.removeItem('analytics_token');
      router.push('/login');
    }
  }, [router]);

  if (!isAuthed) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  return <>{children}</>;
}
```

### `src/hooks/useAuth.ts`

```typescript
"use client"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { jwtDecode } from "jwt-decode"
import { analyticsAPI } from "@/lib/api"

interface AuthUser {
  userId: string
  email: string
  role: string
}

export function useAuth() {
  const router = useRouter()
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("analytics_token")
    if (token) {
      try {
        const decoded: any = jwtDecode(token)
        if (decoded.exp * 1000 > Date.now() && decoded.role === "superadmin") {
          setUser({
            userId: decoded.userId,
            email: decoded.email,
            role: decoded.role,
          })
        }
      } catch {
        // Invalid token, ignore
      }
    }
    setLoading(false)
  }, [])

  const login = useCallback(
    async (email: string, password: string) => {
      const response = await analyticsAPI.login(email, password)
      const { token, user: userData } = response.data

      if (userData.role !== "superadmin") {
        throw new Error("Access denied. SuperAdmin role required.")
      }

      localStorage.setItem("analytics_token", token)
      setUser({
        userId: userData._id,
        email: userData.email,
        role: userData.role,
      })
      router.push("/dashboard")
    },
    [router],
  )

  const logout = useCallback(() => {
    localStorage.removeItem("analytics_token")
    setUser(null)
    router.push("/login")
  }, [router])

  return { user, loading, login, logout }
}
```

### `src/app/login/page.tsx`

```typescript
'use client';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err: any) {
      setError(err.message || 'Login failed. Check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          Analytics Dashboard
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md
                         focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md
                         focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md
                       hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="mt-4 text-xs text-gray-500 text-center">
          SuperAdmin access only
        </p>
      </div>
    </div>
  );
}
```

**Login flow:**

1. User enters email + password on the login page.
2. The form POSTs to `/api/v3/auth/loginrx` (the same endpoint the mobile app uses).
3. On success, the response includes a JWT token and user object.
4. The client validates that `user.role === 'superadmin'` -- if not, it rejects with an error message.
5. On valid superadmin login, the JWT is stored in `localStorage` under the key `analytics_token`.
6. The user is redirected to `/dashboard`.
7. On logout, the token is cleared and the user is sent back to `/login`.

---

## Step 6.6: Dashboard Layout

### `src/app/dashboard/layout.tsx`

```typescript
import AuthGuard from '@/components/layout/AuthGuard';
import Sidebar from '@/components/layout/Sidebar';
import Header from '@/components/layout/Header';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-auto p-6">{children}</main>
        </div>
      </div>
    </AuthGuard>
  );
}
```

### `src/components/layout/Sidebar.tsx`

```typescript
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { label: 'Overview',  href: '/dashboard',           icon: 'HomeIcon' },
  { label: 'Live Feed', href: '/dashboard/live',      icon: 'ActivityIcon' },
  { label: 'Funnels',   href: '/dashboard/funnels',   icon: 'FilterIcon' },
  { label: 'Retention', href: '/dashboard/retention', icon: 'UsersIcon' },
  { label: 'Sessions',  href: '/dashboard/sessions',  icon: 'ClockIcon' },
  { label: 'Events',    href: '/dashboard/events',    icon: 'ListIcon' },
  { label: 'Users',     href: '/dashboard/users',     icon: 'PeopleIcon' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-gray-900 text-gray-100 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold">Dzzlo Analytics</h1>
      </div>
      <nav className="flex-1 py-4">
        {navItems.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== '/dashboard' && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center px-4 py-3 text-sm transition-colors
                ${isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
            >
              <span className="ml-2">{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-700">
        <button className="text-sm text-gray-400 hover:text-white">
          Logout
        </button>
      </div>
    </aside>
  );
}
```

### `src/components/layout/Header.tsx`

```typescript
'use client';
import DateRangePicker from '@/components/filters/DateRangePicker';
import CompanyFilter from '@/components/filters/CompanyFilter';

export default function Header() {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3
                        flex items-center justify-between">
      <DateRangePicker />
      <CompanyFilter />
    </header>
  );
}
```

**Sidebar navigation items:**

| Label     | Icon     | Route                  |
| --------- | -------- | ---------------------- |
| Overview  | Home     | `/dashboard`           |
| Live Feed | Activity | `/dashboard/live`      |
| Funnels   | Filter   | `/dashboard/funnels`   |
| Retention | Users    | `/dashboard/retention` |
| Sessions  | Clock    | `/dashboard/sessions`  |
| Events    | List     | `/dashboard/events`    |
| Users     | People   | `/dashboard/users`     |

---

## Step 6.7: Overview Dashboard Page

### `src/app/dashboard/page.tsx`

This is the landing page after login. It provides a high-level snapshot of the product's health using KPI cards and summary charts.

### Layout wireframe

```
+--------------------------------------------------------------+
|  Date Range Picker                          Company Filter    |
+----------+----------+----------+----------+------------------+
|   DAU    |   WAU    |   MAU    |  Events  | Avg Session Dur  |
|   142    |   823    |  1,240   |  3,456   |   4m 32s         |
|  +12%    |   +5%    |   +8%   |  +15%    |   -3%            |
+----------+----------+----------+----------+------------------+
|                                                               |
|   DAU Trend (30 days) -- Area Chart                          |
|   ........................................................   |
|                                                               |
+------------------------------+--------------------------------+
|  Top Events (Bar Chart)      |  Events by Category (Donut)   |
|  order_submitted: ==== 450   |  +----------+                  |
|  screen_view: ======== 890   |  |  order   | 35%             |
|  invoice_created: == 230     |  |  auth    | 20%             |
|                              |  |  system  | 15%             |
+------------------------------+--------------------------------+
```

### Implementation details

**KPI cards** -- each card shows:

- Metric label (DAU, WAU, MAU, Events Today, Avg Session Duration)
- Current value (formatted: numbers with comma separators, duration as `Xm Ys`)
- Percentage change from the previous equivalent period (day-over-day for DAU, week-over-week for WAU, etc.)
- Color coding: green for positive change, red for negative

**DAU trend chart** -- 30-day area chart:

- X-axis: dates (last 30 days)
- Y-axis: daily active users
- Data source: call `getEventCounts` with `group_by: 'day'` and a 30-day window, counting distinct users
- Uses Tremor `<AreaChart>`

**Top events bar chart** -- horizontal bar chart:

- Shows the top 10 events by count for the selected date range
- Data source: `getOverview` response's `top_events` array
- Uses Tremor `<BarChart>`

**Events by category donut chart** -- category breakdown:

- Groups events into categories (order, auth, system, etc.)
- Shows proportional distribution
- Uses Tremor `<DonutChart>`

### Tremor components used

```typescript
import {
  Card,
  Metric,
  Text,
  Flex,
  BadgeDelta,
  Grid,
  AreaChart,
  BarChart,
  DonutChart,
} from "@tremor/react"
```

### Data fetching pattern

```typescript
'use client';
import { useEffect, useState } from 'react';
import { analyticsAPI } from '@/lib/api';
import type { OverviewData } from '@/lib/types';

export default function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchOverview() {
      try {
        const response = await analyticsAPI.getOverview();
        setData(response.data.data);
      } catch (err: any) {
        setError(err.message || 'Failed to load overview');
      } finally {
        setLoading(false);
      }
    }
    fetchOverview();
  }, []);

  if (loading) return <LoadingSkeleton />;
  if (error) return <ErrorState message={error} />;
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* KPI Row */}
      <Grid numItemsMd={3} numItemsLg={5} className="gap-4">
        <KPICard title="DAU" value={data.dau} /* ... */ />
        <KPICard title="WAU" value={data.wau} /* ... */ />
        <KPICard title="MAU" value={data.mau} /* ... */ />
        <KPICard title="Events Today" value={data.events_today} /* ... */ />
        <KPICard title="Avg Session" value={formatDuration(data.avg_session_duration_ms)} /* ... */ />
      </Grid>

      {/* DAU Trend */}
      <Card>
        <Text>Daily Active Users (30 days)</Text>
        <AreaChart data={dauTrend} index="date" categories={['users']} />
      </Card>

      {/* Bottom row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <Text>Top Events</Text>
          <BarChart data={data.top_events} index="_id" categories={['count']} />
        </Card>
        <Card>
          <Text>Events by Category</Text>
          <DonutChart data={categoryData} index="category" category="count" />
        </Card>
      </div>
    </div>
  );
}
```

### `src/components/charts/KPICard.tsx`

```typescript
import { Card, Metric, Text, Flex, BadgeDelta } from '@tremor/react';

interface KPICardProps {
  title: string;
  value: string | number;
  delta?: string;         // e.g. "+12%"
  deltaType?: 'increase' | 'decrease' | 'unchanged';
}

export default function KPICard({ title, value, delta, deltaType }: KPICardProps) {
  return (
    <Card>
      <Text>{title}</Text>
      <Flex justifyContent="start" alignItems="baseline" className="space-x-2 mt-2">
        <Metric>{value}</Metric>
        {delta && (
          <BadgeDelta deltaType={deltaType || 'unchanged'}>
            {delta}
          </BadgeDelta>
        )}
      </Flex>
    </Card>
  );
}
```

### Utility: duration formatting

```typescript
// src/lib/utils.ts
export function formatDuration(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  if (minutes === 0) return `${seconds}s`
  return `${minutes}m ${seconds}s`
}

export function formatNumber(n: number): string {
  return n.toLocaleString("en-IN")
}
```

---

## Step 6.8: Live Event Feed Page

### `src/app/dashboard/live/page.tsx`

A real-time scrolling view of the latest analytics events as they arrive.

### Features

- **Auto-refresh**: fetches latest events every 10 seconds (configurable via a dropdown: 5s, 10s, 30s, off)
- **Filters**: event name, event category, user role, device OS
- **Event rows**: each row displays timestamp, event name, user email, screen name, device info, and event properties (expandable JSON on click)
- **Color-coded categories**: auth = blue, order = green, error = red, system = gray, navigation = purple

### Implementation

```typescript
'use client';
import { useEffect, useState, useRef } from 'react';
import { analyticsAPI } from '@/lib/api';
import type { LiveEvent } from '@/lib/types';
import {
  Card,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Badge,
  Select,
  SelectItem,
} from '@tremor/react';

const CATEGORY_COLORS: Record<string, string> = {
  auth: 'blue',
  order: 'green',
  error: 'red',
  system: 'gray',
  navigation: 'purple',
};

export default function LiveFeedPage() {
  const [events, setEvents] = useState<LiveEvent[]>([]);
  const [refreshInterval, setRefreshInterval] = useState(10000); // ms
  const [filters, setFilters] = useState({
    event_name: '',
    event_category: '',
    role: '',
    device_os: '',
  });
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchEvents = async () => {
    const params: any = { limit: 50 };
    if (filters.event_name) params.event_name = filters.event_name;
    if (filters.event_category) params.event_category = filters.event_category;
    if (filters.role) params.role = filters.role;
    if (filters.device_os) params.device_os = filters.device_os;

    const res = await analyticsAPI.getLiveEvents(params);
    setEvents(res.data.data);
  };

  useEffect(() => {
    fetchEvents();
    if (refreshInterval > 0) {
      intervalRef.current = setInterval(fetchEvents, refreshInterval);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [refreshInterval, filters]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Live Event Feed</h2>
        <Select value={String(refreshInterval)} onValueChange={(v) => setRefreshInterval(Number(v))}>
          <SelectItem value="5000">Refresh: 5s</SelectItem>
          <SelectItem value="10000">Refresh: 10s</SelectItem>
          <SelectItem value="30000">Refresh: 30s</SelectItem>
          <SelectItem value="0">Paused</SelectItem>
        </Select>
      </div>

      {/* Filter bar */}
      {/* ... filter inputs for event_name, category, role, device_os ... */}

      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Time</TableHeaderCell>
              <TableHeaderCell>Event</TableHeaderCell>
              <TableHeaderCell>Category</TableHeaderCell>
              <TableHeaderCell>User</TableHeaderCell>
              <TableHeaderCell>Screen</TableHeaderCell>
              <TableHeaderCell>Device</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {events.map((event) => (
              <TableRow key={event._id} className="cursor-pointer hover:bg-gray-50">
                <TableCell>{formatTime(event.server_timestamp)}</TableCell>
                <TableCell className="font-mono text-sm">{event.event_name}</TableCell>
                <TableCell>
                  <Badge color={CATEGORY_COLORS[event.event_category] || 'gray'}>
                    {event.event_category}
                  </Badge>
                </TableCell>
                <TableCell>{event.user_id}</TableCell>
                <TableCell>{event.screen_name}</TableCell>
                <TableCell>{event.device_os} {event.app_version}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
```

### Expandable event properties

When a row is clicked, it expands to show the full `event_properties` JSON in a formatted `<pre>` block. This uses React state to toggle an `expandedId`, and conditionally renders an additional row below the clicked event.

---

## Step 6.9: Funnel Analysis Page

### `src/app/dashboard/funnels/page.tsx`

Visualizes multi-step conversion funnels to understand where users drop off.

### Features

- **Preset funnels dropdown** with common flows:
  - "Order Flow": `order_create_started` -> `order_submitted` -> `invoice_created` -> `payment_completed`
  - "Auth Flow": `auth_login_started` -> `auth_login_success`
  - "Custom": free-text input where the user types comma-separated event names
- **Date range selector** for the analysis window
- **Company filter** to scope to a specific company
- **Funnel visualization**: horizontal bar chart with decreasing widths per step

### Layout wireframe

```
Funnel: [Order Flow v]    From: [2026-03-01]  To: [2026-04-01]  Company: [All v]

Order Flow Funnel (Last 30 days)
+------------------------------------------------------------+
| order_create_started  ============================== 450    |
|                                                   100.0%    |
| order_submitted       ========================  380         |
|                                              84.4%   -15.6% |
| invoice_created       ==================  290               |
|                                       64.4%   -23.7%       |
| payment_completed     ===============  250                  |
|                                    55.6%   -13.8%          |
+------------------------------------------------------------+
Overall: 55.6% conversion (order_create_started -> payment_completed)
```

### Implementation

```typescript
'use client';
import { useState } from 'react';
import { analyticsAPI } from '@/lib/api';
import type { FunnelData } from '@/lib/types';
import { Card, Text, BarChart } from '@tremor/react';

const PRESET_FUNNELS = [
  {
    label: 'Order Flow',
    steps: 'order_create_started,order_submitted,invoice_created,payment_completed',
  },
  {
    label: 'Auth Flow',
    steps: 'auth_login_started,auth_login_success',
  },
  {
    label: 'Custom',
    steps: '',
  },
];

export default function FunnelsPage() {
  const [selectedPreset, setSelectedPreset] = useState(PRESET_FUNNELS[0]);
  const [customSteps, setCustomSteps] = useState('');
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [companyId, setCompanyId] = useState('');
  const [funnelData, setFunnelData] = useState<FunnelData | null>(null);
  const [loading, setLoading] = useState(false);

  const runFunnel = async () => {
    setLoading(true);
    const steps = selectedPreset.label === 'Custom'
      ? customSteps
      : selectedPreset.steps;

    try {
      const res = await analyticsAPI.getFunnel({
        steps,
        from: dateRange.from,
        to: dateRange.to,
        company_id: companyId || undefined,
      });
      setFunnelData(res.data.data);
    } catch (err) {
      // handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls bar */}
      {/* ... preset selector, date inputs, company filter, Run button ... */}

      {funnelData && (
        <Card>
          <Text className="text-lg font-semibold mb-4">
            {selectedPreset.label} Funnel
          </Text>
          {funnelData.steps.map((step, i) => (
            <FunnelStepBar
              key={i}
              step={step}
              maxUsers={funnelData.total_users}
              previousUsers={i > 0 ? funnelData.steps[i - 1].users : step.users}
            />
          ))}
          <div className="mt-4 text-sm text-gray-600">
            Overall: {funnelData.steps[funnelData.steps.length - 1]?.overall_rate} conversion
          </div>
        </Card>
      )}
    </div>
  );
}
```

### `src/components/charts/FunnelChart.tsx`

```typescript
interface FunnelStepBarProps {
  step: FunnelStep;
  maxUsers: number;
  previousUsers: number;
}

export function FunnelStepBar({ step, maxUsers, previousUsers }: FunnelStepBarProps) {
  const widthPercent = (step.users / maxUsers) * 100;
  const dropOff = previousUsers > 0
    ? (((previousUsers - step.users) / previousUsers) * 100).toFixed(1)
    : '0.0';

  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="font-mono">{step.event_name}</span>
        <span>
          {step.users} users ({step.overall_rate})
          {step.step_index > 0 && (
            <span className="text-red-500 ml-2">-{dropOff}%</span>
          )}
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded h-8">
        <div
          className="bg-blue-500 h-8 rounded transition-all duration-500"
          style={{ width: `${widthPercent}%` }}
        />
      </div>
    </div>
  );
}
```

---

## Step 6.10: Retention Grid Page

### `src/app/dashboard/retention/page.tsx`

Displays cohort-based retention analysis as a color-coded heat map grid.

### Features

- **Period selector**: weekly or monthly cohorts
- **Number of cohorts**: 4, 8, or 12
- **Company filter** to scope by company
- **Heat map grid**: rows are cohorts, columns are periods, cells are color-coded by retention rate

### Layout wireframe

```
Period: [Weekly v]   Cohorts: [8 v]   Company: [All v]

Retention -- Weekly Cohorts
+----------+------+-------+-------+-------+-------+
| Cohort   | Size | Wk 0  | Wk 1  | Wk 2  | Wk 3  |
+----------+------+-------+-------+-------+-------+
| Mar 3-9  |  45  | 100%  |  62%  |  48%  |  41%  |
| Mar 10-16|  52  | 100%  |  58%  |  44%  |       |
| Mar 17-23|  38  | 100%  |  55%  |       |       |
| Mar 24-30|  61  | 100%  |       |       |       |
+----------+------+-------+-------+-------+-------+

Colors: 80%+ = dark green, 60-80% = green, 40-60% = yellow, 20-40% = orange, <20% = red
```

### `src/components/charts/RetentionGrid.tsx`

```typescript
import type { RetentionCohort } from '@/lib/types';

interface RetentionGridProps {
  cohorts: RetentionCohort[];
  periodLabel: string; // "Wk" or "Mo"
}

function getCellColor(rate: number): string {
  if (rate >= 80) return 'bg-green-700 text-white';
  if (rate >= 60) return 'bg-green-500 text-white';
  if (rate >= 40) return 'bg-yellow-400 text-gray-900';
  if (rate >= 20) return 'bg-orange-400 text-white';
  return 'bg-red-500 text-white';
}

export default function RetentionGrid({ cohorts, periodLabel }: RetentionGridProps) {
  // Determine max number of periods across all cohorts
  const maxPeriods = Math.max(...cohorts.map((c) => c.retention.length));

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="bg-gray-50">
            <th className="px-3 py-2 text-left font-medium text-gray-600">Cohort</th>
            <th className="px-3 py-2 text-center font-medium text-gray-600">Size</th>
            {Array.from({ length: maxPeriods }, (_, i) => (
              <th key={i} className="px-3 py-2 text-center font-medium text-gray-600">
                {periodLabel} {i}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cohorts.map((cohort) => (
            <tr key={cohort.cohort_start} className="border-t">
              <td className="px-3 py-2 whitespace-nowrap text-gray-700">
                {formatCohortDate(cohort.cohort_start, cohort.cohort_end)}
              </td>
              <td className="px-3 py-2 text-center text-gray-700">
                {cohort.cohort_size}
              </td>
              {Array.from({ length: maxPeriods }, (_, i) => {
                const period = cohort.retention.find((r) => r.period_index === i);
                if (!period) {
                  return <td key={i} className="px-3 py-2" />;
                }
                const rateNum = parseFloat(period.retention_rate);
                return (
                  <td
                    key={i}
                    className={`px-3 py-2 text-center font-medium rounded ${getCellColor(rateNum)}`}
                  >
                    {period.retention_rate}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Color scale rationale

| Retention Rate | Color      | Meaning                             |
| -------------- | ---------- | ----------------------------------- |
| 80%+           | Dark green | Excellent retention, sticky feature |
| 60-80%         | Green      | Good retention                      |
| 40-60%         | Yellow     | Average, room for improvement       |
| 20-40%         | Orange     | Concerning drop-off                 |
| Below 20%      | Red        | Critical churn, needs investigation |

---

## Step 6.11: Session Explorer Page

### `src/app/dashboard/sessions/page.tsx`

Lets analysts browse individual user sessions, understand session length distribution, and drill into what happened during a session.

### Features

- **Filters**: date range, user ID/email search, min/max duration sliders
- **Paginated session list** (20 per page, with previous/next controls)
- **Session cards** showing:
  - User name + email (linked to user timeline page)
  - Duration formatted as "Xm Ys"
  - Event count
  - Device: iOS/Android + app version
  - Screens visited as tag pills
- **Click to expand**: shows all events within that session in chronological order

### Session card component

```typescript
interface SessionCardProps {
  session: Session;
  isExpanded: boolean;
  onToggle: () => void;
}

function SessionCard({ session, isExpanded, onToggle }: SessionCardProps) {
  return (
    <Card className="cursor-pointer" onClick={onToggle}>
      <div className="flex items-center justify-between">
        <div>
          <Text className="font-semibold">
            {session.user_id.username || session.user_id.email}
          </Text>
          <Text className="text-gray-500 text-sm">
            {formatDateTime(session.started_at)}
          </Text>
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>{formatDuration(session.duration_ms)}</span>
          <span>{session.event_count} events</span>
          <Badge>{session.device_os} {session.app_version}</Badge>
        </div>
      </div>

      {/* Screen tags */}
      <div className="flex flex-wrap gap-1 mt-2">
        {session.screens_visited.map((screen) => (
          <span key={screen} className="px-2 py-0.5 bg-gray-100 rounded text-xs">
            {screen}
          </span>
        ))}
      </div>

      {/* Expanded: session events timeline */}
      {isExpanded && <SessionTimeline sessionId={session.session_id} />}
    </Card>
  );
}
```

### `src/components/charts/SessionTimeline.tsx`

```typescript
'use client';
import { useEffect, useState } from 'react';
import { analyticsAPI } from '@/lib/api';

interface SessionTimelineProps {
  sessionId: string;
}

export default function SessionTimeline({ sessionId }: SessionTimelineProps) {
  const [events, setEvents] = useState<LiveEvent[]>([]);

  useEffect(() => {
    // Fetch events for this specific session
    analyticsAPI
      .getLiveEvents({ session_id: sessionId, limit: 200 } as any)
      .then((res) => setEvents(res.data.data));
  }, [sessionId]);

  return (
    <div className="mt-4 border-t pt-4">
      <div className="relative border-l-2 border-blue-200 ml-4">
        {events.map((event, i) => (
          <div key={event._id} className="mb-4 ml-6 relative">
            {/* Timeline dot */}
            <div className="absolute -left-[29px] w-3 h-3 bg-blue-500 rounded-full" />
            <div className="text-xs text-gray-400">
              {formatTime(event.server_timestamp)}
            </div>
            <div className="text-sm font-mono">{event.event_name}</div>
            <div className="text-xs text-gray-500">{event.screen_name}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Step 6.12: Event Explorer Page

### `src/app/dashboard/events/page.tsx`

Allows deep-diving into specific event types to understand their frequency and trends over time.

### Features

- **Event name dropdown**: populated by calling the overview API and extracting the `top_events` list; also allows free-text input for any event name
- **Time grouping selector**: hour, day, week, month
- **Date range selector**: from/to date pickers
- **Toggle**: total event count vs. unique users (two separate lines if both selected)
- **Time-series line chart**: plots event count (or unique users) on the Y-axis, time periods on the X-axis
- **Raw data table below the chart**: sortable by period, count, unique users

### Implementation

```typescript
'use client';
import { useState, useEffect } from 'react';
import { analyticsAPI } from '@/lib/api';
import type { EventCount } from '@/lib/types';
import {
  Card,
  Text,
  LineChart,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  Select,
  SelectItem,
} from '@tremor/react';

export default function EventExplorerPage() {
  const [eventName, setEventName] = useState('');
  const [groupBy, setGroupBy] = useState<'hour' | 'day' | 'week' | 'month'>('day');
  const [dateRange, setDateRange] = useState({ from: '', to: '' });
  const [data, setData] = useState<EventCount[]>([]);
  const [showUnique, setShowUnique] = useState(false);

  const fetchData = async () => {
    if (!eventName || !dateRange.from || !dateRange.to) return;

    const res = await analyticsAPI.getEventCounts({
      event_name: eventName,
      group_by: groupBy,
      from: dateRange.from,
      to: dateRange.to,
    });
    setData(res.data.data);
  };

  useEffect(() => {
    fetchData();
  }, [eventName, groupBy, dateRange]);

  const chartCategories = showUnique ? ['unique_users'] : ['count'];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-semibold">Event Explorer</h2>
        {/* Event name input/select */}
        {/* Group by selector */}
        {/* Date range inputs */}
        {/* Toggle: Count vs Unique Users */}
      </div>

      <Card>
        <LineChart
          data={data}
          index="period"
          categories={chartCategories}
          colors={['blue']}
        />
      </Card>

      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>Period</TableHeaderCell>
              <TableHeaderCell>Count</TableHeaderCell>
              <TableHeaderCell>Unique Users</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((row) => (
              <TableRow key={row.period}>
                <TableCell>{row.period}</TableCell>
                <TableCell>{formatNumber(row.count)}</TableCell>
                <TableCell>{formatNumber(row.unique_users)}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
```

---

## Step 6.13: User Activity and Timeline Pages

### `src/app/dashboard/users/page.tsx` -- User Activity List

A searchable, sortable list of all users who have generated analytics events.

### Features

- **Search**: by email or username (debounced input, triggers API call after 300ms)
- **Sortable columns**: event count, session count, last active (default: last active descending)
- **Pagination**: 20 users per page
- **Each row shows**: user info (name, email, role), total event count, total session count, last active timestamp, devices used (tag pills)
- **Click row**: navigates to `/dashboard/users/[userId]` for detailed timeline

```typescript
'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { analyticsAPI } from '@/lib/api';
import type { UserActivity } from '@/lib/types';
import {
  Card,
  Table,
  TableHead,
  TableRow,
  TableHeaderCell,
  TableBody,
  TableCell,
  TextInput,
  Badge,
} from '@tremor/react';

export default function UsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<UserActivity[]>([]);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState<'event_count' | 'last_active' | 'session_count'>('last_active');
  const [order, setOrder] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(1);

  useEffect(() => {
    const timeout = setTimeout(() => {
      analyticsAPI.getUserActivity({
        search: search || undefined,
        sort_by: sortBy,
        order,
        page,
        limit: 20,
      }).then((res) => setUsers(res.data.data));
    }, 300); // debounce

    return () => clearTimeout(timeout);
  }, [search, sortBy, order, page]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Users</h2>
        <TextInput
          placeholder="Search by email or username..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
      </div>

      <Card>
        <Table>
          <TableHead>
            <TableRow>
              <TableHeaderCell>User</TableHeaderCell>
              <TableHeaderCell
                className="cursor-pointer"
                onClick={() => toggleSort('event_count')}
              >
                Events
              </TableHeaderCell>
              <TableHeaderCell
                className="cursor-pointer"
                onClick={() => toggleSort('session_count')}
              >
                Sessions
              </TableHeaderCell>
              <TableHeaderCell
                className="cursor-pointer"
                onClick={() => toggleSort('last_active')}
              >
                Last Active
              </TableHeaderCell>
              <TableHeaderCell>Devices</TableHeaderCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => (
              <TableRow
                key={user._id}
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => router.push(`/dashboard/users/${user.user_id}`)}
              >
                <TableCell>
                  <div>
                    <span className="font-medium">{user.user_info.username}</span>
                    <br />
                    <span className="text-gray-500 text-xs">{user.user_info.email}</span>
                  </div>
                </TableCell>
                <TableCell>{formatNumber(user.event_count)}</TableCell>
                <TableCell>{user.session_count}</TableCell>
                <TableCell>{formatRelativeTime(user.last_active)}</TableCell>
                <TableCell>
                  <div className="flex gap-1">
                    {user.devices.map((d) => (
                      <Badge key={d} size="xs">{d}</Badge>
                    ))}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Pagination controls */}
      <div className="flex justify-center gap-2">
        <button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button>
        <span>Page {page}</span>
        <button onClick={() => setPage(page + 1)}>Next</button>
      </div>
    </div>
  );
}
```

### `src/app/dashboard/users/[userId]/page.tsx` -- User Timeline

A detailed view of a single user's complete activity history.

### Features

- **User profile header**: name, email, role, company
- **Activity summary KPIs**: total events, total sessions, first seen, last seen
- **Chronological timeline** merging:
  - Frontend events (screen views, button clicks, form submissions)
  - Backend API calls (correlated via `request_id` if available)
  - Errors and crashes
- **Filters**: event category dropdown, date range picker
- **Pagination**: loads 50 events at a time with "Load more" button

```typescript
'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { analyticsAPI } from '@/lib/api';
import { Card, Metric, Text, Grid, Badge } from '@tremor/react';

export default function UserTimelinePage() {
  const params = useParams();
  const userId = params.userId as string;
  const [userInfo, setUserInfo] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [page, setPage] = useState(1);

  useEffect(() => {
    // Fetch user activity summary
    analyticsAPI.getUserActivity({ search: userId })
      .then((res) => {
        const user = res.data.data[0];
        if (user) setUserInfo(user);
      });
  }, [userId]);

  useEffect(() => {
    // Fetch user timeline events
    analyticsAPI.getUserTimeline(userId, {
      event_category: categoryFilter || undefined,
      page,
      limit: 50,
    }).then((res) => {
      if (page === 1) {
        setTimeline(res.data.data);
      } else {
        setTimeline((prev) => [...prev, ...res.data.data]);
      }
    });
  }, [userId, categoryFilter, page]);

  return (
    <div className="space-y-6">
      {/* User profile header */}
      {userInfo && (
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <Metric>{userInfo.user_info.username}</Metric>
              <Text>{userInfo.user_info.email}</Text>
              <Badge className="mt-1">{userInfo.user_info.role}</Badge>
            </div>
          </div>
        </Card>
      )}

      {/* KPI summary */}
      {userInfo && (
        <Grid numItemsMd={4} className="gap-4">
          <Card>
            <Text>Total Events</Text>
            <Metric>{formatNumber(userInfo.event_count)}</Metric>
          </Card>
          <Card>
            <Text>Sessions</Text>
            <Metric>{userInfo.session_count}</Metric>
          </Card>
          <Card>
            <Text>First Seen</Text>
            <Metric className="text-lg">{formatDate(userInfo.first_active)}</Metric>
          </Card>
          <Card>
            <Text>Last Active</Text>
            <Metric className="text-lg">{formatRelativeTime(userInfo.last_active)}</Metric>
          </Card>
        </Grid>
      )}

      {/* Filters */}
      <div className="flex gap-4">
        {/* Category filter dropdown */}
        {/* Date range picker */}
      </div>

      {/* Timeline */}
      <Card>
        <div className="relative border-l-2 border-gray-200 ml-4">
          {timeline.map((event) => (
            <div key={event._id} className="mb-6 ml-6 relative">
              {/* Timeline dot with category color */}
              <div
                className={`absolute -left-[29px] w-3 h-3 rounded-full ${
                  getCategoryColor(event.event_category)
                }`}
              />
              <div className="flex items-start justify-between">
                <div>
                  <span className="font-mono text-sm font-medium">
                    {event.event_name}
                  </span>
                  <div className="text-xs text-gray-500 mt-0.5">
                    {event.screen_name && `Screen: ${event.screen_name}`}
                  </div>
                  {event.event_properties &&
                    Object.keys(event.event_properties).length > 0 && (
                      <details className="mt-1">
                        <summary className="text-xs text-blue-500 cursor-pointer">
                          Properties
                        </summary>
                        <pre className="text-xs bg-gray-50 p-2 rounded mt-1 max-w-lg overflow-auto">
                          {JSON.stringify(event.event_properties, null, 2)}
                        </pre>
                      </details>
                    )}
                </div>
                <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {formatDateTime(event.server_timestamp)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Load more button */}
        <div className="text-center mt-4">
          <button
            onClick={() => setPage((p) => p + 1)}
            className="text-sm text-blue-600 hover:underline"
          >
            Load more events
          </button>
        </div>
      </Card>
    </div>
  );
}
```

---

## Step 6.14: Shared Filter Components

### `src/components/filters/DateRangePicker.tsx`

```typescript
'use client';
import { useState } from 'react';

interface DateRangePickerProps {
  onChange?: (range: { from: string; to: string }) => void;
}

const PRESETS = [
  { label: 'Today', days: 0 },
  { label: 'Last 7 days', days: 7 },
  { label: 'Last 30 days', days: 30 },
  { label: 'Last 90 days', days: 90 },
];

export default function DateRangePicker({ onChange }: DateRangePickerProps) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');

  const applyPreset = (days: number) => {
    const toDate = new Date();
    const fromDate = new Date();
    fromDate.setDate(fromDate.getDate() - days);

    const fromStr = fromDate.toISOString().split('T')[0];
    const toStr = toDate.toISOString().split('T')[0];

    setFrom(fromStr);
    setTo(toStr);
    onChange?.({ from: fromStr, to: toStr });
  };

  return (
    <div className="flex items-center gap-2">
      {PRESETS.map((preset) => (
        <button
          key={preset.label}
          onClick={() => applyPreset(preset.days)}
          className="px-3 py-1 text-sm rounded-md bg-gray-100 hover:bg-gray-200
                     text-gray-700 transition-colors"
        >
          {preset.label}
        </button>
      ))}
      <div className="flex items-center gap-1 ml-2">
        <input
          type="date"
          value={from}
          onChange={(e) => {
            setFrom(e.target.value);
            if (to) onChange?.({ from: e.target.value, to });
          }}
          className="px-2 py-1 border rounded text-sm"
        />
        <span className="text-gray-400">to</span>
        <input
          type="date"
          value={to}
          onChange={(e) => {
            setTo(e.target.value);
            if (from) onChange?.({ from, to: e.target.value });
          }}
          className="px-2 py-1 border rounded text-sm"
        />
      </div>
    </div>
  );
}
```

### `src/components/filters/CompanyFilter.tsx`

```typescript
'use client';
import { Select, SelectItem } from '@tremor/react';

interface CompanyFilterProps {
  value: string;
  onChange: (value: string) => void;
  companies: { _id: string; name: string }[];
}

export default function CompanyFilter({ value, onChange, companies }: CompanyFilterProps) {
  return (
    <Select value={value} onValueChange={onChange} placeholder="All Companies">
      <SelectItem value="">All Companies</SelectItem>
      {companies.map((c) => (
        <SelectItem key={c._id} value={c._id}>
          {c.name}
        </SelectItem>
      ))}
    </Select>
  );
}
```

### `src/components/filters/RoleFilter.tsx`

```typescript
'use client';
import { Select, SelectItem } from '@tremor/react';

const ROLES = ['admin', 'partner', 'staff', 'superadmin'];

interface RoleFilterProps {
  value: string;
  onChange: (value: string) => void;
}

export default function RoleFilter({ value, onChange }: RoleFilterProps) {
  return (
    <Select value={value} onValueChange={onChange} placeholder="All Roles">
      <SelectItem value="">All Roles</SelectItem>
      {ROLES.map((role) => (
        <SelectItem key={role} value={role}>
          {role}
        </SelectItem>
      ))}
    </Select>
  );
}
```

---

## Step 6.15: Data Fetching Hook

### `src/hooks/useAnalytics.ts`

A reusable hook that wraps API calls with loading, error, and refresh state.

```typescript
"use client"
import { useState, useEffect, useCallback } from "react"

interface UseAnalyticsResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refresh: () => void
}

export function useAnalytics<T>(
  fetcher: () => Promise<{ data: { data: T } }>,
  deps: any[] = [],
): UseAnalyticsResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const refresh = useCallback(() => {
    setRefreshKey((k) => k + 1)
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetcher()
      .then((res) => {
        if (!cancelled) {
          setData(res.data.data)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message || "An error occurred")
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [...deps, refreshKey])

  return { data, loading, error, refresh }
}
```

**Usage example:**

```typescript
const {
  data: overview,
  loading,
  error,
  refresh,
} = useAnalytics(() => analyticsAPI.getOverview({ company_id: companyId }), [companyId])
```

---

## Step 6.16: CORS Configuration

### File to modify: `dzzlo_oms_api/dzzlo_oms.js`

The existing Express server must allow requests from the Next.js dashboard origin. Add the dashboard URLs to the CORS whitelist:

```javascript
app.use(
  cors({
    origin: [
      "http://localhost:3000", // Next.js dev server
      "https://analytics.dzzlo.com", // Production dashboard URL (update as needed)
      // ... existing origins (mobile app deep links, etc.)
    ],
    credentials: true,
  }),
)
```

**Why this is needed**: The Next.js dashboard runs as a separate web application on a different port (dev: 3000) or domain (production). Without CORS configuration, the browser will block API requests from the dashboard to the Express server. The `credentials: true` flag allows the dashboard to send cookies if session-based auth is ever added.

---

## Step 6.17: Deployment

### Development

```bash
cd dzzlo_analytics
npm run dev    # Starts on port 3000 (default)
```

The dev server hot-reloads on file changes. Ensure the Express API is also running on port 8030 for the API calls to work.

### Production Options

#### Option 1: Vercel (recommended for Next.js)

- Zero-config deployment for Next.js apps
- Automatic SSL, CDN, and edge caching
- Connect GitHub repo for automatic deploys on push
- Set environment variables in Vercel dashboard

```bash
npx vercel deploy
```

#### Option 2: PM2 (alongside existing services)

Add to the existing PM2 ecosystem configuration:

```javascript
// ecosystem.config.js
{
  name: "analytics-dashboard",
  script: "npm",
  args: "start",
  cwd: "./dzzlo_analytics",
  env: {
    NODE_ENV: "production",
    PORT: 3001,
  },
}
```

First build the production bundle:

```bash
cd dzzlo_analytics
npm run build
pm2 start ecosystem.config.js --only analytics-dashboard
```

#### Option 3: Docker

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["npm", "start"]
```

---

## Step 6.18: Error and Loading States

Every page should handle three states gracefully. Create shared components for consistency:

### `src/components/layout/LoadingSkeleton.tsx`

```typescript
import { Card } from '@tremor/react';

export function LoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      <div className="grid grid-cols-5 gap-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i}>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-2" />
            <div className="h-8 bg-gray-200 rounded w-3/4" />
          </Card>
        ))}
      </div>
      <Card>
        <div className="h-64 bg-gray-200 rounded" />
      </Card>
    </div>
  );
}
```

### `src/components/layout/ErrorState.tsx`

```typescript
import { Card, Text } from '@tremor/react';

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Card className="text-center py-12">
      <Text className="text-red-500 text-lg mb-2">Something went wrong</Text>
      <Text className="text-gray-500 mb-4">{message}</Text>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Try Again
        </button>
      )}
    </Card>
  );
}
```

### `src/components/layout/EmptyState.tsx`

```typescript
import { Card, Text } from '@tremor/react';

export function EmptyState({ message }: { message: string }) {
  return (
    <Card className="text-center py-12">
      <Text className="text-gray-400 text-lg">{message}</Text>
    </Card>
  );
}
```

---

## Step 6.19: Verification Checklist

- [ ] `npx create-next-app` completes without errors
- [ ] `npm run dev` starts the dev server on port 3000
- [ ] Login page renders and authenticates against the existing API
- [ ] Non-superadmin users are rejected with a clear error message
- [ ] Overview page shows all 5 KPI cards with real data
- [ ] DAU trend area chart renders 30-day history
- [ ] Live feed auto-refreshes and displays new events as they arrive
- [ ] Live feed filters work: by event name, category, role, device OS
- [ ] Funnel page renders preset funnels with correct conversion rates
- [ ] Custom funnel accepts comma-separated event names and renders
- [ ] Retention grid renders with correct color coding
- [ ] Retention period toggle (weekly/monthly) works
- [ ] Session explorer lists sessions with pagination
- [ ] Clicking a session expands to show the event timeline
- [ ] Event explorer plots time-series for a selected event
- [ ] Event explorer toggle between count and unique users works
- [ ] User list searches, sorts, and paginates correctly
- [ ] Clicking a user navigates to their timeline page
- [ ] User timeline shows chronological events with properties
- [ ] All pages are responsive on desktop (1024px and above)
- [ ] Logout clears the token and redirects to login
- [ ] API errors show the ErrorState component (not a crash or blank page)
- [ ] Loading states show skeleton animations while data fetches
- [ ] Empty states show a helpful message when no data is available
- [ ] CORS is configured in the Express server for localhost:3000
- [ ] Production build (`npm run build`) completes without errors

---

## Files Summary

| Action | File                                         | Notes                                      |
| ------ | -------------------------------------------- | ------------------------------------------ |
| CREATE | `dzzlo_analytics/` (entire project)          | New Next.js project via `create-next-app`  |
| CREATE | `src/app/layout.tsx`                         | Root layout                                |
| CREATE | `src/app/page.tsx`                           | Redirect to /dashboard                     |
| CREATE | `src/app/login/page.tsx`                     | Login form                                 |
| CREATE | `src/app/dashboard/layout.tsx`               | Dashboard layout with sidebar + auth guard |
| CREATE | `src/app/dashboard/page.tsx`                 | Overview KPI dashboard                     |
| CREATE | `src/app/dashboard/live/page.tsx`            | Live event feed                            |
| CREATE | `src/app/dashboard/funnels/page.tsx`         | Funnel analysis                            |
| CREATE | `src/app/dashboard/retention/page.tsx`       | Retention cohort grid                      |
| CREATE | `src/app/dashboard/sessions/page.tsx`        | Session explorer                           |
| CREATE | `src/app/dashboard/events/page.tsx`          | Event explorer                             |
| CREATE | `src/app/dashboard/users/page.tsx`           | User activity list                         |
| CREATE | `src/app/dashboard/users/[userId]/page.tsx`  | User timeline                              |
| CREATE | `src/components/layout/Sidebar.tsx`          | Navigation sidebar                         |
| CREATE | `src/components/layout/Header.tsx`           | Top header with filters                    |
| CREATE | `src/components/layout/AuthGuard.tsx`        | Auth wrapper                               |
| CREATE | `src/components/layout/LoadingSkeleton.tsx`  | Loading state                              |
| CREATE | `src/components/layout/ErrorState.tsx`       | Error state                                |
| CREATE | `src/components/layout/EmptyState.tsx`       | Empty state                                |
| CREATE | `src/components/charts/KPICard.tsx`          | Metric card                                |
| CREATE | `src/components/charts/FunnelChart.tsx`      | Funnel bar visualization                   |
| CREATE | `src/components/charts/RetentionGrid.tsx`    | Cohort heat map                            |
| CREATE | `src/components/charts/SessionTimeline.tsx`  | Session event timeline                     |
| CREATE | `src/components/filters/DateRangePicker.tsx` | Date range + presets                       |
| CREATE | `src/components/filters/CompanyFilter.tsx`   | Company dropdown                           |
| CREATE | `src/components/filters/RoleFilter.tsx`      | Role dropdown                              |
| CREATE | `src/lib/api.ts`                             | Axios API client                           |
| CREATE | `src/lib/types.ts`                           | TypeScript interfaces                      |
| CREATE | `src/lib/utils.ts`                           | Formatting utilities                       |
| CREATE | `src/hooks/useAnalytics.ts`                  | Data fetching hook                         |
| CREATE | `src/hooks/useAuth.ts`                       | Auth state hook                            |
| CREATE | `.env.local`                                 | Dev API URL config                         |
| CREATE | `.env.production`                            | Prod API URL config                        |
| MODIFY | `dzzlo_oms_api/dzzlo_oms.js`                 | Add CORS origin for dashboard              |
