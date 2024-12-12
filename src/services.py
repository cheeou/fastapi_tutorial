from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

# JWT 구성 요소
SECRET_KEY = "606e4339bb801dce73f1bef013aba305d02ead1bc99a4db0f2998ecbfd7261b3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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