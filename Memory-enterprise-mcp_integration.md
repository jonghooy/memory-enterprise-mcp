# Memory Enterprise MCP Integration Guide

## 📋 Overview

이 문서는 Memory Enterprise MCP 서버를 Claude Desktop, Cursor, 또는 다른 MCP 클라이언트와 통합하는 방법을 설명합니다.

Memory Enterprise는 다음 MCP 프로토콜을 지원합니다:
- **HTTP**: REST 기반 통신 (웹 클라이언트용)
- **SSE (Server-Sent Events)**: 실시간 단방향 스트리밍 (웹 브라우저용)
- **JSON-RPC over SSE**: 표준 JSON-RPC 2.0 양방향 통신 (고급 웹 애플리케이션용)
- **stdio**: 표준 입출력 통신 (Claude Desktop용)

## 🚀 빠른 시작

### 1. 서버 실행

#### HTTP/SSE 서버 (기본)
```bash
# Docker 서비스 시작
docker-compose up -d

# FastAPI 서버 시작 (HTTP + SSE 프로토콜)
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8005
```

#### stdio 서버 (Claude Desktop용)
```bash
# 별도 터미널에서 stdio 서버 실행
python src/mcp/stdio_server.py
```

서버 상태 확인:
```bash
# HTTP/SSE 서버 상태
curl http://localhost:8005/health

# API 문서 확인
open http://localhost:8005/docs
```

## 🔌 JSON-RPC over SSE 프로토콜

JSON-RPC over SSE는 표준 JSON-RPC 2.0 사양을 SSE 전송 계층 위에 구현한 고급 프로토콜입니다.

### 프로토콜 특징
- **표준 준수**: JSON-RPC 2.0 완벽 지원 (요청, 응답, 알림, 배치)
- **양방향 통신**: SSE (서버→클라이언트) + HTTP POST (클라이언트→서버)
- **세션 기반**: UUID로 각 세션 격리 및 상태 관리
- **비동기 메시징**: 메시지 큐를 통한 비동기 알림 전달
- **배치 처리**: 여러 요청을 한 번에 처리 가능

### 엔드포인트

#### 1. SSE 스트림 연결
```
GET /mcp/jsonrpc-sse/stream/{session_id}
```
서버에서 클라이언트로 실시간 이벤트 스트리밍

#### 2. 단일 요청
```
POST /mcp/jsonrpc-sse/request/{session_id}
```
JSON-RPC 2.0 요청 전송 및 동기 응답 수신

#### 3. 배치 요청
```
POST /mcp/jsonrpc-sse/batch/{session_id}
```
여러 JSON-RPC 요청을 한 번에 처리

### JavaScript 클라이언트 구현

```javascript
class JSONRPCOverSSEClient {
  constructor(baseUrl = 'http://localhost:8005') {
    this.baseUrl = baseUrl;
    this.sessionId = null;
    this.eventSource = null;
    this.requestId = 0;
  }

  // 세션 연결
  connect() {
    this.sessionId = crypto.randomUUID();
    const streamUrl = `${this.baseUrl}/mcp/jsonrpc-sse/stream/${this.sessionId}`;

    this.eventSource = new EventSource(streamUrl);

    this.eventSource.onopen = () => {
      console.log('JSON-RPC over SSE connected');
    };

    this.eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
    };
  }

  // 메시지 처리
  handleMessage(data) {
    if (!data.id) {
      // 알림 메시지 (id가 없음)
      this.handleNotification(data);
    } else {
      // 응답 메시지
      console.log('Response:', data);
    }
  }

  // 알림 처리
  handleNotification(notification) {
    switch (notification.method) {
      case 'session.connected':
        console.log('Session connected:', notification.params.session_id);
        break;
      case 'session.heartbeat':
        // 30초마다 수신되는 heartbeat
        break;
      case 'memory.created':
        console.log('Memory created:', notification.params);
        break;
      default:
        console.log('Notification:', notification);
    }
  }

  // JSON-RPC 요청 전송
  async request(method, params = null) {
    const request = {
      jsonrpc: '2.0',
      method: method,
      id: `req-${++this.requestId}`
    };

    if (params) {
      request.params = params;
    }

    const response = await fetch(
      `${this.baseUrl}/mcp/jsonrpc-sse/request/${this.sessionId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      }
    );

    return response.json();
  }

  // 배치 요청
  async batch(requests) {
    const batchRequest = requests.map((req, idx) => ({
      jsonrpc: '2.0',
      method: req.method,
      params: req.params,
      id: `batch-${++this.requestId}-${idx}`
    }));

    const response = await fetch(
      `${this.baseUrl}/mcp/jsonrpc-sse/batch/${this.sessionId}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(batchRequest)
      }
    );

    return response.json();
  }

  // MCP 초기화
  async initialize() {
    return this.request('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: {
        name: 'Web Client',
        version: '1.0.0'
      }
    });
  }

  // 도구 호출
  async callTool(name, args) {
    return this.request('tools/call', {
      name: name,
      arguments: args
    });
  }

  // 연결 종료
  disconnect() {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.sessionId = null;
  }
}

// 사용 예시
const client = new JSONRPCOverSSEClient();

// 연결 및 초기화
client.connect();
await client.initialize();

// 메모리 생성
const memory = await client.callTool('memory_create', {
  content: 'JSON-RPC over SSE enables bidirectional communication',
  tenant_id: 'app',
  user_id: 'user1',
  metadata: { protocol: 'jsonrpc-sse' }
});

// 검색
const results = await client.callTool('memory_search', {
  query: 'JSON-RPC',
  tenant_id: 'app',
  limit: 10
});

// 배치 작업
const batchResults = await client.batch([
  { method: 'tools/list' },
  {
    method: 'tools/call',
    params: {
      name: 'memory_list',
      arguments: { tenant_id: 'app', limit: 5 }
    }
  }
]);

// 연결 종료
client.disconnect();
```

### React Hook 예시

```jsx
import { useState, useEffect, useCallback } from 'react';

function useJSONRPCOverSSE(baseUrl = 'http://localhost:8005') {
  const [connected, setConnected] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [client, setClient] = useState(null);

  useEffect(() => {
    const rpcClient = new JSONRPCOverSSEClient(baseUrl);

    // 연결 설정
    rpcClient.connect();
    setSessionId(rpcClient.sessionId);
    setClient(rpcClient);

    // 연결 상태 모니터링
    const checkConnection = setInterval(() => {
      setConnected(rpcClient.eventSource?.readyState === EventSource.OPEN);
    }, 1000);

    // Cleanup
    return () => {
      clearInterval(checkConnection);
      rpcClient.disconnect();
    };
  }, [baseUrl]);

  const callTool = useCallback(async (name, args) => {
    if (!client) return null;
    return client.callTool(name, args);
  }, [client]);

  const request = useCallback(async (method, params) => {
    if (!client) return null;
    return client.request(method, params);
  }, [client]);

  return {
    connected,
    sessionId,
    callTool,
    request,
    client
  };
}

// 컴포넌트에서 사용
function MemoryApp() {
  const { connected, sessionId, callTool } = useJSONRPCOverSSE();

  const createMemory = async (content) => {
    const result = await callTool('memory_create', {
      content,
      tenant_id: 'react-app',
      user_id: 'current-user'
    });
    return result;
  };

  return (
    <div>
      <h2>Memory Client</h2>
      <p>Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}</p>
      <p>Session: {sessionId}</p>
      {/* UI components */}
    </div>
  );
}
```

### 테스트 클라이언트

웹 브라우저용 테스트 클라이언트가 제공됩니다:

```bash
# 테스트 클라이언트 열기
open test_jsonrpc_sse.html
```

테스트 클라이언트 기능:
- 세션 연결/종료
- MCP 초기화
- 메모리 CRUD 작업
- 실시간 통신 로그
- JSON-RPC 메시지 시각화

### JSON-RPC over SSE vs 일반 SSE 비교

| 특징 | JSON-RPC over SSE | 일반 SSE |
|------|------------------|----------|
| 표준 준수 | JSON-RPC 2.0 완벽 지원 | 커스텀 프로토콜 |
| 요청 ID | 모든 요청에 고유 ID | ID 없음 |
| 에러 처리 | 표준화된 에러 코드 | 커스텀 에러 처리 |
| 배치 처리 | 지원 | 미지원 |
| 알림 | 표준 notification 형식 | 커스텀 이벤트 |
| 세션 관리 | UUID 기반 격리 | 단순 연결 |

## 🔧 클라이언트 설정

### Claude Desktop 설정

Claude Desktop의 설정 파일을 수정합니다:

**위치**:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

#### 옵션 1: stdio 프로토콜 사용 (권장)
```json
{
  "mcpServers": {
    "memory-enterprise": {
      "command": "python",
      "args": ["/path/to/rag-mcp/src/mcp/stdio_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/rag-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 옵션 2: HTTP 프로토콜 사용
```json
{
  "mcpServers": {
    "memory-enterprise": {
      "type": "http",
      "url": "http://localhost:8005/mcp/request",
      "headers": {
        "Content-Type": "application/json"
      },
      "defaultParams": {
        "tenant_id": "default",
        "user_id": "user1"
      }
    }
  }
}
```

### Cursor IDE 설정

Cursor의 설정 파일을 수정합니다:

**위치**: `.cursor/settings.json` (프로젝트 루트)

```json
{
  "mcp": {
    "servers": {
      "memory-enterprise": {
        "endpoint": "http://localhost:8005/mcp/request",
        "description": "Enterprise Memory Agent for persistent knowledge management",
        "enabled": true,
        "defaultParams": {
          "tenant_id": "project1",
          "user_id": "developer1"
        }
      }
    }
  }
}
```

### VS Code with Continue 설정

Continue 확장 프로그램 설정:

**위치**: `.continue/config.json`

```json
{
  "models": [
    {
      "title": "Claude with Memory",
      "provider": "anthropic",
      "model": "claude-3-opus-20240229",
      "mcpServers": [
        {
          "name": "memory-enterprise",
          "endpoint": "http://localhost:8005/mcp/request",
          "tenant_id": "vscode-project"
        }
      ]
    }
  ]
}
```

### 웹 애플리케이션용 SSE 설정

SSE (Server-Sent Events)는 서버에서 클라이언트로 실시간 단방향 스트리밍을 제공합니다.

#### SSE 엔드포인트
- **스트림 연결**: `GET /mcp/sse/stream` - 실시간 이벤트 스트리밍
- **메시지 처리**: `POST /mcp/sse/message` - MCP 메시지 송신

#### JavaScript 클라이언트 구현

```javascript
// 1. SSE 스트림 연결
const eventSource = new EventSource('http://localhost:8005/mcp/sse/stream');

// 2. 이벤트 리스너 설정
eventSource.addEventListener('connected', (event) => {
  const data = JSON.parse(event.data);
  console.log('Connected with session:', data.session_id);
  // 세션 ID를 저장하여 추후 요청에 사용 가능
});

eventSource.addEventListener('ping', (event) => {
  const data = JSON.parse(event.data);
  console.log('Heartbeat received:', data.timestamp);
  // 30초마다 heartbeat 수신
});

eventSource.onerror = (error) => {
  console.error('SSE connection error:', error);
  // 연결 오류 처리
};

// 3. MCP 메시지 전송 함수
async function sendMCPMessage(method, params = {}) {
  const response = await fetch('http://localhost:8005/mcp/sse/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      method: method,
      params: params,
      id: crypto.randomUUID()
    })
  });
  return response.json();
}

// 4. 사용 예시
async function initializeMCP() {
  const result = await sendMCPMessage('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {}
  });
  console.log('Initialized:', result);
}

async function createMemory(content, metadata = {}) {
  const result = await sendMCPMessage('tools/call', {
    name: 'memory_create',
    arguments: {
      content: content,
      tenant_id: 'web-app',
      user_id: 'current-user',
      metadata: metadata
    }
  });
  return result;
}

async function searchMemories(query) {
  const result = await sendMCPMessage('tools/call', {
    name: 'memory_search',
    arguments: {
      query: query,
      tenant_id: 'web-app',
      limit: 10
    }
  });
  return JSON.parse(result.result.content[0].text);
}

// 5. 연결 종료 시 정리
window.addEventListener('beforeunload', () => {
  eventSource.close();
});
```

#### React 컴포넌트 예시

```jsx
import React, { useEffect, useState } from 'react';

function MCPMemoryClient() {
  const [sessionId, setSessionId] = useState(null);
  const [connected, setConnected] = useState(false);
  const [eventSource, setEventSource] = useState(null);

  useEffect(() => {
    // SSE 연결 초기화
    const sse = new EventSource('http://localhost:8005/mcp/sse/stream');

    sse.addEventListener('connected', (event) => {
      const data = JSON.parse(event.data);
      setSessionId(data.session_id);
      setConnected(true);
    });

    sse.addEventListener('ping', (event) => {
      console.log('Heartbeat:', JSON.parse(event.data).timestamp);
    });

    sse.onerror = () => {
      setConnected(false);
    };

    setEventSource(sse);

    // Cleanup on unmount
    return () => {
      sse.close();
    };
  }, []);

  const callMCP = async (method, params) => {
    const response = await fetch('http://localhost:8005/mcp/sse/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method,
        params,
        id: crypto.randomUUID()
      })
    });
    return response.json();
  };

  return (
    <div>
      <p>Status: {connected ? '🟢 Connected' : '🔴 Disconnected'}</p>
      <p>Session: {sessionId || 'Not initialized'}</p>
    </div>
  );
}
```

#### SSE 프로토콜 특징
- **단방향 통신**: 서버 → 클라이언트 실시간 스트리밍
- **자동 재연결**: 브라우저가 연결 끊김 시 자동 재연결 시도
- **텍스트 기반**: UTF-8 인코딩된 텍스트 데이터
- **이벤트 형식**: `event: type\ndata: json\n\n`
- **Heartbeat**: 30초마다 ping 이벤트로 연결 상태 확인

## 📚 사용 가능한 MCP 도구들

### 1. memory_search
지식 베이스에서 정보 검색

**사용 예시**:
```
@memory-enterprise Search for authentication implementation details
```

**파라미터**:
- `query` (string, required): 검색 쿼리
- `tenant_id` (string, required): 테넌트 ID
- `limit` (number, optional): 최대 결과 수 (기본값: 10)

### 2. memory_create
새로운 지식 항목 생성

**사용 예시**:
```
@memory-enterprise Remember that we use JWT tokens with 24-hour expiration
```

**파라미터**:
- `content` (string, required): 저장할 내용
- `tenant_id` (string, required): 테넌트 ID
- `user_id` (string, required): 사용자 ID
- `metadata` (object, optional): 추가 메타데이터
- `source` (object, optional): 소스 정보

### 3. memory_update
기존 지식 항목 수정

**사용 예시**:
```
@memory-enterprise Update the JWT token info to include refresh token rotation
```

**파라미터**:
- `memory_id` (string, required): 메모리 ID
- `content` (string, optional): 새로운 내용
- `metadata` (object, optional): 업데이트할 메타데이터

### 4. memory_delete
지식 항목 삭제

**사용 예시**:
```
@memory-enterprise Delete the outdated authentication documentation
```

**파라미터**:
- `memory_id` (string, required): 삭제할 메모리 ID

### 5. memory_list
지식 목록 조회

**사용 예시**:
```
@memory-enterprise Show all memories related to authentication
```

**파라미터**:
- `tenant_id` (string, required): 테넌트 ID
- `user_id` (string, optional): 특정 사용자로 필터링
- `skip` (number, optional): 건너뛸 항목 수
- `limit` (number, optional): 최대 항목 수

### 6. wiki_link_extract
텍스트에서 Wiki 링크 추출

**사용 예시**:
```
@memory-enterprise Extract entities from "The [[authentication]] uses [[JWT]] tokens"
```

**파라미터**:
- `text` (string, required): Wiki 링크를 추출할 텍스트

### 7. wiki_link_graph
Wiki 링크 기반 지식 그래프 생성

**사용 예시**:
```
@memory-enterprise Show knowledge graph around [[authentication]]
```

**파라미터**:
- `tenant_id` (string, required): 테넌트 ID
- `entity` (string, optional): 중심 엔티티
- `depth` (number, optional): 그래프 깊이


## 🏢 멀티 테넌시 설정

### 프로젝트별 테넌트 구성

여러 프로젝트에 대해 서로 다른 테넌트 설정:

```json
{
  "mcpServers": {
    "memory-project-alpha": {
      "url": "http://localhost:8005/mcp",
      "defaultParams": {
        "tenant_id": "project-alpha",
        "user_id": "dev-team"
      }
    },
    "memory-project-beta": {
      "url": "http://localhost:8005/mcp",
      "defaultParams": {
        "tenant_id": "project-beta",
        "user_id": "dev-team"
      }
    }
  }
}
```

### 팀별 네임스페이스

팀별로 독립된 지식 베이스 유지:

```json
{
  "mcpServers": {
    "memory-backend": {
      "url": "http://localhost:8005/mcp",
      "defaultParams": {
        "tenant_id": "backend-team",
        "namespace": "api-docs"
      }
    },
    "memory-frontend": {
      "url": "http://localhost:8005/mcp",
      "defaultParams": {
        "tenant_id": "frontend-team",
        "namespace": "ui-components"
      }
    }
  }
}
```

## 📊 사용 예시

### 프로젝트 지식 관리

```python
# 아키텍처 결정 저장
@memory-enterprise Remember: We decided to use PostgreSQL as main database and Redis for caching

# 이전 결정 검색
@memory-enterprise What database technology did we choose for this project?

# 연관 정보 연결
@memory-enterprise The [[authentication]] system uses [[PostgreSQL]] for user storage and [[Redis]] for session management
```

### 코드 문서화

```python
# 구현 세부사항 저장
@memory-enterprise The rate limiting is implemented using sliding window algorithm with Redis

# 구현 방법 검색
@memory-enterprise How does our rate limiting work?

# 관련 컴포넌트 추적
@memory-enterprise Show all memories related to rate limiting
```

### 팀 지식 공유

```python
# 팀 규칙 저장
@memory-enterprise Team convention: All API endpoints must have OpenAPI documentation

# 팀 관례 검색
@memory-enterprise What are our API documentation requirements?

# 지식 그래프 생성
@memory-enterprise Show knowledge graph for [[API conventions]]
```

## 🔍 문제 해결

### 연결 문제

1. **서버 상태 확인**:
```bash
curl http://localhost:8005/health
```

2. **MCP 엔드포인트 테스트**:
```bash
# HTTP 엔드포인트
curl http://localhost:8005/mcp/tools

# SSE 스트림 테스트 (연결 확인)
curl -N http://localhost:8005/mcp/sse/stream

# SSE 스트림 이벤트 확인 (5초간)
curl -N http://localhost:8005/mcp/sse/stream 2>&1 | head -5
```

3. **테스트 요청 실행**:
```bash
# HTTP 프로토콜
curl -X POST http://localhost:8005/mcp/request \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "id": "test-1"
  }'

# SSE 프로토콜 - 초기화
curl -X POST http://localhost:8005/mcp/sse/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {"protocolVersion": "2024-11-05"},
    "id": "test-init"
  }'

# SSE 프로토콜 - 도구 목록
curl -X POST http://localhost:8005/mcp/sse/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "test-tools"
  }'

# SSE 프로토콜 - 메모리 생성
curl -X POST http://localhost:8005/mcp/sse/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "memory_create",
      "arguments": {
        "content": "Test memory via SSE",
        "tenant_id": "test",
        "user_id": "user1"
      }
    },
    "id": "test-create"
  }'

# JSON-RPC over SSE 프로토콜 - 세션 생성 및 스트림 연결
SESSION_ID=$(uuidgen)  # macOS/Linux
# 또는 SESSION_ID=$(cat /proc/sys/kernel/random/uuid)  # Linux only

# JSON-RPC over SSE - 스트림 연결 (백그라운드)
curl -N http://localhost:8005/mcp/jsonrpc-sse/stream/$SESSION_ID &

# JSON-RPC over SSE - 초기화
curl -X POST http://localhost:8005/mcp/jsonrpc-sse/request/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {}
    },
    "id": "init-1"
  }'

# JSON-RPC over SSE - 도구 목록
curl -X POST http://localhost:8005/mcp/jsonrpc-sse/request/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "tools-1"
  }'

# JSON-RPC over SSE - 배치 요청
curl -X POST http://localhost:8005/mcp/jsonrpc-sse/batch/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '[
    {"jsonrpc": "2.0", "method": "tools/list", "id": "batch-1"},
    {
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
        "name": "memory_list",
        "arguments": {"tenant_id": "test", "limit": 5}
      },
      "id": "batch-2"
    }
  ]'
```

4. **stdio 서버 테스트**:
```bash
# stdio 프로토콜 테스트 (JSON-RPC 2.0)
echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | python src/mcp/stdio_server.py
```

### SSE 특정 문제 해결

#### SSE 연결이 끊어지는 경우
- **원인**: Nginx/프록시 타임아웃, 네트워크 불안정
- **해결방법**:
  ```nginx
  # Nginx 설정
  location /mcp/sse {
    proxy_pass http://localhost:8005;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_buffering off;
    proxy_cache off;
    proxy_read_timeout 86400s;
    proxy_set_header X-Accel-Buffering no;
  }
  ```

#### SSE 이벤트가 수신되지 않는 경우
- **브라우저 콘솔에서 확인**:
  ```javascript
  const sse = new EventSource('http://localhost:8005/mcp/sse/stream');
  sse.onmessage = (e) => console.log('Message:', e.data);
  sse.onerror = (e) => console.error('Error:', e);
  ```

#### CORS 오류 발생 시
- **FastAPI 서버에 이미 CORS 설정되어 있음**
- **추가 설정이 필요한 경우 src/main.py 확인**

### 일반적인 오류

#### "Connection refused" 오류
- 서버가 실행 중인지 확인
- 포트 번호가 올바른지 확인 (기본: 8005)
- 방화벽 설정 확인

#### "Tenant not found" 오류
- tenant_id가 올바르게 설정되어 있는지 확인
- 대소문자 구분 확인

#### "Authentication failed" 오류
- API 키나 토큰이 올바른지 확인
- 환경 변수가 제대로 설정되어 있는지 확인

### 로그 확인

서버 로그:
```bash
# FastAPI 서버 로그 (HTTP/SSE)
docker-compose logs -f api

# stdio 서버 로그
tail -f /tmp/mcp_server.log
```

클라이언트 로그 (Claude Desktop):
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\Logs\`
- Linux: `~/.local/share/Claude/logs/`

## 📈 성능 최적화

### 캐싱 설정

Redis 캐싱 활성화:
```json
{
  "mcpServers": {
    "memory-enterprise": {
      "url": "http://localhost:8005/mcp",
      "cache": {
        "enabled": true,
        "ttl": 300,
        "max_size": 1000
      }
    }
  }
}
```

### 배치 작업

여러 작업을 한 번에 처리:
```json
{
  "method": "batch",
  "params": {
    "operations": [
      {
        "method": "memory_create",
        "params": { ... }
      },
      {
        "method": "memory_create",
        "params": { ... }
      }
    ]
  }
}
```

## 🚀 프로덕션 배포

### Docker Compose 설정

```yaml
version: '3.8'

services:
  mcp-server:
    image: memory-enterprise:latest
    ports:
      - "8005:8000"
    environment:
      - ENVIRONMENT=production
      - VECTOR_STORE_TYPE=pinecone
      - PINECONE_API_KEY=${PINECONE_API_KEY}
    volumes:
      - ./config:/app/config
    restart: always
```

### HTTPS 설정

Nginx 리버스 프록시:
```nginx
server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /mcp {
        proxy_pass http://localhost:8005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔐 보안 고려사항

### 현재 구현 상태
⚠️ **주의**: 현재 MVP 버전은 인증이 구현되지 않은 상태입니다.

**TODO 항목**:
- JWT 토큰 기반 인증 구현
- Google OAuth 통합 완성
- API 키 인증 추가
- Rate limiting 구현
- 테넌트 기반 접근 제어

### 프로덕션 배포 전 체크리스트
- [ ] 인증 미들웨어 활성화
- [ ] HTTPS 설정 필수
- [ ] CORS 설정 검토
- [ ] Rate limiting 설정
- [ ] API 키 관리 시스템
- [ ] 감사 로깅 활성화

## 📚 추가 리소스

- [MCP Protocol Specification](https://github.com/anthropics/mcp-spec)
- [Memory Enterprise API Documentation](http://localhost:8005/docs)
- [프로젝트 GitHub Repository](https://github.com/your-org/memory-enterprise)

## 💬 지원

문제가 발생하거나 도움이 필요한 경우:
1. [GitHub Issues](https://github.com/your-org/memory-enterprise/issues)에 문제 제출
2. [Discord 커뮤니티](https://discord.gg/your-invite) 참여
3. 이메일 문의: support@memory-enterprise.com

## 📝 버전 히스토리

### v0.1.0 (현재)
- **MCP 프로토콜 완전 지원**:
  - HTTP: REST API 기반 동기 통신
  - SSE: 실시간 단방향 스트리밍 (웹 클라이언트)
  - JSON-RPC over SSE: 표준 JSON-RPC 2.0 양방향 통신 (고급 웹 애플리케이션)
  - stdio: JSON-RPC 2.0 표준 입출력 (Claude Desktop)
- **7가지 메모리 관리 도구**:
  - memory_search: 시맨틱 검색
  - memory_create: 메모리 생성
  - memory_update: 메모리 수정
  - memory_delete: 메모리 삭제
  - memory_list: 목록 조회
  - wiki_link_extract: Wiki 링크 추출
  - wiki_link_graph: 지식 그래프 (개발 중)
- **핵심 기능**:
  - Wiki-link 시스템 (`[[entity]]` 형식)
  - 멀티 테넌시 지원 (테넌트별 격리)
  - 세션 관리 (UUID 기반)
  - Heartbeat (30초 간격 ping)
  - JSON-RPC 2.0 표준 완벽 지원 (요청/응답/알림/배치)
  - 비동기 메시지 큐 기반 알림 시스템
  - 웹 브라우저 테스트 클라이언트 포함
- **기술 스택**:
  - FastAPI (웹 프레임워크)
  - LlamaIndex 0.11.23 (RAG 엔진)
  - Pydantic (데이터 검증)
  - asyncio (비동기 처리)