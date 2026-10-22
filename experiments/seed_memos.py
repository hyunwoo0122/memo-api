# 테스트용 메모 100개를 서버에 생성하는 스크립트
# 사용법: 서버(uvicorn main:app)를 켠 상태에서 python experiments/seed_memos.py
import sys
from getpass import getpass

import httpx

BASE_URL = "http://127.0.0.1:8000"
MEMO_COUNT = 100

# 주제별로 (제목, 내용 템플릿, 바꿔 넣을 단어들)
TOPICS = [
    ("장보기", "마트에서 {item} 사기. 할인하는지 확인하고 영수증 챙기기.",
     ["우유와 계란", "양파와 대파", "닭가슴살", "사과 한 봉지", "쌀 10kg", "두부와 콩나물", "세제와 휴지"]),
    ("회의", "{item} 회의. 안건 미리 정리하고 회의록 공유하기.",
     ["주간 팀", "신규 기능 기획", "분기 실적 리뷰", "디자인 검토", "고객 피드백 정리", "배포 일정 조율", "1:1 면담"]),
    ("병원", "{item} 예약. 진료 시간 10분 전에 도착하기.",
     ["치과 스케일링", "안과 정기 검진", "피부과 진료", "건강검진", "정형외과 물리치료", "내과 감기 진료", "이비인후과 진료"]),
    ("운동", "오늘은 {item}. 끝나고 스트레칭 10분 하기.",
     ["러닝 5km", "헬스장 하체 운동", "수영 30분", "요가 클래스", "자전거 타기 1시간", "등산", "홈트레이닝 30분"]),
    ("공부", "{item} 공부하기. 정리한 내용은 노트에 남기기.",
     ["FastAPI 의존성 주입", "SQLAlchemy 관계 설정", "React useEffect", "영어 단어 50개", "자료구조 해시맵", "Docker 기초", "RAG 임베딩 원리"]),
    ("여행", "{item} 여행 준비. 숙소 예약과 교통편 확인하기.",
     ["제주도", "부산", "강릉", "경주", "여수", "전주", "속초"]),
    ("요리", "저녁 메뉴는 {item}. 필요한 재료 미리 손질해 두기.",
     ["김치찌개", "된장국", "제육볶음", "파스타", "카레라이스", "계란말이", "잡채"]),
    ("청소", "{item} 청소하기. 쓰레기 분리수거도 같이 하기.",
     ["욕실", "주방 싱크대", "냉장고 정리", "창틀과 베란다", "옷장 정리", "책상 정리", "현관"]),
]


def make_memo(index):
    topic, template, items = TOPICS[index % len(TOPICS)]
    number = index + 1
    item = items[(index // len(TOPICS)) % len(items)]
    return {
        "title": f"{topic} 메모 {number}",
        "content": f"[{number}번] " + template.format(item=item),
    }


def main():
    username = input("아이디: ")
    password = getpass("비밀번호: ")

    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        try:
            response = client.post("/login", json={"username": username, "password": password})
        except httpx.RequestError as e:
            print(f"서버에 연결할 수 없습니다. 서버가 켜져 있는지 확인하세요. ({e})")
            sys.exit(1)

        if response.status_code != 200:
            print(f"로그인 실패: {response.status_code} {response.text}")
            sys.exit(1)

        access_token = response.json()["access_token"]
        headers = {"Authorization": "Bearer " + access_token}

        for i in range(MEMO_COUNT):
            try:
                response = client.post("/memos", json=make_memo(i), headers=headers)
            except httpx.RequestError as e:
                print(f"{i + 1}번째 메모 생성 중 서버 연결이 끊겼습니다. ({e})")
                sys.exit(1)

            if response.status_code != 200:
                print(f"{i + 1}번째 메모 생성 실패: {response.status_code} {response.text}")
                sys.exit(1)

    print(f"{MEMO_COUNT}개 생성 완료")


if __name__ == "__main__":
    main()
