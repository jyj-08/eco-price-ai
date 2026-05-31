from database import SessionLocal
from models import MarketPrice
import json

db = SessionLocal()
items = db.query(MarketPrice).limit(5).all()
result = []
for item in items:
    result.append({
        "item_name": item.item_name,
        "price": item.price,
        "unit": item.unit,
        "market_name": item.market_name
    })
with open("db_output.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
db.close()
