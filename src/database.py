from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
"""
DATABASE_URL = "postgresql://myuser:mypassword@localhost:portnumber/myshop"
':///' : 상대적 경로
':////': 절대적 경로
':memory': 스토리지 X, 메모리에서 임시적으로 DB 사용. 접속 끊기면 DB 리셋
"""

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
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized")
