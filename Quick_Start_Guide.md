# 다른 프로젝트에 AI PRD 생성기 적용하기

## 🚀 빠른 시작 가이드

### 1단계: 필요한 파일 복사
```bash
# 현재 프로젝트에서 필요한 파일들을 새 프로젝트로 복사
cp simple_langchain_prd.py /path/to/new/project/
cp requirements_ai.txt /path/to/new/project/
```

### 2단계: 의존성 설치
```bash
# 새 프로젝트 디렉토리로 이동
cd /path/to/new/project/

# 필요한 패키지 설치
pip install langchain openai pydantic python-dotenv
```

### 3단계: OpenAI API 키 설정
```bash
# 방법 1: 환경변수로 설정
export OPENAI_API_KEY='your-api-key-here'

# 방법 2: .env 파일 생성
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### 4단계: 실행
```bash
# 기본 실행
python simple_langchain_prd.py --project-root . --output MyProject_PRD.md

# API 키와 함께 실행
python simple_langchain_prd.py --project-root . --output MyProject_PRD.md --api-key your-api-key
```

## 📁 프로젝트 구조별 적용 방법

### 1. 풀스택 웹 애플리케이션 (백엔드 + 프론트엔드)
```
your-project/
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── app/
├── frontend/
│   ├── package.json
│   └── src/
└── simple_langchain_prd.py
```

### 2. 백엔드 전용 프로젝트
```
your-project/
├── requirements.txt
├── main.py
├── app/
└── simple_langchain_prd.py
```

### 3. 프론트엔드 전용 프로젝트
```
your-project/
├── package.json
├── src/
└── simple_langchain_prd.py
```

## 🔧 프로젝트 타입별 커스터마이징

### Node.js 프로젝트 지원 추가
```python
# simple_langchain_prd.py의 _detect_project_type 메서드에 추가
elif self._has_file('package.json'):
    confidence += 0.6
    if self._search_in_file('package.json', 'express'):
        project_type = 'nodejs_backend'
        confidence += 0.3
    elif self._search_in_file('package.json', 'next'):
        project_type = 'nextjs_webapp'
        confidence += 0.3
```

### Java 프로젝트 지원 추가
```python
# _detect_project_type 메서드에 추가
elif self._has_file('pom.xml'):
    project_type = 'java_spring_backend'
    confidence += 0.8
```

### Go 프로젝트 지원 추가
```python
# _detect_project_type 메서드에 추가
elif self._has_file('go.mod'):
    project_type = 'go_backend'
    confidence += 0.8
```

## 🎯 비즈니스 도메인별 커스터마이징

### 새로운 도메인 추가
```python
# _analyze_business_domain 메서드의 domain_keywords에 추가
'fintech': ['payment', 'wallet', 'transaction', 'banking', 'fintech', 'crypto'],
'healthcare': ['patient', 'doctor', 'medical', 'health', 'clinic', 'hospital'],
'iot': ['sensor', 'device', 'iot', 'smart', 'automation', 'telemetry'],
'ai_ml': ['model', 'prediction', 'training', 'algorithm', 'neural', 'ai', 'ml']
```

## 📊 실행 예시

### 예시 1: React + Node.js 프로젝트
```bash
python simple_langchain_prd.py --project-root . --output ReactApp_PRD.md --api-key sk-xxx
```

### 예시 2: Django + Vue.js 프로젝트
```bash
python simple_langchain_prd.py --project-root . --output DjangoVue_PRD.md --api-key sk-xxx
```

### 예시 3: 마이크로서비스 프로젝트
```bash
python simple_langchain_prd.py --project-root . --output Microservices_PRD.md --api-key sk-xxx
```

## 🔍 결과 확인

생성된 PRD 파일을 확인하여:
1. 프로젝트 타입이 정확히 감지되었는지
2. 기술 스택이 올바르게 분석되었는지
3. 비즈니스 도메인이 적절히 분류되었는지
4. AI가 생성한 PRD 내용이 프로젝트에 맞는지

## 🚨 문제 해결

### 일반적인 문제들
1. **API 키 오류**: OpenAI API 키가 올바른지 확인
2. **패키지 설치 오류**: pip install로 필요한 패키지 설치
3. **프로젝트 타입 미감지**: 새로운 프로젝트 타입 추가 필요
4. **분석 신뢰도 낮음**: 프로젝트 구조가 표준적이지 않을 수 있음

### 디버깅 방법
```bash
# 상세 로그와 함께 실행
python simple_langchain_prd.py --project-root . --output debug_PRD.md --api-key sk-xxx -v
```
