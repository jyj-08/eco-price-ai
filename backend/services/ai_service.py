import os
import json
import re
import logging
from typing import List, Dict
from dotenv import load_dotenv
from google import genai

# .env 파일 로드
load_dotenv()

# ===== Logging 설정 =====
logger = logging.getLogger(__name__)

# ===== Gemini API 키 검증 (비어있으면 즉시 서버 중단) =====
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your-gemini-api-key-here":
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

# ===== SDK 임포트 검증 (실패 시 즉시 서버 중단) =====
try:
    from google import genai
except ImportError:
    raise ImportError("google-genai 패키지가 설치되지 않았습니다.")

# ===== 클라이언트 초기화 =====
try:
    _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    logger.info(
        f"Gemini API 클라이언트 초기화 완료 (model=gemini-1.5-flash) | "
        f"KEY 앞 8자: {GEMINI_API_KEY[:8]}..."
    )
except Exception as e:
    raise RuntimeError(f"Gemini 클라이언트 생성 실패: {e}") from e

MODEL_NAME = "gemini-3.5-flash"


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
    API 호출 중 발생하는 모든 예외는 그대로 상위로 전파됩니다.
    """
    # ===== [1] 강력한 클라이언트 검증 =====
    if not _genai_client:
        raise ValueError(
            "Gemini API 키가 설정되지 않았거나 클라이언트가 초기화되지 않았습니다. "
            ".env 파일을 확인하세요."
        )

    logger.info(f"[generate_recipe] 시작 — 재료={ingredients}")
    ingredients_str = ", ".join(ingredients)

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

    # ===== [3] 강제 에러 전파: API 호출 실패 시 RuntimeError로 래핑해서 전파 =====
    try:
        logger.info(f"[generate_recipe] Gemini API 호출 시작 (model={MODEL_NAME})")
        response = _genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        logger.info(f"[generate_recipe] Gemini API 응답 수신: {len(response.text)}자")
        logger.debug(f"[generate_recipe] 원본 응답:\n{response.text}")
    except Exception as e:
        logger.error(
            f"[generate_recipe] Gemini API 호출 실패! "
            f"에러 타입: {type(e).__name__} | 메시지: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"AI 서버 통신 에러: {str(e)}") from e

    # ===== [2] JSON 파싱 방어 코드: AI 원본 응답을 에러 메시지에 포함 =====
    try:
        response_text = _extract_json(response.text)
        recipe_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(
            f"[generate_recipe] JSON 파싱 실패! "
            f"원본 응답: {response.text!r} | 에러: {e}",
            exc_info=True,
        )
        raise ValueError(f"AI JSON 파싱 실패: {response_text}") from e

    logger.info(f"[generate_recipe] 완료 — title={recipe_data.get('title')}")
    return recipe_data


def generate_storage_guide(item_name: str) -> Dict:
    """
    Gemini를 사용하여 식재료의 보관 가이드를 생성합니다.
    API 호출 중 발생하는 모든 예외는 그대로 상위로 전파됩니다.
    """
    # ===== [1] 강력한 클라이언트 검증 =====
    if not _genai_client:
        raise ValueError(
            "Gemini API 키가 설정되지 않았거나 클라이언트가 초기화되지 않았습니다. "
            ".env 파일을 확인하세요."
        )

    logger.info(f"[generate_storage_guide] 시작 — item_name={item_name}")

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

    # ===== [3] 강제 에러 전파: API 호출 실패 시 RuntimeError로 래핑해서 전파 =====
    try:
        logger.info(f"[generate_storage_guide] Gemini API 호출 시작 (model={MODEL_NAME})")
        response = _genai_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )
        logger.info(f"[generate_storage_guide] Gemini API 응답 수신: {len(response.text)}자")
        logger.debug(f"[generate_storage_guide] 원본 응답:\n{response.text}")
    except Exception as e:
        logger.error(
            f"[generate_storage_guide] Gemini API 호출 실패! "
            f"에러 타입: {type(e).__name__} | 메시지: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"AI 서버 통신 에러: {str(e)}") from e

    # ===== [2] JSON 파싱 방어 코드: AI 원본 응답을 에러 메시지에 포함 =====
    try:
        response_text = _extract_json(response.text)
        storage_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(
            f"[generate_storage_guide] JSON 파싱 실패! "
            f"원본 응답: {response.text!r} | 에러: {e}",
            exc_info=True,
        )
        raise ValueError(f"AI JSON 파싱 실패: {response_text}") from e

    logger.info(
        f"[generate_storage_guide] 완료 — item_name={item_name}, "
        f"shelf_life={storage_data.get('shelf_life_days')}일"
    )
    return storage_data
