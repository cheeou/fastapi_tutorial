# 1. 베이스 이미지 설정
FROM python:3.12-slim

# 2. 작업 디렉토리 설정
WORKDIR /app



# 3. 종속성 설치
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root --no-dev
# Install uvicorn explicitly
RUN poetry add uvicorn

# 4. 소스 코드 복사
COPY ./src /app/src

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]