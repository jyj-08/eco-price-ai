import os
import json
from typing import List, Dict
from dotenv import load_dotenv
import google.generativeai as genai

# .env 파일 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=GEMINI_API_KEY)


def generate_recipe(ingredients: List[str]) -> Dict:
    """
    Gemini 1.5 Pro를 사용하여 저가형 레시피를 생성합니다.
    
    Args:
        ingredients: 사용할 재료 리스트 (예: ["애호박", "무", "계란"])
    
    Returns:
        JSON 형식의 레시피 데이터:
        {
            "title": str,
            "ingredients": list,
            "instructions": list or str,
            "cost_estimate": int
        }
    """
    
    # 모델 초기화
    model = genai.GenerativeModel("gemini-1.5-pro")
    
    # 재료 문자열 생성
    ingredients_str = ", ".join(ingredients)
    
    # 프롬프트 작성
    prompt = f"""너는 가성비 요리 전문가야. 입력된 재료를 활용하되, 가장 저렴하게 만들 수 있는 레시피를 제안해줘. 
결과는 반드시 다음 JSON 포맷으로 리턴해야 해:

{{
    "title": "요리 이름",
    "ingredients": ["재료1", "재료2", ...],
    "instructions": ["1단계", "2단계", "3단계", ...],
    "cost_estimate": 예상비용(원 단위)
}}

입력 재료: [{ingredients_str}]

주의:
- 조리 시간이 짧고 난이도가 낮아야 함
- 비용을 최소화하는 방향으로 레시피 제안
- 가능한 한 입력된 재료를 최대로 활용
- JSON만 반환 (추가 텍스트 없음)"""
    
    try:
        # Gemini API 호출
        response = model.generate_content(prompt)
        
        # 응답 텍스트 파싱
        response_text = response.text.strip()
        
        # JSON 추출 (마크다운 코드 블록 제거)
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # ```json 제거
        if response_text.startswith("```"):
            response_text = response_text[3:]  # ``` 제거
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # ``` 제거
        
        # JSON 파싱
        recipe_data = json.loads(response_text.strip())
        
        return recipe_data
    
    except json.JSONDecodeError as e:
        raise ValueError(f"AI 응답을 JSON으로 파싱할 수 없습니다: {e}")
    except Exception as e:
        raise Exception(f"Gemini API 호출 실패: {str(e)}")


# 테스트용 함수
if __name__ == "__main__":
    # 테스트 재료
    test_ingredients = ["애호박", "무", "계란", "양파", "마늘"]
    
    print("🍳 레시피 생성 중...")
    print(f"입력 재료: {test_ingredients}\n")
    
    recipe = generate_recipe(test_ingredients)
    
    print("=" * 50)
    print(f"📌 {recipe['title']}")
    print("=" * 50)
    print(f"\n🥘 재료:")
    for ingredient in recipe['ingredients']:
        print(f"  - {ingredient}")
    
    print(f"\n👨‍🍳 조리 순서:")
    if isinstance(recipe['instructions'], list):
        for i, instruction in enumerate(recipe['instructions'], 1):
            print(f"  {i}. {instruction}")
    else:
        print(f"  {recipe['instructions']}")
    
    print(f"\n💰 예상 비용: {recipe['cost_estimate']:,}원")
    print("\n" + "=" * 50)
    print("\n📋 JSON 형식:")
    print(json.dumps(recipe, ensure_ascii=False, indent=2))
