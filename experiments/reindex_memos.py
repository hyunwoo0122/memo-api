# memo.db에 이미 있는 메모를 벡터DB(chroma_db)에 한 번에 넣는 스크립트
# 사용법: Ollama가 켜진 상태에서 python experiments/reindex_memos.py (서버는 꺼두는 것을 권장)
# 벡터 id가 str(memo.id)라서 여러 번 실행해도 중복되지 않고 덮어쓴다.
import os
import sys

# memo.db, chroma_db 경로가 프로젝트 루트 기준 상대경로라서 루트로 이동한 뒤 main을 불러온다
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)
sys.path.insert(0, PROJECT_ROOT)

import models
from database import SessionLocal
from main import vectorstore, memo_to_document

BATCH_SIZE = 50


def main():
    db = SessionLocal()
    try:
        memos = db.query(models.MemoDB).all()
    finally:
        db.close()

    if not memos:
        print("DB에 메모가 없습니다.")
        return

    for start in range(0, len(memos), BATCH_SIZE):
        batch = memos[start:start + BATCH_SIZE]
        vectorstore.add_documents(
            [memo_to_document(memo) for memo in batch],
            ids=[str(memo.id) for memo in batch],
        )
        print(f"{min(start + BATCH_SIZE, len(memos))}/{len(memos)}개 처리")

    print(f"{len(memos)}개 메모 재색인 완료")


if __name__ == "__main__":
    main()
