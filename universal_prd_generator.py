#!/usr/bin/env python3
"""
범용 PRD 생성기
다양한 프로젝트 타입과 기술 스택을 지원하는 PRD 자동 생성기
"""

import os
import json
import re
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class UniversalCodebaseAnalyzer:
    """범용 코드베이스 분석 클래스"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analysis_result = {
            'project_info': {},
            'tech_stack': {},
            'models': {},
            'apis': {},
            'features': {},
            'project_type': 'unknown',
            'business_domain': 'unknown'
        }

    def analyze_project(self):
        """프로젝트 전체 분석"""
        self._detect_project_type()
        self._analyze_tech_stack()
        self._extract_models()
        self._extract_apis()
        self._extract_features()
        self._analyze_business_domain()

    def _detect_project_type(self):
        """프로젝트 타입 자동 감지"""
        project_type = 'unknown'

        # 분리된 백엔드/프론트엔드 구조 감지
        if self._has_file('backend/requirements.txt') and self._has_file('frontend/package.json'):
            if self._has_file('backend/main.py'):
                project_type = 'fastapi_nextjs_fullstack'
            elif self._has_file('backend/app.py'):
                project_type = 'flask_nextjs_fullstack'
            else:
                project_type = 'python_nextjs_fullstack'
        # 단일 폴더 구조 감지
        elif self._has_file('package.json') and self._has_file('next.config.js'):
            project_type = 'nextjs_webapp'
        elif self._has_file('package.json') and self._has_file('src/App.js'):
            project_type = 'react_webapp'
        elif self._has_file('requirements.txt') and self._has_file('main.py'):
            project_type = 'fastapi_backend'
        elif self._has_file('requirements.txt') and self._has_file('app.py'):
            project_type = 'flask_backend'
        elif self._has_file('pom.xml'):
            project_type = 'java_application'
        elif self._has_file('Cargo.toml'):
            project_type = 'rust_application'
        elif self._has_file('go.mod'):
            project_type = 'go_application'

        self.analysis_result['project_type'] = project_type

    def _analyze_business_domain(self):
        """비즈니스 도메인 분석"""
        domain_keywords = {
            'education': ['quiz', 'course', 'lesson', 'student', 'teacher', 'learning', 'question', 'answer', 'score', 'ranking'],
            'ecommerce': ['shop', 'cart', 'order', 'product', 'payment', 'checkout', 'buy', 'sell'],
            'social': ['user', 'post', 'comment', 'like', 'follow', 'feed'],
            'finance': ['account', 'transaction', 'balance', 'wallet', 'bank'],
            'healthcare': ['patient', 'doctor', 'appointment', 'medical', 'health'],
            'gaming': ['game', 'player', 'level', 'achievement', 'play'],
            'iot': ['sensor', 'device', 'monitor', 'data', 'telemetry'],
            'ai_ml': ['model', 'prediction', 'training', 'algorithm', 'neural'],
            'cms': ['content', 'article', 'page', 'media', 'publish'],
            'api_service': ['api', 'service', 'endpoint', 'microservice']
        }

        # 파일명과 내용에서 키워드 검색
        found_domains = []
        for domain, keywords in domain_keywords.items():
            score = 0
            for keyword in keywords:
                if self._search_keyword_in_files(keyword):
                    score += 1
            if score >= 2:  # 2개 이상 키워드 발견
                found_domains.append((domain, score))

        # 가장 높은 점수의 도메인 선택
        if found_domains:
            found_domains.sort(key=lambda x: x[1], reverse=True)
            self.analysis_result['business_domain'] = found_domains[0][0]

    def _search_keyword_in_files(self, keyword: str) -> bool:
        """파일에서 키워드 검색"""
        for file_path in self.project_root.rglob('*.py'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if keyword.lower() in f.read().lower():
                        return True
            except:
                continue
        return False

    def _analyze_tech_stack(self):
        """기술 스택 분석"""
        tech_stack = {
            'backend': {},
            'frontend': {},
            'database': {},
            'infrastructure': {}
        }

        # 백엔드 분석 (분리된 구조 지원)
        if self._has_file('backend/requirements.txt'):
            tech_stack['backend'] = self._analyze_python_backend('backend/')
        elif self._has_file('requirements.txt'):
            tech_stack['backend'] = self._analyze_python_backend('')
        elif self._has_file('pom.xml'):
            tech_stack['backend'] = self._analyze_java_backend()
        elif self._has_file('Cargo.toml'):
            tech_stack['backend'] = self._analyze_rust_backend()
        elif self._has_file('go.mod'):
            tech_stack['backend'] = self._analyze_go_backend()

        # 프론트엔드 분석 (분리된 구조 지원)
        if self._has_file('frontend/package.json'):
            tech_stack['frontend'] = self._analyze_frontend('frontend/')
        elif self._has_file('package.json'):
            tech_stack['frontend'] = self._analyze_frontend('')

        # 데이터베이스 분석
        tech_stack['database'] = self._analyze_database()

        # 인프라 분석
        tech_stack['infrastructure'] = self._analyze_infrastructure()

        self.analysis_result['tech_stack'] = tech_stack

    def _analyze_python_backend(self, backend_path: str = '') -> Dict:
        """Python 백엔드 분석"""
        backend_info = {
            'language': 'Python',
            'framework': 'Unknown',
            'dependencies': []
        }

        # 프레임워크 감지
        main_file = f'{backend_path}main.py' if backend_path else 'main.py'
        if self._has_file(main_file):
            try:
                with open(self.project_root / main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'FastAPI' in content:
                        backend_info['framework'] = 'FastAPI'
                    elif 'Flask' in content:
                        backend_info['framework'] = 'Flask'
                    elif 'Django' in content:
                        backend_info['framework'] = 'Django'
            except Exception as e:
                print(f"백엔드 분석 오류: {e}")

        # 의존성 분석
        req_file = f'{backend_path}requirements.txt' if backend_path else 'requirements.txt'
        if self._has_file(req_file):
            try:
                with open(self.project_root / req_file, 'r', encoding='utf-8') as f:
                    backend_info['dependencies'] = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            except Exception as e:
                print(f"의존성 분석 오류: {e}")

        return backend_info

    def _analyze_java_backend(self) -> Dict:
        """Java 백엔드 분석"""
        return {
            'language': 'Java',
            'framework': 'Spring Boot',
            'dependencies': []
        }

    def _analyze_rust_backend(self) -> Dict:
        """Rust 백엔드 분석"""
        return {
            'language': 'Rust',
            'framework': 'Actix Web',
            'dependencies': []
        }

    def _analyze_go_backend(self) -> Dict:
        """Go 백엔드 분석"""
        return {
            'language': 'Go',
            'framework': 'Gin/Echo',
            'dependencies': []
        }

    def _analyze_frontend(self, frontend_path: str = '') -> Dict:
        """프론트엔드 분석"""
        frontend_info = {
            'framework': 'Unknown',
            'ui_library': 'Unknown',
            'dependencies': []
        }

        package_file = f'{frontend_path}package.json' if frontend_path else 'package.json'
        if self._has_file(package_file):
            try:
                with open(self.project_root / package_file, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    dependencies = package_data.get('dependencies', {})

                    # 프레임워크 감지
                    if 'next' in dependencies:
                        frontend_info['framework'] = 'Next.js'
                    elif 'react' in dependencies:
                        frontend_info['framework'] = 'React'
                    elif 'vue' in dependencies:
                        frontend_info['framework'] = 'Vue.js'
                    elif 'angular' in dependencies:
                        frontend_info['framework'] = 'Angular'

                    # UI 라이브러리 감지
                    if 'react-bootstrap' in dependencies:
                        frontend_info['ui_library'] = 'React Bootstrap'
                    elif 'antd' in dependencies:
                        frontend_info['ui_library'] = 'Ant Design'
                    elif 'material-ui' in dependencies:
                        frontend_info['ui_library'] = 'Material-UI'
                    elif 'bootstrap' in dependencies:
                        frontend_info['ui_library'] = 'Bootstrap'

                    frontend_info['dependencies'] = list(dependencies.keys())
            except Exception as e:
                print(f"프론트엔드 분석 오류: {e}")

        return frontend_info

    def _analyze_database(self) -> Dict:
        """데이터베이스 분석"""
        db_info = {
            'type': 'Unknown',
            'orm': 'Unknown'
        }

        # 설정 파일에서 데이터베이스 타입 감지 (분리된 구조 지원)
        config_files = [
            'backend/config.py', 'backend/settings.py', 'backend/database.py',
            'backend/app.py', 'backend/main.py',
            'config.py', 'settings.py', 'database.py', 'app.py', 'main.py'
        ]

        for config_file in config_files:
            if self._has_file(config_file):
                try:
                    with open(self.project_root / config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'postgresql' in content.lower():
                            db_info['type'] = 'PostgreSQL'
                        elif 'mysql' in content.lower():
                            db_info['type'] = 'MySQL'
                        elif 'sqlite' in content.lower():
                            db_info['type'] = 'SQLite'
                        elif 'mongodb' in content.lower():
                            db_info['type'] = 'MongoDB'

                        if 'sqlalchemy' in content.lower():
                            db_info['orm'] = 'SQLAlchemy'
                        elif 'django' in content.lower():
                            db_info['orm'] = 'Django ORM'
                except Exception as e:
                    print(f"데이터베이스 분석 오류: {e}")
                    continue

        return db_info

    def _analyze_infrastructure(self) -> Dict:
        """인프라 분석"""
        infra_info = {
            'containerization': 'None',
            'deployment': 'Unknown',
            'monitoring': 'None'
        }

        if self._has_file('Dockerfile'):
            infra_info['containerization'] = 'Docker'
        elif self._has_file('docker-compose.yml'):
            infra_info['containerization'] = 'Docker Compose'

        if self._has_file('.github/workflows'):
            infra_info['deployment'] = 'GitHub Actions'
        elif self._has_file('.gitlab-ci.yml'):
            infra_info['deployment'] = 'GitLab CI'

        return infra_info

    def _extract_models(self):
        """데이터 모델 추출"""
        models = {}

        # Python 모델 추출 (분리된 구조 지원)
        if self._has_file('backend/requirements.txt') or self._has_file('requirements.txt'):
            # 백엔드 폴더에서 모델 찾기
            models_paths = [
                self.project_root / 'backend' / 'app' / 'models',
                self.project_root / 'app' / 'models',
                self.project_root / 'models'
            ]

            for models_path in models_paths:
                if models_path.exists():
                    for model_file in models_path.glob('*.py'):
                        if model_file.name == '__init__.py':
                            continue
                        model_name = model_file.stem
                        models[model_name] = self._parse_python_model(model_file)
                    break  # 첫 번째로 찾은 모델 폴더만 사용

        self.analysis_result['models'] = models

    def _parse_python_model(self, model_file: Path) -> Dict:
        """Python 모델 파일 파싱"""
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()

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

    def _extract_apis(self):
        """API 엔드포인트 추출"""
        apis = {}

        # Python API 추출 (분리된 구조 지원)
        if self._has_file('backend/requirements.txt') or self._has_file('requirements.txt'):
            # 백엔드 폴더에서 라우트 찾기
            routes_paths = [
                self.project_root / 'backend' / 'app' / 'routes',
                self.project_root / 'app' / 'routes',
                self.project_root / 'routes'
            ]

            for routes_path in routes_paths:
                if routes_path.exists():
                    for route_file in routes_path.glob('*.py'):
                        if route_file.name == '__init__.py':
                            continue
                        route_name = route_file.stem
                        apis[route_name] = self._parse_python_routes(route_file)
                    break  # 첫 번째로 찾은 라우트 폴더만 사용

        self.analysis_result['apis'] = apis

    def _parse_python_routes(self, route_file: Path) -> List[Dict]:
        """Python 라우트 파일 파싱"""
        with open(route_file, 'r', encoding='utf-8') as f:
            content = f.read()

        endpoints = []

        # FastAPI/Flask 라우터 패턴 매칭
        route_pattern = r'@(?:router|app)\.(get|post|put|delete)\(["\']([^"\']+)["\']\)\s*\n\s*(?:async\s+)?def\s+(\w+)'
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
        pattern = rf'(?:async\s+)?def\s+{function_name}[^:]*:\s*\n\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_features(self):
        """프론트엔드 기능 추출"""
        features = {}

        # 프론트엔드 폴더에서 기능 추출 (분리된 구조 지원)
        if self._has_file('frontend/package.json') or self._has_file('package.json'):
            # 프론트엔드 폴더에서 앱 구조 찾기
            app_paths = [
                self.project_root / 'frontend' / 'app',
                self.project_root / 'app',
                self.project_root / 'src'
            ]

            for app_path in app_paths:
                if app_path.exists():
                    for page_dir in app_path.iterdir():
                        if page_dir.is_dir() and not page_dir.name.startswith('.'):
                            page_name = page_dir.name
                            features[page_name] = {
                                'path': f'/{page_name}',
                                'description': self._extract_page_description(page_dir)
                            }
                    break  # 첫 번째로 찾은 앱 폴더만 사용

        self.analysis_result['features'] = features

    def _extract_page_description(self, page_dir: Path) -> str:
        """페이지 설명 추출"""
        page_file = page_dir / 'page.js'
        if page_file.exists():
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
                return f"React 컴포넌트 기반 {page_dir.name} 페이지"
        return ""

    def _has_file(self, filename: str) -> bool:
        """파일 존재 여부 확인"""
        return (self.project_root / filename).exists()

class UniversalPRDGenerator:
    """범용 PRD 생성기 클래스"""

    def __init__(self, analysis_result: Dict):
        self.analysis = analysis_result

    def generate_prd(self) -> str:
        """PRD 생성"""
        project_name = self._get_project_name()
        current_date = datetime.now().strftime('%Y-%m-%d')

        prd_content = f"""# {project_name} PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: {current_date}
- **작성자**: Universal PRD Generator
- **마지막 수정**: {current_date}
- **프로젝트 타입**: {self.analysis['project_type']}
- **비즈니스 도메인**: {self.analysis['business_domain']}

## 🎯 1. 제품 개요
### 1.1 제품명
{project_name}

### 1.2 제품 비전
{self._generate_vision()}

### 1.3 핵심 가치
{self._generate_core_values()}

### 1.4 타겟 사용자
{self._generate_target_users()}

## 🏗️ 2. 기술 스택
{self._generate_tech_stack_section()}

## ⚙️ 3. 핵심 기능
{self._generate_features_section()}

## 📊 4. 데이터 모델
{self._generate_models_section()}

## 🔌 5. API 명세
{self._generate_api_section()}

## 🎨 6. 사용자 경험
{self._generate_ux_section()}

## 🔒 7. 보안 요구사항
{self._generate_security_section()}

## 📈 8. 성능 요구사항
{self._generate_performance_section()}

## 🚀 9. 배포 및 운영
{self._generate_deployment_section()}

## 📅 10. 개발 로드맵
{self._generate_roadmap_section()}

## 📊 11. 성공 지표 (KPI)
{self._generate_kpi_section()}

## 📝 12. 부록
### 12.1 용어 정의
{self._generate_glossary()}

### 12.2 참고 자료
{self._generate_references()}

### 12.3 변경 이력
| 버전 | 날짜 | 변경사항 | 작성자 |
|------|------|----------|--------|
| v1.0 | {current_date} | 초기 버전 | Universal PRD Generator |
"""
        return prd_content

    def _get_project_name(self) -> str:
        """프로젝트명 추출"""
        # 프로젝트 루트 디렉토리명 사용
        project_root = self.analysis.get('project_info', {}).get('root', '')
        if project_root:
            return Path(project_root).name

        # 기본값으로 현재 디렉토리명 사용
        return 'Coding Quiz Platform'

    def _generate_vision(self) -> str:
        """비전 생성"""
        domain_visions = {
            'ecommerce': '온라인 쇼핑몰 플랫폼으로 사용자에게 편리하고 안전한 쇼핑 경험을 제공합니다.',
            'education': '학습자 중심의 교육 플랫폼으로 효과적인 학습 경험을 제공합니다.',
            'social': '사용자 간 소통과 연결을 촉진하는 소셜 플랫폼을 제공합니다.',
            'finance': '안전하고 편리한 금융 서비스를 제공하는 플랫폼입니다.',
            'healthcare': '의료진과 환자를 연결하는 의료 서비스 플랫폼입니다.',
            'gaming': '사용자에게 몰입감 있는 게임 경험을 제공하는 플랫폼입니다.',
            'iot': '사물인터넷 기반 스마트 솔루션을 제공하는 플랫폼입니다.',
            'ai_ml': '인공지능과 머신러닝 기술을 활용한 지능형 서비스를 제공합니다.',
            'cms': '콘텐츠 관리와 배포를 효율적으로 지원하는 플랫폼입니다.',
            'api_service': '다양한 서비스와의 연동을 위한 API 서비스를 제공합니다.'
        }

        domain = self.analysis.get('business_domain', 'unknown')
        return domain_visions.get(domain, '사용자에게 가치 있는 서비스를 제공하는 플랫폼입니다.')

    def _generate_core_values(self) -> str:
        """핵심 가치 생성"""
        return """- **사용자 중심**: 사용자 경험을 최우선으로 고려
- **안정성**: 안정적이고 신뢰할 수 있는 서비스 제공
- **확장성**: 미래 성장에 대비한 확장 가능한 아키텍처
- **보안**: 사용자 데이터와 시스템의 보안 보장"""

    def _generate_target_users(self) -> str:
        """타겟 사용자 생성"""
        domain_users = {
            'ecommerce': '온라인 쇼핑을 원하는 일반 소비자, 쇼핑몰 운영자',
            'education': '학습자, 교육자, 교육 기관',
            'social': '소셜 네트워킹을 원하는 사용자',
            'finance': '금융 서비스를 이용하는 개인 및 기업',
            'healthcare': '환자, 의료진, 의료 기관',
            'gaming': '게임 플레이어, 게임 개발자',
            'iot': 'IoT 기기 사용자, 시스템 관리자',
            'ai_ml': 'AI/ML 서비스를 이용하는 개발자 및 기업',
            'cms': '콘텐츠 관리자, 웹사이트 운영자',
            'api_service': 'API를 활용하는 개발자 및 서비스 제공자'
        }

        domain = self.analysis.get('business_domain', 'unknown')
        return domain_users.get(domain, '서비스 이용자, 시스템 관리자')

    def _generate_tech_stack_section(self) -> str:
        """기술 스택 섹션 생성"""
        tech_stack = self.analysis.get('tech_stack', {})

        sections = []

        # 백엔드
        if tech_stack.get('backend'):
            backend = tech_stack['backend']
            sections.append(f"""### 2.1 백엔드
- **Language**: {backend.get('language', 'Unknown')}
- **Framework**: {backend.get('framework', 'Unknown')}
- **Dependencies**: {', '.join(backend.get('dependencies', [])[:5])}""")

        # 프론트엔드
        if tech_stack.get('frontend'):
            frontend = tech_stack['frontend']
            sections.append(f"""### 2.2 프론트엔드
- **Framework**: {frontend.get('framework', 'Unknown')}
- **UI Library**: {frontend.get('ui_library', 'Unknown')}
- **Dependencies**: {', '.join(frontend.get('dependencies', [])[:5])}""")

        # 데이터베이스
        if tech_stack.get('database'):
            database = tech_stack['database']
            sections.append(f"""### 2.3 데이터베이스
- **Type**: {database.get('type', 'Unknown')}
- **ORM**: {database.get('orm', 'Unknown')}""")

        # 인프라
        if tech_stack.get('infrastructure'):
            infra = tech_stack['infrastructure']
            sections.append(f"""### 2.4 인프라
- **Containerization**: {infra.get('containerization', 'None')}
- **Deployment**: {infra.get('deployment', 'Unknown')}
- **Monitoring**: {infra.get('monitoring', 'None')}""")

        return '\n\n'.join(sections)

    def _generate_features_section(self) -> str:
        """기능 섹션 생성"""
        features = self.analysis.get('features', {})
        apis = self.analysis.get('apis', {})

        sections = []
        feature_count = 1

        for page_name, page_info in features.items():
            # 관련 API 찾기
            related_apis = []
            for api_name, endpoints in apis.items():
                if api_name.lower() in page_name.lower() or page_name.lower() in api_name.lower():
                    related_apis.extend([f"{endpoint['method']} {endpoint['path']}" for endpoint in endpoints])

            sections.append(f"""### 3.{feature_count} {page_name.title()} 기능
- **설명**: {page_info['description']}
- **우선순위**: High
- **경로**: {page_info['path']}
- **관련 API**: {', '.join(related_apis) if related_apis else 'N/A'}""")
            feature_count += 1

        return '\n\n'.join(sections) if sections else "### 3.1 기본 기능\n- **설명**: 프로젝트의 핵심 기능\n- **우선순위**: High"

    def _generate_models_section(self) -> str:
        """모델 섹션 생성"""
        models = self.analysis.get('models', {})

        sections = []
        model_count = 1

        for model_name, model_info in models.items():
            sections.append(f"""### 4.{model_count} {model_name.title()}
```python
class {model_name}:
    - table_name: {model_info.get('table_name', 'unknown')}
    - fields: {', '.join(model_info.get('fields', []))}
```""")
            model_count += 1

        return '\n\n'.join(sections) if sections else "### 4.1 데이터 모델\n- **설명**: 프로젝트의 데이터 구조\n- **필드**: 프로젝트에 따라 정의"

    def _generate_api_section(self) -> str:
        """API 섹션 생성"""
        apis = self.analysis.get('apis', {})

        sections = []
        api_count = 1

        for route_name, endpoints in apis.items():
            sections.append(f"""### 5.{api_count} {route_name.title()} API""")
            for endpoint in endpoints:
                sections.append(f"- `{endpoint['method']} {endpoint['path']}` - {endpoint['description']}")
            sections.append("")
            api_count += 1

        return '\n'.join(sections) if sections else "### 5.1 API 명세\n- **설명**: 프로젝트의 API 엔드포인트\n- **메서드**: GET, POST, PUT, DELETE"

    def _generate_ux_section(self) -> str:
        """UX 섹션 생성"""
        features = self.analysis.get('features', {})

        sections = []
        ux_count = 1

        for page_name, page_info in features.items():
            sections.append(f"""### 6.{ux_count} {page_name.title()} 페이지
- **목적**: {page_info['description']}
- **주요 기능**: 사용자 인터랙션 및 데이터 표시
- **사용자 플로우**: 페이지 접근 → 기능 이용 → 결과 확인""")
            ux_count += 1

        return '\n\n'.join(sections) if sections else "### 6.1 사용자 경험\n- **목적**: 사용자 중심의 직관적인 인터페이스 제공\n- **주요 기능**: 사용자 인터랙션 및 데이터 표시"

    def _generate_security_section(self) -> str:
        """보안 섹션 생성"""
        return """### 7.1 인증/인가
- JWT 토큰 기반 인증
- 비밀번호 해싱
- 토큰 만료 시간 관리

### 7.2 데이터 보안
- SQL Injection 방지
- XSS 방지
- CORS 정책 적용

### 7.3 입력 검증
- 입력 데이터 검증
- 비즈니스 로직 검증
- 에러 처리"""

    def _generate_performance_section(self) -> str:
        """성능 섹션 생성"""
        return """### 8.1 응답 시간
- API 응답 시간: 200ms 이하
- 페이지 로딩 시간: 2초 이하

### 8.2 동시성
- 동시 사용자: 100명 이상 지원
- 비동기 처리

### 8.3 확장성
- 마이크로서비스 아키텍처 준비
- 데이터베이스 분리 가능"""

    def _generate_deployment_section(self) -> str:
        """배포 섹션 생성"""
        return """### 9.1 환경 구성
- **Development**: 로컬 개발 환경
- **Production**: 운영 환경

### 9.2 모니터링
- 서버 상태 모니터링
- 에러 로깅 및 추적

### 9.3 백업 전략
- 데이터베이스 정기 백업
- 설정 파일 백업"""

    def _generate_roadmap_section(self) -> str:
        """로드맵 섹션 생성"""
        return """### 10.1 Phase 1 (1-3개월)
- 기본 기능 완성
- 사용자 인증 시스템 구축

### 10.2 Phase 2 (3-6개월)
- 고급 기능 구현
- 성능 최적화

### 10.3 Phase 3 (6-12개월)
- 확장 기능 추가
- 모바일 지원"""

    def _generate_kpi_section(self) -> str:
        """KPI 섹션 생성"""
        return """### 11.1 사용자 지표
- 일일 활성 사용자 (DAU)
- 월간 활성 사용자 (MAU)
- 사용자 유지율

### 11.2 비즈니스 지표
- 서비스 이용률
- 사용자 만족도
- 수익성

### 11.3 기술 지표
- API 응답 시간
- 시스템 가용성
- 에러 발생률"""

    def _generate_glossary(self) -> str:
        """용어 정의 생성"""
        return """- **API**: Application Programming Interface
- **ORM**: Object-Relational Mapping
- **JWT**: JSON Web Token
- **CORS**: Cross-Origin Resource Sharing"""

    def _generate_references(self) -> str:
        """참고 자료 생성"""
        return """- 프로젝트 관련 공식 문서
- 사용된 기술 스택 공식 문서
- 관련 표준 및 규격"""

def main():
    parser = argparse.ArgumentParser(description='범용 PRD 생성기')
    parser.add_argument('--project-root', default='.', help='프로젝트 루트 디렉토리')
    parser.add_argument('--output', default='Universal_PRD.md', help='출력 파일명')

    args = parser.parse_args()

    # 코드베이스 분석
    analyzer = UniversalCodebaseAnalyzer(args.project_root)
    analyzer.analyze_project()

    # PRD 생성
    generator = UniversalPRDGenerator(analyzer.analysis_result)
    prd_content = generator.generate_prd()

    # 파일 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(prd_content)

    print(f"✅ 범용 PRD가 {args.output}에 생성되었습니다.")
    print(f"📊 프로젝트 타입: {analyzer.analysis_result['project_type']}")
    print(f"🏢 비즈니스 도메인: {analyzer.analysis_result['business_domain']}")
    print(f"📄 파일 크기: {len(prd_content)} 문자")

if __name__ == "__main__":
    main()
