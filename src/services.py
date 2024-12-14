from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

from database import Session
from schema import UserCreate
from models import User

from dotenv import load_dotenv
import os

load_dotenv()

# 환경 변수 가져오기
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# JWT 구성 요소
ALGORITHM = "HS256"



class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def hash_password(self, password: str) -> str:
        """
        비밀번호를 해싱하여 반환
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        입력된 비밀번호가 저장된 해시와 일치하는지 확인
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def register_user(self, user: UserCreate, db: Session):
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # 비밀번호 해싱처리
        hashed_password = self.hash_password(user.password)

        # User 객체 생성 데이터베이스 추가
        new_user = User(username=user.username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user


class JWTService:
    def create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """
        JWT 토큰 생성
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_access_token(self, token: str) -> str:
        """
        JWT 토큰 디코딩
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise JWTError("Missing username in token")
            return username
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )