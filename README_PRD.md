# PRD 자동 생성 가이드

## 📋 개요
코드베이스를 분석하여 Product Requirements Document (PRD)를 자동으로 생성하는 도구들입니다.

## 🛠️ 제공 도구

### 1. 간단한 PRD 생성기 (`generate_prd.py`)
현재 프로젝트에 맞춰 기본 PRD를 생성합니다.

```bash
python generate_prd.py
```

**특징:**
- 현재 프로젝트 구조에 맞춘 PRD 생성
- 하드코딩된 내용으로 빠른 생성
- 기본적인 PRD 구조 제공

### 2. 고급 PRD 생성기 (`prd_generator.py`)
코드베이스를 실제로 분석하여 동적으로 PRD를 생성합니다.

```bash
python prd_generator.py --project-root . --output PRD_Analyzed.md
```

**특징:**
- 코드베이스 자동 분석
- 모델, API, 기능 자동 추출
- 동적 PRD 생성

### 3. PRD 템플릿 (`prd_template.md`)
표준화된 PRD 템플릿입니다.

**사용법:**
1. 템플릿을 복사
2. `{변수명}` 부분을 실제 값으로 교체
3. 프로젝트에 맞게 내용 수정

## 🚀 사용 방법

### 방법 1: 간단한 생성
```bash
# 현재 프로젝트용 PRD 생성
python generate_prd.py
```

### 방법 2: 고급 분석
```bash
# 코드베이스 분석 후 PRD 생성
python prd_generator.py --project-root . --output PRD.md
```

### 방법 3: 템플릿 사용
1. `prd_template.md` 파일 열기
2. `{변수명}` 부분을 실제 값으로 교체
3. 프로젝트에 맞게 내용 수정

## 📊 생성되는 PRD 구조

```
1. 제품 개요
   - 제품명, 비전, 핵심 가치, 타겟 사용자

2. 기술 스택
   - 백엔드, 프론트엔드, 데이터베이스, 인프라

3. 핵심 기능
   - 각 기능별 상세 설명 및 API

4. 데이터 모델
   - 데이터베이스 모델 정의

5. API 명세
   - REST API 엔드포인트 목록

6. 사용자 경험
   - 페이지별 UX 설계

7. 보안 요구사항
   - 인증, 데이터 보안, 입력 검증

8. 성능 요구사항
   - 응답 시간, 동시성, 확장성

9. 배포 및 운영
   - 환경 구성, 모니터링, 백업

10. 개발 로드맵
    - 단계별 개발 계획

11. 성공 지표 (KPI)
    - 사용자, 비즈니스, 기술 지표
```

## 🔧 커스터마이징

### PRD 내용 수정
생성된 PRD 파일을 열어서 다음 부분을 수정하세요:

1. **제품 정보**: 제품명, 비전, 타겟 사용자
2. **기술 스택**: 실제 사용하는 기술로 수정
3. **기능**: 프로젝트에 맞는 기능으로 수정
4. **로드맵**: 실제 개발 계획에 맞게 수정
5. **KPI**: 측정하고 싶은 지표로 수정

### 자동화 스크립트 수정
`prd_generator.py`를 수정하여 다음을 개선할 수 있습니다:

1. **모델 파싱**: 더 정교한 모델 분석
2. **API 추출**: 더 많은 API 정보 추출
3. **기능 분석**: 프론트엔드 기능 자동 분석
4. **보안 분석**: 보안 설정 자동 감지

## 📝 예시 사용법

### 1. 기본 PRD 생성
```bash
python generate_prd.py
# PRD.md 파일이 생성됩니다
```

### 2. 분석 기반 PRD 생성
```bash
python prd_generator.py --project-root . --output MyProject_PRD.md
# MyProject_PRD.md 파일이 생성됩니다
```

### 3. 특정 디렉토리 분석
```bash
python prd_generator.py --project-root /path/to/project --output Custom_PRD.md
```

## 🎯 활용 팁

1. **정기적 업데이트**: 코드 변경 시 PRD도 함께 업데이트
2. **팀 공유**: 생성된 PRD를 팀원들과 공유하여 일관성 유지
3. **버전 관리**: PRD도 코드와 함께 버전 관리
4. **검토**: 자동 생성된 내용을 검토하고 수정

## 🔍 문제 해결

### 자주 발생하는 문제

1. **모듈 import 오류**
   ```bash
   pip install -r requirements.txt
   ```

2. **파일 경로 오류**
   - 프로젝트 루트에서 실행하세요
   - 상대 경로를 확인하세요

3. **생성된 PRD가 비어있음**
   - 코드베이스 구조를 확인하세요
   - 파일 권한을 확인하세요

## 📚 추가 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Next.js 공식 문서](https://nextjs.org/docs)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [PRD 작성 가이드](https://www.atlassian.com/agile/project-management/product-requirements-document)

## 🤝 기여하기

PRD 생성기를 개선하고 싶다면:

1. 이슈 등록
2. 코드 수정
3. Pull Request 생성

---

**생성일**: 2024-01-XX
**버전**: v1.0
**작성자**: PRD Generator
