import ollama
import numpy as np

# 반복되는 임베당 생성코드를 함수로 지정
def get_embedding(text):
    response = ollama.embeddings(
        model = "nomic-embed-text",
        prompt = text
    )

    # 응답받은 리스트를 numpy로 변환
    return np.array(response["embedding"])

def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))



memos = [
    "오늘 팀 회의는 3시에 진행됩니다.",
    "저녁에 장 봐서 계란이랑 우유 사기",
    "프로젝트 마감일은 다음주 금요일입니다",
    "고양이 사료가 떨어져서 주문해야 함"
]

query = "회의는 언제야?"

query_vector = get_embedding("search_query: " + query)

best_score = -1
best_memo = None

for memo in memos:
    memo_vector = get_embedding("search_document: " + memo)
    score = cosine_similarity(query_vector, memo_vector)
    print(f"'{memo}' -> 유사도: {score:.4f}")

    if score > best_score:
        best_score = score
        best_memo = memo

print()
print(f"가장 관련 있는 메모: '{best_memo}' (유사도): {best_score:.4f})")    


prompt = f"""다음 메모를 참고해서 질문에 답해줘.

메모 : {best_memo}

질문 : {query}
"""

response = ollama.chat(
    model = "llama3.1:8b",
    messages = [
        {"role": "user", "content": prompt}
    ]
)

print()
print("=== 최종 답변 ===")
print(response["message"]["content"])