# 다른 프로젝트에 AI PRD 생성기 적용 가이드

## 🎯 적용 가능한 프로젝트 타입

### 1. 지원되는 프로젝트 구조
- **풀스택 웹 애플리케이션** (백엔드 + 프론트엔드)
- **백엔드 전용 API 서버**
- **프론트엔드 전용 웹 애플리케이션**
- **마이크로서비스 아키텍처**
- **모바일 앱 백엔드**

### 2. 지원되는 기술 스택
- **백엔드**: Python (FastAPI, Flask, Django), Node.js, Java, Go, Rust
- **프론트엔드**: React, Next.js, Vue.js, Angular, Svelte
- **데이터베이스**: PostgreSQL, MySQL, SQLite, MongoDB, Redis
- **인프라**: Docker, Kubernetes, AWS, Azure, GCP

## 🛠️ 적용 단계별 가이드

### Step 1: 환경 설정
```bash
# 1. 필요한 패키지 설치
pip install langchain openai pydantic python-dotenv

# 2. OpenAI API 키 설정
export OPENAI_API_KEY='your-api-key-here'

# 3. 프로젝트 루트 디렉토리로 이동
cd /path/to/your/project
```

### Step 2: 코드베이스 분석기 커스터마이징

#### 2.1 새로운 프로젝트 타입 추가
```python
def _detect_project_type(self):
    # 기존 코드...

    # 새로운 프로젝트 타입 감지 로직 추가
    elif self._has_file('go.mod'):
        project_type = 'go_backend'
        confidence += 0.8
    elif self._has_file('Cargo.toml'):
        project_type = 'rust_backend'
        confidence += 0.8
    elif self._has_file('package.json') and self._search_in_file('package.json', 'react-native'):
        project_type = 'react_native_app'
        confidence += 0.7
```

#### 2.2 새로운 기술 스택 분석 추가
```python
def _analyze_backend(self) -> Dict:
    # 기존 코드...

    # Go 백엔드 감지
    elif self._has_file('go.mod'):
        backend_info['language'] = 'Go'
        backend_info['framework'] = 'Gin/Echo'
        backend_info['patterns'].append('Go Modules')

    # Rust 백엔드 감지
    elif self._has_file('Cargo.toml'):
        backend_info['language'] = 'Rust'
        backend_info['framework'] = 'Actix Web'
        backend_info['patterns'].append('Cargo')
```

#### 2.3 새로운 비즈니스 도메인 추가
```python
def _analyze_business_domain(self):
    domain_keywords = {
        # 기존 도메인들...

        # 새로운 도메인 추가
        'fintech': ['payment', 'wallet', 'transaction', 'banking', 'fintech', 'crypto', 'blockchain'],
        'healthcare': ['patient', 'doctor', 'medical', 'health', 'clinic', 'hospital', 'prescription'],
        'iot': ['sensor', 'device', 'iot', 'smart', 'automation', 'telemetry'],
        'ai_ml': ['model', 'prediction', 'training', 'algorithm', 'neural', 'ai', 'ml']
    }
```

### Step 3: 프롬프트 커스터마이징

#### 3.1 도메인별 프롬프트 템플릿
```python
def _get_domain_specific_prompt(self, domain: str) -> str:
    prompts = {
        'education': "교육 플랫폼에 특화된 PRD를 생성하세요...",
        'ecommerce': "전자상거래 플랫폼에 특화된 PRD를 생성하세요...",
        'fintech': "핀테크 서비스에 특화된 PRD를 생성하세요...",
        'healthcare': "헬스케어 플랫폼에 특화된 PRD를 생성하세요..."
    }
    return prompts.get(domain, "일반적인 웹 애플리케이션 PRD를 생성하세요...")
```

#### 3.2 기술 스택별 프롬프트 조정
```python
def _get_tech_specific_guidance(self, tech_stack: Dict) -> str:
    guidance = []

    if tech_stack['backend']['framework'] == 'FastAPI':
        guidance.append("FastAPI의 비동기 처리와 자동 문서화 기능을 강조하세요.")

    if tech_stack['frontend']['framework'] == 'Next.js':
        guidance.append("Next.js의 SSR/SSG 기능과 성능 최적화를 언급하세요.")

    if tech_stack['database']['type'] == 'PostgreSQL':
        guidance.append("PostgreSQL의 ACID 특성과 확장성을 설명하세요.")

    return " ".join(guidance)
```

### Step 4: 실행 및 테스트

#### 4.1 기본 실행
```bash
# 기본 실행
python simple_langchain_prd.py --project-root . --output MyProject_PRD.md

# API 키와 함께 실행
python simple_langchain_prd.py --project-root . --output MyProject_PRD.md --api-key your-api-key
```

#### 4.2 배치 처리
```bash
# 여러 프로젝트 일괄 처리
for project in project1 project2 project3; do
    python simple_langchain_prd.py --project-root ./$project --output ./$project/PRD.md
done
```

## 🔧 고급 커스터마이징

### 1. 커스텀 분석기 추가
```python
class CustomAnalyzer(CodebaseAnalyzer):
    def _analyze_custom_patterns(self):
        """커스텀 패턴 분석"""
        # 프로젝트별 특수한 분석 로직
        pass

    def _extract_custom_metrics(self):
        """커스텀 메트릭 추출"""
        # 프로젝트별 특수한 메트릭
        pass
```

### 2. 다국어 지원
```python
def _get_localized_prompt(self, language: str = 'ko') -> str:
    prompts = {
        'ko': "한국어로 PRD를 작성하세요...",
        'en': "Write the PRD in English...",
        'ja': "日本語でPRDを書いてください..."
    }
    return prompts.get(language, prompts['ko'])
```

### 3. 출력 포맷 확장
```python
def generate_multiple_formats(self, analysis_result: Dict):
    """여러 포맷으로 출력"""
    # Markdown
    self._generate_markdown(analysis_result)

    # HTML
    self._generate_html(analysis_result)

    # PDF
    self._generate_pdf(analysis_result)

    # Word
    self._generate_word(analysis_result)
```

## 📊 성공 사례 및 모범 사례

### 1. 성공 사례
- **교육 플랫폼**: 퀴즈 시스템 분석 → 교육 도메인 PRD 생성
- **전자상거래**: 쇼핑몰 분석 → 이커머스 도메인 PRD 생성
- **핀테크**: 결제 시스템 분석 → 핀테크 도메인 PRD 생성

### 2. 모범 사례
- **정확한 분석**: 프로젝트 구조를 정확히 파악
- **도메인 특화**: 비즈니스 도메인에 맞는 프롬프트 사용
- **지속적 개선**: 피드백을 통한 프롬프트 최적화
- **보안 고려**: API 키 보안 관리

## 🚨 주의사항 및 제한사항

### 1. 주의사항
- **API 비용**: OpenAI API 사용량에 따른 비용 발생
- **보안**: API 키 노출 방지
- **정확성**: AI 생성 결과 검증 필요
- **컨텍스트**: 대용량 프로젝트의 경우 컨텍스트 제한

### 2. 제한사항
- **언어 지원**: 주로 영어/한국어 지원
- **프레임워크**: 일부 새로운 프레임워크 미지원
- **복잡성**: 매우 복잡한 아키텍처 분석 한계

## 🔄 지속적 개선 방안

### 1. 피드백 수집
- 생성된 PRD 품질 평가
- 사용자 피드백 수집
- 오류 패턴 분석

### 2. 모델 업그레이드
- GPT-4 업그레이드 고려
- 다른 LLM 모델 실험
- 파인튜닝 모델 개발

### 3. 기능 확장
- 실시간 분석 기능
- 협업 기능 추가
- 버전 관리 기능
