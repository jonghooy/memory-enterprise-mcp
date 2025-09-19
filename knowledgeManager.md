# 지식 관리 인터페이스 설계안 (v2.1 - UI 개발 계획 포함)

## 1. 목표 및 핵심 고려사항

### 1.1 목표
사용자가 분산된 지식을 한 곳에서 탐색, 관리하는 것을 넘어, 자연어 질문을 통해 여러 소스를 넘나드는 복합적인 답변과 통찰을 얻을 수 있는 RAG 네이티브(Native) 인터페이스를 제공한다.

### 1.2 RAG 최적화 핵심 고려사항

- **대화형 인터페이스 (Conversational Interface)**: 단순 키워드 검색이 아닌, 완전한 문장의 질문을 입력하는 것을 기본 상호작용 방식으로 유도한다.
- **종합된 답변 (Synthesized Answer)**: 분산된 정보 조각들을 LLM이 종합하여 생성한, 읽기 쉬운 요약 답변을 최우선으로 제시한다.
- **투명한 출처 제시 (Source Attribution)**: AI가 어떤 근거(문서, 메모리)를 바탕으로 답변을 생성했는지 명확히 보여주어 사용자의 신뢰를 확보한다.

2. 메뉴 시스템 (좌측 네비게이션 바) - 수정
💬 AI 어시스턴트 (AI Assistant) - [신규]

RAG의 핵심 기능이 집약된 공간. 사용자가 자연어 질문을 통해 지식 베이스 전체와 대화하는 메인 인터페이스.

🏠 홈 (Home)

빠른 질문 입력창과 개인화된 지식 현황판을 제공.

📚 지식 베이스 (Knowledge Base)

모든 지식 리소스를 파일 탐색기처럼 탐색하고 필터링하는 공간.

🔗 연결 관리 (Connections)

외부 데이터 소스를 연동하고 관리하는 공간.

⚙️ 설정 (Settings)

개인 프로필, 알림 등 계정 관련 설정을 관리.

3. UI 와이어프레임 (RAG 최적화)
3.1 AI 어시스턴트 / 검색 결과 뷰 - [신규 핵심 화면]
목적: 사용자의 질문에 대해 LLM이 종합한 답변과 그 근거를 명확하고 신뢰도 높게 제시한다.

+--------------------------------------------------------------------------+
| [ AI 어시스턴트 ]                                                          |
|  > 3분기 실적 보고서의 핵심 요약과 AI팀의 다음 액션 아이템은 무엇인가요?        |
+--------------------------------------------------------------------------+
|                                                                          |
|  ## 답변 요약                                                            |
|  3분기 실적은 목표 대비 105%를 달성했으며, 특히 신규 고객 유입이 주요     |
|  요인이었습니다. (출처 1) AI팀의 다음 액션 아이템은 '고객 이탈 예측 모델' |
|  을 개발하는 것으로, 10월 25일까지 프로토타입을 완성해야 합니다. (출처 2) |
|                                                                          |
|  ---                                                                     |
|                                                                          |
|  ## 답변 근거 (Sources)                                                  |
|  +----------------------------------------------------------------+      |
|  | 1. 📄 3분기 실적 보고서 초안.pdf                               |      |
|  |    "...신규 고객 유입률이 전 분기 대비 15% 증가하여, 전체 실적은 |      |
|  |    목표 대비 105%를 달성하는 데 기여했다..." [자세히 보기]        |      |
|  +----------------------------------------------------------------+      |
|  | 2. 🤝 AI팀 주간 회의록 (2025-09-17)                            |      |
|  |    "...논의 결과, 다음 액션 아이템으로 '고객 이탈 예측 모델' 개발 |      |
|  |    건을 확정함. 담당자: [[이영희 (PM)]], 1차 목표: 10/25..." [자세히 보기] |      |
|  +----------------------------------------------------------------+      |
|                                                                          |
|  [ 후속 질문을 입력하거나, 위 답변에 대해 더 물어보세요... ]               |
+--------------------------------------------------------------------------+

3.2 홈 (Home) - 개인 대시보드 (수정)
목적: 서비스의 첫인상을 '검색'이 아닌 '질문'으로 유도하고, 개인화된 정보를 제공.

+--------------------------------------------------------------------------+
| [ OOO님의 메모리 허브 ]                                     [ 내 프로필 O ] |
+--------------------------------------------------------------------------+
|                                                                          |
|            +----------------------------------------------+              |
|            | 무엇이든 물어보세요...                         |              |
|            | 예: "2025년 신규 프로젝트 관련 최근 업데이트 내용 요약해 줘" |              |
|            +----------------------------------------------+              |
|                                                                          |
|  [최근 추가된 메모리]                  [자주 찾는 엔티티]                    |
|  +--------------------------+        +--------------------------+        |
|  | 📄 3분기 실적 보고서 초안   |        | 👤 이영희 (PM)            |        |
|  | 🤝 AI팀 주간 회의록        |        | 💡 2025년 신규 프로젝트   |        |
|  +--------------------------+        +--------------------------+        |
|                                                                          |
|                                                              [+ 새 메모리] |
+--------------------------------------------------------------------------+

3.3 지식 베이스 (모든 메모리 뷰) - (기존 유지)
목적: 파일 탐색기처럼 지식을 탐색하고 필터링하는 보조 기능. RAG 검색의 대상 범위를 좁히는 데 사용될 수 있다.

(v1.0 와이어프레임과 동일)

3.4 지식 상세 뷰 - (기존 유지)
목적: 개별 지식의 내용과 그 맥락(연결된 다른 지식)을 함께 파악.

(v1.0 와이어프레임과 동일)

3.5 연결 관리 (소스 관리 뷰) - (기존 유지)
목적: 외부 지식 소스를 연결하고 관리.

(v1.0 와이어프레임과 동일)

---

## 4. UI 개발 상세 계획

### 4.1 기술 스택 선정

#### Frontend Framework
- **Next.js 14** (App Router)
  - Server Components로 초기 로딩 성능 최적화
  - API Routes로 백엔드 통합 간소화
  - Built-in 인증 및 미들웨어 지원

#### UI Component Library
- **shadcn/ui + Radix UI**
  - 커스터마이징 가능한 컴포넌트
  - Accessibility 기본 지원
  - Tailwind CSS 기반 스타일링

#### 상태 관리
- **Zustand** (글로벌 상태)
- **TanStack Query** (서버 상태 관리)
- **React Hook Form** (폼 상태 관리)

#### 스타일링
- **Tailwind CSS** + **CSS Modules**
- **Framer Motion** (애니메이션)

#### 개발 도구
- **TypeScript** (타입 안정성)
- **ESLint + Prettier** (코드 품질)
- **Storybook** (컴포넌트 개발)

### 4.2 프로젝트 구조

```
frontend/
├── app/                      # Next.js App Router
│   ├── (dashboard)/         # 메인 대시보드 레이아웃
│   │   ├── layout.tsx       # 사이드바 포함 레이아웃
│   │   ├── page.tsx         # 홈 (대시보드)
│   │   ├── assistant/       # AI 어시스턴트
│   │   ├── knowledge/       # 지식 베이스
│   │   ├── connections/     # 연결 관리
│   │   └── settings/        # 설정
│   ├── api/                 # API Routes
│   │   ├── memories/
│   │   └── chat/
│   └── layout.tsx           # 루트 레이아웃
├── components/
│   ├── ui/                  # shadcn/ui 컴포넌트
│   ├── layout/              # 레이아웃 컴포넌트
│   │   ├── Sidebar/
│   │   ├── Header/
│   │   └── Footer/
│   ├── features/            # 기능별 컴포넌트
│   │   ├── assistant/       # AI 어시스턴트 컴포넌트
│   │   │   ├── ChatInterface/
│   │   │   ├── MessageList/
│   │   │   ├── SourceCard/
│   │   │   └── SuggestedQuestions/
│   │   ├── knowledge/       # 지식 베이스 컴포넌트
│   │   │   ├── MemoryCard/
│   │   │   ├── MemoryList/
│   │   │   ├── FilterPanel/
│   │   │   └── WikiLinkPreview/
│   │   ├── connections/     # 연결 관리 컴포넌트
│   │   │   ├── SourceCard/
│   │   │   ├── OAuthConnect/
│   │   │   └── SyncStatus/
│   │   └── search/          # 검색 컴포넌트
│   │       ├── SearchBar/
│   │       └── SearchResults/
│   └── shared/              # 공통 컴포넌트
│       ├── Avatar/
│       ├── LoadingSpinner/
│       └── ErrorBoundary/
├── lib/                     # 유틸리티 및 설정
│   ├── api/                # API 클라이언트
│   ├── hooks/              # Custom Hooks
│   ├── utils/              # 유틸리티 함수
│   └── constants/          # 상수
├── styles/                 # 글로벌 스타일
├── public/                 # 정적 파일
└── types/                  # TypeScript 타입 정의
```

### 4.3 핵심 컴포넌트 개발 계획

#### Phase 1: 기초 설정 (Week 1)
1. **프로젝트 초기화**
   - Next.js 14 프로젝트 생성
   - TypeScript, Tailwind CSS 설정
   - ESLint, Prettier 설정
   - shadcn/ui 설치 및 설정

2. **레이아웃 구조**
   - 기본 레이아웃 컴포넌트
   - 사이드바 네비게이션
   - 헤더 컴포넌트
   - 반응형 디자인 구현

3. **기본 라우팅**
   - 페이지 라우팅 설정
   - 네비게이션 구현
   - 404 페이지
   - 에러 바운더리

#### Phase 2: AI 어시스턴트 (Week 2)
1. **채팅 인터페이스**
   ```typescript
   // components/features/assistant/ChatInterface.tsx
   interface ChatInterfaceProps {
     onSendMessage: (message: string) => void
     isLoading: boolean
     suggestions?: string[]
   }
   ```
   - 메시지 입력 UI
   - 실시간 타이핑 인디케이터
   - 자동 완성 제안

2. **메시지 디스플레이**
   ```typescript
   // components/features/assistant/MessageList.tsx
   interface Message {
     id: string
     type: 'user' | 'assistant'
     content: string
     sources?: Source[]
     timestamp: Date
   }
   ```
   - 메시지 버블 UI
   - Markdown 렌더링
   - 코드 하이라이팅

3. **소스 어트리뷰션**
   ```typescript
   // components/features/assistant/SourceCard.tsx
   interface Source {
     id: string
     title: string
     excerpt: string
     type: 'document' | 'memory' | 'external'
     url?: string
     relevance: number
   }
   ```
   - 출처 카드 UI
   - 관련도 표시
   - 원문 미리보기

#### Phase 3: 지식 베이스 (Week 3)
1. **메모리 리스트 뷰**
   - 그리드/리스트 토글
   - 무한 스크롤
   - 정렬 옵션

2. **필터 패널**
   ```typescript
   interface FilterOptions {
     type?: MemoryType[]
     tags?: string[]
     dateRange?: { start: Date; end: Date }
     sources?: string[]
   }
   ```
   - 타입별 필터
   - 태그 필터
   - 날짜 범위 선택
   - 소스별 필터

3. **위키링크 시스템**
   - `[[entity]]` 파싱 및 렌더링
   - 호버 시 미리보기
   - 클릭 시 네비게이션

#### Phase 4: 연결 관리 (Week 4)
1. **소스 관리 대시보드**
   - 연결된 소스 리스트
   - 연결 상태 표시
   - 동기화 상태

2. **외부 서비스 연동**
   - Google Docs API 연결
   - Notion API 연결 (향후)
   - API 키 관리

3. **동기화 설정**
   - 수동/자동 동기화
   - 동기화 스케줄
   - 선택적 동기화

#### Phase 5: 검색 및 홈 (Week 5)
1. **통합 검색**
   - 실시간 검색
   - 검색 결과 하이라이팅
   - 필터 적용

2. **홈 대시보드**
   - 최근 활동
   - 통계 위젯
   - 빠른 액션

3. **개인화**
   - 사용자 설정
   - 테마 설정
   - 알림 설정

### 4.4 API 통합 계획

#### API Client 구조
```typescript
// lib/api/client.ts
class APIClient {
  private baseURL: string
  private token: string | null

  // Memory API
  async searchMemories(query: string, filters?: FilterOptions)
  async getMemory(id: string)
  async createMemory(data: MemoryCreate)
  async updateMemory(id: string, data: MemoryUpdate)
  async deleteMemory(id: string)

  // Assistant API
  async sendMessage(message: string, context?: string[])
  async getConversation(id: string)
  async getSuggestions(context: string)

  // Connection API
  async getConnections()
  async connectGoogle(code: string)
  async syncSource(sourceId: string)
}
```

#### Real-time 통신
```typescript
// lib/api/websocket.ts
class WebSocketClient {
  private ws: WebSocket

  // 실시간 메시지
  onMessage(callback: (message: Message) => void)

  // 동기화 상태
  onSyncUpdate(callback: (status: SyncStatus) => void)

  // 알림
  onNotification(callback: (notification: Notification) => void)
}
```

### 4.5 상태 관리 설계

#### Global Store (Zustand)
```typescript
// stores/useAppStore.ts
interface AppState {
  // User
  user: User | null
  setUser: (user: User | null) => void

  // UI
  sidebarOpen: boolean
  toggleSidebar: () => void

  // Theme
  theme: 'light' | 'dark'
  setTheme: (theme: 'light' | 'dark') => void
}

// stores/useMemoryStore.ts
interface MemoryState {
  memories: Memory[]
  selectedMemory: Memory | null
  filters: FilterOptions
  setFilters: (filters: FilterOptions) => void
  addMemory: (memory: Memory) => void
  updateMemory: (id: string, updates: Partial<Memory>) => void
  deleteMemory: (id: string) => void
}
```

### 4.6 성능 최적화 전략

1. **코드 분할**
   - 라우트별 자동 코드 분할
   - 동적 import로 컴포넌트 lazy loading
   - Suspense boundaries 설정

2. **데이터 페칭**
   - React Query로 캐싱
   - Optimistic updates
   - Background refetching

3. **렌더링 최적화**
   - React.memo 활용
   - useMemo/useCallback 최적화
   - Virtual scrolling (대량 리스트)

4. **Asset 최적화**
   - Next.js Image 컴포넌트
   - Font 최적화
   - SVG 스프라이트

### 4.7 테스팅 전략

1. **Unit Tests**
   - Jest + React Testing Library
   - 컴포넌트 단위 테스트
   - Hook 테스트

2. **Integration Tests**
   - API 통합 테스트
   - 라우팅 테스트

3. **E2E Tests**
   - Playwright
   - 주요 사용자 플로우 테스트

4. **Visual Regression**
   - Storybook + Chromatic

### 4.8 배포 계획

1. **Development**
   - Vercel Preview Deployments
   - Branch별 자동 배포

2. **Staging**
   - 프로덕션 환경 미러링
   - 실제 API 연동 테스트

3. **Production**
   - Vercel 프로덕션 배포
   - CDN 설정
   - 모니터링 설정

### 4.9 개발 일정

| 주차 | 작업 내용 | 완료 기준 |
|------|-----------|-----------|
| Week 1 | 프로젝트 설정, 레이아웃, 라우팅 | 네비게이션 가능한 기본 앱 |
| Week 2 | AI 어시스턴트 구현 | 채팅 인터페이스 동작 |
| Week 3 | 지식 베이스 구현 | CRUD 및 필터링 동작 |
| Week 4 | 연결 관리 구현 | Google Docs 연동 |
| Week 5 | 검색, 홈, 최적화 | 전체 기능 통합 완료 |
| Week 6 | 테스팅, 버그 수정, 배포 | 프로덕션 배포 완료 |

### 4.10 MVP 체크리스트

#### 필수 기능 (P0)
- [ ] AI 어시스턴트 채팅
- [ ] 메모리 CRUD
- [ ] 벡터 검색
- [ ] 위키링크 지원
- [ ] Google Docs 연동
- [ ] 반응형 디자인

#### 권장 기능 (P1)
- [ ] 다크 모드
- [ ] 실시간 동기화
- [ ] 고급 필터링
- [ ] 내보내기 기능
- [ ] 키보드 단축키

#### 향후 기능 (P2)
- [ ] Notion 연동
- [ ] 협업 기능
- [ ] 모바일 앱
- [ ] 브라우저 확장