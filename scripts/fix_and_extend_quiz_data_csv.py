from __future__ import annotations

import csv
from pathlib import Path

from app.core.ulid import generate_ulid, is_valid_ulid


CSV_PATH = Path("csv_files/quiz_data.csv")
BROKEN_MARKER = "??"


def _row_is_broken(row: list[str]) -> bool:
    # The corrupted rows contain literal "??" sequences.
    return any(BROKEN_MARKER in (cell or "") for cell in row)


# These 61 questions were previously appended, but got corrupted to "??" due to encoding issues.
# We keep the original ULID "id" and overwrite the rest, so DB sync via session.merge() updates
# existing records rather than creating duplicates.
FIXED_QUESTIONS_61: list[dict[str, str]] = [
    # FastAPI
    {
        "question": "FastAPI에서 의존성 주입(Dependency Injection)을 위해 사용하는 함수는?",
        "explanation": "엔드포인트 파라미터에 Depends(...)를 선언하면 FastAPI가 의존성을 실행해 값을 주입합니다.",
        "answer": "Depends",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 라우터를 모듈 단위로 분리할 때 사용하는 클래스는?",
        "explanation": "APIRouter로 라우트를 묶고, app.include_router(...)로 앱에 등록합니다.",
        "answer": "APIRouter",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 분리된 라우터(APIRouter)를 앱에 등록할 때 사용하는 메서드는?",
        "explanation": "FastAPI/Starlette 앱 객체에서 include_router(router, prefix=..., tags=...) 형태로 등록합니다.",
        "answer": "include_router",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 CORS 정책을 설정하기 위해 사용하는 미들웨어는?",
        "explanation": "프론트 도메인(Origin) 허용, allow_methods/allow_headers 등을 설정할 때 CORSMiddleware를 사용합니다.",
        "answer": "CORSMiddleware",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 HTTP 에러를 발생시키는 기본 예외 클래스는?",
        "explanation": "raise HTTPException(status_code=..., detail=...) 형태로 클라이언트에 에러 응답을 반환합니다.",
        "answer": "HTTPException",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 HTTP 상태 코드 상수(HTTP_200_OK 등)가 정의된 모듈은?",
        "explanation": "from fastapi import status 로 가져와 status.HTTP_200_OK 같은 상수를 사용할 수 있습니다.",
        "answer": "status/fastapi.status",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 Bearer 토큰을 받기 위한 간단한 Security 스킴 클래스는?",
        "explanation": "HTTPBearer()는 Authorization: Bearer <token> 형식의 헤더를 파싱해 credentials를 제공합니다.",
        "answer": "HTTPBearer",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 OAuth2 Password Flow 기반으로 토큰을 받기 위해 사용하는 dependency는?",
        "explanation": "OAuth2PasswordBearer(tokenUrl=...)는 Authorization 헤더에서 토큰 문자열을 가져옵니다.",
        "answer": "OAuth2PasswordBearer",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 Authorization 헤더의 scheme과 credentials를 파싱해주는 유틸 함수는?",
        "explanation": "fastapi.security.utils.get_authorization_scheme_param(authorization_header)로 (scheme, token)을 얻습니다.",
        "answer": "get_authorization_scheme_param",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 (scheme, credentials)를 담는 타입은?",
        "explanation": "HTTPBearer 같은 보안 스킴이 반환하는 값으로, scheme과 credentials 필드를 가집니다.",
        "answer": "HTTPAuthorizationCredentials",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 요청 정보를 다루는 객체 타입은?",
        "explanation": "헤더/쿼리/클라이언트 IP 등 요청 메타데이터를 접근할 때 Request를 주입받아 사용합니다.",
        "answer": "Request",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 응답 헤더/쿠키 등을 직접 조작하고 싶을 때 주입받는 타입은?",
        "explanation": "Response 객체를 파라미터로 받아 set_cookie, headers 업데이트 등을 수행할 수 있습니다.",
        "answer": "Response",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 쿼리 파라미터의 기본값/검증(ge, le 등)을 지정할 때 사용하는 함수는?",
        "explanation": "Query(..., ge=0, le=100)처럼 선언하여 쿼리 파라미터 검증과 문서화를 지원합니다.",
        "answer": "Query",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 Path 파라미터에 대한 검증/메타데이터를 지정할 때 사용하는 함수는?",
        "explanation": "Path(..., min_length=1)처럼 선언하여 경로 파라미터 검증과 문서화를 지원합니다.",
        "answer": "Path",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 multipart/form-data 폼 필드를 받을 때 사용하는 함수는?",
        "explanation": "Form(...)을 사용하면 폼 필드를 요청 바디에서 읽어옵니다.",
        "answer": "Form",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 파일 업로드를 받을 때 사용하는 타입은?",
        "explanation": "UploadFile은 파일 스트림을 효율적으로 다루며, 파일명/콘텐츠 타입 등을 제공합니다.",
        "answer": "UploadFile",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 요청 처리 후 비동기 작업을 실행하도록 등록할 때 사용하는 클래스는?",
        "explanation": "BackgroundTasks에 task를 add_task(...)로 등록하면 응답 반환 후 실행됩니다.",
        "answer": "BackgroundTasks",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 응답 스키마를 지정할 때 라우트 데코레이터에 사용하는 인자 이름은?",
        "explanation": "@router.get(..., response_model=MySchema)처럼 지정하여 응답 직렬화/문서화를 제어합니다.",
        "answer": "response_model",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 전역 예외 핸들러를 등록하는 데코레이터는?",
        "explanation": "@app.exception_handler(SomeException)로 특정 예외에 대한 공통 응답을 정의할 수 있습니다.",
        "answer": "exception_handler",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 API를 테스트할 때 자주 사용하는 동기식 테스트 클라이언트는?",
        "explanation": "fastapi.testclient.TestClient(app)로 엔드포인트를 호출하여 테스트할 수 있습니다.",
        "answer": "TestClient",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 의존성(Depends)과 타입힌트를 함께 명확히 표현할 때 자주 사용하는 typing 기능은?",
        "explanation": "Annotated[T, Depends(...)] 형태로 타입과 의존성 선언을 함께 표현합니다.",
        "answer": "Annotated",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 보안 의존성을 선언할 때 Depends 대신 자주 쓰는 함수는?",
        "explanation": "Security(...)는 OAuth2 scopes 등 보안 컨텍스트에서 사용하기 좋습니다.",
        "answer": "Security",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 startup/shutdown 이벤트(@app.on_event) 대신 권장되는 애플리케이션 생명주기 방식은?",
        "explanation": "최근 FastAPI에서는 lifespan 컨텍스트를 사용해 startup/shutdown 로직을 구성하는 것을 권장합니다.",
        "answer": "lifespan",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI/Starlette에서 기본 JSON 응답에 사용하는 Response 클래스는?",
        "explanation": "dict를 반환하면 내부적으로 JSONResponse로 직렬화되어 응답됩니다.",
        "answer": "JSONResponse",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 파일 다운로드 응답에 자주 사용하는 Response 클래스는?",
        "explanation": "정적 파일 또는 생성된 파일을 반환할 때 FileResponse를 사용합니다.",
        "answer": "FileResponse",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 대용량 데이터를 스트리밍으로 내려줄 때 사용하는 Response 클래스는?",
        "explanation": "StreamingResponse로 generator/iterable을 스트리밍 전송할 수 있습니다.",
        "answer": "StreamingResponse",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 정적 파일(이미지, css 등)을 서빙할 때 사용하는 클래스는?",
        "explanation": "StaticFiles 디렉터리를 mount하여 /static 같은 경로로 제공합니다.",
        "answer": "StaticFiles",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI/Starlette에서 커스텀 미들웨어를 만들 때 많이 상속하는 클래스는?",
        "explanation": "BaseHTTPMiddleware를 상속해 dispatch 메서드에서 요청/응답을 가로챌 수 있습니다.",
        "answer": "BaseHTTPMiddleware",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 WebSocket 엔드포인트를 선언할 때 사용하는 데코레이터(핵심 키워드)는?",
        "explanation": "HTTP 라우트(@app.get)와 별도로 @app.websocket(\"/ws\") 형태로 정의합니다.",
        "answer": "websocket/@app.websocket",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 ORM 객체 등을 JSON 직렬화 가능한 형태로 변환할 때 자주 쓰는 함수는?",
        "explanation": "fastapi.encoders.jsonable_encoder(obj)는 datetime/ORM 등을 JSON-friendly 구조로 바꿉니다.",
        "answer": "jsonable_encoder",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI 프로젝트에서 현재 로그인 사용자를 주입받는 의존성 함수 이름으로 흔히 쓰는 것은?",
        "explanation": "보통 get_current_user 같은 함수를 Depends(get_current_user)로 주입받아 인증을 강제합니다.",
        "answer": "get_current_user",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 요청 검증(ValidationError) 실패 시 기본 응답 status code는?",
        "explanation": "요청 바디/쿼리/패스 파라미터 검증 실패 시 기본적으로 422를 반환합니다.",
        "answer": "422/HTTP_422_UNPROCESSABLE_ENTITY",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 요청/응답 스키마로 사용하는 Pydantic의 기본 클래스는?",
        "explanation": "Pydantic BaseModel을 상속하여 request/response 모델을 정의합니다.",
        "answer": "BaseModel",
        "category": "FastAPI",
    },
    {
        "question": "Pydantic v2에서 ORM 객체에서 값을 읽을 수 있게 하는 ConfigDict 옵션은?",
        "explanation": "from_attributes=True를 설정하면 ORM 객체의 attribute에서 값을 읽어 모델을 만들 수 있습니다.",
        "answer": "from_attributes",
        "category": "FastAPI",
    },
    {
        "question": "Pydantic v2에서 모델을 dict로 변환할 때 사용하는 메서드는?",
        "explanation": "v1의 .dict() 대신 v2에서는 .model_dump()를 사용합니다.",
        "answer": "model_dump",
        "category": "FastAPI",
    },
    {
        "question": "Pydantic v2에서 입력 데이터를 검증해 모델을 만드는 클래스 메서드는?",
        "explanation": "model_validate(data)로 타입/값 검증 후 인스턴스를 생성할 수 있습니다.",
        "answer": "model_validate",
        "category": "FastAPI",
    },
    {
        "question": "Pydantic에서 정의되지 않은 extra 필드를 금지하는 설정 값은?",
        "explanation": "ConfigDict(extra=\"forbid\") 처럼 설정하면 스키마에 없는 필드가 들어오면 검증 에러가 발생합니다.",
        "answer": "forbid",
        "category": "FastAPI",
    },
    {
        "question": "dependency_injector를 FastAPI Depends와 함께 쓸 때 컨테이너 Provider를 참조하는 객체는?",
        "explanation": "Depends(Provide[Container.some_service]) 형태로 주입받을 때 Provide를 사용합니다.",
        "answer": "Provide",
        "category": "FastAPI",
    },
    {
        "question": "dependency_injector에서 함수/엔드포인트에 주입을 활성화하는 데코레이터는?",
        "explanation": "@inject 데코레이터와 Provide를 조합해 DI 컨테이너 객체를 주입할 수 있습니다.",
        "answer": "inject/@inject",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 i18n 메시지 키와 함께 던지는 커스텀 HTTPException 클래스 이름은?",
        "explanation": "일반 HTTPException을 래핑해 다국어 메시지 처리를 돕는 커스텀 예외입니다.",
        "answer": "i18nHTTPException",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 status/msg/data 형태로 응답을 감싸는 공통 응답 모델 이름은?",
        "explanation": "프로젝트마다 응답 포맷을 통일하기 위해 WrappedResponse 같은 래퍼 모델을 두기도 합니다.",
        "answer": "WrappedResponse",
        "category": "FastAPI",
    },
    # SQLAlchemy
    {
        "question": "SQLAlchemy 2.0 스타일에서 SELECT 문을 구성하는 함수는?",
        "explanation": "from sqlalchemy import select 를 사용해 select(Model) 같은 형태로 쿼리를 구성합니다.",
        "answer": "select",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy 비동기 ORM에서 사용하는 세션 타입은?",
        "explanation": "async 환경에서는 sqlalchemy.ext.asyncio.AsyncSession을 사용합니다.",
        "answer": "AsyncSession",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy에서 PK 기준으로 insert/update(업서트 유사)를 처리할 때 사용할 수 있는 메서드는?",
        "explanation": "session.merge(entity)는 PK가 있으면 업데이트, 없으면 삽입에 가까운 동작을 합니다.",
        "answer": "merge",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy에서 commit 후 DB에 반영된 값을 객체에 다시 로드할 때 사용하는 메서드는?",
        "explanation": "self.db.refresh(obj)처럼 사용하여 DB 트리거/기본값/PK 등을 반영합니다.",
        "answer": "refresh",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy에서 N+1 문제를 줄이기 위해 컬렉션 관계를 효율적으로 eager load할 때 자주 쓰는 로더는?",
        "explanation": "selectinload는 IN 쿼리를 사용해 관련 컬렉션을 한 번에 가져올 수 있습니다.",
        "answer": "selectinload",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy에서 join을 사용해 관계를 eager load할 때 자주 쓰는 로더는?",
        "explanation": "joinedload는 join으로 한 번에 가져오지만 중복 row 증가 등 트레이드오프가 있습니다.",
        "answer": "joinedload",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy에서 중복을 막기 위한 유니크 제약을 선언할 때 사용하는 클래스는?",
        "explanation": "UniqueConstraint(\"col1\", \"col2\") 형태로 복합 유니크 제약도 선언할 수 있습니다.",
        "answer": "UniqueConstraint",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy에서 인덱스를 선언할 때 사용하는 클래스는?",
        "explanation": "Index(\"ix_name\", Model.col) 형태로 인덱스를 정의할 수 있습니다.",
        "answer": "Index",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy 2.0 ORM에서 타입힌트 기반으로 컬럼을 선언할 때 사용하는 함수는?",
        "explanation": "Mapped[T]와 mapped_column(...) 조합으로 타입 안전한 모델 정의가 가능합니다.",
        "answer": "mapped_column",
        "category": "SQLAlchemy",
    },
    {
        "question": "SQLAlchemy 2.0 ORM에서 타입힌트로 매핑 컬럼을 표현하는 제네릭 타입은?",
        "explanation": "예: name: Mapped[str] = mapped_column(String(...))",
        "answer": "Mapped",
        "category": "SQLAlchemy",
    },
    # Python
    {
        "question": "Python에서 비동기 함수를 정의할 때 사용하는 키워드는?",
        "explanation": "async def func(): 형태로 코루틴 함수를 정의합니다.",
        "answer": "async/async def",
        "category": "Python",
    },
    {
        "question": "Python에서 코루틴 실행 결과를 기다릴 때 사용하는 키워드는?",
        "explanation": "await some_coroutine()처럼 사용하며, async 함수 내부에서만 사용할 수 있습니다.",
        "answer": "await",
        "category": "Python",
    },
    {
        "question": "Python asyncio에서 코루틴을 실행하는 대표적인 함수는?",
        "explanation": "asyncio.run(main())으로 이벤트 루프를 만들고 코루틴을 실행합니다.",
        "answer": "asyncio.run",
        "category": "Python",
    },
    {
        "question": "Python 3.10+에서 Optional[str]을 대체하는 타입 표기법은?",
        "explanation": "Optional[str] 대신 str | None 처럼 | 연산자로 Union 타입을 표현할 수 있습니다.",
        "answer": "str|None/str | None",
        "category": "Python",
    },
    {
        "question": "python-dotenv에서 .env 파일을 로드할 때 사용하는 함수는?",
        "explanation": "load_dotenv()를 호출하면 .env의 환경변수가 os.environ에 로드됩니다.",
        "answer": "load_dotenv",
        "category": "Python",
    },
    {
        "question": "bcrypt 해시 알고리즘에서 비밀번호는 최대 몇 바이트까지 안전하게 처리하는 것이 권장되나?",
        "explanation": "bcrypt는 72바이트 제한이 있어 그 이상은 잘림/오류 등 문제가 될 수 있습니다.",
        "answer": "72",
        "category": "Python",
    },
    {
        "question": "Python에서 context manager를 사용하는 구문은?",
        "explanation": "with 문을 사용하면 파일/락/세션 같은 자원을 자동으로 정리할 수 있습니다.",
        "answer": "with",
        "category": "Python",
    },
    {
        "question": "Python에서 타입 힌트 관련 기능이 들어있는 표준 라이브러리 모듈은?",
        "explanation": "typing 모듈에는 Optional, Annotated, Protocol 등 다양한 타입 힌트 도구가 있습니다.",
        "answer": "typing",
        "category": "Python",
    },
    {
        "question": "Python에서 패키지에서 외부로 노출할 심볼을 제한할 때 사용하는 변수는?",
        "explanation": "__all__ 리스트를 정의하면 from package import * 동작을 제어할 수 있습니다.",
        "answer": "__all__",
        "category": "Python",
    },
    {
        "question": "Python에서 경로(Path)를 객체로 다루기 위한 표준 라이브러리는?",
        "explanation": "pathlib.Path를 사용하면 OS별 경로 처리 코드를 단순하게 만들 수 있습니다.",
        "answer": "pathlib",
        "category": "Python",
    },
]


# Extra questions to append (new ULIDs will be generated).
EXTRA_QUESTIONS: list[dict[str, str]] = [
    # FastAPI params & routing
    {
        "question": "FastAPI에서 요청 바디(Body) 파라미터에 메타데이터를 달 때 사용하는 함수는?",
        "explanation": "Body(...)를 사용하면 요청 바디 파라미터의 기본값/예시/검증을 선언할 수 있습니다.",
        "answer": "Body",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 요청 헤더 값을 받을 때 사용하는 함수는?",
        "explanation": "Header(...)를 사용해 특정 헤더 값을 파라미터로 선언하고 검증할 수 있습니다.",
        "answer": "Header",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 쿠키 값을 받을 때 사용하는 함수는?",
        "explanation": "Cookie(...)를 사용하면 쿠키 값을 파라미터로 선언하고 문서화할 수 있습니다.",
        "answer": "Cookie",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 파일 업로드 필드를 선언할 때 UploadFile과 함께 자주 사용하는 함수는?",
        "explanation": "File(...)은 multipart/form-data 파일 필드를 선언할 때 사용합니다.",
        "answer": "File",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 라우트 데코레이터에 고정 응답 status code를 지정할 때 사용하는 인자 이름은?",
        "explanation": "@router.post(..., status_code=201)처럼 지정할 수 있습니다.",
        "answer": "status_code",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 라우터(APIRouter)에 공통 의존성을 강제하려면 주로 어떤 인자를 사용하나?",
        "explanation": "APIRouter(..., dependencies=[Depends(...)])로 라우터 전체에 의존성을 적용할 수 있습니다.",
        "answer": "dependencies",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 Swagger UI 문서 페이지의 URL 경로를 바꾸는 FastAPI 생성자 인자는?",
        "explanation": "FastAPI(docs_url=\"/docs\")처럼 설정합니다.",
        "answer": "docs_url",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 OpenAPI 스펙 JSON의 URL 경로를 바꾸는 FastAPI 생성자 인자는?",
        "explanation": "FastAPI(openapi_url=\"/openapi.json\")처럼 설정합니다.",
        "answer": "openapi_url",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 ReDoc 문서 페이지의 URL 경로를 바꾸는 FastAPI 생성자 인자는?",
        "explanation": "FastAPI(redoc_url=\"/redoc\")처럼 설정합니다.",
        "answer": "redoc_url",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 response_model에서 None 값을 가진 필드를 제외하려면 어떤 인자를 사용하나?",
        "explanation": "response_model_exclude_none=True로 설정하면 None 필드를 응답에서 빼줍니다.",
        "answer": "response_model_exclude_none",
        "category": "FastAPI",
    },
    {
        "question": "FastAPI에서 response_model에서 요청에 없었던(unset) 필드를 제외하려면 어떤 인자를 사용하나?",
        "explanation": "response_model_exclude_unset=True로 설정할 수 있습니다.",
        "answer": "response_model_exclude_unset",
        "category": "FastAPI",
    },
    # JWT / Security
    {
        "question": "JWT에서 만료 시간을 나타내는 표준 claim 키는?",
        "explanation": "exp는 만료 시간을 의미하며, 토큰이 만료되면 서버에서 거부해야 합니다.",
        "answer": "exp",
        "category": "Security",
    },
    {
        "question": "JWT에서 subject(주체)를 나타내는 표준 claim 키는?",
        "explanation": "sub는 토큰의 주체(예: user email)를 표현할 때 자주 사용합니다.",
        "answer": "sub",
        "category": "Security",
    },
    {
        "question": "PyJWT에서 토큰이 만료되었을 때 발생하는 예외는?",
        "explanation": "jwt.ExpiredSignatureError는 exp가 지난 토큰을 decode할 때 발생합니다.",
        "answer": "ExpiredSignatureError/jwt.ExpiredSignatureError",
        "category": "Security",
    },
    {
        "question": "PyJWT에서 토큰이 유효하지 않을 때(서명/형식 오류 등) 발생하는 대표 예외는?",
        "explanation": "jwt.InvalidTokenError는 다양한 토큰 오류를 포괄합니다.",
        "answer": "InvalidTokenError/jwt.InvalidTokenError",
        "category": "Security",
    },
    {
        "question": "admarket_fastapi_BE에서 Bearer 토큰을 파싱하는 커스텀 Security 스킴 클래스 이름은?",
        "explanation": "HTTPBearer를 상속해서 토큰이 없거나 scheme이 다르면 i18nHTTPException을 던지도록 구현되어 있습니다.",
        "answer": "CustomBearer",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 현재 로그인 사용자 정보를 주입받는 dependency 함수 이름은?",
        "explanation": "get_current_user는 토큰을 decode 후 UserInfo 형태로 변환해 반환합니다.",
        "answer": "get_current_user",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 관리자 권한을 확인한 뒤 사용자 정보를 반환하는 dependency 함수는?",
        "explanation": "get_admin_user는 roles에 admin이 없으면 i18nHTTPException을 던집니다.",
        "answer": "get_admin_user",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 토큰 payload를 Pydantic으로 검증하는 모델 클래스 이름은?",
        "explanation": "jwt.decode 결과를 TokenInfo(**payload)로 검증합니다.",
        "answer": "TokenInfo",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 유저 정보를 API 레이어로 전달하기 위한 모델 클래스 이름은?",
        "explanation": "tokeninfo_to_userinfo 함수가 TokenInfo를 UserInfo로 변환합니다.",
        "answer": "UserInfo",
        "category": "FastAPI",
    },
    {
        "question": "admarket_fastapi_BE에서 membership 타입을 표현하는 Enum 클래스 이름은?",
        "explanation": "Membership Enum은 숫자 값을 받아 적절한 등급을 반환하는 from_value를 제공합니다.",
        "answer": "Membership",
        "category": "Python",
    },
    {
        "question": "admarket_fastapi_BE에서 토큰의 roles 안에 admin이 있는지 검사하는 함수 이름은?",
        "explanation": "admin이 없으면 ADMIN_REQUIRED 에러로 i18nHTTPException을 던집니다.",
        "answer": "check_is_admin",
        "category": "FastAPI",
    },
    # Transactions / cache (admarket patterns)
    {
        "question": "admarket_fastapi_BE에서 DB 세션을 제공하고 commit/rollback을 처리하는 asynccontextmanager 함수 이름은?",
        "explanation": "get_db는 yield 이후 commit, 예외 시 rollback을 수행합니다.",
        "answer": "get_db",
        "category": "SQLAlchemy",
    },
    {
        "question": "admarket_fastapi_BE에서 DB 트랜잭션을 API 메서드 단위로 묶는 데코레이터는?",
        "explanation": "transactional 데코레이터는 persistence에 db 세션을 주입해줍니다.",
        "answer": "transactional",
        "category": "Architecture",
    },
    {
        "question": "admarket_fastapi_BE에서 Redis 연결을 제공하는 asynccontextmanager 함수 이름은?",
        "explanation": "get_redis는 yield 이후 연결을 닫아줍니다.",
        "answer": "get_redis",
        "category": "Architecture",
    },
    {
        "question": "admarket_fastapi_BE에서 Redis 캐시 컨텍스트를 주입하는 데코레이터는?",
        "explanation": "caching 데코레이터는 persistence에 cache를 주입해줍니다.",
        "answer": "caching",
        "category": "Architecture",
    },
    {
        "question": "admarket_fastapi_BE에서 DB와 Redis를 함께 주입하는 데코레이터는?",
        "explanation": "transactional_caching은 persistence에 db와 cache를 함께 주입합니다.",
        "answer": "transactional_caching",
        "category": "Architecture",
    },
    {
        "question": "admarket_fastapi_BE에서 DB/Cache 객체를 함께 담는 Pydantic 모델 클래스 이름은?",
        "explanation": "Persistent 모델은 cache와 db 필드를 가집니다.",
        "answer": "Persistent",
        "category": "Architecture",
    },
    # Testing
    {
        "question": "pytest에서 예외가 발생하는지 검증하는 context manager는?",
        "explanation": "with pytest.raises(SomeError): 형태로 예외 발생을 검증합니다.",
        "answer": "pytest.raises/raises",
        "category": "Testing",
    },
    {
        "question": "pytest에서 fixture를 정의할 때 사용하는 데코레이터는?",
        "explanation": "@pytest.fixture로 테스트용 의존성(세팅/tearDown)을 정의합니다.",
        "answer": "pytest.fixture/fixture",
        "category": "Testing",
    },
    # ULID (this project)
    {
        "question": "ULID 문자열은 기본적으로 몇 글자인가?",
        "explanation": "ULID는 128비트를 Crockford Base32로 인코딩해 26자 문자열로 표현합니다.",
        "answer": "26",
        "category": "Python",
    },
    {
        "question": "ULID는 시간 기반 정렬이 가능한 ID 형식이다. 시간 정보는 밀리초(ms) 단위로 저장된다. (O/X)",
        "explanation": "ULID는 48-bit timestamp(ms) + 80-bit randomness로 구성됩니다.",
        "answer": "O/True",
        "category": "Python",
    },
]


def main() -> None:
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != ["id", "question", "explanation", "answer", "category"]:
            raise SystemExit(f"Unexpected header: {header!r}")
        rows = [row for row in reader if row]

    for r in rows:
        if len(r) != 5:
            raise SystemExit(f"Invalid row length (expected 5): {r!r}")

    broken_rows = [r for r in rows if _row_is_broken(r)]
    if len(broken_rows) not in (0, len(FIXED_QUESTIONS_61)):
        raise SystemExit(
            f"Broken row count mismatch: found={len(broken_rows)} expected=0 or {len(FIXED_QUESTIONS_61)}. "
            f"(If you edited the CSV manually, adjust FIXED_QUESTIONS_61 accordingly.)"
        )

    fixed_iter = iter(FIXED_QUESTIONS_61) if broken_rows else None
    new_rows: list[list[str]] = []
    existing_ids: set[str] = set()
    existing_qas: set[tuple[str, str, str]] = set()

    for row in rows:
        quiz_id = row[0].strip()
        if not is_valid_ulid(quiz_id):
            raise SystemExit(f"Invalid ULID id: {quiz_id!r}")
        if quiz_id in existing_ids:
            raise SystemExit(f"Duplicate id detected: {quiz_id}")
        existing_ids.add(quiz_id)

        if _row_is_broken(row):
            assert fixed_iter is not None
            item = next(fixed_iter)
            new_rows.append(
                [
                    quiz_id,
                    item["question"],
                    item["explanation"],
                    item["answer"],
                    item["category"],
                ]
            )
            existing_qas.add((item["question"], item["answer"], item["category"]))
        else:
            new_rows.append(row)
            existing_qas.add((row[1], row[3], row[4]))

    # Append extra questions with new ULIDs.
    added = 0
    for item in EXTRA_QUESTIONS:
        key = (item["question"], item["answer"], item["category"])
        if key in existing_qas:
            continue
        new_id = generate_ulid()
        while new_id in existing_ids:
            new_id = generate_ulid()
        existing_ids.add(new_id)
        new_rows.append([new_id, item["question"], item["explanation"], item["answer"], item["category"]])
        existing_qas.add(key)
        added += 1

    tmp_path = CSV_PATH.with_suffix(".csv.tmp")
    with tmp_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "question", "explanation", "answer", "category"])
        writer.writerows(new_rows)

    tmp_path.replace(CSV_PATH)
    print(f"fixed_rows={len(broken_rows)} added_rows={added} total_rows={len(new_rows)}")


if __name__ == "__main__":
    main()
