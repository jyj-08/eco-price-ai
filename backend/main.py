# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import engine, Base, get_db
from services.ai_service import generate_recipe
import models  # 중요: 테이블 인식을 위해 models를 반드시 임포트해야 합니다.

# 앱 시작 시 DB에 테이블 자동 생성 (DDL 실행)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eco-Price AI Service")


# ===== Pydantic 스키마 =====
class RecipeRequest(BaseModel):
    """AI 레시피 생성 요청 모델"""
    ingredients: List[str]


class RecipeResponse(BaseModel):
    """AI 레시피 응답 모델"""
    recipe_id: int
    title: str
    main_ingredients: List[str]
    instructions: dict | str
    estimated_cost: int
    created_at: str

    class Config:
        from_attributes = True


# ===== 헬스 체크 =====
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Eco-Price AI Database Connected"}


# ===== 마켓 가격 조회 (기존) =====
@app.get("/items")
def read_prices(db: Session = Depends(get_db)):
    # db 세션을 통해 쿼리 수행 가능
    return db.query(models.MarketPrice).all()


# ===== AI 레시피 생성 및 저장 =====
@app.post("/api/ai/recipe", response_model=RecipeResponse)
def create_ai_recipe(request: RecipeRequest, db: Session = Depends(get_db)):
    """
    Gemini AI를 사용해 저가형 레시피를 생성하고 DB에 저장합니다.
    
    Args:
        request: 재료 리스트를 포함한 요청 객체
        db: 데이터베이스 세션
    
    Returns:
        저장된 레시피 정보
    """
    try:
        # 1. AI 서비스에서 레시피 생성
        recipe_data = generate_recipe(request.ingredients)
        
        # 2. ingredients가 list인지 확인, instructions이 dict 또는 list인지 확인
        ingredients = recipe_data.get("ingredients", request.ingredients)
        if not isinstance(ingredients, list):
            ingredients = [ingredients]
        
        instructions = recipe_data.get("instructions", "")
        
        # 3. 데이터베이스에 저장
        ai_recipe = models.AIRecipe(
            title=recipe_data.get("title", "제목 없음"),
            main_ingredients=ingredients,
            instructions=instructions,  # JSONB는 dict 또는 list를 자동 변환
            estimated_cost=recipe_data.get("cost_estimate", 0),
        )
        
        db.add(ai_recipe)
        db.commit()
        db.refresh(ai_recipe)
        
        return ai_recipe
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"입력 오류: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"레시피 생성 오류: {str(e)}")