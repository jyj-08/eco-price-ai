import logging
import sys
import os

# 현재 디렉토리가 backend가 아닌 경우를 대비한 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from database import engine

# ===== Logging 설정 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_advanced_features():
    logger.info("고급 DB 기능(View, Trigger) 설정을 시작합니다...")
    
    # 1. 실무적인 View 생성 (각 품목별 평균 가격 및 수집된 시장 개수)
    create_view_sql = """
    CREATE OR REPLACE VIEW v_item_price_summary AS 
    SELECT 
        item_name, 
        ROUND(AVG(price)) as avg_price, 
        COUNT(market_name) as market_count 
    FROM market_prices 
    GROUP BY item_name;
    """
    
    # 2. 실무적인 Trigger 생성을 위한 트리거 함수 정의 (가격 무결성 검증)
    create_trigger_function_sql = """
    CREATE OR REPLACE FUNCTION check_positive_price()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.price <= 0 THEN
            RAISE EXCEPTION '가격은 0보다 커야 합니다. 입력된 가격: %', NEW.price;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    # 기존 트리거 삭제 (중복 생성 방지)
    drop_trigger_sql = """
    DROP TRIGGER IF EXISTS trg_check_price ON market_prices;
    """
    
    # 3. 트리거 연결
    create_trigger_sql = """
    CREATE TRIGGER trg_check_price
    BEFORE INSERT OR UPDATE ON market_prices
    FOR EACH ROW
    EXECUTE FUNCTION check_positive_price();
    """

    try:
        # SQLAlchemy 2.0+ 에서는 연결(connection)을 컨텍스트 매니저로 열고, 명시적으로 commit()을 호출해야 합니다.
        with engine.begin() as conn:
            # 뷰 생성
            logger.info("뷰(v_item_price_summary) 생성 중...")
            conn.execute(text(create_view_sql))
            logger.info("✅ 뷰 생성 성공!")
            
            # 트리거 함수 생성
            logger.info("트리거 함수(check_positive_price) 생성 중...")
            conn.execute(text(create_trigger_function_sql))
            logger.info("✅ 트리거 함수 생성 성공!")
            
            # 기존 트리거 삭제 및 새 트리거 연결
            logger.info("트리거(trg_check_price) 연결 중...")
            conn.execute(text(drop_trigger_sql))
            conn.execute(text(create_trigger_sql))
            logger.info("✅ 트리거 연결 성공!")
            
        logger.info("모든 고급 DB 기능(View, Trigger) 설정이 성공적으로 완료되었습니다!")

    except Exception as e:
        logger.error(f"고급 DB 기능 설정 중 에러 발생: {e}")

if __name__ == "__main__":
    setup_advanced_features()
