from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import bcrypt

app = FastAPI()

# 데이터 모델
class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str # 서버 db password

# 가상 db
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "full_name": "John Doe",
        "disabled": False,
        "hashed_password": bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# 사용자 확인
def auth_user(username: str, password: str) -> Optional[UserInDB]:
    user_dict = fake_users_db.get(username)
    if not user_dict:
        return None
    user = UserInDB(**user_dict)  # UserInDB 객체 생성
    if not verify_password(password, user.hashed_password):
        return None
    return user


@app.post("/login/")
async def login(request: LoginRequest):
    user = auth_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"message": f"hi, {user.username}"}