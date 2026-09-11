# passlib 도구를 가져온다
from passlib.context import CryptContext
# 토큰의 만료시간,
from datetime import datetime, timedelta
# 실제로 토큰을 만들고 해석하는 기능
from jose import jwt



# bcrypt방식으로 비밀번호를 보호한다 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # 원본 비밀번호를 받아서 암호화된 문자열로 바꿔 반환한다
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 저장된 암호와 같은지 판별해줌
    return pwd_context.verify(plain_password, hashed_password)

# 토큰을 암호화 할때 사용하는 비밀키
SECRET_KEY = "temporary-secret-key-change-later"
# 알고리즘 이름 JWT에서 널리 쓰이는 알고리즘
ALGORITHM = "HS256"
# 토큰 만료시간을 설정. 짦게 하는 이유는 길게 하면 탈취당할 확률이 있기 떄문
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    # 원본데이터를 건들지 않기 위해 복사
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)