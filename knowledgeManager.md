# Memory Enterprise Knowledge Management System

## 프로젝트 개요
AI 기반 지식 관리 시스템으로 RAG (Retrieval-Augmented Generation) 기능과 MCP (Model Context Protocol) 통합을 제공하는 엔터프라이즈급 솔루션입니다.

## 🚀 배포 현황

### 접속 정보
- **Production URL**: https://www.llmdash.com/kms/
- **Local Development**: http://localhost:3000
- **Status**: ✅ Production 운영 중

### 기술 스택
- **Frontend**: Next.js 14 (App Router)
- **UI Components**: shadcn/ui (Radix UI 기반)
- **State Management**: Zustand
- **Styling**: Tailwind CSS
- **Process Manager**: PM2
- **Web Server**: Nginx (Reverse Proxy)
- **Language**: TypeScript

## 📋 구현 완료 기능

### 1. UI/UX 구현
- ✅ **AI Assistant 페이지**: 지식 베이스와 대화하는 채팅 인터페이스
- ✅ **Knowledge Base 페이지**: 문서 관리 및 검색
- ✅ **Connections 페이지**: 외부 데이터 소스 연동 관리
- ✅ **Settings 페이지**: 시스템 설정 및 사용자 환경 설정
- ✅ **Dashboard**: 홈 대시보드
- ✅ **Responsive Design**: 모바일/데스크톱 반응형 디자인

### 2. 프론트엔드 아키텍처
- ✅ **Next.js 14 App Router**: 최신 라우팅 시스템
- ✅ **TypeScript**: 타입 안정성
- ✅ **Zustand Store**: 전역 상태 관리
- ✅ **API Client**: Axios 기반 API 통신 레이어
- ✅ **Component Architecture**: 재사용 가능한 컴포넌트 구조

### 3. 인프라 및 배포
- ✅ **PM2 Process Management**:
  - 자동 재시작
  - 로그 관리
  - 리소스 모니터링
  - Dev/Production 환경 분리
- ✅ **Nginx Reverse Proxy**:
  - SSL/HTTPS 지원
  - 서브패스 라우팅 (/kms)
  - 정적 파일 캐싱
  - WebSocket 지원
- ✅ **Production Build Optimization**:
  - Base Path 설정
  - Asset Prefix 설정
  - Static Generation

## 🛠 시스템 구성

### 디렉토리 구조
```
/home/jonghooy/work/rag-mcp/
├── frontend/                    # Next.js 애플리케이션
│   ├── app/                    # App Router 페이지
│   │   ├── page.tsx           # AI Assistant (메인)
│   │   ├── home/              # Dashboard
│   │   ├── knowledge/         # Knowledge Base
│   │   ├── connections/       # Connections
│   │   └── settings/          # Settings
│   ├── components/            # React 컴포넌트
│   │   ├── sidebar.tsx       # 사이드바 네비게이션
│   │   ├── header.tsx        # 헤더
│   │   ├── chat-interface.tsx # 채팅 UI
│   │   └── ui/               # shadcn/ui 컴포넌트
│   ├── lib/                   # 유틸리티
│   │   ├── api.ts            # API 클라이언트
│   │   └── store.ts          # Zustand store
│   ├── ecosystem.config.js    # PM2 설정
│   ├── .env.production        # 프로덕션 환경변수
│   └── logs/                  # PM2 로그
└── knowledgeManager.md        # 이 문서
```

### PM2 프로세스 관리
```javascript
// ecosystem.config.js
{
  apps: [
    {
      name: 'memory-enterprise-frontend',
      script: 'npm',
      args: 'start',
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        BASE_PATH: '/kms',
        ASSET_PREFIX: '/kms'
      }
    },
    {
      name: 'memory-enterprise-dev',
      script: 'npm',
      args: 'run dev',
      env: {
        NODE_ENV: 'development',
        PORT: 3000
      }
    }
  ]
}
```

### Nginx 설정
```nginx
upstream kms_frontend {
    server localhost:3000;
}

location /kms/ {
    proxy_pass http://kms_frontend/kms/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /kms/_next/ {
    proxy_pass http://kms_frontend/kms/_next/;
    # 정적 파일 캐싱
    proxy_cache_valid 200 30d;
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

## 🔧 주요 명령어

### PM2 관리
```bash
# 상태 확인
pm2 status

# 프로덕션 시작
pm2 start ecosystem.config.js --only memory-enterprise-frontend

# 개발 모드 시작
pm2 start ecosystem.config.js --only memory-enterprise-dev

# 로그 확인
pm2 logs memory-enterprise-frontend

# 재시작
pm2 restart memory-enterprise-frontend

# 중지
pm2 stop memory-enterprise-frontend
```

### 빌드 및 배포
```bash
# 프로덕션 빌드
BASE_PATH=/kms ASSET_PREFIX=/kms npm run build

# 개발 서버
npm run dev

# 프로덕션 서버
npm start
```

### Nginx 관리
```bash
# 설정 테스트
sudo nginx -t

# 설정 리로드
sudo systemctl reload nginx

# 상태 확인
sudo systemctl status nginx
```

## 📈 진행 현황

### 완료된 작업 (2025-09-20)
1. **Frontend 구현**
   - Next.js 14 프로젝트 생성 및 설정
   - TypeScript 설정
   - shadcn/ui 컴포넌트 라이브러리 통합
   - 5개 주요 페이지 구현
   - Zustand 상태 관리 구현
   - API 클라이언트 구현

2. **PM2 설정**
   - Process management 설정
   - Dev/Production 환경 분리
   - 자동 재시작 및 로깅 설정
   - 리소스 모니터링 활성화

3. **Nginx 배포**
   - Reverse proxy 설정
   - 서브패스 라우팅 (/kms) 구현
   - SSL/HTTPS 적용
   - 정적 파일 최적화

4. **Production 최적화**
   - Base path 설정으로 서브패스 지원
   - 정적 파일 캐싱
   - Build 최적화
   - UI 렌더링 문제 해결

### 해결된 이슈
1. **UI 렌더링 문제**: CSS 파일 경로 문제 해결
2. **라우팅 문제**: Nginx proxy_pass 설정 수정
3. **Base Path 문제**: Next.js basePath 및 assetPrefix 설정
4. **정적 파일 404 에러**: Nginx location 블록 수정으로 해결

## 🎯 향후 계획

### Phase 1: Backend Integration (다음 단계)
- [ ] FastAPI backend 서버 구현 (port 8000)
- [ ] PostgreSQL 데이터베이스 연동
- [ ] Vector DB 통합 (Pinecone/Qdrant)
- [ ] Authentication 시스템 구현

### Phase 2: Core Features
- [ ] RAG (Retrieval-Augmented Generation) 구현
- [ ] Document upload 및 processing
- [ ] Google Docs 연동
- [ ] MCP server 통합

### Phase 3: Advanced Features
- [ ] Real-time collaboration
- [ ] Advanced search capabilities
- [ ] Analytics dashboard
- [ ] Multi-tenant support

### Phase 4: Enterprise Features
- [ ] SSO integration
- [ ] Audit logging
- [ ] Backup & recovery
- [ ] Performance optimization

## 📝 Notes

### 현재 상태
- Frontend는 완전히 구현되어 프로덕션에서 운영 중
- Backend API는 아직 미구현 (mock 데이터 사용 중)
- 데이터베이스 연결 대기 중
- 인증 시스템 미구현

### 중요 파일 경로
- **Nginx Config**: `/etc/nginx/sites-available/llmdash`
- **PM2 Config**: `/home/jonghooy/work/rag-mcp/frontend/ecosystem.config.js`
- **Environment**: `/home/jonghooy/work/rag-mcp/frontend/.env.production`
- **Logs**: `/home/jonghooy/work/rag-mcp/frontend/logs/`

### 접근 권한
- **Server IP**: 124.194.32.36
- **Domain**: www.llmdash.com, llmdash.com
- **SSL**: Let's Encrypt 인증서 적용

## 🚨 Troubleshooting

### 일반적인 문제 해결

1. **UI가 깨져 보이는 경우**
   - PM2 프로세스 재시작: `pm2 restart memory-enterprise-frontend`
   - 빌드 재실행: `BASE_PATH=/kms npm run build`
   - Nginx 재시작: `sudo systemctl reload nginx`

2. **404 에러**
   - Base path 확인: `.env.production`의 `BASE_PATH=/kms`
   - Nginx 설정 확인: proxy_pass 경로
   - Next.js 라우팅 확인

3. **PM2 프로세스 문제**
   - 로그 확인: `pm2 logs memory-enterprise-frontend`
   - 프로세스 재시작: `pm2 restart memory-enterprise-frontend`
   - PM2 업데이트: `pm2 update`

4. **정적 파일 로드 실패**
   - Asset prefix 확인: `.env.production`의 `ASSET_PREFIX=/kms`
   - Nginx location 블록 확인
   - 빌드 출력 확인

## 🌟 주요 개선 사항 (2025-09-20)

### 프로덕션 배포 완료
- ✅ Nginx 설정 수정으로 올바른 라우팅 구현
- ✅ 정적 파일 서빙 문제 해결
- ✅ Base path 설정으로 서브도메인 경로 지원
- ✅ PM2를 통한 안정적인 프로세스 관리

### 기술적 성과
- Zero-downtime 배포 구현
- 정적 파일 캐싱으로 성능 최적화
- 프로덕션/개발 환경 완벽 분리
- 자동 재시작 및 모니터링 체계 구축

## 📚 참고 문서
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [PM2 Documentation](https://pm2.keymetrics.io)
- [Nginx Documentation](https://nginx.org/en/docs)
- [RAG Architecture Guide](./docs/rag-architecture.md) (예정)
- [MCP Integration Guide](./docs/mcp-integration.md) (예정)

---

*Last Updated: 2025-09-20*
*Author: Memory Enterprise Team*
*Version: 1.0.0*
*Status: Production Deployed*