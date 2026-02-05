from logging.config import fileConfig

# SQLAlchemy 헬퍼: 엔진 생성기와 커넥션 풀 구현.
from sqlalchemy import engine_from_config, pool

from alembic_models import *  # noqa: F401, F403  # 모델을 import하여 Base.metadata가 채워지게 함.

# Alembic 런타임 컨텍스트: 마이그레이션 설정에 사용.
from alembic import context

# 프로젝트 설정과 SQLAlchemy Base 메타데이터.
from app.core.config import config as app_config
from app.core.database import Base

# Alembic Config 객체: alembic.ini 값을 읽음.
config = context.config

# alembic.ini 설정을 사용해 로깅 구성.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 프로젝트 DATABASE_URL로 sqlalchemy.url을 덮어씀.
# 앱 설정과 Alembic 설정을 일치시킴.
config.set_main_option("sqlalchemy.url", app_config.DATABASE_URL)

# Alembic 버전 테이블 이름을 커스터마이즈.
version_table_name = "coding_quiz_alembic_version"

# "autogenerate"(차이 감지)에 사용할 모델 메타데이터 제공.
target_metadata = Base.metadata

# 다른 설정값은 아래처럼 접근 가능:
# my_important_option = config.get_main_option("my_important_option")


def run_migrations_offline() -> None:
    # config에서 DB URL 읽기 (위에서 이미 설정됨).
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,  # 오프라인 모드에서는 Engine 없이 URL만 사용.
        target_metadata=target_metadata,  # autogenerate 활성화.
        literal_binds=True,  # 실제 값을 SQL 문자열에 렌더링.
        dialect_opts={"paramstyle": "named"},  # SQL에서 named 파라미터 사용.
        compare_type=True,  # 컬럼 타입 변경 감지.
        render_as_batch="sqlite" in url,  # SQLite는 배치 모드 필요.
        version_table=version_table_name,  # 커스텀 버전 테이블 사용.
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # config 설정을 사용해 Engine 생성.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",  # SQLAlchemy 설정은 이 prefix 하위에 존재.
        poolclass=pool.NullPool,  # 마이그레이션은 풀을 사용하지 않음.
    )

    with connectable.connect() as connection:
        # 실제 DB 커넥션으로 마이그레이션 컨텍스트 구성.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # 컬럼 타입 변경 감지.
            render_as_batch="sqlite" in app_config.DATABASE_URL,  # SQLite 배치 모드.
            version_table=version_table_name,  # 커스텀 버전 테이블 사용.
        )

        with context.begin_transaction():
            context.run_migrations()


# Alembic CLI 인자에 따라 오프라인/온라인 모드 선택.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
