# DB에 어떻게 연결할지 담당하는 파일
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 사용항 DB위치. sqlite:///.뒤에 파일경로, memo.db라는 파일을 만들어 사용해라(자동으로 만들어짐)
SQLALCHEMY_DATABASE_URL = "sqlite:///./memo.db" 

#이 URL을 바탕으로 실제 DB와 연결을 담당하는 엔진객체를 만듬 
# connect_args={"check_same_thread": False}는 SQLite를 FastAPI와 함께 쓸 때 필요한 설정값
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread" : False})

# DB와 대화(쿼리실행)를 할 때 사용할 세션을 만드는 틀. API가 요청 받을때마다 이 세션을 하나씩 열어서 DB작업을 하게 된다
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

# 앞으로 만들 DB테이블 클래스들이 공통으로 상속받은 기본 클래스.
Base = declarative_base()