# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models # 중요: 테이블 인식을 위해 models를 반드시 임포트해야 합니다.

# 앱 시작 시 DB에 테이블 자동 생성 (DDL 실행)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Eco-Price AI Service")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Eco-Price AI Database Connected"}

# 예시: DB 세션을 사용하는 라우터
@app.get("/items")
def read_prices(db: Session = Depends(get_db)):
    # db 세션을 통해 쿼리 수행 가능
    return db.query(models.MarketPrice).all()