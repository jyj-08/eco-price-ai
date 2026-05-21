import os
import json
import re
import logging
from typing import List, Dict
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ===== Logging 설정 =====
logger = logging.getLogger(__name__)

# Gemini API 설정 시도 (실패해도 Mock 모드로 계속 동작)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
_genai_client = None

try:
    from google import genai
    if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key-here":
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini API 클라이언트 초기화 완료 (model=gemini-2.0-flash)")
    else:
        logger.warning("GEMINI_API_KEY 미설정 — Mock 모드로 동작합니다.")
except Exception as e:
    logger.warning(f"Gemini SDK 초기화 실패 — Mock 모드로 동작합니다: {e}")

MODEL_NAME = "gemini-2.0-flash"


def _extract_json(text: str) -> str:
    """AI 응답 텍스트에서 JSON 객체만 안전하게 추출합니다."""
    text = text.strip()
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def generate_recipe(ingredients: List[str]) -> Dict:
    """
    Gemini를 사용하여 저가형 레시피를 생성합니다.
    API 호출 실패 시 Mock 데이터를 반환합니다.
    """
    logger.info(f"레시피 생성 시작: 재료={ingredients}")
    ingredients_str = ", ".join(ingredients)

    # Gemini API 호출 시도
    if _genai_client:
        try:
            prompt = f"""너는 가성비 요리 전문가야. 입력된 재료를 활용하되, 가장 저렴하게 만들 수 있는 레시피를 제안해줘.
결과는 반드시 다음 JSON 포맷으로 리턴해야 해:

{{
    "title": "요리 이름",
    "ingredients": ["재료1", "재료2"],
    "instructions": ["1단계", "2단계", "3단계"],
    "cost_estimate": 예상비용(원 단위 정수)
}}

입력 재료: [{ingredients_str}]

주의:
- 조리 시간이 짧고 난이도가 낮아야 함
- 비용을 최소화하는 방향으로 레시피 제안
- JSON만 반환 (추가 텍스트 없음)"""

            response = _genai_client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            logger.debug(f"Gemini API 응답 수신: 크기={len(response.text)}자")
            response_text = _extract_json(response.text)
            recipe_data = json.loads(response_text)
            logger.info(f"레시피 생성 완료: title={recipe_data.get('title')}")
            return recipe_data

        except Exception as e:
            logger.warning(f"Gemini API 호출 실패 — Mock 레시피 반환: {e}")

    # Fallback: Mock 레시피 데이터 반환
    logger.info("Mock 레시피 데이터 반환")
    return {
        "title": f"{ingredients[0] if ingredients else '재료'} 활용 가성비 요리",
        "ingredients": ingredients + ["소금", "참기름", "마늘"],
        "instructions": [
            "재료를 깨끗이 씻어 준비합니다.",
            "팬에 기름을 두르고 마늘을 볶습니다.",
            f"{ingredients_str}를 넣고 중불에서 5분간 볶습니다.",
            "소금으로 간을 맞추고 참기름을 넣어 완성합니다.",
        ],
        "cost_estimate": 5000,
    }


def generate_storage_guide(item_name: str) -> Dict:
    """
    Gemini를 사용하여 식재료의 보관 가이드를 생성합니다.
    API 호출 실패 시 Mock 데이터를 반환합니다.
    """
    logger.info(f"보관 가이드 생성 시작: item_name={item_name}")

    # Gemini API 호출 시도
    if _genai_client:
        try:
            prompt = f"""너는 식재료 보관 전문가야. 주어진 식재료의 최적 보관 방법을 제안해줘.
결과는 반드시 다음 JSON 포맷으로 리턴해야 해:

{{
    "item_name": "{item_name}",
    "storage_method": "보관 방법 상세 설명 (냉장/냉동 여부, 온도, 용기 등)",
    "shelf_life_days": 유통기한(일 수 정수),
    "is_freezable": true 또는 false
}}

식재료: {item_name}

주의:
- storage_method는 구체적이고 실용적이어야 함
- shelf_life_days는 개봉 후 냉장 보관 기준 정수값
- JSON만 반환 (추가 텍스트 없음)"""

            response = _genai_client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            logger.debug(f"Gemini API 응답 수신: 크기={len(response.text)}자")
            response_text = _extract_json(response.text)
            storage_data = json.loads(response_text)
            logger.info(f"보관 가이드 생성 완료: item_name={item_name}, shelf_life={storage_data.get('shelf_life_days')}일")
            return storage_data

        except Exception as e:
            logger.warning(f"Gemini API 호출 실패 — Mock 보관 가이드 반환: {e}")

    # Fallback: Mock 보관 가이드 데이터 반환
    logger.info(f"Mock 보관 가이드 데이터 반환: item_name={item_name}")
    return {
        "item_name": item_name,
        "storage_method": "실온 보관 시 서늘하고 통풍이 잘되는 곳에 두시고, 장기 보관 시 밀폐 용기에 담아 냉장/냉동 보관하세요.",
        "shelf_life_days": 30,
        "is_freezable": True,
    }
