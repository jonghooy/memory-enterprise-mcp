# PM2 Management Guide

PM2를 사용한 Memory Enterprise 웹 서비스 관리 가이드입니다.

## PM2 설정 완료 ✅

### 설치된 구성 요소
1. **PM2 Global Package**: 프로세스 관리자
2. **ecosystem.config.js**: PM2 설정 파일
3. **pm2-manager.sh**: 관리 스크립트
4. **npm scripts**: package.json에 PM2 명령어 추가

## 사용 방법

### 1. 기본 명령어

#### 개발 모드 시작
```bash
# 방법 1: npm script
npm run pm2:dev

# 방법 2: 직접 실행
./pm2-manager.sh dev

# 방법 3: PM2 명령어
pm2 start ecosystem.config.js --only memory-enterprise-dev
```

#### 프로덕션 모드 시작
```bash
# 방법 1: npm script (빌드 후 시작)
npm run pm2:prod

# 방법 2: 직접 실행
./pm2-manager.sh prod
```

### 2. 프로세스 관리

#### 상태 확인
```bash
npm run pm2:status
# 또는
pm2 status
```

#### 로그 확인
```bash
npm run pm2:logs
# 또는
pm2 logs memory-enterprise-dev --lines 50
```

#### 모니터링 대시보드
```bash
npm run pm2:monitor
# 또는
pm2 monit
```

#### 재시작
```bash
npm run pm2:restart
# 또는
pm2 restart memory-enterprise-dev
```

#### 중지
```bash
npm run pm2:stop
# 또는
pm2 stop memory-enterprise-dev
```

### 3. 시스템 부팅 시 자동 시작 설정

```bash
# 1. PM2 startup 설정
npm run pm2:setup
# 또는
pm2 startup

# 2. 현재 프로세스 저장
npm run pm2:save
# 또는
pm2 save
```

### 4. 로그 관리

#### 로그 위치
- **개발 모드 로그**: `./logs/pm2-dev-*.log`
- **프로덕션 로그**: `./logs/pm2-*.log`

#### 로그 초기화
```bash
npm run pm2:flush
# 또는
pm2 flush
```

## PM2 설정 상세 정보

### ecosystem.config.js 구성

#### 개발 모드 (`memory-enterprise-dev`)
- **Script**: `npm run dev`
- **Watch**: app/, components/, lib/ 디렉토리 변경 감지
- **자동 재시작**: 파일 변경 시
- **메모리 제한**: 500MB
- **로그 파일**: `./logs/pm2-dev-*.log`

#### 프로덕션 모드 (`memory-enterprise-frontend`)
- **Script**: `npm start`
- **Watch**: 비활성화
- **자동 재시작**: 프로세스 크래시 시
- **메모리 제한**: 500MB
- **로그 파일**: `./logs/pm2-*.log`

### 환경 변수

```bash
NODE_ENV=development|production
PORT=3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 유용한 PM2 명령어

```bash
# 특정 프로세스 정보 상세 보기
pm2 info memory-enterprise-dev

# CPU/메모리 사용량 실시간 모니터링
pm2 monit

# JSON 형식으로 상태 출력
pm2 jlist

# 프로세스 리로드 (Zero-downtime)
pm2 reload memory-enterprise-frontend

# 프로세스 스케일링 (클러스터 모드)
pm2 scale memory-enterprise-frontend 2

# 모든 프로세스 삭제
pm2 delete all

# PM2 데몬 종료
pm2 kill

# PM2 웹 대시보드 (별도 설치 필요)
pm2 plus
```

## 문제 해결

### 포트 충돌
```bash
# 3000 포트 사용 중인 프로세스 확인
lsof -i :3000

# 프로세스 종료
kill -9 <PID>
```

### PM2 업데이트
```bash
# PM2 글로벌 업데이트
npm install -g pm2@latest

# PM2 인메모리 업데이트
pm2 update
```

### 로그 권한 문제
```bash
# 로그 디렉토리 권한 설정
chmod -R 755 logs/
```

## 모니터링 대시보드

PM2는 기본 모니터링 기능을 제공합니다:

1. **pm2 monit**: 터미널 기반 실시간 모니터링
2. **pm2 status**: 프로세스 상태 테이블
3. **pm2 info <app-name>**: 상세 프로세스 정보
4. **pm2 logs**: 실시간 로그 스트리밍

## 프로덕션 체크리스트

- [ ] `npm run build` 실행하여 빌드 에러 확인
- [ ] 환경 변수 설정 확인 (`.env.local`)
- [ ] PM2 시작 스크립트 설정 (`pm2 startup`)
- [ ] 프로세스 저장 (`pm2 save`)
- [ ] 로그 로테이션 설정 (선택사항)
- [ ] 모니터링 알람 설정 (선택사항)

## 현재 실행 상태

```
name: memory-enterprise-dev
status: online
port: 3000
mode: development
watching: enabled
```

앱에 접속하려면: http://localhost:3000