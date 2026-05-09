# models.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Text, Boolean, ARRAY, func
from sqlalchemy.dialects.postgresql import JSONB
from database import Base # database.py에서 정의한 Base 임포트

# 1. 실제 공공데이터 활용 테이블 (Market_Price)
class MarketPrice(Base):
    __tablename__ = "market_prices"

    price_id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    unit = Column(String(50))
    market_name = Column(String(100))
    region = Column(String(100))
    update_date = Column(Date, server_default=func.current_date())

# 2. LLM 생성 데이터 활용 테이블 (AI_Recipe)
class AIRecipe(Base):
    __tablename__ = "ai_recipes"

    recipe_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    main_ingredients = Column(ARRAY(String)) # ["애호박", "무"] 형태의 배열
    instructions = Column(JSONB)             # 조리 단계별 JSON (LLM 결과물)
    estimated_cost = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

# 3. LLM 생성 보관 가이드 테이블 (Storage_Guide)
class StorageGuide(Base):
    __tablename__ = "storage_guides"

    guide_id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), unique=True, nullable=False)
    storage_method = Column(Text)
    shelf_life_days = Column(Integer)
    is_freezable = Column(Boolean, default=True)