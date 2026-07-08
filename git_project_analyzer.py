#!/usr/bin/env python3
"""
Git 저장소에서 AI PRD 생성기를 적용하는 스크립트
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
import sys

def clone_and_analyze(git_url: str, api_key: str = None):
    """
    Git 저장소를 클론하고 AI PRD를 생성하는 함수

    Args:
        git_url: Git 저장소 URL
        api_key: OpenAI API 키
    """

    print(f"🌐 Git 저장소를 클론합니다: {git_url}")

    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        try:
            # Git 클론
            print("📥 저장소를 클론하는 중...")
            result = subprocess.run(
                ['git', 'clone', git_url, 'project'],
                cwd=temp_path,
                capture_output=True,
                text=True,
                timeout=300  # 5분 타임아웃
            )

            if result.returncode != 0:
                print(f"❌ Git 클론 실패: {result.stderr}")
                return False

            project_path = temp_path / 'project'
            print(f"✅ 클론 완료: {project_path}")

            # 프로젝트 구조 분석
            print("🔍 프로젝트 구조를 분석합니다...")
            analyze_project_structure(project_path)

            # AI PRD 생성기 파일 복사
            current_dir = Path(__file__).parent
            prd_generator = current_dir / 'simple_langchain_prd.py'

            if prd_generator.exists():
                shutil.copy2(prd_generator, project_path / 'simple_langchain_prd.py')
                print("✅ AI PRD 생성기 파일 복사 완료")
            else:
                print("❌ AI PRD 생성기 파일을 찾을 수 없습니다")
                return False

            # 의존성 설치
            print("📦 필요한 패키지를 설치합니다...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install',
                    'langchain', 'openai', 'pydantic', 'python-dotenv'
                ], check=True, capture_output=True)
                print("✅ 패키지 설치 완료")
            except subprocess.CalledProcessError as e:
                print(f"❌ 패키지 설치 실패: {e}")
                return False

            # AI PRD 생성
            print("🤖 AI PRD를 생성합니다...")

            env = os.environ.copy()
            if api_key:
                env['OPENAI_API_KEY'] = api_key

            cmd = [sys.executable, 'simple_langchain_prd.py', '--project-root', '.', '--output', 'GitProject_PRD.md']
            if api_key:
                cmd.extend(['--api-key', api_key])

            result = subprocess.run(cmd, cwd=project_path, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ AI PRD 생성 완료!")
                print(result.stdout)

                # 생성된 PRD 파일을 현재 디렉토리로 복사
                prd_file = project_path / 'GitProject_PRD.md'
                if prd_file.exists():
                    output_file = Path.cwd() / f"GitProject_PRD_{Path(git_url).stem}.md"
                    shutil.copy2(prd_file, output_file)
                    print(f"📄 PRD 파일 저장: {output_file}")
                    print(f"📊 파일 크기: {output_file.stat().st_size} bytes")

                return True
            else:
                print(f"❌ PRD 생성 실패: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Git 클론 타임아웃 (5분 초과)")
            return False
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return False

def analyze_project_structure(project_path: Path):
    """프로젝트 구조 분석"""

    print(f"\n📁 프로젝트 구조 분석:")
    print(f"프로젝트 경로: {project_path}")

    # 주요 파일들 확인
    key_files = [
        'package.json', 'requirements.txt', 'pom.xml', 'go.mod', 'Cargo.toml',
        'main.py', 'app.py', 'index.js', 'main.go', 'main.rs', 'Dockerfile'
    ]

    found_files = []
    for file_name in key_files:
        if (project_path / file_name).exists():
            found_files.append(file_name)

    print(f"📄 발견된 주요 파일: {', '.join(found_files) if found_files else '없음'}")

    # 디렉토리 구조 확인
    subdirs = [d.name for d in project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    print(f"📂 하위 디렉토리: {', '.join(subdirs[:10]) if subdirs else '없음'}")
    if len(subdirs) > 10:
        print(f"   ... 및 {len(subdirs) - 10}개 더")

    # README 파일 확인
    readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
    for readme in readme_files:
        if (project_path / readme).exists():
            print(f"📖 README 파일 발견: {readme}")
            break

    # 프로젝트 타입 추정
    project_type = estimate_project_type(found_files, subdirs)
    print(f"🎯 추정 프로젝트 타입: {project_type}")

    return project_type, found_files, subdirs

def estimate_project_type(found_files: list, subdirs: list) -> str:
    """프로젝트 타입 추정"""

    if 'package.json' in found_files and 'requirements.txt' in found_files:
        return "풀스택 웹 애플리케이션 (Node.js + Python)"
    elif 'package.json' in found_files:
        if 'next' in subdirs or any('next' in str(f) for f in found_files):
            return "Next.js 웹 애플리케이션"
        elif 'src' in subdirs:
            return "React/Vue.js 웹 애플리케이션"
        else:
            return "Node.js 프로젝트"
    elif 'requirements.txt' in found_files:
        if 'Django' in str(found_files) or 'django' in subdirs:
            return "Django 웹 애플리케이션"
        elif 'FastAPI' in str(found_files) or 'fastapi' in subdirs:
            return "FastAPI 웹 애플리케이션"
        else:
            return "Python 프로젝트"
    elif 'pom.xml' in found_files:
        return "Java/Maven 프로젝트"
    elif 'go.mod' in found_files:
        return "Go 프로젝트"
    elif 'Cargo.toml' in found_files:
        return "Rust 프로젝트"
    elif 'Dockerfile' in found_files:
        return "Docker 컨테이너 프로젝트"
    else:
        return "알 수 없는 프로젝트 타입"

def analyze_github_repo(github_url: str, api_key: str = None):
    """
    GitHub 저장소 URL을 분석하는 함수
    예: https://github.com/user/repo
    """

    if not github_url.startswith('https://github.com/'):
        print("❌ GitHub URL 형식이 올바르지 않습니다.")
        print("예시: https://github.com/username/repository")
        return False

    # Git URL로 변환
    git_url = github_url.replace('https://github.com/', 'https://github.com/') + '.git'

    print(f"🔗 GitHub 저장소 분석: {github_url}")
    print(f"📥 Git URL: {git_url}")

    return clone_and_analyze(git_url, api_key)

def main():
    """메인 함수"""
    print("🤖 AI PRD 생성기 - Git 저장소 분석 도구")
    print("=" * 50)

    print("분석할 저장소를 선택하세요:")
    print("1. GitHub 저장소 URL (https://github.com/user/repo)")
    print("2. Git 저장소 URL (https://gitlab.com/user/repo.git)")
    print("3. 직접 Git URL 입력")

    choice = input("선택 (1-3): ").strip()

    if choice == "1":
        github_url = input("GitHub 저장소 URL을 입력하세요: ").strip()
        if not github_url:
            print("❌ URL을 입력해주세요.")
            return
        success = analyze_github_repo(github_url)
    elif choice == "2":
        git_url = input("Git 저장소 URL을 입력하세요: ").strip()
        if not git_url:
            print("❌ URL을 입력해주세요.")
            return
        success = clone_and_analyze(git_url)
    elif choice == "3":
        git_url = input("Git 저장소 URL을 입력하세요: ").strip()
        if not git_url:
            print("❌ URL을 입력해주세요.")
            return
        success = clone_and_analyze(git_url)
    else:
        print("❌ 올바른 선택을 해주세요.")
        return

    # API 키 입력
    api_key = input("OpenAI API 키를 입력하세요 (선택사항): ").strip()
    if not api_key:
        print("⚠️ API 키를 입력하지 않으면 폴백 모드로 실행됩니다.")

    print()

    # 분석 실행
    if choice == "1":
        success = analyze_github_repo(github_url, api_key if api_key else None)
    else:
        success = clone_and_analyze(git_url, api_key if api_key else None)

    if success:
        print("\n🎉 성공적으로 분석되었습니다!")
        print("📄 생성된 PRD 파일을 확인하세요.")
    else:
        print("\n❌ 분석에 실패했습니다.")

if __name__ == "__main__":
    main()
