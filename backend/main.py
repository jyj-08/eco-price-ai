# main.py
import logging
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import engine, Base, get_db
from services.ai_service import generate_recipe, generate_storage_guide
import models  # 중요: 테이블 인식을 위해 models를 반드시 임포트해야 합니다.

# ===== Logging 설정 =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 앱 시작 시 DB에 테이블 자동 생성 (DDL 실행)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eco-Price AI Service")

logger.info("FastAPI 애플리케이션 시작")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 요청 로깅 미들웨어 =====
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """모든 API 요청과 응답을 로깅합니다."""
    
    # 요청 정보
    request_id = datetime.now().isoformat()
    client_ip = request.client.host if request.client else "Unknown"
    logger.info(
        f"[요청 시작] {request.method} {request.url.path} | "
        f"클라이언트: {client_ip} | ID: {request_id}"
    )
    
    try:
        response = await call_next(request)
        logger.info(
            f"[요청 완료] {request.method} {request.url.path} | "
            f"상태코드: {response.status_code} | ID: {request_id}"
        )
        return response
    except Exception as e:
        logger.error(
            f"[요청 에러] {request.method} {request.url.path} | "
            f"에러: {str(e)} | ID: {request_id}", 
            exc_info=True
        )
        raise


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


class StorageGuideResponse(BaseModel):
    """보관 가이드 응답 모델"""
    guide_id: int
    item_name: str
    storage_method: str
    shelf_life_days: int
    is_freezable: bool

    class Config:
        from_attributes = True


# ===== 헬스 체크 =====
@app.get("/")
def health_check():
    logger.info("헬스 체크 요청")
    return {"status": "ok", "message": "Eco-Price AI Database Connected"}


# ===== 마켓 가격 조회 (기존) =====
@app.get("/items")
def read_prices(q: str = Query(None, description="아이템 이름 검색 키워드"), db: Session = Depends(get_db)):
    """마켓 가격 데이터를 조회합니다. 검색 키워드가 제공되면 아이템 이름으로 필터링합니다."""
    try:
        logger.info(f"마켓 가격 조회 요청: 검색어='{q}'")
        
        # 기본 쿼리
        query = db.query(models.MarketPrice)
        
        # 검색 키워드가 제공되면 필터링
        if q:
            query = query.filter(models.MarketPrice.item_name.ilike(f"%{q}%"))
            logger.debug(f"검색 필터 적용: item_name ILIKE '%{q}%'")
        
        prices = query.all()
        logger.info(f"마켓 가격 조회 완료: {len(prices)}개 항목" + (f" (검색어: '{q}')" if q else ""))
        
        return prices
    except Exception as e:
        logger.error(f"마켓 가격 조회 중 오류 발생: 검색어='{q}', 에러={str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"마켓 가격 조회 오류: {str(e)}")


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
    logger.info(f"AI 레시피 생성 요청: 재료={request.ingredients}")
    
    try:
        # 1. AI 서비스에서 레시피 생성
        logger.debug("Gemini AI 호출 시작...")
        recipe_data = generate_recipe(request.ingredients)
        logger.info(f"AI 레시피 생성 완료: {recipe_data.get('title', '제목 없음')}")
        
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
        
        logger.debug("AI 레시피 데이터베이스 저장 시작...")
        db.add(ai_recipe)
        db.commit()
        db.refresh(ai_recipe)
        logger.info(f"AI 레시피 데이터베이스 저장 완료: recipe_id={ai_recipe.recipe_id}")
        
        return ai_recipe
    
    except ValueError as e:
        logger.warning(f"AI 레시피 생성 입력 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=f"입력 오류: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"AI 레시피 생성 중 심각한 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"레시피 생성 오류: {str(e)}")


# ===== 보관 가이드 조회 및 생성 =====
@app.get("/api/storage/{item_name}", response_model=StorageGuideResponse)
def get_storage_guide(item_name: str, db: Session = Depends(get_db)):
    """
    식재료의 보관 가이드를 조회합니다.
    DB에 없으면 AI로 생성 후 저장합니다.
    
    Args:
        item_name: 식재료 이름
        db: 데이터베이스 세션
    
    Returns:
        보관 가이드 정보
    """
    logger.info(f"보관 가이드 조회 요청: item_name={item_name}")
    
    try:
        # 1. DB에서 기존 보관 가이드 조회
        logger.debug(f"데이터베이스에서 '{item_name}' 보관 가이드 검색...")
        existing_guide = db.query(models.StorageGuide).filter(
            models.StorageGuide.item_name == item_name
        ).first()
        
        if existing_guide:
            logger.info(f"기존 보관 가이드 발견: guide_id={existing_guide.guide_id}")
            return existing_guide
        
        # 2. DB에 없으면 AI로 생성
        logger.info(f"새로운 보관 가이드 생성 시작: item_name={item_name}")
        logger.debug("Gemini AI 호출 시작...")
        storage_data = generate_storage_guide(item_name)
        logger.info(f"AI 보관 가이드 생성 완료: {item_name}")
        
        # 3. 데이터베이스에 저장
        storage_guide = models.StorageGuide(
            item_name=storage_data.get("item_name", item_name),
            storage_method=storage_data.get("storage_method", ""),
            shelf_life_days=storage_data.get("shelf_life_days", 7),
            is_freezable=storage_data.get("is_freezable", True),
        )
        
        logger.debug("보관 가이드 데이터베이스 저장 시작...")
        db.add(storage_guide)
        db.commit()
        db.refresh(storage_guide)
        logger.info(f"보관 가이드 데이터베이스 저장 완료: guide_id={storage_guide.guide_id}")
        
        return storage_guide
    
    except ValueError as e:
        logger.warning(f"보관 가이드 생성 입력 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=f"입력 오류: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"보관 가이드 생성 중 심각한 오류 발생: item_name={item_name}, 에러={str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"보관 가이드 생성 오류: {str(e)}")