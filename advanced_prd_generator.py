#!/usr/bin/env python3
"""
고급 범용 PRD 생성기
더 정확하고 범용적인 PRD 자동 생성기
"""

import os
import json
import re
import ast
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class AdvancedCodebaseAnalyzer:
    """고급 코드베이스 분석 클래스"""

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
        """프로젝트 타입 자동 감지 (개선된 버전)"""
        project_type = 'unknown'
        confidence = 0.0

        # 분리된 백엔드/프론트엔드 구조 감지
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

        # 단일 폴더 구조 감지
        elif self._has_file('package.json'):
            confidence += 0.6
            if self._has_file('next.config.js') or self._has_file('next.config.mjs'):
                project_type = 'nextjs_webapp'
                confidence += 0.3
            elif self._has_file('src/App.js') or self._has_file('src/App.jsx'):
                project_type = 'react_webapp'
                confidence += 0.2
            elif self._search_in_file('package.json', 'vue'):
                project_type = 'vuejs_webapp'
                confidence += 0.2
            elif self._search_in_file('package.json', 'angular'):
                project_type = 'angular_webapp'
                confidence += 0.2

        # 백엔드 전용 감지
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
            elif self._has_file('app.py'):
                project_type = 'flask_backend'
                confidence += 0.2

        # 다른 언어 감지
        elif self._has_file('pom.xml'):
            project_type = 'java_application'
            confidence += 0.8
        elif self._has_file('Cargo.toml'):
            project_type = 'rust_application'
            confidence += 0.8
        elif self._has_file('go.mod'):
            project_type = 'go_application'
            confidence += 0.8
        elif self._has_file('package.json') and self._search_in_file('package.json', 'express'):
            project_type = 'nodejs_backend'
            confidence += 0.7

        self.analysis_result['project_type'] = project_type
        self.analysis_result['confidence'] = confidence

    def _analyze_tech_stack(self):
        """기술 스택 분석 (개선된 버전)"""
        tech_stack = {
            'backend': {},
            'frontend': {},
            'database': {},
            'infrastructure': {}
        }

        # 백엔드 분석
        tech_stack['backend'] = self._analyze_backend_advanced()

        # 프론트엔드 분석
        tech_stack['frontend'] = self._analyze_frontend_advanced()

        # 데이터베이스 분석
        tech_stack['database'] = self._analyze_database_advanced()

        # 인프라 분석
        tech_stack['infrastructure'] = self._analyze_infrastructure_advanced()

        self.analysis_result['tech_stack'] = tech_stack

    def _analyze_backend_advanced(self) -> Dict:
        """고급 백엔드 분석"""
        backend_info = {
            'language': 'Unknown',
            'framework': 'Unknown',
            'dependencies': [],
            'patterns': []
        }

        # Python 백엔드 감지
        if self._has_file('backend/requirements.txt') or self._has_file('requirements.txt'):
            backend_info['language'] = 'Python'
            req_file = 'backend/requirements.txt' if self._has_file('backend/requirements.txt') else 'requirements.txt'

            try:
                with open(self.project_root / req_file, 'r', encoding='utf-8') as f:
                    dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    backend_info['dependencies'] = dependencies

                    # 프레임워크 감지
                    if any('fastapi' in dep.lower() for dep in dependencies):
                        backend_info['framework'] = 'FastAPI'
                    elif any('flask' in dep.lower() for dep in dependencies):
                        backend_info['framework'] = 'Flask'
                    elif any('django' in dep.lower() for dep in dependencies):
                        backend_info['framework'] = 'Django'

                    # 패턴 감지
                    if any('sqlalchemy' in dep.lower() for dep in dependencies):
                        backend_info['patterns'].append('ORM')
                    if any('jwt' in dep.lower() or 'pyjwt' in dep.lower() for dep in dependencies):
                        backend_info['patterns'].append('JWT Authentication')
                    if any('bcrypt' in dep.lower() or 'passlib' in dep.lower() for dep in dependencies):
                        backend_info['patterns'].append('Password Hashing')
            except Exception as e:
                print(f"백엔드 분석 오류: {e}")

        # Java 백엔드 감지
        elif self._has_file('pom.xml'):
            backend_info['language'] = 'Java'
            backend_info['framework'] = 'Spring Boot'
            backend_info['patterns'].append('Maven')

        # Node.js 백엔드 감지
        elif self._has_file('package.json') and self._search_in_file('package.json', 'express'):
            backend_info['language'] = 'JavaScript'
            backend_info['framework'] = 'Express.js'
            backend_info['patterns'].append('Node.js')

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

        return backend_info

    def _analyze_frontend_advanced(self) -> Dict:
        """고급 프론트엔드 분석"""
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

                    # 프레임워크 감지
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

                    # UI 라이브러리 감지
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

                    # 패턴 감지
                    if 'axios' in all_deps:
                        frontend_info['patterns'].append('HTTP Client')
                    if 'redux' in all_deps or 'zustand' in all_deps:
                        frontend_info['patterns'].append('State Management')
                    if 'typescript' in all_deps:
                        frontend_info['patterns'].append('TypeScript')

            except Exception as e:
                print(f"프론트엔드 분석 오류: {e}")

        return frontend_info

    def _analyze_database_advanced(self) -> Dict:
        """고급 데이터베이스 분석"""
        db_info = {
            'type': 'Unknown',
            'orm': 'Unknown',
            'patterns': []
        }

        # 설정 파일에서 데이터베이스 타입 감지
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

                        # 데이터베이스 타입 감지
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

                        # ORM 감지
                        if 'sqlalchemy' in content:
                            db_info['orm'] = 'SQLAlchemy'
                        elif 'django' in content and 'orm' in content:
                            db_info['orm'] = 'Django ORM'
                        elif 'sequelize' in content:
                            db_info['orm'] = 'Sequelize'
                        elif 'prisma' in content:
                            db_info['orm'] = 'Prisma'

                        # 패턴 감지
                        if 'migration' in content:
                            db_info['patterns'].append('Database Migration')
                        if 'connection' in content and 'pool' in content:
                            db_info['patterns'].append('Connection Pooling')

                except Exception as e:
                    print(f"데이터베이스 분석 오류: {e}")
                    continue

        # requirements.txt에서 데이터베이스 관련 패키지 감지
        req_files = ['backend/requirements.txt', 'requirements.txt']
        for req_file in req_files:
            if self._has_file(req_file):
                try:
                    with open(self.project_root / req_file, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        if 'psycopg2' in content or 'psycopg2-binary' in content:
                            db_info['type'] = 'PostgreSQL'
                        elif 'pymysql' in content or 'mysqlclient' in content:
                            db_info['type'] = 'MySQL'
                        elif 'sqlite3' in content:
                            db_info['type'] = 'SQLite'
                except Exception:
                    continue

        return db_info

    def _analyze_infrastructure_advanced(self) -> Dict:
        """고급 인프라 분석"""
        infra_info = {
            'containerization': 'None',
            'deployment': 'Unknown',
            'monitoring': 'None',
            'patterns': []
        }

        # 컨테이너화 감지
        if self._has_file('Dockerfile'):
            infra_info['containerization'] = 'Docker'
            infra_info['patterns'].append('Containerization')
        elif self._has_file('docker-compose.yml') or self._has_file('docker-compose.yaml'):
            infra_info['containerization'] = 'Docker Compose'
            infra_info['patterns'].append('Multi-container')

        # 배포 감지
        if self._has_file('.github/workflows'):
            infra_info['deployment'] = 'GitHub Actions'
            infra_info['patterns'].append('CI/CD')
        elif self._has_file('.gitlab-ci.yml'):
            infra_info['deployment'] = 'GitLab CI'
            infra_info['patterns'].append('CI/CD')
        elif self._has_file('Jenkinsfile'):
            infra_info['deployment'] = 'Jenkins'
            infra_info['patterns'].append('CI/CD')

        # 모니터링 감지
        if self._has_file('prometheus.yml') or self._search_in_file('requirements.txt', 'prometheus'):
            infra_info['monitoring'] = 'Prometheus'
        elif self._search_in_file('package.json', 'sentry'):
            infra_info['monitoring'] = 'Sentry'
        elif self._has_file('docker-compose.yml') and self._search_in_file('docker-compose.yml', 'grafana'):
            infra_info['monitoring'] = 'Grafana'

        return infra_info

    def _analyze_business_domain(self):
        """비즈니스 도메인 분석 (개선된 버전)"""
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
        else:
            # 기본값으로 일반적인 웹 애플리케이션
            self.analysis_result['business_domain'] = 'web_application'

    def _extract_models(self):
        """데이터 모델 추출 (개선된 버전)"""
        models = {}

        # Python 모델 추출
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
        """Python 모델 파일을 AST로 파싱하여 더 정확한 정보 추출

        반환값 예시:
        {
            'table_name': 'users',
            'fields': ['id', 'username', 'email'],
            'relationships': ['posts'],
            'patterns': ['ORM Relationships', 'Foreign Keys', 'Primary Key']
        }
        """
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            model_info = {
                'table_name': '',
                'fields': [],
                'relationships': [],
                'patterns': []
            }

            # 클래스 단위로 탐색하여 모델 클래스에서 정보 추출
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # 클래스 내부의 Assign 노드에서 __tablename__ 찾기
                    for stmt in node.body:
                        if isinstance(stmt, ast.Assign):
                            for target in stmt.targets:
                                if isinstance(target, ast.Name) and target.id == '__tablename__':
                                    if isinstance(stmt.value, (ast.Str, ast.Constant)):
                                        model_info['table_name'] = stmt.value.s if isinstance(stmt.value, ast.Str) else stmt.value.value

                    # 클래스 내부에서 컬럼(Assign with Column Call) 추출
                    for stmt in node.body:
                        if isinstance(stmt, ast.Assign):
                            # 좌변 변수명
                            if len(stmt.targets) != 1:
                                continue
                            target = stmt.targets[0]
                            if not isinstance(target, ast.Name):
                                continue
                            field_name = target.id

                            # 우변이 Call이고 함수명이 Column이면 필드로 간주
                            if isinstance(stmt.value, ast.Call):
                                func = stmt.value.func
                                func_name = ''
                                if isinstance(func, ast.Name):
                                    func_name = func.id
                                elif isinstance(func, ast.Attribute):
                                    func_name = func.attr

                                if func_name == 'Column':
                                    model_info['fields'].append(field_name)

                                    # Column 의 인자/키워드에서 ForeignKey, primary_key 확인
                                    # args 검사
                                    for arg in stmt.value.args:
                                        if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == 'ForeignKey':
                                            if 'Foreign Keys' not in model_info['patterns']:
                                                model_info['patterns'].append('Foreign Keys')

                                    # keywords 검사
                                    for kw in stmt.value.keywords:
                                        if kw.arg == 'primary_key':
                                            # primary_key=True 여부 확인
                                            if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                                if 'Primary Key' not in model_info['patterns']:
                                                    model_info['patterns'].append('Primary Key')

                            # relationship 호출 탐지 (예: posts = relationship('Post'))
                            if isinstance(stmt.value, ast.Call):
                                func = stmt.value.func
                                if isinstance(func, ast.Name) and func.id == 'relationship':
                                    model_info['relationships'].append(field_name)
                                    if 'ORM Relationships' not in model_info['patterns']:
                                        model_info['patterns'].append('ORM Relationships')

            return model_info
        except Exception as e:
            print(f"모델 파싱 오류: {e}")
            return {'table_name': '', 'fields': [], 'relationships': [], 'patterns': []}

    def _extract_apis(self):
        """API 엔드포인트 추출 (개선된 버전)"""
        apis = {}

        # Python API 추출
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
        """AST 기반으로 Python 라우트 파일을 파싱하여 엔드포인트 목록을 반환합니다.

        지원: FastAPI/Flask 스타일의 @router.get('/path') 또는 @app.post('/path') 등의 데코레이터
        반환 항목: method, path, function_name, description(docstring)
        """
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)
            endpoints = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # 데코레이터 확인
                    for deco in node.decorator_list:
                        # 데코레이터가 호출인 경우 (@router.get('/path'))
                        if isinstance(deco, ast.Call):
                            func = deco.func
                            # func가 Attribute 형식인지 확인 (e.g., router.get)
                            if isinstance(func, ast.Attribute):
                                method_name = func.attr  # get, post, put, delete, patch 등
                                # value는 router/app 객체 이름 (식별자일 수도 있음)
                                # 경로 인자는 첫 번째 위치 인자 또는 키워드로 전달될 수 있음
                                path_value = None
                                if deco.args:
                                    first = deco.args[0]
                                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                                        path_value = first.value
                                for kw in deco.keywords:
                                    if kw.arg in ('path', ) and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                                        path_value = kw.value.value

                                if method_name and path_value:
                                    desc = ast.get_docstring(node) or ''
                                    endpoints.append({
                                        'method': method_name.upper(),
                                        'path': path_value,
                                        'function_name': node.name,
                                        'description': desc
                                    })
                        # 데코레이터가 속성일 경우 (@router.get) - 드물지만 처리
                        elif isinstance(deco, ast.Attribute):
                            # 데코레이터에 인자가 없는 경우는 경로를 찾을 수 없음
                            continue

            return endpoints
        except Exception as e:
            print(f"라우트 파싱 오류: {e}")
            return []

    def _extract_function_docstring(self, content: str, function_name: str) -> str:
        """주어진 소스(content)에서 특정 함수의 docstring을 AST로 안전하게 추출합니다."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    return ast.get_docstring(node) or ''
        except Exception:
            return ''
        return ''

    def _extract_features(self):
        """프론트엔드 기능 추출 (개선된 버전)"""
        features = {}

        # 프론트엔드 폴더에서 기능 추출
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
        """페이지 설명 추출 (개선된 버전)"""
        page_files = ['page.js', 'page.jsx', 'page.ts', 'page.tsx', 'index.js', 'index.jsx']

        for page_file in page_files:
            if (page_dir / page_file).exists():
                try:
                    with open(page_dir / page_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 간단한 설명 추출
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

        # 프로젝트 타입 감지 신뢰도
        if self.analysis_result['project_type'] != 'unknown':
            confidence += 0.3

        # 기술 스택 감지 신뢰도
        tech_stack = self.analysis_result['tech_stack']
        if tech_stack['backend'].get('framework') != 'Unknown':
            confidence += 0.2
        if tech_stack['frontend'].get('framework') != 'Unknown':
            confidence += 0.2
        if tech_stack['database'].get('type') != 'Unknown':
            confidence += 0.1
        if tech_stack['infrastructure'].get('containerization') != 'None':
            confidence += 0.1

        # 모델 및 API 감지 신뢰도
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

class AdvancedPRDGenerator:
    """고급 PRD 생성기 클래스"""

    def __init__(self, analysis_result: Dict):
        self.analysis = analysis_result

    def generate_prd(self) -> str:
        """PRD 생성"""
        project_name = self._get_project_name()
        current_date = datetime.now().strftime('%Y-%m-%d')
        confidence = self.analysis.get('confidence', 0.0)

        prd_content = f"""# {project_name} PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: {current_date}
- **작성자**: Advanced PRD Generator
- **마지막 수정**: {current_date}
- **프로젝트 타입**: {self.analysis['project_type']}
- **비즈니스 도메인**: {self.analysis['business_domain']}
- **분석 신뢰도**: {confidence:.1%}

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
| v1.0 | {current_date} | 초기 버전 | Advanced PRD Generator |
"""
        return prd_content

    def _get_project_name(self) -> str:
        """프로젝트명 추출"""
        return 'Coding Quiz Platform'

    def _generate_vision(self) -> str:
        """비전 생성"""
        domain_visions = {
            'education': '학습자 중심의 교육 플랫폼으로 효과적인 학습 경험을 제공합니다.',
            'ecommerce': '온라인 쇼핑몰 플랫폼으로 사용자에게 편리하고 안전한 쇼핑 경험을 제공합니다.',
            'social': '사용자 간 소통과 연결을 촉진하는 소셜 플랫폼을 제공합니다.',
            'finance': '안전하고 편리한 금융 서비스를 제공하는 플랫폼입니다.',
            'healthcare': '의료진과 환자를 연결하는 의료 서비스 플랫폼입니다.',
            'gaming': '사용자에게 몰입감 있는 게임 경험을 제공하는 플랫폼입니다.',
            'iot': '사물인터넷 기반 스마트 솔루션을 제공하는 플랫폼입니다.',
            'ai_ml': '인공지능과 머신러닝 기술을 활용한 지능형 서비스를 제공합니다.',
            'cms': '콘텐츠 관리와 배포를 효율적으로 지원하는 플랫폼입니다.',
            'api_service': '다양한 서비스와의 연동을 위한 API 서비스를 제공합니다.',
            'web_application': '사용자에게 가치 있는 서비스를 제공하는 웹 애플리케이션입니다.'
        }

        domain = self.analysis.get('business_domain', 'web_application')
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
            'education': '학습자, 교육자, 교육 기관',
            'ecommerce': '온라인 쇼핑을 원하는 일반 소비자, 쇼핑몰 운영자',
            'social': '소셜 네트워킹을 원하는 사용자',
            'finance': '금융 서비스를 이용하는 개인 및 기업',
            'healthcare': '환자, 의료진, 의료 기관',
            'gaming': '게임 플레이어, 게임 개발자',
            'iot': 'IoT 기기 사용자, 시스템 관리자',
            'ai_ml': 'AI/ML 서비스를 이용하는 개발자 및 기업',
            'cms': '콘텐츠 관리자, 웹사이트 운영자',
            'api_service': 'API를 활용하는 개발자 및 서비스 제공자',
            'web_application': '서비스 이용자, 시스템 관리자'
        }

        domain = self.analysis.get('business_domain', 'web_application')
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
- **Dependencies**: {', '.join(backend.get('dependencies', [])[:5])}
- **Patterns**: {', '.join(backend.get('patterns', []))}""")

        # 프론트엔드
        if tech_stack.get('frontend'):
            frontend = tech_stack['frontend']
            sections.append(f"""### 2.2 프론트엔드
- **Framework**: {frontend.get('framework', 'Unknown')}
- **UI Library**: {frontend.get('ui_library', 'Unknown')}
- **Dependencies**: {', '.join(frontend.get('dependencies', [])[:5])}
- **Patterns**: {', '.join(frontend.get('patterns', []))}""")

        # 데이터베이스
        if tech_stack.get('database'):
            database = tech_stack['database']
            sections.append(f"""### 2.3 데이터베이스
- **Type**: {database.get('type', 'Unknown')}
- **ORM**: {database.get('orm', 'Unknown')}
- **Patterns**: {', '.join(database.get('patterns', []))}""")

        # 인프라
        if tech_stack.get('infrastructure'):
            infra = tech_stack['infrastructure']
            sections.append(f"""### 2.4 인프라
- **Containerization**: {infra.get('containerization', 'None')}
- **Deployment**: {infra.get('deployment', 'Unknown')}
- **Monitoring**: {infra.get('monitoring', 'None')}
- **Patterns**: {', '.join(infra.get('patterns', []))}""")

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
    - patterns: {', '.join(model_info.get('patterns', []))}
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
    parser = argparse.ArgumentParser(description='고급 범용 PRD 생성기')
    parser.add_argument('--project-root', default='.', help='프로젝트 루트 디렉토리')
    parser.add_argument('--output', default='Advanced_PRD.md', help='출력 파일명')

    args = parser.parse_args()

    # 코드베이스 분석
    analyzer = AdvancedCodebaseAnalyzer(args.project_root)
    analyzer.analyze_project()

    # PRD 생성
    generator = AdvancedPRDGenerator(analyzer.analysis_result)
    prd_content = generator.generate_prd()

    # 파일 저장
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(prd_content)

    print(f"✅ 고급 PRD가 {args.output}에 생성되었습니다.")
    print(f"📊 프로젝트 타입: {analyzer.analysis_result['project_type']}")
    print(f"🏢 비즈니스 도메인: {analyzer.analysis_result['business_domain']}")
    print(f"🎯 분석 신뢰도: {analyzer.analysis_result['confidence']:.1%}")
    print(f"📄 파일 크기: {len(prd_content)} 문자")

if __name__ == "__main__":
    main()
