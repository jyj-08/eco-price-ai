import sys

file_path = r'c:\dev\GitHub\eco-price-ai\backend\services\ai_service.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

new_content = content.replace('response = model.generate_content(prompt)', '''try:
            response = model.generate_content(prompt, request_options={"timeout": 10.0})
        except Exception as e:
            logger.error(f"Gemini API 시간 초과 또는 네트워크 오류: {str(e)}")
            raise TimeoutError("AI 응답 지연: 10초를 초과하여 요청이 취소되었습니다.")''')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Replaced')
