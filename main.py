# FastAPI패키지에서 FastAPI라는 클래스를 가져온다.
# Depends는 FastAPI에게 이 함수를 실행하기 전에 의존성을 먼저 실행시켜주는 역할
from fastapi import FastAPI, Depends, HTTPException

# HTTPBearer → "요청 헤더에 Authorization: Bearer <토큰> 형식으로 값이 왔는지" 자동으로 확인해주는 FastAPI의 보안 도구
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from pydantic import BaseModel
from database import Base, engine
import models
# 요청이 들어올때 마다 database.py에서 만든 SessionLocal로 세션을 하나 열어서, 그 세션으로 DB에 쿼리를 보내야 한다.
# FastAPI에서는 이걸 Dependency(의존성 주입)이라는 방식으로 처리 한다
from sqlalchemy.orm import Session
from database import SessionLocal

import auth


app = FastAPI() # 클래스를 실제 애플리케이션 객체 app을 만든다. 이후 모든 API는 app에 등록된다

# Base에 등록된 모든 테이블 정의를 실제로 engine이 연결된 DB에 생성하라는 뜻.
Base.metadata.create_all(bind=engine)

def get_db():
    # 새 DB세션을 하나 연다
    db = SessionLocal()
    try :
        # 값을 잠깐 넘겨주고 다시 이 함수로 돌아온다
        yield db
    finally :
        db.close()

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        # 토큰이 위조 되었거나 다른 키로 만들어져 있으면 에러가 발생함(JWTError)
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail= "유효하지 않은 토큰입니다.")
    except JWTError:
        raise HTTPException(status_code= 401, detail= "유효하지 않은 토큰입니다.")

    user = db.query(models.UserDB).filter(models.UserDB.username == username).first()
    if user is None:
        raise HTTPException(status_code= 401, detail= "사용자를 찾을 수 없습니다.")

    return user
    
class Memo(BaseModel): # BaseModel을 상속받아 Memo라는 새 클라스를 정의 하고 "메모 하나의 데이터 형태"를 나타냄
    # 메모가 반드시 가져야 하는 항목
    title: str
    content: str

class UserCreate(BaseModel):
    username: str
    password: str

# id를 포함한 정보를 응답받음 
class MemoResponse(BaseModel):
    id: int
    title: str
    content: str

    # 원래 Pydantic은 딕셔너리를 기대하는데 True로 하면 SQLAlchemy객체(MemoDB 인스턴스)처럼 같은 속성의 값도 가져온다 
    class Config:
        from_attributes = True

@app.get("/health") # 데코레이션 >> /health라는 주소로 GET방식의 요청이 왔을때 바로 아래 함수를 실행해라
def health_check(): # 실제로 실행되는 함수
    return {"status": "ok"} # Python 딕셔너리를 FastAPI가 자동으로 JSON으로 변환해 응답한다


@app.get("/memos/{memo_id}") # URL경로 안에 {memo_id}라는 자리를 만들어 매개변수를 전달함
def get_memo(memo_id: int): # 받는 값이 URL의 매개변수와 같아야 한다. int는 타입을 미리 알려줘서 문자열 같은걸 자동으로 정수형으로 변환시켜준다. FaastAPI가 알아서 Erorr를 반환해줌.
    return {"memo_id": memo_id} # 지금은 확인용 Json

@app.get("/memos", response_model=list[MemoResponse])
def get_memos(db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)): # DB세션을 주입
    return db.query(models.MemoDB).filter(models.MemoDB.user_id == current_user.id).all()  # MemoDB 테이블에 있는 모든 행을 조회해서 리스트로 돌려줌

@app.post("/memos", response_model=MemoResponse) # /memos주소로 POST방식의 요청이 왔을때 바로 아래 함수를 실행(GET은 데이터 조회, POST는 데이터 생성)
# 매개변수를 위에서 만든 Memo클래스 타입으로 지정. 요청에 들어온 JSON을 자동으로 클래스 타입인 Memo로 변환
# Depends(get_db)는 "이 요청이 들어올 때마다 get_db()를 실행해서 얻은 세션을 db에 넣어달라"는 뜻
def create_memo(memo: Memo, db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)): 
    # 요청으로 받은 Pydantic Memo 객체(memo)의 값을 이용해서, DB 테이블용 객체(MemoDB)를 새로 만듬
    # (Pydantic 모델과 DB 모델이 이름은 비슷해도 서로 다른 객체라 이렇게 변환해줘야 한다)
    new_memo = models.MemoDB(title=memo.title, content=memo.content, user_id = current_user.id)
    # 이 객체를 DB 세션에 "추가할 예정"으로 등록 (아직 실제 DB에 저장된 건 아님)
    db.add(new_memo)
    # 지금까지 등록된 변경사항을 실제로 DB 파일에 반영(저장)함. 이 줄이 실행돼야 진짜 저장이 완료
    db.commit()
    # DB가 자동으로 채워준 값(예: id)을 new_memo 객체에 다시 불러온다. (커밋 직후엔 id가 아직 비어있을 수 있어서 필요합니다.)
    db.refresh(new_memo)
    return new_memo

# URL에서 어떤 메모를 수정할지 ID를 받음
@app.put("/memos/{memo_id}", response_model=MemoResponse) 
# 3가지 변수를 한번에 받음. URL의 memo_id, 요청본문의 새 내용, 
def update_memo(memo_id: int, memo: Memo, db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    # 테이블에서 ID가 같은 첫번째 행을 찾아 가져온다
    db_memo = db.query(models.MemoDB).filter(models.MemoDB.id == memo_id).first()

    # ID가 같지 않음 404에러를 출력시킨다
    if db_memo is None:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")

    # 403 > 누구인지는 확인 했지만 권한이 없다 401 > 누구인지 조차 몰라
    if db_memo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="이 메모를 수정할 권한이 없습니다.")

    # 찾은ID의 값을 새 값으로 덮어씌운다
    db_memo.title = memo.title
    db_memo.content = memo.content
    # 실제로 반영
    db.commit()
    # 최신상태를 불러온다 
    db.refresh(db_memo)
    return db_memo

# URL에서 어떤 메모를 수정할지 ID를 받음
@app.delete("/memos/{memo_id}") 
# 3가지 변수를 한번에 받음. URL의 memo_id, 요청본문의 새 내용, 
def delete_memo(memo_id: int, db: Session = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    # 테이블에서 ID가 같은 첫번째 행을 찾아 가져온다
    db_memo = db.query(models.MemoDB).filter(models.MemoDB.id == memo_id).first()

    # ID가 같지 않음 404에러를 출력시킨다
    if db_memo is None:
        raise HTTPException(status_code=404, detail="메모를 찾을 수 없습니다.")

    if db_memo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="이 메모를 수정할 권한이 없습니다.")



    # 찾은ID의 값을 지운다
    db.delete(db_memo)
    # 실제로 반영
    db.commit()
    return {"message": "삭제되었습니다."}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # username이 있는지 확인
    existring_user = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()

    if existring_user:
        # 400인 이유 : 요청 자체가 잘못되었기 떄문에 404 : 찾는 대상이 없음
        raise HTTPException(status_code=400, detail="이미 존재하는 ID입니다.")

    # 비밀번호를 암호화
    hashed_pw = auth.hash_password(user.password)
    new_user = models.UserDB(username = user.username, hashed_password = hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "회원가입 성공", "username": new_user.username} 

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()

    # ID, PW 둘중 하나라고 없으면을 체크
    if db_user is None or not auth.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code= 401, detail= "ID 또는 PW가 올바르지 않습니다.")

    access_token = auth.create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}
