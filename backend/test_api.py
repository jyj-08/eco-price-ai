import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("PUBLIC_DATA_API_KEY")

# 상품정보 조회 엔드포인트 예시
url = "https://openapi.price.go.kr/openApiImpl/ProductPriceInfoService/getProductInfoSvc.do"
params = {
    "serviceKey": api_key,
    "format": "json" # XML이 기본이라면 json으로 요청 시도
}

response = requests.get(url, params=params)
print(f"상태 코드: {response.status_code}")
print(f"응답 내용: {response.text}")