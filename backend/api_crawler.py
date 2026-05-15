import logging
import os
from datetime import datetime
from typing import Any, Dict, Generator, Iterable, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database import get_db
from models import MarketPrice

load_dotenv()

API_KEY_ENV = "PUBLIC_DATA_API_KEY"
API_URL_ENV = "PUBLIC_DATA_API_URL"
DEFAULT_API_URL = "https://api.odcloud.kr/api/15063980/v1/uddi:bcd05d59-17ae-4d06-9a43-931d896950a2"
BATCH_SIZE = 300

logger = logging.getLogger(__name__)


def get_env_value(key: str, required: bool = True) -> str:
    """환경 변수를 읽습니다."""
    value = os.getenv(key, "")
    if required and not value:
        logger.error(f"필수 환경 변수 누락: {key}")
        raise EnvironmentError(f"Missing required environment variable: {key}")
    if not value:
        logger.warning(f"환경 변수 값이 비어있음: {key}")
    else:
        logger.debug(f"환경 변수 로드: {key}=***")
    return value


def get_db_session() -> Tuple[Generator[Session, None, None], Session]:
    db_generator = get_db()
    db_session = next(db_generator)
    return db_generator, db_session


def fetch_public_data_page(api_key: str, api_url: str, page_no: int = 1, num_of_rows: int = 500) -> Dict[str, Any]:
    """공공 데이터 API에서 한 페이지의 데이터를 가져옵니다."""
    params = {
        "serviceKey": api_key,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "_type": "json",
    }
    
    try:
        logger.debug(f"API 호출: page={page_no}, rows={num_of_rows}")
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()
        logger.debug(f"API 응답 수신: status_code={response.status_code}, size={len(response.text)}자")
        return response.json()
    except requests.exceptions.Timeout as e:
        logger.error(f"API 호출 타임아웃 (page={page_no}): {str(e)}", exc_info=True)
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"API HTTP 에러 (page={page_no}, status_code={response.status_code}): {str(e)}", exc_info=True)
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"API 요청 실패 (page={page_no}): {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"API 응답 파싱 실패 (page={page_no}): {str(e)}", exc_info=True)
        raise


def extract_items_from_response(response_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(response_json, dict):
        return []

    if "items" in response_json and isinstance(response_json["items"], list):
        return response_json["items"]

    if "data" in response_json and isinstance(response_json["data"], list):
        return response_json["data"]

    if "response" in response_json:
        response_block = response_json["response"]
        if isinstance(response_block, dict):
            body = response_block.get("body")
            if isinstance(body, dict):
                items = body.get("items")
                if isinstance(items, list):
                    return items
    return []


def normalize_price(value: Any) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).replace(",", "").strip()
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def normalize_date(value: Any) -> Optional[datetime.date]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).date()
    except (ValueError, TypeError):
        return None


def get_value(record: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return str(record[key]).strip()
    return None


def parse_market_price_records(raw_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    parsed_records: List[Dict[str, Any]] = []

    for raw in raw_items:
        item_name = get_value(raw, ["item_name", "itemNm", "prdtNm", "품목명", "PRDT_NM"])
        price_value = get_value(raw, ["price", "prc", "dprc", "offerPrc", "가격"])
        unit = get_value(raw, ["unit", "prdtUnit", "단위"])
        market_name = get_value(raw, ["market_name", "marketNm", "market", "시장명"])
        region = get_value(raw, ["region", "area", "ctyNm", "지역"])
        update_date_value = get_value(raw, ["update_date", "trdDd", "stdt", "date", "pblntfPcldt"])

        price = normalize_price(price_value)
        update_date = normalize_date(update_date_value)

        if not item_name or price is None or update_date is None:
            continue

        parsed_records.append(
            {
                "item_name": item_name,
                "price": price,
                "unit": unit or "",
                "market_name": market_name or "",
                "region": region or "",
                "update_date": update_date,
            }
        )

    return parsed_records


def dedupe_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique: Dict[Tuple[str, str, str, str, str], Dict[str, Any]] = {}
    for record in records:
        key = (
            record["item_name"],
            record["market_name"],
            record["region"],
            record["unit"],
            record["update_date"].isoformat(),
        )
        unique[key] = record
    return list(unique.values())


def build_natural_key(record: Dict[str, Any]) -> Tuple[str, str, str, str, Any]:
    return (
        record["item_name"],
        record["market_name"],
        record["region"],
        record["unit"],
        record["update_date"],
    )


def bulk_upsert_market_prices(db: Session, records: List[Dict[str, Any]]) -> None:
    """시장 가격 데이터를 배치로 삽입 또는 업데이트합니다."""
    if not records:
        logger.info("저장할 마켓 가격 레코드가 없습니다.")
        return

    try:
        logger.info(f"마켓 가격 Upsert 시작: {len(records)}개 레코드")
        
        records = dedupe_records(records)
        logger.debug(f"중복 제거 완료: {len(records)}개 레코드")
        
        natural_keys = [build_natural_key(record) for record in records]
        dates = {record["update_date"] for record in records}
        item_names = {record["item_name"] for record in records}

        logger.debug(f"데이터베이스 조회: {len(item_names)}개 아이템, {len(dates)}개 날짜")
        existing = (
            db.query(MarketPrice)
            .filter(MarketPrice.update_date.in_(dates), MarketPrice.item_name.in_(item_names))
            .all()
        )
        logger.debug(f"기존 레코드 발견: {len(existing)}개")

        existing_map: Dict[Tuple[str, str, str, str, Any], MarketPrice] = {
            build_natural_key(
                {
                    "item_name": item.item_name,
                    "market_name": item.market_name,
                    "region": item.region,
                    "unit": item.unit,
                    "update_date": item.update_date,
                }
            ): item
            for item in existing
        }

        insert_rows: List[Dict[str, Any]] = []
        update_rows: List[Dict[str, Any]] = []

        for record in records:
            key = build_natural_key(record)
            existing_item = existing_map.get(key)
            if existing_item:
                update_data = {
                    "price_id": existing_item.price_id,
                    "price": record["price"],
                    "item_name": record["item_name"],
                    "unit": record["unit"],
                    "market_name": record["market_name"],
                    "region": record["region"],
                    "update_date": record["update_date"],
                }
                update_rows.append(update_data)
            else:
                insert_rows.append(record)

        if insert_rows:
            logger.info(f"{len(insert_rows)}개 새로운 마켓 가격 레코드 삽입 중...")
            db.bulk_insert_mappings(MarketPrice, insert_rows)
            logger.debug("삽입 완료")

        if update_rows:
            logger.info(f"{len(update_rows)}개 기존 마켓 가격 레코드 업데이트 중...")
            db.bulk_update_mappings(MarketPrice, update_rows)
            logger.debug("업데이트 완료")

        logger.debug("데이터베이스 커밋 중...")
        db.commit()
        logger.info(f"Upsert 완료: {len(insert_rows)}개 삽입, {len(update_rows)}개 업데이트")
        
    except Exception as e:
        db.rollback()
        logger.error(f"마켓 가격 Upsert 중 오류 발생: {str(e)}", exc_info=True)
        raise


def fetch_all_public_data(api_key: str, api_url: str) -> List[Dict[str, Any]]:
    """모든 공공 데이터를 페이지 단위로 가져옵니다."""
    all_records: List[Dict[str, Any]] = []
    page = 1
    
    try:
        logger.info("공공 데이터 전체 조회 시작")
        
        while True:
            logger.debug(f"페이지 {page} 조회 중...")
            response_json = fetch_public_data_page(api_key, api_url, page_no=page, num_of_rows=BATCH_SIZE)
            raw_items = extract_items_from_response(response_json)
            
            if not raw_items:
                logger.info(f"마지막 페이지 도달 (page={page})")
                break

            logger.debug(f"페이지 {page}: {len(raw_items)}개 항목 추출")
            parsed = parse_market_price_records(raw_items)
            logger.debug(f"페이지 {page}: {len(parsed)}개 항목 파싱 완료")
            all_records.extend(parsed)

            if len(raw_items) < BATCH_SIZE:
                logger.info(f"마지막 페이지 도달 (page={page}, items={len(raw_items)})")
                break

            page += 1

        logger.info(f"공공 데이터 조회 완료: 총 {len(all_records)}개 레코드")
        return all_records
        
    except Exception as e:
        logger.error(f"공공 데이터 조회 중 오류 (page={page}): {str(e)}", exc_info=True)
        raise


def run_crawler() -> None:
    """마켓 가격 크롤러를 실행합니다."""
    try:
        logger.info("=" * 60)
        logger.info("마켓 가격 크롤러 시작")
        logger.info("=" * 60)
        
        api_key = get_env_value(API_KEY_ENV)
        api_url = os.getenv(API_URL_ENV, DEFAULT_API_URL)

        if api_url == DEFAULT_API_URL:
            logger.warning(f"기본 API URL 사용: {API_URL_ENV} 환경변수로 수정 가능")

        logger.info(f"크롤러 시작: url={api_url}")
        records = fetch_all_public_data(api_key, api_url)
        logger.info(f"공공 데이터에서 {len(records)}개 레코드 조회 완료")

        if not records:
            logger.warning("조회된 레코드가 없습니다. 데이터베이스 업데이트 스킵")
            return

        logger.info("데이터베이스 세션 시작")
        db_generator, db_session = get_db_session()
        try:
            bulk_upsert_market_prices(db_session, records)
            logger.info("=" * 60)
            logger.info("마켓 가격 크롤러 완료 (성공)")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"데이터베이스 Upsert 실패: {str(e)}", exc_info=True)
            raise
        finally:
            db_generator.close()
            logger.debug("데이터베이스 세션 종료")
            
    except EnvironmentError as e:
        logger.error(f"환경 설정 오류: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"마켓 가격 크롤러 실패: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    # ===== Logging 설정 =====
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler('crawler.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        run_crawler()
    except Exception as exc:
        logger.error(f"크롤러 실패: {str(exc)}", exc_info=True)
        raise
