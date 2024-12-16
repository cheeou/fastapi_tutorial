from pydantic import BaseModel, Field

# 공통 데이터 스키마
class UserBase(BaseModel):
    username: str
    disabled: bool = False  # 기본값 설정

    class Config:
        from_attributes = True


# 사용자 생성 시 요청 스키마
class UserCreate(UserBase):
    password: str
    class Config:
        from_attributes = True  # V2->SQLAlchemy 모델과 호환 설정
        # orm_mode = True -> V1

