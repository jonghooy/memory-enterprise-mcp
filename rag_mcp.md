## Memory Agent Enterprise MVP: 최종 계획안 (v1.1)


### **🎯 프로젝트 개요**

#### **목표**

개인과 팀의 파편화된 지식(Google Docs, Notion, 개인 메모 등)을 실시간으로 연결하고, 대화형 인터페이스(MCP)를 통해 즉시 활용 가능한 \*\*'통합 두뇌(Corporate Second Brain)'\*\*를 제공한다.

#### **핵심 가치 제안**

  * **유일한 엔터프라이즈급 MCP 메모리 솔루션**: 보안과 확장성을 갖춘 MCP 기반 지식 관리 시스템.
  * **지능형 지식 연결**: Obsidian 스타일의 위키링크와 의미론적 검색을 통해 숨겨진 지식의 맥락을 발견.
  * **실시간 데이터 통합**: Google Docs, Notion 등 핵심 업무 도구의 데이터를 별도 동기화 없이 라이브로 검색.
  * **신속한 MVP 출시**: 3개월 내 핵심 가치를 검증할 수 있는 MVP 출시.

### **📋 MVP 기능 정의**

#### **🔥 Must Have (P0)**

  * **[ ] 기본 메모리 CRUD**: 메모리 생성/조회/수정/삭제. 생성 시 **출처(Source) 및 유형(Type) 메타데이터** 포함.
  * **[ ] 벡터 검색**: 의미론적 검색 및 키워드 하이브리드 검색.
  * **[ ] MCP 인터페이스**: Claude Desktop/Cursor 연동을 위한 핵심 MCP Tools 구현.
  * **[ ] 멀티테넌시**: 조직(테넌트)별 데이터의 완벽한 논리적/물리적 격리 (Pinecone Namespace 활용).
  * **[ ] 기본 인증**: OAuth 2.1 기반 사용자 인증 (Google, Microsoft 우선).
  * **[ ] 위키링크 지원**: `[[entity]]` 형태의 양방향 링크 파싱 및 엔티티 관계 매핑.
  * **[ ] Google Docs 라이브 검색**: 사용자 계정 기반 실시간 Google Docs 접근 및 검색.
  * **[ ] 사용자 온보딩**: 신규 사용자가 서비스에 가입하고 외부 계정(Google)을 안전하게 연결하는 프로세스.
  * **[ ] 비동기 데이터 인덱싱**: 대용량 문서의 초기 인덱싱을 백그라운드에서 처리하는 기능.

#### **⚡ Should Have (P1)**

  * **[ ] 개인용 웹 인터페이스**: 사용자가 연결된 데이터 소스를 관리하고, 최근 메모리를 확인하는 개인화된 '메모리 허브'.
  * **[ ] Notion 연동**: Notion 페이지 라이브 검색 기능 추가.
  * **[ ] 필터 시스템**: `<filter>` 태그 기반 정보 필터링.
  * **[ ] 기본 분석**: 개인/팀의 메모리 사용량, 인기 엔티티 등 기본 통계 대시보드.
  * **[ ] RESTful API**: MCP 외 외부 시스템 연동을 위한 기본적인 API 인터페이스 제공.

#### **💡 Could Have & Post-MVP (P2)**

  * **[ ] Slack 연동**: Slack 채널의 대화 내역 검색.
  * **[ ] 고급 검색 필터**: 날짜 범위, 태그 조합, 소스별 다중 필터 기능.
  * **[ ] 메모리 관계 시각화**: 엔티티 간의 연결 관계를 보여주는 네트워크 그래프.
  * **[ ] 역할 기반 접근 제어 (RBAC)**: 테넌트 내 사용자 역할을 Admin, Editor, Viewer 등으로 나누어 접근 권한 제어.
  * **[ ] 정기 동기화**: Webhook 외 주기적인 스케줄링을 통한 데이터 소스 동기화.

-----

### **🏗️ 기술 아키텍처**

#### **Core Stack**

  * **Framework**: LlamaIndex (RAG Core)
  * **Vector DB**: Pinecone (Production) / Qdrant (Development)
  * **MCP/API Framework**: FastAPI
  * **Database**: PostgreSQL (Metadata, User/Tenant Info)
  * **Task Queue**: Celery + Redis (Broker)
  * **Cache**: Redis
  * **Authentication**: OAuth 2.1 (Google, Microsoft)
  * **Deployment**: Docker + Docker Compose (MVP), Kubernetes (Production)

#### **MVP Architecture Diagram**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Clients   │───▶│    FastAPI      │───▶│   LlamaIndex    │
│ Claude/Cursor   │    │ (API/MCP Server)│    │   RAG Engine    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       ▲ │                    │   │                      ↕
       │ └────────────────────┼───┤             ┌─────────────────┐
       │                      ▼   ▼             │   Pinecone      │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │ (Vector Store)  │
│ Web Interface   │───▶│  PostgreSQL     │    │      Redis      │    └─────────────────┘
└─────────────────┘    │ (Metadata)      │    │ (Cache/Queue)   │
                        └─────────────────┘    └─────────────────┘
                                │                      │
                                ▼                      ▼
                        ┌─────────────────┐    ┌─────────────────┐
                        │ External APIs   │    │   Celery Worker │
                        │ Google, Notion  │    │(Async Indexing) │
                        └─────────────────┘    └─────────────────┘
```

-----

### **📅 개발 타임라인 (13주)**

#### **Phase 0: Pre-development (Week 0)**

  * **목표**: 핵심 기술 검증 및 상세 설계
  * **[ ] Task**: LlamaIndex `GoogleDocsReader` PoC, Pinecone `namespace` 격리 PoC, 최종 데이터 모델(Pydantic) 확정.

#### **Phase 1: Foundation (Week 1-4)**

  * **목표**: 기본 RAG + MCP 시스템 및 멀티테넌시 기반 구축
  * **Week 1**: 프로젝트 셋업, Docker 환경 구성, CI/CD 파이프라인 설정, 로깅/예외 처리 전략 수립.
  * **Week 2**: Core RAG System 구축 (LlamaIndex 설정, Embedding 모델(`BAAI/bge-m3-en-v1.5`) 선정), 기본 메모리 모델 및 CRUD 로직 구현.
  * **Week 3**: MCP 서버 구현 (FastMCP), 핵심 MCP Tools 개발, Claude 연동 테스트.
  * **Week 4**: PostgreSQL 스키마 설계, OAuth 2.1 기본 구현 (Google), 테넌트별 데이터 격리 로직 구현.

#### **Phase 2: MVP Core Features (Week 5-9)**

  * **목표**: 핵심 MVP 기능 완성
  * **Week 5**: 위키링크(`[[entity]]`) 파싱 및 엔티티 관계 매핑 구현.
  * **Week 6**: Google Docs API 통합 및 사용자 계정 연동 플로우 개발.
  * **Week 7**: **Task Queue (Celery) 연동** 및 Google Docs **비동기 인덱싱 로직** 구현.
  * **Week 8**: 필터 시스템 및 고급 검색 옵션 (날짜, 태그, 소스) 구현.
  * **Week 9**: 전체 시스템 통합 테스트, 성능 최적화 (쿼리 응답 \< 500ms 목표), 내부 데모 및 피드백 반영.

#### **Phase 3: Production Ready (Week 10-12)**

  * **목표**: 프로덕션 배포 및 런치 준비
  * **Week 10**: 웹 인터페이스 (개인용 메모리 허브), Notion 연동 기능 개발.
  * **Week 11**: 프로덕션 배포 준비 (Docker 최적화, K8s 매니페스트), 모니터링/로깅 설정 (Prometheus+Grafana), **보안 강화 (코드 리뷰, 기본 취약점 점검)**.
  * **Week 12**: 베타 테스터 온보딩, 최종 퍼포먼스 튜닝, **문서화 (API, 사용자 가이드, 운영 Runbook)**, 런치 준비.

-----

### **👥 팀 구성 & 역할**

  * **Tech Lead (1명)**: 전체 아키텍처, LlamaIndex 전문, 코드 리뷰.
  * **Backend Developer (1명)**: MCP/API 서버, 인증, 데이터베이스, 비동기 작업.
  * **Full-stack Developer (1명)**: 웹 인터페이스, 사용자 온보딩, 외부 서비스 연동.
  * **DevOps Engineer (0.5명)**: 배포 자동화, 인프라 관리, 모니터링.
  * **Product Owner (Part-time, 0.5명)**: 사용자 스토리 정의, 백로그 관리, 비즈니스 목표와 개발의 연결.

### **💰 예산 추정 (첫 해)**

  * **개발 인력 비용 (3개월)**: \~$132K
  * **인프라 비용 (연간)**:
      * Cloud Provider (AWS/GCP): $2,400
      * Pinecone (Starter): $840
      * Auth Provider (Auth0/Okta): $300
      * Logging/Monitoring (Datadog/Sentry): $1,200
      * **총 인프라**: \~$4,740/년
  * **기타 비용**: 개발 도구, 외부 API, 법률 자문 등 \~$5K
  * **총 예산**: **\~$142K**

-----

### **📊 성공 지표 (KPI)**

  * **기술적 KPI**:
      * [ ] 검색 응답 시간 (P95): \< 500ms
      * [ ] 시스템 가용성: 99.5% uptime
      * [ ] 인덱싱 속도: 100페이지 문서 \< 5분
  * **비즈니스 KPI**:
      * [ ] 사용자 채택: 클로즈드 베타 기간 내 **활성 테넌트 5개 이상** 확보 (조직원 3명 이상이 주 3회 이상 사용).
      * [ ] 사용자 유지율 (Retention): 4주차 유지율 \> 40%
      * [ ] 핵심 기능 채택률: Google Docs 검색 기능 사용자 비율 \> 60%
      * [ ] NPS (Net Promoter Score): \> 50

### **🚀 출시 전략**

  * **MVP 출시 (Week 12)**: \*\*'지식 관리에 대한 니즈가 높은 10\~50인 규모의 기술 스타트업'\*\*을 ICP로 정의, 5\~10개 파트너사 대상 클로즈드 베타 진행.
  * **피드백 수집 (2주)**: 베타 기간 동안 정기적인 사용자 인터뷰 및 설문을 통해 피드백 수집 및 우선순위화.
  * **Post-MVP (3개월 후)**: 오픈 베타 전환, 유료화 모델 설계, 추가 연동 기능(Slack 등) 개발 착수.

-----

### **⚠️ 위험 요소 & 대응책**

  * **기술적 위험**:
      * **LlamaIndex 성능 이슈**: 초기 PoC 단계에서 충분한 성능 검증. 성능 저하 시 특정 모듈은 LangChain으로 대체하는 플랜 B 준비.
      * **외부 API 의존성 (Google/Notion)**: API 정책 변경 및 Rate Limit에 대응하기 위한 Exponential Backoff 로직 적용. 주요 API 변경사항 모니터링 자동화.
  * **비즈니스 위험**:
      * **시장 수요 불확실성**: 클로즈드 베타에서 유료 전환 의사를 명확히 측정하고, B2B SaaS로서의 가치를 검증.
      * **사용자 경험(UX) 복잡성**: MCP는 파워 유저용으로 포지셔닝하고, 일반 사용자는 직관적인 웹 인터페이스를 통해 온보딩 및 핵심 기능을 사용하도록 유도.
  * **보안 및 규제 위험**:
      * **데이터 프라이버시 및 규제 준수**: 개발 초기부터 **Privacy by Design** 원칙 적용. 모든 데이터 전송 구간(TLS) 및 저장소(at-rest) 암호화. 법률 자문을 통해 개인정보 처리 방침 마련.