from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

from passlib.context import CryptContext

from pydantic import BaseModel

import logging

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

"""
SECRET_KEY/ALGORITHM/ACCESS_TOKEN_EXPIRE_MINUTES

JWT 토큰 발행 위한 필수 구성 요소

"""
SECRET_KEY = "606e4339bb801dce73f1bef013aba305d02ead1bc99a4db0f2998ecbfd7261b3" # jwt 토큰 서명,검증 할때 사용되는 키
ALGORITHM = "HS256" # jwt 토큰 생성시 사용할 암호화 해싱 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # 토큰 만료시간

"""
Passlib CryptContext 설정
bcrypt라는 알고리즘을 사용해 비밀번호를 해싱(암호화)하고, 
나중에 그 해시된 비밀번호를 검증(사용자가 입력한 비밀번호와 일치하는지 확인)
"""

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 가상 DB user 정보
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": pwd_context.hash("password123"), # bcrypt 해시 생성
    }
}

# 유저 모델
class User(BaseModel):
    username: str


class UserInDB(User):
    hashed_password: str

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    유저 패스워드 검증
    """
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db, username: str, password: str):
    """
    사용자 인증  검사

    """
    user = db.get(username)
    if not user:
        return None  # 유저가 존재하지 않음
    user_in_db = UserInDB(**user)
    if not verify_password(password, user_in_db.hashed_password):
        return None  # 비밀번호 불일치
    return user_in_db  #

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    JWT 토큰 생성 함수
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})  # 만료 시간 설정
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(fake_users_db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}