#!/usr/bin/env python3
"""
PRD 자동 생성기
코드베이스를 분석하여 Product Requirements Document를 자동 생성합니다.
"""

import os
import re
import json
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class CodebaseAnalyzer:
    """코드베이스 분석 클래스"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_result = {
            'project_info': {},
            'tech_stack': {},
            'models': {},
            'apis': {},
            'features': {},
            'security': {},
            'database': {}
        }

    def analyze_project_structure(self):
        """프로젝트 구조 분석"""
        backend_path = self.project_root / 'backend'
        frontend_path = self.project_root / 'frontend'

        # 백엔드 분석
        if backend_path.exists():
            self.analysis_result['tech_stack']['backend'] = self._analyze_backend(backend_path)
            self.analysis_result['models'] = self._extract_models(backend_path)
            self.analysis_result['apis'] = self._extract_apis(backend_path)
            self.analysis_result['database'] = self._analyze_database(backend_path)

        # 프론트엔드 분석
        if frontend_path.exists():
            self.analysis_result['tech_stack']['frontend'] = self._analyze_frontend(frontend_path)
            self.analysis_result['features'] = self._extract_frontend_features(frontend_path)

    def _analyze_backend(self, backend_path: Path) -> Dict:
        """백엔드 기술 스택 분석"""
        requirements_file = backend_path / 'requirements.txt'
        main_file = backend_path / 'main.py'

        tech_stack = {
            'framework': 'FastAPI',
            'dependencies': [],
            'database_orm': 'SQLAlchemy',
            'authentication': 'JWT + bcrypt'
        }

        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                tech_stack['dependencies'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        return tech_stack

    def _analyze_frontend(self, frontend_path: Path) -> Dict:
        """프론트엔드 기술 스택 분석"""
        package_json = frontend_path / 'package.json'

        tech_stack = {
            'framework': 'Next.js',
            'ui_library': 'React Bootstrap',
            'dependencies': []
        }

        if package_json.exists():
            with open(package_json, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
                tech_stack['dependencies'] = list(package_data.get('dependencies', {}).keys())
                tech_stack['version'] = package_data.get('version', '1.0.0')

        return tech_stack

    def _extract_models(self, backend_path: Path) -> Dict:
        """데이터 모델 추출"""
        models = {}
        models_path = backend_path / 'app' / 'models'

        if models_path.exists():
            for model_file in models_path.glob('*.py'):
                if model_file.name == '__init__.py':
                    continue

                model_name = model_file.stem
                models[model_name] = self._parse_model_file(model_file)

        return models

    def _parse_model_file(self, model_file: Path) -> Dict:
        """모델 파일 파싱"""
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # SQLAlchemy 모델 파싱
        model_info = {
            'table_name': '',
            'fields': [],
            'relationships': []
        }

        # 테이블명 추출
        table_match = re.search(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
        if table_match:
            model_info['table_name'] = table_match.group(1)

        # 컬럼 추출
        column_pattern = r'(\w+)\s*=\s*Column\([^)]+\)'
        columns = re.findall(column_pattern, content)
        model_info['fields'] = columns

        return model_info

    def _extract_apis(self, backend_path: Path) -> Dict:
        """API 엔드포인트 추출"""
        apis = {}
        routes_path = backend_path / 'app' / 'routes'

        if routes_path.exists():
            for route_file in routes_path.glob('*.py'):
                if route_file.name == '__init__.py':
                    continue

                route_name = route_file.stem
                apis[route_name] = self._parse_route_file(route_file)

        return apis

    def _parse_route_file(self, route_file: Path) -> List[Dict]:
        """라우트 파일 파싱"""
        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()

        endpoints = []

        # FastAPI 라우터 패턴 매칭
        route_pattern = r'@router\.(get|post|put|delete)\(["\']([^"\']+)["\']\)\s*\n\s*async def (\w+)'
        matches = re.findall(route_pattern, content, re.MULTILINE)

        for method, path, function_name in matches:
            endpoints.append({
                'method': method.upper(),
                'path': path,
                'function_name': function_name,
                'description': self._extract_function_docstring(content, function_name)
            })

        return endpoints

    def _extract_function_docstring(self, content: str, function_name: str) -> str:
        """함수 docstring 추출"""
        pattern = rf'async def {function_name}[^:]*:\s*\n\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _analyze_database(self, backend_path: Path) -> Dict:
        """데이터베이스 설정 분석"""
        config_file = backend_path / 'app' / 'core' / 'config.py'
        database_file = backend_path / 'app' / 'core' / 'database.py'

        db_info = {
            'type': 'SQLite/PostgreSQL',
            'orm': 'SQLAlchemy',
            'migration': False
        }

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'postgresql' in content.lower():
                    db_info['type'] = 'PostgreSQL'
                elif 'sqlite' in content.lower():
                    db_info['type'] = 'SQLite'

        return db_info

    def _extract_frontend_features(self, frontend_path: Path) -> Dict:
        """프론트엔드 기능 추출"""
        features = {}
        app_path = frontend_path / 'app'

        if app_path.exists():
            for page_dir in app_path.iterdir():
                if page_dir.is_dir() and not page_dir.name.startswith('.'):
                    page_name = page_dir.name
                    features[page_name] = {
                        'path': f'/{page_name}',
                        'description': self._extract_page_description(page_dir)
                    }

        return features

    def _extract_page_description(self, page_dir: Path) -> str:
        """페이지 설명 추출"""
        page_file = page_dir / 'page.js'
        if page_file.exists():
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 간단한 설명 추출 (실제로는 더 정교한 파싱 필요)
                return f"React 컴포넌트 기반 {page_dir.name} 페이지"
        return ""

class PRDGenerator:
    """PRD 생성기 클래스"""

    def __init__(self, analysis_result: Dict):
        self.analysis = analysis_result

    def generate_prd(self) -> str:
        """PRD 생성"""
        prd_content = f"""# 코딩 퀴즈 플랫폼 PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: {datetime.now().strftime('%Y-%m-%d')}
- **작성자**: PRD Generator
- **마지막 수정**: {datetime.now().strftime('%Y-%m-%d')}

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
- **Framework**: {self.analysis['tech_stack']['backend']['framework']}
- **ORM**: {self.analysis['tech_stack']['backend']['database_orm']}
- **Authentication**: {self.analysis['tech_stack']['backend']['authentication']}
- **Dependencies**: {', '.join(self.analysis['tech_stack']['backend']['dependencies'])}

### 2.2 프론트엔드
- **Framework**: {self.analysis['tech_stack']['frontend']['framework']}
- **UI Library**: {self.analysis['tech_stack']['frontend']['ui_library']}
- **Dependencies**: {', '.join(self.analysis['tech_stack']['frontend']['dependencies'])}

### 2.3 데이터베이스
- **Type**: {self.analysis['database']['type']}
- **ORM**: {self.analysis['database']['orm']}

## ⚙️ 3. 핵심 기능
{self._generate_features_section()}

## 📊 4. 데이터 모델
{self._generate_models_section()}

## 🔌 5. API 명세
{self._generate_api_section()}

## 🎨 6. 사용자 경험
{self._generate_ux_section()}

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
"""
        return prd_content

    def _generate_features_section(self) -> str:
        """기능 섹션 생성"""
        features = []
        for page_name, page_info in self.analysis['features'].items():
            features.append(f"### 3.{len(features)+1} {page_name.title()} 기능")
            features.append(f"- **설명**: {page_info['description']}")
            features.append(f"- **경로**: {page_info['path']}")
            features.append("")
        return "\n".join(features)

    def _generate_models_section(self) -> str:
        """모델 섹션 생성"""
        models = []
        for model_name, model_info in self.analysis['models'].items():
            models.append(f"### 4.{len(models)+1} {model_name.title()}")
            models.append(f"- **테이블명**: {model_info['table_name']}")
            models.append(f"- **필드**: {', '.join(model_info['fields'])}")
            models.append("")
        return "\n".join(models)

    def _generate_api_section(self) -> str:
        """API 섹션 생성"""
        apis = []
        for route_name, endpoints in self.analysis['apis'].items():
            apis.append(f"### 5.{len(apis)+1} {route_name.title()} API")
            for endpoint in endpoints:
                apis.append(f"- `{endpoint['method']} {endpoint['path']}` - {endpoint['description']}")
            apis.append("")
        return "\n".join(apis)

    def _generate_ux_section(self) -> str:
        """UX 섹션 생성"""
        ux = []
        for page_name, page_info in self.analysis['features'].items():
            ux.append(f"### 6.{len(ux)+1} {page_name.title()} 페이지")
            ux.append(f"- **목적**: {page_info['description']}")
            ux.append(f"- **주요 기능**: 사용자 인터랙션 및 데이터 표시")
            ux.append("")
        return "\n".join(ux)

def main():
    parser = argparse.ArgumentParser(description='PRD 자동 생성기')
    parser.add_argument('--project-root', default='.', help='프로젝트 루트 디렉토리')
    parser.add_argument('--output', default='PRD.md', help='출력 파일명')

    args = parser.parse_args()

    # 코드베이스 분석
    analyzer = CodebaseAnalyzer(args.project_root)
    analyzer.analyze_project_structure()

    # PRD 생성
    generator = PRDGenerator(analyzer.analysis_result)
    prd_content = generator.generate_prd()

    # 파일 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(prd_content)

    print(f"PRD가 {args.output}에 생성되었습니다.")
    print(f"분석된 모델 수: {len(analyzer.analysis_result['models'])}")
    print(f"분석된 API 수: {sum(len(apis) for apis in analyzer.analysis_result['apis'].values())}")

if __name__ == "__main__":
    main()
