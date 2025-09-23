#!/usr/bin/env python3
"""
간단한 PRD 생성 스크립트
현재 프로젝트에 맞춰 PRD를 자동 생성합니다.
"""

import os
import json
from datetime import datetime
from pathlib import Path

def generate_prd():
    """PRD 생성"""

    # 프로젝트 정보
    project_name = "코딩 퀴즈 플랫폼"
    current_date = datetime.now().strftime('%Y-%m-%d')

    prd_content = f"""# {project_name} PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: {current_date}
- **작성자**: PRD Generator
- **마지막 수정**: {current_date}

## 🎯 1. 제품 개요
### 1.1 제품명
{project_name}

### 1.2 제품 비전
기술 면접을 준비하는 개발자들을 위한 실전형 코딩 퀴즈 플랫폼으로, 자바스크립트, 자바, 파이썬 등 주요 프로그래밍 언어의 핵심 개념을 학습하고 실전 감각을 기를 수 있도록 지원합니다.

### 1.3 핵심 가치
- **실전 중심**: 실제 면접에서 출제되는 유형의 문제 제공
- **즉시 피드백**: 실시간 채점 및 상세한 해설 제공
- **진도 관리**: 사용자별 학습 진도 및 성취도 추적
- **경쟁 학습**: 랭킹 시스템을 통한 동기부여

### 1.4 타겟 사용자
- 기술 면접을 준비하는 개발자
- 프로그래밍 언어 학습자
- 코딩 테스트 준비생

## 🏗️ 2. 기술 스택
### 2.1 백엔드
- **Framework**: FastAPI (Python)
- **Language**: Python 3.8+
- **ORM**: SQLAlchemy
- **Authentication**: JWT + bcrypt
- **Dependencies**: uvicorn, pydantic, passlib, pyjwt, watchdog

### 2.2 프론트엔드
- **Framework**: Next.js 15.1.7 (React 19)
- **UI Library**: React Bootstrap 2.10.9
- **State Management**: React Context API
- **Dependencies**: axios, sweetalert2

### 2.3 데이터베이스
- **Type**: SQLite (개발) / PostgreSQL (운영)
- **ORM**: SQLAlchemy
- **Migration**: SQLAlchemy Alembic

### 2.4 인프라
- **Containerization**: Docker
- **Deployment**: AWS EC2
- **Monitoring**: FastAPI built-in logging

## ⚙️ 3. 핵심 기능
### 3.1 사용자 인증 시스템
- **설명**: JWT 기반 사용자 인증 및 권한 관리
- **우선순위**: High
- **API 엔드포인트**:
  - `POST /auth/signup` - 회원가입
  - `POST /auth/login` - 로그인
  - `POST /auth/verify-token` - 토큰 검증
  - `POST /auth/logout` - 로그아웃
- **데이터 모델**: User
- **사용자 플로우**: 회원가입 → 로그인 → 토큰 발급 → 인증된 서비스 이용

### 3.2 퀴즈 시스템
- **설명**: 카테고리별 퀴즈 제공 및 실시간 채점
- **우선순위**: High
- **API 엔드포인트**:
  - `GET /quiz/get?category=<category>` - 퀴즈 목록 조회
  - `GET /quiz/categories` - 카테고리 목록 조회
  - `POST /quiz/submit` - 점수 제출
- **데이터 모델**: Quiz, Score
- **사용자 플로우**: 카테고리 선택 → 퀴즈 풀기 → 실시간 채점 → 결과 제출

### 3.3 랭킹 시스템
- **설명**: 사용자별 점수 기반 랭킹 제공
- **우선순위**: Medium
- **API 엔드포인트**:
  - `GET /ranking/get?category=<category>` - 랭킹 조회
- **데이터 모델**: Score, User
- **사용자 플로우**: 점수 제출 → 랭킹 업데이트 → 순위 확인

### 3.4 콘텐츠 관리 시스템
- **설명**: CSV 파일 기반 문제 데이터 관리
- **우선순위**: Medium
- **API 엔드포인트**: 없음 (파일 시스템 기반)
- **데이터 모델**: Quiz
- **사용자 플로우**: CSV 파일 수정 → 자동 감지 → 데이터베이스 업데이트

## 📊 4. 데이터 모델
### 4.1 User (사용자)
```python
class User:
    - id: Integer (Primary Key)
    - username: String (Unique, 사용자명)
    - email: String (Unique, 이메일)
    - hashed_password: String (해싱된 비밀번호)
```

### 4.2 Quiz (퀴즈)
```python
class Quiz:
    - id: Integer (Primary Key)
    - question: String (문제 내용)
    - explanation: String (해설)
    - answer: String (정답, 다중 정답 지원)
    - category: String (카테고리)
```

### 4.3 Score (점수)
```python
class Score:
    - id: Integer (Primary Key)
    - user_id: Integer (Foreign Key, 사용자 ID)
    - category: String (카테고리)
    - score: Integer (점수)
    - created_at: DateTime (생성 시간)
```

## 🔌 5. API 명세
### 5.1 인증 API
- `POST /auth/signup` - 회원가입
- `POST /auth/login` - 로그인
- `POST /auth/verify-token` - 토큰 검증
- `POST /auth/logout` - 로그아웃

### 5.2 퀴즈 API
- `GET /quiz/get?category=<category>` - 퀴즈 목록 조회
- `GET /quiz/categories` - 카테고리 목록 조회
- `POST /quiz/submit` - 점수 제출

### 5.3 랭킹 API
- `GET /ranking/get?category=<category>` - 랭킹 조회

## 🎨 6. 사용자 경험
### 6.1 메인 페이지
- **목적**: 제품 소개 및 퀴즈 시작 유도
- **주요 기능**:
  - 제품 소개
  - 퀴즈 시작 버튼
  - 반응형 디자인
- **사용자 플로우**: 접속 → 제품 확인 → 퀴즈 시작
- **UI 컴포넌트**: Hero Section, CTA Button

### 6.2 퀴즈 페이지
- **목적**: 퀴즈 풀이 및 실시간 채점
- **주요 기능**:
  - 카테고리 선택
  - 퀴즈 표시 (페이지네이션)
  - 실시간 채점
  - 진도 저장
- **사용자 플로우**: 카테고리 선택 → 퀴즈 풀기 → 실시간 채점 → 제출
- **UI 컴포넌트**: CategorySelector, QuizCard, Pagination

### 6.3 결과 페이지
- **목적**: 점수 표시 및 오답 노트 제공
- **주요 기능**:
  - 점수 표시
  - 오답 노트
  - 랭킹 표시
  - 재시도 옵션
- **사용자 플로우**: 점수 확인 → 오답 분석 → 랭킹 확인 → 재시도
- **UI 컴포넌트**: ScoreCard, WrongAnswerList, RankingTable

### 6.4 로그인/회원가입 페이지
- **목적**: 사용자 인증
- **주요 기능**:
  - 회원가입
  - 로그인
  - 폼 검증
- **사용자 플로우**: 정보 입력 → 검증 → 제출 → 인증
- **UI 컴포넌트**: AuthForm, InputField, SubmitButton

## 🔒 7. 보안 요구사항
### 7.1 인증/인가
- JWT 토큰 기반 인증
- bcrypt를 통한 비밀번호 해싱
- 토큰 만료 시간 관리 (30분)

### 7.2 데이터 보안
- SQL Injection 방지 (SQLAlchemy ORM 사용)
- CORS 정책 적용
- 환경별 도메인 제한

### 7.3 입력 검증
- Pydantic을 통한 요청 데이터 검증
- 이메일 형식 검증
- 비밀번호 강도 검증

## 📈 8. 성능 요구사항
### 8.1 응답 시간
- API 응답 시간: 200ms 이하
- 페이지 로딩 시간: 2초 이하
- 퀴즈 데이터 로딩: 1초 이하

### 8.2 동시성
- 동시 사용자: 100명 이상 지원
- 데이터베이스 연결 풀링
- 비동기 처리 (FastAPI async/await)

### 8.3 확장성
- 마이크로서비스 아키텍처 준비
- 데이터베이스 분리 가능
- CDN 통합 가능

## 🚀 9. 배포 및 운영
### 9.1 환경 구성
- **Development**: 로컬 개발 환경 (SQLite)
- **Production**: AWS EC2 (PostgreSQL)
- **Docker**: 컨테이너화된 배포

### 9.2 모니터링
- FastAPI built-in logging
- 서버 상태 모니터링
- 에러 로깅 및 추적

### 9.3 백업 전략
- 데이터베이스 정기 백업
- CSV 파일 버전 관리
- 설정 파일 백업

## 📅 10. 개발 로드맵
### 10.1 Phase 1 (1-3개월)
- 기본 퀴즈 기능 완성
- 사용자 인증 시스템 구축
- 기본 UI/UX 구현

### 10.2 Phase 2 (3-6개월)
- 랭킹 시스템 구현
- 성능 최적화
- 모바일 반응형 개선

### 10.3 Phase 3 (6-12개월)
- 고급 기능 추가 (문제 난이도 분류)
- 사용자 통계 대시보드
- 모바일 앱 개발

## 📊 11. 성공 지표 (KPI)
### 11.1 사용자 지표
- 일일 활성 사용자 (DAU): 50명
- 월간 활성 사용자 (MAU): 500명
- 사용자 유지율: 60%

### 11.2 비즈니스 지표
- 퀴즈 완료율: 80%
- 평균 세션 시간: 15분
- 사용자 만족도: 4.5/5

### 11.3 기술 지표
- API 응답 시간: 200ms 이하
- 시스템 가용성: 99% 이상
- 에러 발생률: 1% 이하

## 📝 12. 부록
### 12.1 용어 정의
- **퀴즈**: 프로그래밍 관련 문제
- **카테고리**: 문제 분류 (Java, JavaScript, Python)
- **랭킹**: 사용자별 점수 기반 순위
- **점수**: 정답률을 백분율로 표현

### 12.2 참고 자료
- FastAPI 공식 문서
- Next.js 공식 문서
- SQLAlchemy 공식 문서
- React Bootstrap 공식 문서

### 12.3 변경 이력
| 버전 | 날짜 | 변경사항 | 작성자 |
|------|------|----------|--------|
| v1.0 | {current_date} | 초기 버전 | PRD Generator |
"""

    return prd_content

def main():
    """메인 함수"""
    prd_content = generate_prd()

    # PRD 파일 저장
    output_file = "PRD.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prd_content)

    print(f"✅ PRD가 {output_file}에 생성되었습니다.")
    print(f"📄 파일 크기: {len(prd_content)} 문자")
    print(f"📅 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
