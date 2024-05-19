# 베이스 이미지로 Python 3.9 이미지를 사용합니다.
FROM python:3.9-slim

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# 필요한 파일을 복사합니다.
COPY requirements.txt .

# 필요한 라이브러리를 설치합니다.
RUN pip install -r requirements.txt

# 소스 코드를 현재 컨테이너의 작업 디렉토리로 복사합니다.
COPY . .

# 컨테이너가 시작될 때 실행할 명령을 지정합니다.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
