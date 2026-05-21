import sys
import re

file_path = r'c:\dev\GitHub\eco-price-ai\backend\services\ai_service.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update model
content = content.replace('model = genai.GenerativeModel("gemini-1.5-pro")', 'model = genai.GenerativeModel("gemini-1.5-flash")')

# 2. Add timeout to generate_content
timeout_code = '''try:
            response = model.generate_content(prompt, request_options={"timeout": 10.0})
        except Exception as e:
            logger.error(f"Gemini API 시간 초과 또는 네트워크 오류: {str(e)}")
            raise TimeoutError("AI 응답 지연: 10초를 초과하여 요청이 취소되었습니다.")'''

content = content.replace('response = model.generate_content(prompt)', timeout_code)

# 3. Add robust JSON parsing
old_json_parse = '''# JSON 추출 (마크다운 코드 블록 제거)
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # ```json 제거
        if response_text.startswith("```"):
            response_text = response_text[3:]  # ``` 제거
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # ``` 제거
        
        # JSON 파싱
        recipe_data = json.loads(response_text.strip())'''

new_json_parse_recipe = '''# JSON 추출 (정규식 사용)
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx+1]
        
        # JSON 파싱
        recipe_data = json.loads(response_text)'''

content = content.replace(old_json_parse, new_json_parse_recipe)

old_json_parse_storage = '''# JSON 추출 (마크다운 코드 블록 제거)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # JSON 파싱
        storage_data = json.loads(response_text.strip())'''

new_json_parse_storage = '''# JSON 추출 (정규식 사용)
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_text = response_text[start_idx:end_idx+1]
        
        # JSON 파싱
        storage_data = json.loads(response_text)'''

content = content.replace(old_json_parse_storage, new_json_parse_storage)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated ai_service.py successfully")
