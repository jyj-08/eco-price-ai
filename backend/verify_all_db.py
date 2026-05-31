from database import SessionLocal
from models import MarketPrice
import json

db = SessionLocal()
items = db.query(MarketPrice).all()
result = {}
for item in items:
    if item.item_name not in result:
        result[item.item_name] = item.price
with open("all_items.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
db.close()
