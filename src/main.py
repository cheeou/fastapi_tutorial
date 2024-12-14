from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from webtool.cache import RedisCache
from webtool.utils import make_ed_key
from webtool.auth import JWTService

from services import UserService
from models import User
from database import Session
from schema import UserCreate
from database import init_db

from sqlalchemy import text


import logging

init_db()

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨: DEBUG, INFO, WARNING, ERROR, CRITICAL 중 선택
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


redis = RedisCache("redis://127.0.0.1:6379/0")
app = FastAPI()

user_service = UserService()
jwt_service = JWTService(redis, secret_key=make_ed_key())

# DB 세션 생성 의존성
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# UserService 생성
user_service = UserService()

@app.get("/test-db")
async def test_db_connection(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1"))
        return {"db_status": "connected", "result": result}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed",
        )

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # 사용자 이름 중복 체크
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        logger.warning(f"{user.username} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    try:
        # 비밀번호 해싱
        hashed_password = user_service.hash_password(user.password)

        # User 객체 생성 및 데이터베이스에 추가
        new_user = User(username=user.username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": f"User {new_user.username} created successfully"}
    except Exception as e:
        logger.error(f"{e}")
        raise HTTPException()

