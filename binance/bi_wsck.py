import os
import dotenv

# .env 파일 로드
dotenv.load_dotenv()

# 환경 변수 가져오기
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

print(API_KEY)
print(SECRET_KEY)