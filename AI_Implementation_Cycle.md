# AI PRD 생성기 구현 사이클

## 🔄 AI 구현 사이클 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI PRD 생성기 구현 사이클                      │
└─────────────────────────────────────────────────────────────────┘

1. 코드베이스 분석 (Codebase Analysis)
   ↓
   ├── 프로젝트 구조 탐지
   ├── 기술 스택 분석
   ├── 모델/API 추출
   └── 비즈니스 도메인 분석
   ↓

2. 데이터 전처리 (Data Preprocessing)
   ↓
   ├── 분석 결과 구조화
   ├── 프롬프트 템플릿 생성
   └── AI 입력 데이터 포맷팅
   ↓

3. AI 모델 호출 (AI Model Invocation)
   ↓
   ├── LangChain 프레임워크 활용
   ├── OpenAI GPT-3.5-turbo 호출
   └── 구조화된 프롬프트 전달
   ↓

4. 응답 처리 (Response Processing)
   ↓
   ├── AI 응답 검증
   ├── 마크다운 포맷팅
   └── 폴백 처리 (API 실패 시)
   ↓

5. 결과 출력 (Output Generation)
   ↓
   ├── PRD 문서 생성
   ├── 파일 저장
   └── 분석 결과 리포트
```

## 🛠️ 핵심 구현 컴포넌트

### 1. 코드베이스 분석기 (CodebaseAnalyzer)
```python
class CodebaseAnalyzer:
    - 프로젝트 타입 감지
    - 기술 스택 분석 (백엔드/프론트엔드/DB/인프라)
    - 데이터 모델 추출
    - API 엔드포인트 추출
    - 비즈니스 도메인 분석
    - 신뢰도 계산
```

### 2. AI PRD 생성기 (AIPRDGenerator)
```python
class AIPRDGenerator:
    - LangChain + OpenAI 통합
    - 프롬프트 템플릿 관리
    - AI 응답 처리
    - 마크다운 변환
    - 폴백 메커니즘
```

### 3. 프롬프트 엔지니어링
```python
SystemMessage: "전문적인 제품 기획자 역할"
HumanMessage: "구체적인 코드베이스 분석 결과"
→ 구조화된 PRD 생성 지시
```

## 🔧 기술 스택

### 백엔드 분석
- **언어**: Python
- **프레임워크**: FastAPI
- **패턴**: ORM, JWT Authentication, Password Hashing

### 프론트엔드 분석
- **프레임워크**: Next.js
- **UI 라이브러리**: React Bootstrap
- **패턴**: SSR/SSG, HTTP Client

### AI/ML 스택
- **LangChain**: 프레임워크
- **OpenAI GPT-3.5-turbo**: 언어 모델
- **Pydantic**: 데이터 검증
- **Python-dotenv**: 환경 변수 관리

## 📈 성능 지표

- **분석 신뢰도**: 100%
- **프로젝트 타입 감지**: 정확
- **비즈니스 도메인**: 정확
- **기술 스택 감지**: 완전
- **AI 응답 품질**: 높음
