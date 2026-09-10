# passlib 도구를 가져온다
from passlib.context import CryptContext

# bcrypt방식으로 비밀번호를 보호한다 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # 원본 비밀번호를 받아서 암호화된 문자열로 바꿔 반환한다
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 저장된 암호와 같은지 판별해줌
    return pwd_context.verify(plain_password, hashed_password)