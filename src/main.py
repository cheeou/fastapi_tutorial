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
async def test_db_connection(db: Annotated[Session, Depends(get_db)]):
    try:
        result = db.execute(text("SELECT 1"))
        return {"db_status": "connected", "result": result}
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed",
        )

@app.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User created"},
    },
)
async def register(user: UserCreate, db: Annotated[Session, Depends(get_db)]):

    try:
        new_user = user_service.register_user(user, db)
        return {"message": f"User {new_user.username} registered"}

    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )




