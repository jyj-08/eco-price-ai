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
    value = os.getenv(key, "")
    if required and not value:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value


def get_db_session() -> Tuple[Generator[Session, None, None], Session]:
    db_generator = get_db()
    db_session = next(db_generator)
    return db_generator, db_session


def fetch_public_data_page(api_key: str, api_url: str, page_no: int = 1, num_of_rows: int = 500) -> Dict[str, Any]:
    params = {
        "serviceKey": api_key,
        "pageNo": page_no,
        "numOfRows": num_of_rows,
        "_type": "json",
    }

    response = requests.get(api_url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


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
    if not records:
        logger.info("No market price records to upsert.")
        return

    records = dedupe_records(records)
    natural_keys = [build_natural_key(record) for record in records]
    dates = {record["update_date"] for record in records}
    item_names = {record["item_name"] for record in records}

    existing = (
        db.query(MarketPrice)
        .filter(MarketPrice.update_date.in_(dates), MarketPrice.item_name.in_(item_names))
        .all()
    )

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
        logger.info("Inserting %d new market price records.", len(insert_rows))
        db.bulk_insert_mappings(MarketPrice, insert_rows)

    if update_rows:
        logger.info("Updating %d existing market price records.", len(update_rows))
        db.bulk_update_mappings(MarketPrice, update_rows)

    db.commit()
    logger.info("Upsert completed: %d inserted, %d updated.", len(insert_rows), len(update_rows))


def fetch_all_public_data(api_key: str, api_url: str) -> List[Dict[str, Any]]:
    all_records: List[Dict[str, Any]] = []
    page = 1

    while True:
        response_json = fetch_public_data_page(api_key, api_url, page_no=page, num_of_rows=BATCH_SIZE)
        raw_items = extract_items_from_response(response_json)
        if not raw_items:
            break

        parsed = parse_market_price_records(raw_items)
        all_records.extend(parsed)

        if len(raw_items) < BATCH_SIZE:
            break

        page += 1

    return all_records


def run_crawler() -> None:
    api_key = get_env_value(API_KEY_ENV)
    api_url = os.getenv(API_URL_ENV, DEFAULT_API_URL)

    if api_url == DEFAULT_API_URL:
        logger.warning(
            "Using default API URL. Set %s in .env to override the public data endpoint.",
            API_URL_ENV,
        )

    logger.info("Starting market price crawler. url=%s", api_url)
    records = fetch_all_public_data(api_key, api_url)
    logger.info("Fetched %d records from public data source.", len(records))

    if not records:
        logger.warning("No records were fetched; skipping database upsert.")
        return

    db_generator, db_session = get_db_session()
    try:
        bulk_upsert_market_prices(db_session, records)
    finally:
        db_generator.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    try:
        run_crawler()
    except Exception as exc:
        logger.exception("Crawler failed: %s", exc)
        raise
