#!/usr/bin/env python3
"""
간단한 LangChain 기반 AI PRD 생성기
최신 LangChain 버전에 맞춘 간단한 구현
"""

import os
import json
import re
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

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
            'project_type': 'unknown',
            'business_domain': 'unknown',
            'confidence': 0.0
        }

    def analyze_project(self):
        """프로젝트 전체 분석"""
        self._detect_project_type()
        self._analyze_tech_stack()
        self._extract_models()
        self._extract_apis()
        self._extract_features()
        self._analyze_business_domain()
        self._calculate_confidence()

    def _detect_project_type(self):
        """프로젝트 타입 자동 감지"""
        project_type = 'unknown'
        confidence = 0.0

        if self._has_file('backend/requirements.txt') and self._has_file('frontend/package.json'):
            confidence += 0.8
            if self._has_file('backend/main.py'):
                if self._search_in_file('backend/main.py', 'FastAPI'):
                    project_type = 'fastapi_nextjs_fullstack'
                    confidence += 0.2
                else:
                    project_type = 'python_nextjs_fullstack'
            elif self._has_file('backend/app.py'):
                project_type = 'flask_nextjs_fullstack'
            else:
                project_type = 'python_nextjs_fullstack'

        elif self._has_file('package.json'):
            confidence += 0.6
            if self._has_file('next.config.js') or self._has_file('next.config.mjs'):
                project_type = 'nextjs_webapp'
                confidence += 0.3
            elif self._has_file('src/App.js') or self._has_file('src/App.jsx'):
                project_type = 'react_webapp'
                confidence += 0.2

        elif self._has_file('requirements.txt'):
            confidence += 0.7
            if self._has_file('main.py'):
                if self._search_in_file('main.py', 'FastAPI'):
                    project_type = 'fastapi_backend'
                    confidence += 0.2
                elif self._search_in_file('main.py', 'Flask'):
                    project_type = 'flask_backend'
                    confidence += 0.2
                else:
                    project_type = 'python_backend'

        self.analysis_result['project_type'] = project_type
        self.analysis_result['confidence'] = confidence

    def _analyze_tech_stack(self):
        """기술 스택 분석"""
        tech_stack = {
            'backend': {},
            'frontend': {},
            'database': {},
            'infrastructure': {}
        }

        tech_stack['backend'] = self._analyze_backend()
        tech_stack['frontend'] = self._analyze_frontend()
        tech_stack['database'] = self._analyze_database()
        tech_stack['infrastructure'] = self._analyze_infrastructure()

        self.analysis_result['tech_stack'] = tech_stack

    def _analyze_backend(self) -> Dict:
        """백엔드 분석"""
        backend_info = {
            'language': 'Unknown',
            'framework': 'Unknown',
            'dependencies': [],
            'patterns': []
        }

        if self._has_file('backend/requirements.txt') or self._has_file('requirements.txt'):
            backend_info['language'] = 'Python'
            req_file = 'backend/requirements.txt' if self._has_file('backend/requirements.txt') else 'requirements.txt'

            try:
                with open(self.project_root / req_file, 'r', encoding='utf-8') as f:
                    dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    backend_info['dependencies'] = dependencies

                    if any('fastapi' in dep.lower() for dep in dependencies):
                        backend_info['framework'] = 'FastAPI'
                    elif any('flask' in dep.lower() for dep in dependencies):
                        backend_info['framework'] = 'Flask'
                    elif any('django' in dep.lower() for dep in dependencies):
                        backend_info['framework'] = 'Django'

                    if any('sqlalchemy' in dep.lower() for dep in dependencies):
                        backend_info['patterns'].append('ORM')
                    if any('jwt' in dep.lower() or 'pyjwt' in dep.lower() for dep in dependencies):
                        backend_info['patterns'].append('JWT Authentication')
                    if any('bcrypt' in dep.lower() or 'passlib' in dep.lower() for dep in dependencies):
                        backend_info['patterns'].append('Password Hashing')
            except Exception as e:
                print(f"백엔드 분석 오류: {e}")

        return backend_info

    def _analyze_frontend(self) -> Dict:
        """프론트엔드 분석"""
        frontend_info = {
            'framework': 'Unknown',
            'ui_library': 'Unknown',
            'dependencies': [],
            'patterns': []
        }

        package_file = 'frontend/package.json' if self._has_file('frontend/package.json') else 'package.json'

        if self._has_file(package_file):
            try:
                with open(self.project_root / package_file, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    dependencies = package_data.get('dependencies', {})
                    dev_dependencies = package_data.get('devDependencies', {})
                    all_deps = {**dependencies, **dev_dependencies}

                    frontend_info['dependencies'] = list(dependencies.keys())

                    if 'next' in all_deps:
                        frontend_info['framework'] = 'Next.js'
                        frontend_info['patterns'].append('SSR/SSG')
                    elif 'react' in all_deps:
                        frontend_info['framework'] = 'React'
                        frontend_info['patterns'].append('SPA')
                    elif 'vue' in all_deps:
                        frontend_info['framework'] = 'Vue.js'
                        frontend_info['patterns'].append('SPA')
                    elif 'angular' in all_deps:
                        frontend_info['framework'] = 'Angular'
                        frontend_info['patterns'].append('SPA')

                    if 'react-bootstrap' in all_deps:
                        frontend_info['ui_library'] = 'React Bootstrap'
                    elif 'antd' in all_deps:
                        frontend_info['ui_library'] = 'Ant Design'
                    elif 'material-ui' in all_deps or '@mui/material' in all_deps:
                        frontend_info['ui_library'] = 'Material-UI'
                    elif 'bootstrap' in all_deps:
                        frontend_info['ui_library'] = 'Bootstrap'
                    elif 'tailwindcss' in all_deps:
                        frontend_info['ui_library'] = 'Tailwind CSS'

                    if 'axios' in all_deps:
                        frontend_info['patterns'].append('HTTP Client')
                    if 'redux' in all_deps or 'zustand' in all_deps:
                        frontend_info['patterns'].append('State Management')
                    if 'typescript' in all_deps:
                        frontend_info['patterns'].append('TypeScript')

            except Exception as e:
                print(f"프론트엔드 분석 오류: {e}")

        return frontend_info

    def _analyze_database(self) -> Dict:
        """데이터베이스 분석"""
        db_info = {
            'type': 'Unknown',
            'orm': 'Unknown',
            'patterns': []
        }

        config_files = [
            'backend/config.py', 'backend/settings.py', 'backend/database.py',
            'backend/app.py', 'backend/main.py', 'backend/app/core/database.py',
            'config.py', 'settings.py', 'database.py', 'app.py', 'main.py'
        ]

        for config_file in config_files:
            if self._has_file(config_file):
                try:
                    with open(self.project_root / config_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()

                        if 'postgresql' in content or 'postgres' in content:
                            db_info['type'] = 'PostgreSQL'
                        elif 'mysql' in content:
                            db_info['type'] = 'MySQL'
                        elif 'sqlite' in content:
                            db_info['type'] = 'SQLite'
                        elif 'mongodb' in content or 'mongo' in content:
                            db_info['type'] = 'MongoDB'
                        elif 'redis' in content:
                            db_info['type'] = 'Redis'

                        if 'sqlalchemy' in content:
                            db_info['orm'] = 'SQLAlchemy'
                        elif 'django' in content and 'orm' in content:
                            db_info['orm'] = 'Django ORM'
                        elif 'sequelize' in content:
                            db_info['orm'] = 'Sequelize'
                        elif 'prisma' in content:
                            db_info['orm'] = 'Prisma'

                        if 'migration' in content:
                            db_info['patterns'].append('Database Migration')
                        if 'connection' in content and 'pool' in content:
                            db_info['patterns'].append('Connection Pooling')

                except Exception as e:
                    print(f"데이터베이스 분석 오류: {e}")
                    continue

        return db_info

    def _analyze_infrastructure(self) -> Dict:
        """인프라 분석"""
        infra_info = {
            'containerization': 'None',
            'deployment': 'Unknown',
            'monitoring': 'None',
            'patterns': []
        }

        if self._has_file('Dockerfile'):
            infra_info['containerization'] = 'Docker'
            infra_info['patterns'].append('Containerization')
        elif self._has_file('docker-compose.yml') or self._has_file('docker-compose.yaml'):
            infra_info['containerization'] = 'Docker Compose'
            infra_info['patterns'].append('Multi-container')

        if self._has_file('.github/workflows'):
            infra_info['deployment'] = 'GitHub Actions'
            infra_info['patterns'].append('CI/CD')
        elif self._has_file('.gitlab-ci.yml'):
            infra_info['deployment'] = 'GitLab CI'
            infra_info['patterns'].append('CI/CD')
        elif self._has_file('Jenkinsfile'):
            infra_info['deployment'] = 'Jenkins'
            infra_info['patterns'].append('CI/CD')

        return infra_info

    def _analyze_business_domain(self):
        """비즈니스 도메인 분석"""
        domain_keywords = {
            'education': ['quiz', 'course', 'lesson', 'student', 'teacher', 'learning', 'question', 'answer', 'score', 'ranking', 'exam', 'test'],
            'ecommerce': ['shop', 'cart', 'order', 'product', 'payment', 'checkout', 'buy', 'sell', 'inventory', 'customer'],
            'social': ['user', 'post', 'comment', 'like', 'follow', 'feed', 'message', 'chat', 'friend'],
            'finance': ['account', 'transaction', 'balance', 'wallet', 'bank', 'money', 'currency', 'investment'],
            'healthcare': ['patient', 'doctor', 'appointment', 'medical', 'health', 'clinic', 'hospital', 'prescription'],
            'gaming': ['game', 'player', 'level', 'achievement', 'play', 'score', 'leaderboard', 'quest'],
            'iot': ['sensor', 'device', 'monitor', 'data', 'telemetry', 'iot', 'smart', 'automation'],
            'ai_ml': ['model', 'prediction', 'training', 'algorithm', 'neural', 'ai', 'ml', 'machine learning'],
            'cms': ['content', 'article', 'page', 'media', 'publish', 'blog', 'news', 'editor'],
            'api_service': ['api', 'service', 'endpoint', 'microservice', 'rest', 'graphql', 'webhook']
        }

        found_domains = []
        for domain, keywords in domain_keywords.items():
            score = 0
            for keyword in keywords:
                if self._search_keyword_in_files(keyword):
                    score += 1
            if score >= 2:
                found_domains.append((domain, score))

        if found_domains:
            found_domains.sort(key=lambda x: x[1], reverse=True)
            self.analysis_result['business_domain'] = found_domains[0][0]
        else:
            self.analysis_result['business_domain'] = 'web_application'

    def _extract_models(self):
        """데이터 모델 추출"""
        models = {}

        if self._has_file('backend/requirements.txt') or self._has_file('requirements.txt'):
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
                    break

        self.analysis_result['models'] = models

    def _parse_python_model(self, model_file: Path) -> Dict:
        """Python 모델 파일 파싱"""
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()

            model_info = {
                'table_name': '',
                'fields': [],
                'relationships': [],
                'patterns': []
            }

            table_match = re.search(r'__tablename__\s*=\s*["\']([^"\']+)["\']', content)
            if table_match:
                model_info['table_name'] = table_match.group(1)

            column_pattern = r'(\w+)\s*=\s*Column\([^)]+\)'
            columns = re.findall(column_pattern, content)
            model_info['fields'] = columns

            if 'relationship' in content:
                model_info['patterns'].append('ORM Relationships')
            if 'ForeignKey' in content:
                model_info['patterns'].append('Foreign Keys')
            if 'primary_key' in content:
                model_info['patterns'].append('Primary Key')

            return model_info
        except Exception as e:
            print(f"모델 파싱 오류: {e}")
            return {'table_name': '', 'fields': [], 'relationships': [], 'patterns': []}

    def _extract_apis(self):
        """API 엔드포인트 추출"""
        apis = {}

        if self._has_file('backend/requirements.txt') or self._has_file('requirements.txt'):
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
                    break

        self.analysis_result['apis'] = apis

    def _parse_python_routes(self, route_file: Path) -> List[Dict]:
        """Python 라우트 파일 파싱"""
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()

            endpoints = []

            route_pattern = r'@(?:router|app)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']\)\s*\n\s*(?:async\s+)?def\s+(\w+)'
            matches = re.findall(route_pattern, content, re.MULTILINE)

            for method, path, function_name in matches:
                endpoints.append({
                    'method': method.upper(),
                    'path': path,
                    'function_name': function_name,
                    'description': self._extract_function_docstring(content, function_name)
                })

            return endpoints
        except Exception as e:
            print(f"라우트 파싱 오류: {e}")
            return []

    def _extract_function_docstring(self, content: str, function_name: str) -> str:
        """함수 docstring 추출"""
        pattern = rf'(?:async\s+)?def\s+{function_name}[^:]*:\s*\n\s*"""(.*?)"""'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_features(self):
        """프론트엔드 기능 추출"""
        features = {}

        if self._has_file('frontend/package.json') or self._has_file('package.json'):
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
                    break

        self.analysis_result['features'] = features

    def _extract_page_description(self, page_dir: Path) -> str:
        """페이지 설명 추출"""
        page_files = ['page.js', 'page.jsx', 'page.ts', 'page.tsx', 'index.js', 'index.jsx']

        for page_file in page_files:
            if (page_dir / page_file).exists():
                try:
                    with open(page_dir / page_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'export default' in content:
                            return f"React 컴포넌트 기반 {page_dir.name} 페이지"
                        elif 'function' in content:
                            return f"JavaScript 함수 기반 {page_dir.name} 페이지"
                except Exception:
                    continue

        return f"웹 페이지: {page_dir.name}"

    def _calculate_confidence(self):
        """분석 신뢰도 계산"""
        confidence = 0.0

        if self.analysis_result['project_type'] != 'unknown':
            confidence += 0.3

        tech_stack = self.analysis_result['tech_stack']
        if tech_stack['backend'].get('framework') != 'Unknown':
            confidence += 0.2
        if tech_stack['frontend'].get('framework') != 'Unknown':
            confidence += 0.2
        if tech_stack['database'].get('type') != 'Unknown':
            confidence += 0.1
        if tech_stack['infrastructure'].get('containerization') != 'None':
            confidence += 0.1

        if self.analysis_result['models']:
            confidence += 0.1
        if self.analysis_result['apis']:
            confidence += 0.1

        self.analysis_result['confidence'] = min(confidence, 1.0)

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

    def _search_in_file(self, file_path: str, keyword: str) -> bool:
        """특정 파일에서 키워드 검색"""
        try:
            with open(self.project_root / file_path, 'r', encoding='utf-8') as f:
                return keyword.lower() in f.read().lower()
        except:
            return False

    def _has_file(self, filename: str) -> bool:
        """파일 존재 여부 확인"""
        return (self.project_root / filename).exists()

class SimpleLangChainPRDGenerator:
    """간단한 LangChain 기반 AI PRD 생성기"""

    def __init__(self, api_key: str = None):
        """AI PRD 생성기 초기화"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            print("⚠️ OpenAI API 키가 설정되지 않았습니다.")
            print("💡 OpenAI API 키를 얻으려면: https://platform.openai.com/api-keys")
            self.llm = None
        else:
            # OpenAI 모델 초기화
            self.llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                openai_api_key=self.api_key
            )

            # 프롬프트 템플릿 설정
            self.prompt_template = ChatPromptTemplate.from_messages([
                SystemMessage(content="""당신은 전문적인 제품 기획자(Product Manager)입니다.
코드베이스 분석 결과를 바탕으로 전문적이고 상세한 PRD(Product Requirements Document)를 마크다운 형식으로 생성해주세요.

중요: 템플릿이나 플레이스홀더를 사용하지 말고, 실제 구체적인 내용으로 작성해주세요.
분석된 기술 스택과 기능을 바탕으로 실제 프로젝트에 맞는 PRD를 작성해주세요.

다음 구조로 PRD를 작성하세요:

# [실제 프로젝트명] PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: 2025-09-23
- **작성자**: AI PRD Generator (LangChain + OpenAI)
- **프로젝트 타입**: [실제 프로젝트 타입]
- **비즈니스 도메인**: [실제 비즈니스 도메인]
- **분석 신뢰도**: [실제 신뢰도]

## 🎯 1. 제품 개요
### 1.1 제품명
[실제 제품명]

### 1.2 제품 비전
[구체적이고 매력적인 실제 비전]

### 1.3 핵심 가치
- **[실제 가치1]**: [구체적 설명]
- **[실제 가치2]**: [구체적 설명]
- **[실제 가치3]**: [구체적 설명]
- **[실제 가치4]**: [구체적 설명]

### 1.4 타겟 사용자
[구체적인 실제 사용자 그룹과 니즈]

## 🏗️ 2. 기술 아키텍처
[현재 기술 스택의 실제 장단점과 확장성에 대한 구체적 설명]

## ⚙️ 3. 핵심 기능
### 3.1 [실제 기능1]
[상세한 실제 설명과 우선순위]

### 3.2 [실제 기능2]
[상세한 실제 설명과 우선순위]

### 3.3 [실제 기능3]
[상세한 실제 설명과 우선순위]

### 3.4 [실제 기능4]
[상세한 실제 설명과 우선순위]

### 3.5 [실제 기능5]
[상세한 실제 설명과 우선순위]

## 🔒 4. 보안 요구사항
- [구체적인 실제 보안 조치1]
- [구체적인 실제 보안 조치2]
- [구체적인 실제 보안 조치3]

## 📈 5. 성능 요구사항
- [측정 가능한 실제 성능 지표1]
- [측정 가능한 실제 성능 지표2]
- [측정 가능한 실제 성능 지표3]

## 🚀 6. 배포 전략
[단계별 실제 배포 계획]

## 📅 7. 개발 로드맵
### 7.1 Phase 1 (1-3개월)
[실제 목표와 기간]

### 7.2 Phase 2 (3-6개월)
[실제 목표와 기간]

### 7.3 Phase 3 (6-12개월)
[실제 목표와 기간]

## 📊 8. 성공 지표 (KPI)
- [실제 KPI1]: [실제 측정 방법]
- [실제 KPI2]: [실제 측정 방법]
- [실제 KPI3]: [실제 측정 방법]

각 섹션은 구체적이고 실행 가능한 실제 내용으로 작성하되, 기술적이면서도 비즈니스 관점에서 이해하기 쉽게 작성해주세요."""),
                HumanMessage(content="""다음 코드베이스 분석 결과를 바탕으로 구체적인 PRD를 생성해주세요:

프로젝트 정보:
- 프로젝트 타입: {project_type}
- 비즈니스 도메인: {business_domain}
- 분석 신뢰도: {confidence}

기술 스택:
백엔드: {backend_info}
프론트엔드: {frontend_info}
데이터베이스: {database_info}
인프라: {infrastructure_info}

데이터 모델: {models_info}
API 엔드포인트: {apis_info}
프론트엔드 기능: {features_info}

위 정보를 바탕으로 실제 구체적인 내용으로 PRD를 작성해주세요.
템플릿이나 플레이스홀더([실제 프로젝트명] 등)를 사용하지 말고,
실제 프로젝트명, 기능명, 요구사항 등을 구체적으로 작성해주세요.""")
            ])

    def generate_prd(self, analysis_result: Dict) -> str:
        """AI를 사용하여 PRD 생성"""
        if not self.llm:
            return self._generate_fallback_prd(analysis_result)

        try:
            # 분석 결과를 문자열로 변환
            formatted_data = self._format_analysis_data(analysis_result)

            # 프롬프트 생성
            prompt = self.prompt_template.format_messages(
                project_type=analysis_result.get('project_type', 'unknown'),
                business_domain=analysis_result.get('business_domain', 'unknown'),
                confidence=f"{analysis_result.get('confidence', 0.0):.1%}",
                backend_info=formatted_data['backend'],
                frontend_info=formatted_data['frontend'],
                database_info=formatted_data['database'],
                infrastructure_info=formatted_data['infrastructure'],
                models_info=formatted_data['models'],
                apis_info=formatted_data['apis'],
                features_info=formatted_data['features']
            )

            # AI를 사용하여 PRD 생성
            response = self.llm.invoke(prompt)

            # 생성된 PRD 반환
            return response.content

        except Exception as e:
            print(f"AI PRD 생성 오류: {e}")
            return self._generate_fallback_prd(analysis_result)

    def _format_analysis_data(self, analysis_result: Dict) -> Dict:
        """분석 결과를 AI 프롬프트용으로 포맷팅"""
        tech_stack = analysis_result.get('tech_stack', {})

        return {
            'backend': f"언어: {tech_stack.get('backend', {}).get('language', 'Unknown')}, 프레임워크: {tech_stack.get('backend', {}).get('framework', 'Unknown')}, 패턴: {', '.join(tech_stack.get('backend', {}).get('patterns', []))}",
            'frontend': f"프레임워크: {tech_stack.get('frontend', {}).get('framework', 'Unknown')}, UI 라이브러리: {tech_stack.get('frontend', {}).get('ui_library', 'Unknown')}, 패턴: {', '.join(tech_stack.get('frontend', {}).get('patterns', []))}",
            'database': f"타입: {tech_stack.get('database', {}).get('type', 'Unknown')}, ORM: {tech_stack.get('database', {}).get('orm', 'Unknown')}, 패턴: {', '.join(tech_stack.get('database', {}).get('patterns', []))}",
            'infrastructure': f"컨테이너화: {tech_stack.get('infrastructure', {}).get('containerization', 'None')}, 배포: {tech_stack.get('infrastructure', {}).get('deployment', 'Unknown')}, 모니터링: {tech_stack.get('infrastructure', {}).get('monitoring', 'None')}",
            'models': str(analysis_result.get('models', {})),
            'apis': str(analysis_result.get('apis', {})),
            'features': str(analysis_result.get('features', {}))
        }

    def _generate_fallback_prd(self, analysis_result: Dict) -> str:
        """AI를 사용할 수 없을 때 폴백 PRD 생성"""
        current_date = datetime.now().strftime('%Y-%m-%d')

        return f"""# Coding Quiz Platform PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: {current_date}
- **작성자**: Simple LangChain PRD Generator (Fallback Mode)
- **마지막 수정**: {current_date}
- **프로젝트 타입**: {analysis_result.get('project_type', 'unknown')}
- **비즈니스 도메인**: {analysis_result.get('business_domain', 'unknown')}
- **분석 신뢰도**: {analysis_result.get('confidence', 0.0):.1%}

## ⚠️ AI 모드 비활성화
OpenAI API 키가 설정되지 않아 기본 PRD 템플릿을 사용합니다.
AI 기반 PRD 생성을 위해서는 OpenAI API 키를 설정해주세요.

## 🎯 1. 제품 개요
### 1.1 제품명
Coding Quiz Platform

### 1.2 제품 비전
학습자 중심의 교육 플랫폼으로 효과적인 학습 경험을 제공합니다.

### 1.3 핵심 가치
- **사용자 중심**: 사용자 경험을 최우선으로 고려
- **안정성**: 안정적이고 신뢰할 수 있는 서비스 제공
- **확장성**: 미래 성장에 대비한 확장 가능한 아키텍처
- **보안**: 사용자 데이터와 시스템의 보안 보장

### 1.4 타겟 사용자
학습자, 교육자, 교육 기관

## 🏗️ 2. 기술 스택
### 2.1 백엔드
- **Language**: Python
- **Framework**: FastAPI
- **Patterns**: ORM, JWT Authentication, Password Hashing

### 2.2 프론트엔드
- **Framework**: Next.js
- **UI Library**: React Bootstrap
- **Patterns**: SSR/SSG, HTTP Client

### 2.3 데이터베이스
- **Type**: PostgreSQL
- **ORM**: SQLAlchemy

## ⚙️ 3. 핵심 기능
### 3.1 사용자 인증 시스템
- JWT 기반 사용자 인증 및 권한 관리

### 3.2 퀴즈 시스템
- 카테고리별 퀴즈 제공 및 실시간 채점

### 3.3 랭킹 시스템
- 사용자별 점수 기반 랭킹 제공

### 3.4 콘텐츠 관리 시스템
- CSV 파일 기반 문제 데이터 관리

## 🔒 4. 보안 요구사항
- JWT 토큰 기반 인증
- 비밀번호 해싱
- SQL Injection 방지
- XSS 방지
- CORS 정책 적용

## 📈 5. 성능 요구사항
- API 응답 시간: 200ms 이하
- 페이지 로딩 시간: 2초 이하
- 동시 사용자: 100명 이상 지원

## 🚀 6. 배포 전략
- Docker 컨테이너화
- 환경별 설정 분리
- CI/CD 파이프라인 구축

## 📅 7. 개발 로드맵
### 7.1 Phase 1 (1-3개월)
- 기본 퀴즈 기능 완성
- 사용자 인증 시스템 구축

### 7.2 Phase 2 (3-6개월)
- 랭킹 시스템 구현
- 성능 최적화

### 7.3 Phase 3 (6-12개월)
- 고급 기능 추가
- 모바일 지원

## 📊 8. 성공 지표 (KPI)
- 일일 활성 사용자 (DAU)
- 월간 활성 사용자 (MAU)
- 사용자 유지율
- 퀴즈 완료율
- 평균 세션 시간

## 💡 AI 기능 활성화 방법
1. OpenAI API 키 발급: https://platform.openai.com/api-keys
2. 환경변수 설정: `export OPENAI_API_KEY='your-api-key-here'`
3. 또는 명령어 옵션: `--api-key your-api-key-here`
"""

def main():
    parser = argparse.ArgumentParser(description='간단한 LangChain 기반 AI PRD 생성기')
    parser.add_argument('--project-root', default='.', help='프로젝트 루트 디렉토리')
    parser.add_argument('--output', default='Simple_LangChain_PRD.md', help='출력 파일명')
    parser.add_argument('--api-key', help='OpenAI API 키')

    args = parser.parse_args()

    # 코드베이스 분석
    analyzer = CodebaseAnalyzer(args.project_root)
    analyzer.analyze_project()

    # AI PRD 생성
    ai_generator = SimpleLangChainPRDGenerator(args.api_key)
    prd_content = ai_generator.generate_prd(analyzer.analysis_result)

    # 파일 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(prd_content)

    print(f"✅ 간단한 LangChain AI PRD가 {args.output}에 생성되었습니다.")
    print(f"📊 프로젝트 타입: {analyzer.analysis_result['project_type']}")
    print(f"🏢 비즈니스 도메인: {analyzer.analysis_result['business_domain']}")
    print(f"🎯 분석 신뢰도: {analyzer.analysis_result['confidence']:.1%}")
    print(f"📄 파일 크기: {len(prd_content)} 문자")

    if not ai_generator.api_key:
        print("\n💡 AI 기능을 사용하려면 OpenAI API 키를 설정하세요:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   또는 --api-key 옵션을 사용하세요.")

if __name__ == "__main__":
    main()
