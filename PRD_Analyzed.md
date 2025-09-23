# 코딩 퀴즈 플랫폼 PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: 2025-09-23
- **작성자**: PRD Generator
- **마지막 수정**: 2025-09-23

## 🎯 1. 제품 개요
### 1.1 제품명
코딩 면접 대비 퀴즈 플랫폼

### 1.2 제품 비전
기술 면접을 준비하는 개발자들을 위한 실전형 코딩 퀴즈 플랫폼

### 1.3 핵심 가치
- 실전 중심의 문제 제공
- 즉시 피드백 및 상세 해설
- 진도 관리 및 성취도 추적
- 경쟁 학습을 통한 동기부여

## 🏗️ 2. 기술 스택
### 2.1 백엔드
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Authentication**: JWT + bcrypt
- **Dependencies**: fastapi, uvicorn, sqlalchemy, databases, pydantic, watchdog, python-dotenv, passlib[bcrypt], pyjwt[crypto], psycopg2-binary

### 2.2 프론트엔드
- **Framework**: Next.js
- **UI Library**: React Bootstrap
- **Dependencies**: axios, bootstrap, next, react, react-bootstrap, react-dom, sweetalert2

### 2.3 데이터베이스
- **Type**: PostgreSQL
- **ORM**: SQLAlchemy

## ⚙️ 3. 핵심 기능
### 3.1 Login 기능
- **설명**: React 컴포넌트 기반 login 페이지
- **경로**: /login

### 3.5 Quiz 기능
- **설명**: React 컴포넌트 기반 quiz 페이지
- **경로**: /quiz

### 3.9 Ranking 기능
- **설명**: React 컴포넌트 기반 ranking 페이지
- **경로**: /ranking

### 3.13 Result 기능
- **설명**: React 컴포넌트 기반 result 페이지
- **경로**: /result

### 3.17 Signup 기능
- **설명**: React 컴포넌트 기반 signup 페이지
- **경로**: /signup


## 📊 4. 데이터 모델
### 4.1 Quiz
- **테이블명**: quizzes
- **필드**: id, question, explanation, answer, category

### 4.5 Score
- **테이블명**: scores
- **필드**: id, user_id, category, score, created_at

### 4.9 User
- **테이블명**: users
- **필드**: id, username, email, hashed_password


## 🔌 5. API 명세
### 5.1 Auth API
- `POST /signup` - 
- `POST /login` - 
- `POST /verify-token` - 
- `POST /logout` - 

### 5.7 Quiz API
- `GET /get` - 
- `GET /categories` - 
- `POST /submit` - 

### 5.12 Ranking API
- `GET /get` - 


## 🎨 6. 사용자 경험
### 6.1 Login 페이지
- **목적**: React 컴포넌트 기반 login 페이지
- **주요 기능**: 사용자 인터랙션 및 데이터 표시

### 6.5 Quiz 페이지
- **목적**: React 컴포넌트 기반 quiz 페이지
- **주요 기능**: 사용자 인터랙션 및 데이터 표시

### 6.9 Ranking 페이지
- **목적**: React 컴포넌트 기반 ranking 페이지
- **주요 기능**: 사용자 인터랙션 및 데이터 표시

### 6.13 Result 페이지
- **목적**: React 컴포넌트 기반 result 페이지
- **주요 기능**: 사용자 인터랙션 및 데이터 표시

### 6.17 Signup 페이지
- **목적**: React 컴포넌트 기반 signup 페이지
- **주요 기능**: 사용자 인터랙션 및 데이터 표시


## 🔒 7. 보안 요구사항
### 7.1 인증/인가
- JWT 토큰 기반 인증
- bcrypt를 통한 비밀번호 해싱
- 토큰 만료 시간 관리

### 7.2 데이터 보안
- SQL Injection 방지 (SQLAlchemy ORM 사용)
- CORS 정책 적용
- 환경별 도메인 제한

## 📈 8. 성능 요구사항
### 8.1 응답 시간
- API 응답 시간: 200ms 이하
- 페이지 로딩 시간: 2초 이하

### 8.2 동시성
- 동시 사용자: 100명 이상 지원
- 비동기 처리 (FastAPI async/await)

## 🚀 9. 배포 및 운영
### 9.1 환경 구성
- Docker 컨테이너화
- 환경별 설정 분리

### 9.2 모니터링
- 서버 상태 모니터링
- 에러 로깅 및 추적

## 📅 10. 개발 로드맵
### 10.1 Phase 1 (1-3개월)
- 기본 퀴즈 기능 완성
- 사용자 인증 시스템 구축

### 10.2 Phase 2 (3-6개월)
- 랭킹 시스템 구현
- 성능 최적화

### 10.3 Phase 3 (6-12개월)
- 고급 기능 추가
- 모바일 지원

## 📊 11. 성공 지표 (KPI)
### 11.1 사용자 지표
- 일일 활성 사용자 (DAU)
- 월간 활성 사용자 (MAU)

### 11.2 기술 지표
- API 응답 시간
- 시스템 가용성
- 에러 발생률
