from fastapi import FastAPI
from starlette.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

class Address(BaseModel):
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address

@app.get("/")
def index():
    return 'hello'

@app.get("/data")
def get_data():
    return {'hello': "hello text"}

@app.get("/index")
def get_file_data():
    return FileResponse('index.html')

@app.post("/send")
def send_db(data: User):
    return "전송완료"