# QRadar-MCP-Client - Development Plan

> ⚠️ **THIS FILE IS LOCAL ONLY - DO NOT PUSH TO GIT**  
> Add to `.gitignore` before any git operations

---

## 🎯 Project Vision

A **Claude Desktop-like** MCP client with IBM Carbon Design that enables:
- Chat interface to interact with QRadar through natural language
- Multi-QRadar console support
- Multi-MCP server support  
- Multiple LLM model options

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     QRadar-MCP-Client                           │
├─────────────────────────────────────────────────────────────────┤
│  FRONTEND (React + Carbon Design)                               │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  Chat UI     │ │  Settings    │ │  Connection  │            │
│  │  (Claude-    │ │  Panel       │ │  Manager     │            │
│  │   like)      │ │              │ │              │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  BACKEND (FastAPI + Python)                                     │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │  MCP Client  │ │  LLM Router  │ │  QRadar      │            │
│  │  Manager     │ │  (Model      │ │  Connection  │            │
│  │              │ │   Inference) │ │  Pool        │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  CONNECTIONS                                                    │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  MCP Servers          │  QRadar Consoles    │  LLM Models  ││
│  │  - QRadar-MCP-Server  │  - Console 1 (URL)  │  - Watsonx   ││
│  │  - Other MCP Servers  │  - Console 2 (URL)  │  - OpenAI    ││
│  │                       │  - Console N...     │  - Claude    ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Requirements Breakdown

### Connection Configuration (Per QRadar)
```typescript
interface QRadarConnection {
  id: string;
  name: string;           // Display name (e.g., "Production QRadar")
  url: string;            // https://qradar-console.example.com
  token: string;          // API Token (encrypted storage)
  verify: boolean;        // SSL certificate verification (true/false)
  isDefault: boolean;     // Default connection for new chats
}
```

### MCP Server Configuration
```typescript
interface MCPServerConnection {
  id: string;
  name: string;           // Display name
  command: string;        // e.g., "python3 -m src.server"
  args: string[];         // Command arguments
  env: Record<string, string>;  // Environment variables
  qradarConnectionId: string;   // Which QRadar to use
}
```

### LLM Model Configuration
```typescript
interface LLMModelConfig {
  id: string;
  provider: 'watsonx' | 'openai' | 'anthropic' | 'ollama';
  name: string;
  apiKey: string;
  baseUrl?: string;       // For self-hosted
  modelId: string;        // e.g., "gpt-4", "claude-3-opus"
  isDefault: boolean;
}
```

---

## 🎨 UI Components (Carbon Design)

### 1. Main Layout
- **Header**: App name, model selector, settings gear
- **Sidebar** (Left): 
  - **New Chat** button (top)
  - **Chat History** list (like ChatGPT/Claude Desktop)
    - Today's chats
    - Yesterday's chats  
    - Previous 7 days
    - Older (grouped by month)
  - Rename/Delete chat options
  - Search chats
- **Main Area**: Chat interface (Claude Desktop style)
- **Right Panel** (collapsible): QRadar & Connection selector

### 2. Chat Interface
- Message bubbles (user/assistant)
- Code blocks with syntax highlighting
- Tool call displays (show which MCP tool was called)
- Streaming responses
- Copy/export conversation

### 3. Settings Panels
- **QRadar Connections**: Add/Edit/Delete/Test connections
- **MCP Servers**: Manage MCP server configurations
- **LLM Models**: Configure AI model providers
- **Preferences**: Theme, defaults, etc.

### 4. Connection Status Bar
- Show active QRadar connection
- Show MCP server status
- Show selected model

---

## ❓ Do We Need Model Inference?

**YES, absolutely!** Here's why:

An MCP Client needs an LLM to:
1. **Understand** user's natural language question
2. **Decide** which MCP tools to call
3. **Format** the tool call arguments
4. **Interpret** the tool results
5. **Generate** human-readable response

### Model Inference Options

| Provider | Models | Self-Hosted | Cost |
|----------|--------|-------------|------|
| **Watsonx** | granite-3.1, llama-3.3 | Yes (On-prem) | Enterprise |
| **OpenAI** | GPT-4, GPT-4o | No | Pay-per-use |
| **Anthropic** | Claude 3.5 Sonnet | No | Pay-per-use |
| **Ollama** | Llama, Mistral, etc. | Yes (Local) | Free |

**Recommendation**: Support multiple providers, let user choose.

---

## 📁 Proposed Project Structure

```
QRadar-MCP-Client/
├── frontend/                    # React + Vite + Carbon
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── ToolCallDisplay.tsx
│   │   │   │   └── InputArea.tsx
│   │   │   ├── Sidebar/
│   │   │   │   ├── Sidebar.tsx           # Main sidebar container
│   │   │   │   ├── NewChatButton.tsx     # "New Chat" button
│   │   │   │   ├── ChatHistoryList.tsx   # List of past conversations
│   │   │   │   ├── ChatHistoryItem.tsx   # Individual chat item (rename/delete)
│   │   │   │   ├── ChatSearch.tsx        # Search through chats
│   │   │   │   └── ConnectionStatus.tsx
│   │   │   ├── RightPanel/
│   │   │   │   ├── RightPanel.tsx        # Collapsible right panel
│   │   │   │   ├── QRadarSelector.tsx    # Select active QRadar
│   │   │   │   └── ModelSelector.tsx     # Select LLM model
│   │   │   ├── Settings/
│   │   │   │   ├── QRadarConnections.tsx
│   │   │   │   ├── MCPServers.tsx
│   │   │   │   ├── LLMModels.tsx
│   │   │   │   └── SettingsModal.tsx
│   │   │   └── Layout/
│   │   │       ├── Header.tsx
│   │   │       └── MainLayout.tsx
│   │   ├── hooks/
│   │   │   ├── useChat.ts
│   │   │   ├── useConnections.ts
│   │   │   └── useMCP.ts
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── store/
│   │   │   └── index.ts          # State management
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # FastAPI + Python
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── routers/
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── connections.py   # Connection management
│   │   │   └── mcp.py           # MCP server management
│   │   ├── services/
│   │   │   ├── llm/
│   │   │   │   ├── base.py      # LLM interface
│   │   │   │   ├── watsonx.py   # Watsonx provider
│   │   │   │   ├── openai.py    # OpenAI provider
│   │   │   │   └── ollama.py    # Ollama provider
│   │   │   ├── mcp_client.py    # MCP protocol client
│   │   │   └── qradar_pool.py   # QRadar connection pool
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   └── config.py            # Settings
│   ├── requirements.txt
│   └── pyproject.toml
│
├── .gitignore
├── docker-compose.yml           # Optional containerization
└── README.md
```

---

## 🚀 Development Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up Vite + React + Carbon Design
- [ ] Create main layout (Header, Sidebar, Chat area)
- [ ] Set up FastAPI backend structure
- [ ] Basic chat endpoint (mock LLM response)

### Phase 2: Connection Management (Week 2)
- [ ] QRadar connection CRUD (Add/Edit/Delete)
- [ ] Test connection functionality
- [ ] Secure token storage (encrypted)
- [ ] Connection selector UI

### Phase 3: MCP Integration (Week 3)
- [ ] MCP client implementation in backend
- [ ] Connect to QRadar-MCP-Server
- [ ] List available tools from MCP server
- [ ] Tool call execution flow

### Phase 4: LLM Integration (Week 4)
- [ ] LLM provider abstraction layer
- [ ] Watsonx integration (primary)
- [ ] OpenAI integration (secondary)
- [ ] Ollama integration (local option)
- [ ] Model selector UI

### Phase 5: Chat Experience (Week 5)
- [ ] Streaming responses
- [ ] Tool call visualization
- [ ] Code block rendering
- [ ] Chat history persistence (SQLite)
- [ ] Chat history sidebar (grouped by date)
- [ ] Rename/Delete conversations
- [ ] Search through chat history
- [ ] Export conversation

### Phase 6: Polish & Features (Week 6)
- [ ] Multi-chat tabs
- [ ] Keyboard shortcuts
- [ ] Dark/Light theme
- [ ] Error handling & retry
- [ ] Documentation

---

## 🔧 Tech Stack Summary

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI Framework |
| Vite | Build tool |
| @carbon/react | IBM Carbon Design System |
| TypeScript | Type safety |
| React Router | Navigation |
| Zustand/Redux | State management |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | API framework |
| Python 3.11+ | Runtime |
| mcp | MCP protocol library |
| httpx | Async HTTP client |
| SQLite/PostgreSQL | Data persistence |
| Pydantic | Data validation |

### LLM Providers
| Provider | Library |
|----------|---------|
| Watsonx | ibm-watsonx-ai |
| OpenAI | openai |
| Anthropic | anthropic |
| Ollama | ollama |

---

## 📊 API Endpoints (Backend)

```
POST   /api/chat                    # Send message, get response
GET    /api/chat/history            # Get chat history

GET    /api/connections/qradar      # List QRadar connections
POST   /api/connections/qradar      # Add QRadar connection
PUT    /api/connections/qradar/:id  # Update connection
DELETE /api/connections/qradar/:id  # Delete connection
POST   /api/connections/qradar/:id/test  # Test connection

GET    /api/mcp/servers             # List MCP servers
POST   /api/mcp/servers             # Add MCP server
GET    /api/mcp/servers/:id/tools   # Get available tools
POST   /api/mcp/servers/:id/start   # Start MCP server
POST   /api/mcp/servers/:id/stop    # Stop MCP server

GET    /api/models                  # List configured models
POST   /api/models                  # Add model config
PUT    /api/models/:id              # Update model config
```

---

## 🔐 Security Considerations

1. **Token Storage**: Encrypt API tokens at rest
2. **SSL Verification**: Option to disable for self-signed certs
3. **Local-only by default**: No cloud sync of credentials
4. **Environment Variables**: Support env vars for CI/CD

---

## 💡 Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State Management | Zustand | Simpler than Redux, Carbon compatible |
| LLM Default | Watsonx | IBM ecosystem alignment |
| Database | SQLite | Simple, file-based, no setup |
| Streaming | SSE | Real-time responses |

---

## 📅 Current Status

- **Phase**: Not Started
- **Blockers**: None
- **Next Action**: Create frontend foundation with Carbon

---

## 🔗 Related Projects

- **QRadar-MCP-Server**: `/Users/anujshrivastava/code/QRadar-MCP/QRadar-MCP-Server`
  - Status: Implemented with 100+ tools
  - Uses: stdio transport for MCP

---

*Last Updated: 22 January 2026*
