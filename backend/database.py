import os
import logging

# ===== Logging 설정 =====
logger = logging.getLogger(__name__)

# 시스템 에러 메시지를 영어로 고정하여 인코딩 오류를 방지합니다.
os.environ["LANG"] = "en_US.UTF-8"

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_USER = os.getenv("DB_USER", "eco_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "eco_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "eco_price_db")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

logger.info(f"데이터베이스 연결 설정: {DB_HOST}:{DB_PORT}/{DB_NAME}")

try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )
    logger.info("SQLAlchemy 엔진 생성 완료")
except Exception as e:
    logger.error(f"SQLAlchemy 엔진 생성 실패: {str(e)}", exc_info=True)
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    logger.debug("데이터베이스 세션 생성")
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 세션 중 오류 발생: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()
        logger.debug("데이터베이스 세션 종료")
