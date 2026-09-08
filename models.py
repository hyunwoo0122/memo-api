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


