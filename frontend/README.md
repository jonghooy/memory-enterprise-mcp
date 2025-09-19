# Memory Enterprise Frontend

A Next.js 14 application providing the UI for the Memory Enterprise Knowledge Management System.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **API Client**: Axios

## Features

### ✅ Completed (Week 1)
- [x] Project setup with Next.js 14 and TypeScript
- [x] shadcn/ui component library integration
- [x] Basic layout with sidebar navigation
- [x] AI Assistant chat interface
- [x] Knowledge base browsing page
- [x] Connections management page
- [x] Settings page
- [x] Dashboard/Home page
- [x] State management setup with Zustand
- [x] API client configuration

### 🚧 Next Steps (Week 2+)
- [ ] Connect to FastAPI backend
- [ ] Implement real-time chat with backend
- [ ] Add memory CRUD operations
- [ ] Integrate vector search
- [ ] Add Google Docs integration UI
- [ ] Implement file upload for memories
- [ ] Add real-time sync indicators

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Project Structure

```
frontend/
├── app/                  # Next.js 14 app directory
│   ├── layout.tsx       # Root layout with sidebar
│   ├── page.tsx         # AI Assistant (main page)
│   ├── home/           # Dashboard page
│   ├── knowledge/      # Knowledge base page
│   ├── connections/    # Integrations page
│   └── settings/       # Settings page
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   ├── sidebar.tsx     # Navigation sidebar
│   ├── header.tsx      # Top header
│   └── chat-interface.tsx # AI chat component
├── lib/                # Utilities and configs
│   ├── api.ts         # API client setup
│   ├── store.ts       # Zustand store
│   └── utils.ts       # Utility functions
└── public/            # Static assets
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## UI Components

The app uses shadcn/ui components which are built on top of Radix UI and styled with Tailwind CSS. Components include:

- Button
- Card
- Input/Textarea
- Badge
- ScrollArea
- Separator

## State Management

Using Zustand for client-side state management:

- **Memories**: List of knowledge items
- **Chat**: Message history and loading states
- **UI State**: Sidebar toggle, search queries

## API Integration

The frontend is designed to connect to the FastAPI backend at `http://localhost:8000/api/v1` with endpoints for:

- Memory CRUD operations
- Vector search
- Chat/RAG interactions
- MCP server communication

## Development Notes

1. The app uses Next.js 14's App Router for file-based routing
2. All components use TypeScript for type safety
3. Tailwind CSS with CSS variables for theming
4. Mobile-responsive design with collapsible sidebar
5. Real-time features ready for WebSocket integration