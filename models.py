# 테이블에 어떤 컬럼(열)이 있는지를 정의 하는 파일
from sqlalchemy import Column, Integer, String
from database import Base

# Base를 상속받아 실제 테이블을 나타내는 클래스를 만듬
class MemoDB(Base):
    # 실제 SQLite 안에 생성될 테이블 이름을 지정합니다.
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)

# Base를 상속받아 테이블을 정의 
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # 사용자 이름을 저장하는 컬럼 unique는 중복불가를 해주는 역할
    username = Column(String, unique=True, index=True)
    # 비밀번호를 저장할때 암호화 해주는 부분
    hashed_password = Column(String)
