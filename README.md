# Memory Agent Enterprise

엔터프라이즈급 MCP (Model Context Protocol) 기반 통합 지식 관리 시스템

## 🎯 프로젝트 개요

Memory Agent Enterprise는 개인과 팀의 파편화된 지식(Google Docs, Notion, 개인 메모 등)을 실시간으로 연결하고, 대화형 인터페이스(MCP)를 통해 즉시 활용 가능한 **통합 두뇌(Corporate Second Brain)** 를 제공합니다.

### 핵심 기능

- 🔍 **의미론적 검색**: LlamaIndex 기반 벡터 검색 및 하이브리드 검색
- 🔗 **위키링크 지원**: `[[entity]]` 형태의 양방향 링크로 지식 연결
- 🏢 **멀티테넌시**: 조직별 완벽한 데이터 격리 (Pinecone Namespace)
- 📄 **실시간 연동**: Google Docs, Notion 등 외부 서비스 라이브 검색
- 🤖 **MCP 인터페이스**: Claude Desktop/Cursor와 원활한 통합
- 🔐 **엔터프라이즈 보안**: OAuth 2.1, 데이터 암호화, RBAC

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (패키지 관리)
- PostgreSQL 16+
- Redis 7+

### 설치 및 실행

1. **저장소 클론**
```bash
git clone https://github.com/your-org/memory-agent-enterprise.git
cd memory-agent-enterprise
```

2. **환경 설정**
```bash
make env-setup
# .env 파일을 편집하여 필요한 설정 입력
```

3. **의존성 설치**
```bash
make dev-install
```

4. **Docker 서비스 시작**
```bash
make docker-up
```

5. **데이터베이스 마이그레이션**
```bash
make db-upgrade
```

6. **개발 서버 실행**
```bash
make dev
```

API는 http://localhost:8000 에서 접근 가능합니다.

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Clients   │───▶│    FastAPI      │───▶│   LlamaIndex    │
│ Claude/Cursor   │    │ (API/MCP Server)│    │   RAG Engine    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │   │                      ↕
                              ▼   ▼             ┌─────────────────┐
┌─────────────────┐    ┌─────────────────┐    │   Pinecone      │
│ Web Interface   │───▶│  PostgreSQL     │    │ (Vector Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📦 기술 스택

- **Framework**: FastAPI, LlamaIndex
- **Vector DB**: Pinecone (Production) / Qdrant (Development)
- **Database**: PostgreSQL (메타데이터)
- **Cache/Queue**: Redis + Celery
- **Embedding**: BAAI/bge-m3
- **Authentication**: OAuth 2.1 (Google, Microsoft)
- **Deployment**: Docker, Kubernetes

## 🧪 PoC 실행

### Google Docs 연동 테스트
```bash
make poc-google
```

### Pinecone 멀티테넌시 테스트
```bash
export PINECONE_API_KEY="your-api-key"
make poc-pinecone
```

## 📝 개발 가이드

### 코드 스타일
```bash
# 코드 포맷팅
make format

# 린팅 검사
make lint

# 테스트 실행
make test
```

### 새로운 마이그레이션 생성
```bash
make db-migration
```

### Docker 로그 확인
```bash
make docker-logs
```

## 📊 프로젝트 진행 상태

Phase 0 (Pre-development) 완료:
- ✅ 프로젝트 구조 설정
- ✅ 개발 환경 구성
- ✅ Pydantic 데이터 모델 정의
- ✅ Docker 환경 구성
- ✅ LlamaIndex GoogleDocsReader PoC
- ✅ Pinecone namespace 격리 PoC
- ✅ CI/CD 파이프라인 설정

다음 단계: Phase 1 (Foundation) - Core RAG System 구축

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 문의

- Project Lead: [email@example.com]
- Documentation: [docs.memory-agent.example.com]
- Issues: [GitHub Issues](https://github.com/your-org/memory-agent-enterprise/issues)