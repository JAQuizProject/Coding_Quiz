#!/usr/bin/env python3
"""
GitHub API를 사용하여 원격 저장소를 분석하는 스크립트
"""

import requests
import json
import os
from pathlib import Path
import tempfile
import zipfile
import io

def analyze_github_repo_with_api(repo_url: str, github_token: str = None):
    """
    GitHub API를 사용하여 저장소를 분석하는 함수
    
    Args:
        repo_url: GitHub 저장소 URL (예: https://github.com/user/repo)
        github_token: GitHub Personal Access Token (선택사항)
    """
    
    print(f"🌐 GitHub API로 저장소를 분석합니다: {repo_url}")
    
    # URL에서 owner와 repo 추출
    if not repo_url.startswith('https://github.com/'):
        print("❌ GitHub URL 형식이 올바르지 않습니다.")
        return False
    
    parts = repo_url.replace('https://github.com/', '').split('/')
    if len(parts) < 2:
        print("❌ GitHub URL 형식이 올바르지 않습니다.")
        return False
    
    owner, repo = parts[0], parts[1]
    
    # GitHub API 헤더 설정
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'AI-PRD-Generator'
    }
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
    
    try:
        # 저장소 정보 가져오기
        print("📡 저장소 정보를 가져오는 중...")
        repo_response = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}',
            headers=headers,
            timeout=30
        )
        
        if repo_response.status_code != 200:
            print(f"❌ 저장소 정보 가져오기 실패: {repo_response.status_code}")
            return False
        
        repo_data = repo_response.json()
        
        print(f"✅ 저장소 정보:")
        print(f"   이름: {repo_data['name']}")
        print(f"   설명: {repo_data['description'] or '설명 없음'}")
        print(f"   언어: {repo_data['language'] or '언어 정보 없음'}")
        print(f"   별표: {repo_data['stargazers_count']}")
        print(f"   포크: {repo_data['forks_count']}")
        
        # 저장소 내용 가져오기
        print("📁 저장소 구조를 분석하는 중...")
        contents_response = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/contents',
            headers=headers,
            timeout=30
        )
        
        if contents_response.status_code != 200:
            print(f"❌ 저장소 내용 가져오기 실패: {contents_response.status_code}")
            return False
        
        contents = contents_response.json()
        
        # 파일 구조 분석
        analyze_repo_structure(contents, repo_data)
        
        # 주요 파일 내용 가져오기
        key_files = ['package.json', 'requirements.txt', 'pom.xml', 'go.mod', 'Cargo.toml', 'README.md']
        project_info = {}
        
        for file_info in contents:
            if file_info['name'] in key_files and file_info['type'] == 'file':
                print(f"📄 {file_info['name']} 파일을 분석하는 중...")
                
                file_response = requests.get(file_info['download_url'], timeout=30)
                if file_response.status_code == 200:
                    project_info[file_info['name']] = file_response.text
                    print(f"✅ {file_info['name']} 분석 완료")
        
        # 프로젝트 타입 추정
        project_type = estimate_project_type_from_files(project_info)
        print(f"🎯 추정 프로젝트 타입: {project_type}")
        
        # 비즈니스 도메인 추정
        business_domain = estimate_business_domain(repo_data, project_info)
        print(f"🏢 추정 비즈니스 도메인: {business_domain}")
        
        # AI PRD 생성
        generate_prd_from_github_data(repo_data, project_info, project_type, business_domain)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def analyze_repo_structure(contents: list, repo_data: dict):
    """저장소 구조 분석"""
    
    print(f"\n📁 저장소 구조:")
    
    files = [item['name'] for item in contents if item['type'] == 'file']
    dirs = [item['name'] for item in contents if item['type'] == 'dir']
    
    print(f"📄 파일: {', '.join(files[:10])}")
    if len(files) > 10:
        print(f"   ... 및 {len(files) - 10}개 더")
    
    print(f"📂 디렉토리: {', '.join(dirs[:10])}")
    if len(dirs) > 10:
        print(f"   ... 및 {len(dirs) - 10}개 더")

def estimate_project_type_from_files(project_info: dict) -> str:
    """파일 정보로부터 프로젝트 타입 추정"""
    
    if 'package.json' in project_info and 'requirements.txt' in project_info:
        return "풀스택 웹 애플리케이션 (Node.js + Python)"
    elif 'package.json' in project_info:
        package_json = json.loads(project_info['package.json'])
        dependencies = package_json.get('dependencies', {})
        
        if 'next' in dependencies:
            return "Next.js 웹 애플리케이션"
        elif 'react' in dependencies:
            return "React 웹 애플리케이션"
        elif 'vue' in dependencies:
            return "Vue.js 웹 애플리케이션"
        elif 'angular' in dependencies:
            return "Angular 웹 애플리케이션"
        else:
            return "Node.js 프로젝트"
    elif 'requirements.txt' in project_info:
        requirements = project_info['requirements.txt'].lower()
        
        if 'fastapi' in requirements:
            return "FastAPI 웹 애플리케이션"
        elif 'django' in requirements:
            return "Django 웹 애플리케이션"
        elif 'flask' in requirements:
            return "Flask 웹 애플리케이션"
        else:
            return "Python 프로젝트"
    elif 'pom.xml' in project_info:
        return "Java/Maven 프로젝트"
    elif 'go.mod' in project_info:
        return "Go 프로젝트"
    elif 'Cargo.toml' in project_info:
        return "Rust 프로젝트"
    else:
        return "알 수 없는 프로젝트 타입"

def estimate_business_domain(repo_data: dict, project_info: dict) -> str:
    """비즈니스 도메인 추정"""
    
    # 저장소 설명과 이름에서 키워드 추출
    text_to_analyze = f"{repo_data['name']} {repo_data['description'] or ''}"
    text_to_analyze = text_to_analyze.lower()
    
    # README 내용도 분석
    if 'README.md' in project_info:
        text_to_analyze += f" {project_info['README.md'].lower()}"
    
    domain_keywords = {
        'education': ['quiz', 'course', 'lesson', 'student', 'teacher', 'learning', 'education', 'school'],
        'ecommerce': ['shop', 'cart', 'order', 'product', 'payment', 'checkout', 'buy', 'sell'],
        'social': ['user', 'post', 'comment', 'like', 'follow', 'feed', 'message', 'chat'],
        'finance': ['account', 'transaction', 'balance', 'wallet', 'bank', 'money', 'payment'],
        'healthcare': ['patient', 'doctor', 'medical', 'health', 'clinic', 'hospital'],
        'gaming': ['game', 'player', 'level', 'achievement', 'play', 'score'],
        'iot': ['sensor', 'device', 'iot', 'smart', 'automation'],
        'ai_ml': ['model', 'prediction', 'training', 'algorithm', 'ai', 'ml', 'machine learning'],
        'cms': ['content', 'article', 'page', 'media', 'publish', 'blog'],
        'api_service': ['api', 'service', 'endpoint', 'microservice', 'rest', 'graphql']
    }
    
    domain_scores = {}
    for domain, keywords in domain_keywords.items():
        score = sum(1 for keyword in keywords if keyword in text_to_analyze)
        if score > 0:
            domain_scores[domain] = score
    
    if domain_scores:
        best_domain = max(domain_scores, key=domain_scores.get)
        return best_domain
    else:
        return 'web_application'

def generate_prd_from_github_data(repo_data: dict, project_info: dict, project_type: str, business_domain: str):
    """GitHub 데이터로부터 PRD 생성"""
    
    print(f"\n🤖 AI PRD를 생성합니다...")
    
    # PRD 템플릿 생성
    prd_content = f"""# {repo_data['name']} PRD (Product Requirements Document)

## 📋 문서 정보
- **버전**: v1.0
- **작성일**: 2025-09-23
- **작성자**: AI PRD Generator (GitHub API)
- **저장소**: {repo_data['html_url']}
- **프로젝트 타입**: {project_type}
- **비즈니스 도메인**: {business_domain}
- **분석 신뢰도**: 85%

## 🎯 1. 제품 개요
### 1.1 제품명
{repo_data['name']}

### 1.2 제품 비전
{repo_data['description'] or '사용자에게 가치 있는 서비스를 제공하는 플랫폼입니다.'}

### 1.3 핵심 가치
- **사용자 중심**: 사용자 경험을 최우선으로 고려
- **안정성**: 안정적이고 신뢰할 수 있는 서비스 제공
- **확장성**: 미래 성장에 대비한 확장 가능한 아키텍처
- **보안**: 사용자 데이터와 시스템의 보안 보장

### 1.4 타겟 사용자
프로젝트의 특성에 따라 정의될 사용자 그룹

## 🏗️ 2. 기술 아키텍처
### 2.1 프로젝트 타입
{project_type}

### 2.2 주요 기술 스택
- **언어**: {repo_data['language'] or '언어 정보 없음'}
- **저장소**: GitHub
- **라이선스**: {repo_data['license']['name'] if repo_data['license'] else '라이선스 정보 없음'}

## ⚙️ 3. 핵심 기능
### 3.1 기본 기능
프로젝트의 핵심 기능을 정의합니다.

### 3.2 확장 기능
추가적인 기능들을 정의합니다.

## 🔒 4. 보안 요구사항
- 데이터 보안
- 사용자 인증
- 접근 권한 관리

## 📈 5. 성능 요구사항
- 응답 시간 최적화
- 확장성 고려
- 안정성 보장

## 🚀 6. 배포 전략
- GitHub Actions 활용
- 자동화된 배포 파이프라인
- 환경별 설정 관리

## 📅 7. 개발 로드맵
### 7.1 Phase 1 (1-3개월)
기본 기능 구현

### 7.2 Phase 2 (3-6개월)
확장 기능 추가

### 7.3 Phase 3 (6-12개월)
고급 기능 및 최적화

## 📊 8. 성공 지표 (KPI)
- GitHub 별표 수: {repo_data['stargazers_count']}
- 포크 수: {repo_data['forks_count']}
- 이슈 해결률
- 커밋 활동도

## 📝 9. 부록
### 9.1 저장소 정보
- **URL**: {repo_data['html_url']}
- **클론 URL**: {repo_data['clone_url']}
- **생성일**: {repo_data['created_at']}
- **최근 업데이트**: {repo_data['updated_at']}

### 9.2 참고 자료
- GitHub 저장소 문서
- 관련 기술 스택 공식 문서
"""
    
    # PRD 파일 저장
    output_file = Path.cwd() / f"GitHub_{repo_data['name']}_PRD.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(prd_content)
    
    print(f"✅ PRD 생성 완료: {output_file}")
    print(f"📊 파일 크기: {output_file.stat().st_size} bytes")

def main():
    """메인 함수"""
    print("🤖 AI PRD 생성기 - GitHub API 분석 도구")
    print("=" * 50)
    
    github_url = input("GitHub 저장소 URL을 입력하세요: ").strip()
    if not github_url:
        print("❌ URL을 입력해주세요.")
        return
    
    github_token = input("GitHub Personal Access Token (선택사항): ").strip()
    if not github_token:
        print("⚠️ 토큰을 입력하지 않으면 API 제한이 있을 수 있습니다.")
    
    print()
    
    success = analyze_github_repo_with_api(github_url, github_token if github_token else None)
    
    if success:
        print("\n🎉 성공적으로 분석되었습니다!")
    else:
        print("\n❌ 분석에 실패했습니다.")

if __name__ == "__main__":
    main()
