from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from services import UserService, JWTService
from database import fake_users_db
from models import User, Token

app = FastAPI()

# 서비스 인스턴스 생성
user_service = UserService()
jwt_service = JWTService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # User 모델 생성
    user = User(**user_dict)

    # 비밀번호 검증
    if not user_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # JWT 토큰 발급
    access_token = jwt_service.create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    username = jwt_service.decode_access_token(token)
    user_dict = fake_users_db.get(username)
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_dict)