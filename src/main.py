from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from services import UserService
from database import fake_users_db
from models import User, Token

from webtool.cache import RedisCache
from webtool.utils import make_ed_key
from webtool.auth import JWTService

from dotenv import load_dotenv
import os


redis = RedisCache("redis://127.0.0.1:6379/0")
app = FastAPI()

user_service = UserService()
jwt_service = JWTService(redis, secret_key=make_ed_key())

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    user = User(**user_dict)
    if not user_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    # JWT 토큰 발급
    access_token, refresh_token = await jwt_service.create_token({"sub": form_data.username})
    return {"access_token": access_token, "token_type": refresh_token }


@app.get("/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    username = jwt_service.decode_access_token(token)
    user_dict = fake_users_db.get(username)
    if not user_dict:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user_dict)



