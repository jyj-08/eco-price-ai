import requests
import json

url = "http://211.237.50.150:7080/openapi/0b998f4534d4a1cde328426d5acb6b0bfdb79d7162898e131d41f14bcfc12193/json/Grid_20260128000000000689_1/1/100"
response = requests.get(url)
data = response.json()
grid_key = "Grid_20260128000000000689_1"
rows = data[grid_key].get("row", [])

item_names = [row.get("ITEM_NM", "") for row in rows]
with open("item_names.txt", "w", encoding="utf-8") as f:
    for name in item_names:
        f.write(name + "\n")
