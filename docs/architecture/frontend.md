# Frontend Architecture

**Next.js 15 application with React 18, Tailwind CSS, and specialized visualization libraries.**

## Overview

The IntellyWeave frontend is built on Weaviate's Elysia frontend, extended with OSINT-specific visualizations including Mapbox 3D maps, vis-network relationship graphs, and multi-agent display components.

## Directory Structure

```text
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page
│   └── components/        # React components
│       ├── chat/          # Chat interface
│       │   ├── displays/  # Message renderers
│       │   │   ├── Courthouse/     # Courthouse debate
│       │   │   ├── Intelligence/   # Intelligence agent
│       │   │   └── ...
│       │   └── ...
│       ├── contexts/      # React contexts
│       ├── map/           # Mapbox components
│       ├── network/       # vis-network components
│       └── ui/            # Radix UI primitives
├── hooks/                 # Custom React hooks
├── lib/                   # Utility libraries
├── public/                # Static assets
└── styles/                # Global styles
```

## Key Components

### 1. Chat Interface

| Component | Purpose |
|-----------|---------|
| `ChatPanel` | Main chat container |
| `MessageList` | Renders conversation |
| `MessageInput` | User input handling |
| `displays/*` | Specialized message renderers |

### 2. Visualization Components

| Component | Library | Purpose |
|-----------|---------|---------|
| `MapboxMap` | Mapbox GL 3.16 | 3D geospatial visualization |
| `NetworkGraph` | vis-network 10.0.2 | Entity relationship graphs |
| `BarChart` | Custom + DSPy | Data visualization |
| `TableView` | Custom | Structured data display |

### 3. Multi-Agent Displays

| Display | Location | Purpose |
|---------|----------|---------|
| `CourthouseAgentMessage` | `displays/Courthouse/` | Defense/Prosecution/Judge |
| `IntelligenceAgentMessage` | `displays/Intelligence/` | 6-phase orchestrator |

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 15.x | React framework |
| React | 18.x | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| Radix UI | Latest | Accessible components |
| Mapbox GL | 3.16 | 3D maps |
| vis-network | 10.0.2 | Network graphs |
| Framer Motion | Latest | Animations |

## State Management

| Context | Purpose |
|---------|---------|
| `ChatContext` | Conversation state |
| `ToastContext` | Notifications |
| `ThemeContext` | Dark/light mode |

## API Integration

The frontend communicates with the backend via:

| Method | Use Case |
|--------|----------|
| REST API | Document upload, queries |
| WebSocket | Streaming responses |

```typescript
// Example: Query API call
const response = await fetch('/api/query', {
  method: 'POST',
  body: JSON.stringify({ query, collection_name })
});
```

## Build Configuration

### TypeScript (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "strict": true,
    "paths": { "@/*": ["./*"] }
  }
}
```

### Path Aliases

| Alias | Maps To |
|-------|---------|
| `@/components` | `./app/components` |
| `@/hooks` | `./hooks` |
| `@/lib` | `./lib` |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN` | Mapbox API token |
| `NEXT_PUBLIC_API_URL` | Backend API URL |

## See Also

- [Backend Architecture](backend.md) - API and services
- [Geospatial Mapping Guide](../guides/geospatial-mapping/index.md) - Mapbox usage
- [Network Analysis Guide](../guides/network-analysis/index.md) - vis-network usage
- [Visualization Guide](../guides/visualization/index.md) - All visualization methods
