### 프로젝트 초기 설정 가이드 (FastAPI + Next.js with React)

이 문서는 **FastAPI(백엔드)와 Next.js(프론트엔드)** 를 처음부터 설치하고, 프로젝트 파일 구조 및 각 기술에 대한 설명을 포함하고 있습니다.

---

## 1. 프로젝트 초기 설정

### **(1) Git 저장소 클론**
```bash
git clone <저장소_URL>
cd CodingQuizProject
```

### **(2) 백엔드 (FastAPI) 환경 설정**
```bash
cd backend
python -m venv venv  # 가상환경 생성 (최초 1회)
source venv/bin/activate  # 가상환경 활성화 (Windows는 venv\Scripts\activate)
pip install -r requirements.txt  # 패키지 설치
uvicorn main:app --reload  # FastAPI 서버 실행
```
> FastAPI 서버 실행: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

### **(3) 프론트엔드 (Next.js + React) 환경 설정**
```bash
cd frontend
npx create-next-app@latest .  # Next.js 프로젝트 초기화
npm install  # 패키지 설치
npm run dev  # 개발 서버 실행
```
> Next.js 서버 실행: [http://localhost:3000/](http://localhost:3000/)

---

## 2. 프로젝트 파일 구조
```plaintext
CodingQuizProject/
│── backend/            # FastAPI 백엔드
│   ├── main.py         # FastAPI 서버 실행
│   ├── requirements.txt # Python 패키지 리스트
│
│── frontend/           # Next.js 프론트엔드 (React 기반)
│   ├── node_modules/   # npm 패키지 (Git에 올리지 않음)
│   ├── public/         # 정적 파일 (이미지, 폰트 등)
│   ├── src/            # Next.js 소스 코드
│   │   ├── components/ # UI 컴포넌트 폴더
│   │   ├── pages/      # Next.js 페이지 라우팅
│   ├── .env            # 환경 변수 파일
│   ├── package.json    # 프론트엔드 종속성 정보
│   ├── package-lock.json # npm 종속성 잠금 파일
│   ├── next.config.mjs # Next.js 설정 파일
```

---

## 3. 마무리 및 실행 확인
### 🔹 **프로젝트 실행 순서**
1. **백엔드 실행**
```bash
cd backend
uvicorn main:app --reload
```
2. **프론트엔드 실행**
```bash
cd frontend
npm run dev
```
✅ 두 서버가 정상적으로 실행되면 다음 URL을 통해 확인 가능:
- **FastAPI API 문서** → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Next.js 웹 페이지** → [http://localhost:3000/](http://localhost:3000/)

이제 프로젝트 개발을 시작할 수 있습니다! 🚀

