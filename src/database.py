from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

import os

dotenv_path = Path(__file__).resolve().parent.parent / "docker/.env"
load_dotenv(dotenv_path)

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES__USER')}:{os.getenv('POSTGRES__PASSWORD')}@{os.getenv('POSTGRES__HOST')}:{os.getenv('POSTGRES__PORT')}/{os.getenv('POSTGRES__DB')}"
print(f"pos host>>>>>>>>>{os.getenv("POSTGRES__HOST")}")
"""
DATABASE_URL = "postgresql://myuser:mypassword@localhost:portnumber/myshop"
':///' : 상대적 경로
':////': 절대적 경로
':memory': 스토리지 X, 메모리에서 임시적으로 DB 사용. 접속 끊기면 DB 리셋
"""

print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True) # echo=True : SQL 쿼리 출력

"""
Sesstion : DB에 연결하여 쿼리를 실행하고 CRUD, 트랜젝션 작업, DB 연결 관리
"""
Session = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

"""
Declaretive mapping

declareative_base() -> Base 
-Base 상속 받아 ORM 클래스와 DB 맵핑

"""
class Base(DeclarativeBase):
    pass

def init_db():
    from src.models import User
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
