import logging
import requests
import sys
import os

# 현재 디렉토리가 backend가 아닌 경우를 대비한 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine, Base
from models import MarketPrice

# ===== Logging 설정 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 테이블 생성 (최초 실행 시)
Base.metadata.create_all(bind=engine)

def fetch_and_store_data():
    url = "http://211.237.50.150:7080/openapi/0b998f4534d4a1cde328426d5acb6b0bfdb79d7162898e131d41f14bcfc12193/json/Grid_20260128000000000689_1/1/100"
    
    logger.info(f"API 데이터 요청 시작: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        logger.error(f"API 요청 실패: {e}")
        return

    # 최상위 키 추출
    grid_key = "Grid_20260128000000000689_1"
    if grid_key not in data:
        logger.error(f"응답 데이터에 '{grid_key}' 키가 없습니다.")
        return
        
    rows = data[grid_key].get("row", [])
    if not rows:
        logger.warning("응답 데이터에 'row' 리스트가 비어 있습니다.")
        return
        
    logger.info(f"총 {len(rows)}개의 아이템을 가져왔습니다. 파싱 및 저장 시작...")
    
    # 첫 번째 아이템 콘솔 출력 (요청사항 2번)
    first_item = rows[0]
    logger.info("첫 번째 아이템 구조 (키값 확인용):")
    for k, v in first_item.items():
        logger.info(f"  {k}: {v}")

    db = SessionLocal()
    try:
        # DB 초기화 (새로운 데이터를 덮어씌울 목적이면 truncate 사용 가능하지만, 일단 보존 후 추가/업데이트)
        # 이번 예제에서는 데모를 위해 전체 삭제 후 새로 삽입
        logger.info("기존 MarketPrice 데이터 삭제 중...")
        db.query(MarketPrice).delete()
        db.commit()

        import re
        
        # API 스펙상 단위가 명확하지 않은 품목들에 대한 도매 기준 용량(문자열) 매핑
        unit_map = {
            "쌀": "20kg",
            "감자": "20kg",
            "고구마": "10kg",
            "양파": "20kg",
            "무": "20kg",
            "배추": "10kg",
            "상추": "4kg",
            "오이": "10kg",
            "호박": "10kg",
            "사과": "10kg",
            "배": "15kg",
            "딸기": "2kg",
            "포도": "5kg",
            "수박": "8kg"
        }

        grouped_items = {}

        for item in rows:
            # 1. 품목명 추출
            item_name = item.get("ITEM_NM")
            if not item_name:
                continue
                
            # 2. 원본 도매 가격 파싱
            price_raw = item.get("AVG_AMT")
            if price_raw is None:
                continue
                
            try:
                if isinstance(price_raw, str):
                    price_raw = price_raw.replace(",", "")
                original_wholesale_price = int(float(price_raw))
            except ValueError:
                logger.warning(f"가격 변환 실패: {item_name} ({price_raw})")
                continue
                
            # 3. 단위 파싱 및 순수 그램(g) 추출 로직 (정규식 사용)
            # API 응답에 unit 필드가 있으면 우선 사용, 없으면 unit_map에서 참조 (기본 1kg)
            unit_raw = item.get("UNIT", item.get("단위", item.get("unit", unit_map.get(item_name, "1kg"))))
            
            total_g = 1000 # 기본값 1000g (1kg)
            
            if unit_raw:
                match_kg = re.search(r'([\d\.]+)\s*kg', unit_raw, re.IGNORECASE)
                match_g = re.search(r'([\d\.]+)\s*g', unit_raw, re.IGNORECASE)
                
                if match_kg:
                    # "kg"이 포함되어 있으면 1000을 곱함
                    total_g = int(float(match_kg.group(1)) * 1000)
                elif match_g:
                    # "g"만 있으면 숫자 그대로 사용
                    total_g = int(float(match_g.group(1)))
            
            # 4. 100g 당 정확한 가격 계산: (원본_도매가 / 총_그램) * 100
            price_per_100g = (original_wholesale_price / total_g) * 100
            
            # 5. 소매가 변환 (마진율 적용) 및 int() 처리
            retail_margin = 1.5
            final_retail_price = int(price_per_100g * retail_margin)
            
            # 그룹화 데이터에 저장
            if item_name not in grouped_items:
                grouped_items[item_name] = []
            
            grouped_items[item_name].append(final_retail_price)

        # 평균 가격 산출 및 DB 적재
        inserted_count = 0
        for item_name, prices in grouped_items.items():
            avg_price = int(sum(prices) / len(prices))
            
            # 6. DB 적재
            market_price = MarketPrice(
                item_name=item_name,
                price=avg_price,
                unit="100g", # UI 표시용 단위
                market_name="전국 도매시장 평균",
                region="전국"
            )
            db.add(market_price)
            inserted_count += 1            
        db.commit()
        logger.info(f"데이터베이스 적재 완료! 총 {inserted_count}개의 항목이 성공적으로 저장되었습니다.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"DB 저장 중 에러 발생: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fetch_and_store_data()
