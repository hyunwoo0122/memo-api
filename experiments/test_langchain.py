from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 임베딩 전용 모델 설정 (텍스트를 벡터로 변환하는 역할)
embeddings = OllamaEmbeddings(model = "nomic-embed-text")

memos = [
    "오늘 팀 회의는 3시에 진행됩니다.",
    "저녁에 장 봐서 계란이랑 우유 사기",
    "프로잭트 마감일은 다음주 금요일입니다",
    "고양이 사료가 떨어져서 주문해야 함"
]

# nomic-embed-text는 문서 임베딩 시 "search_document: " 접두사가 필요함 (없으면 검색 정확도 떨어짐)
documents = [Document(page_content="search_document: " + memo) for memo in memos]

# 각 문서를 자동으로 벡터화해서 Chroma 벡터DB에 저장
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings
)

query = "회의는 언제야?"

# 질문도 동일하게 "search_query: " 접두사 필요, k=1은 가장 유사한 1개만 반환
results = vectorstore.similarity_search("search_query: " + query, k=1)

# 검색 결과에서 접두사를 제거해 원본 메모만 추출
found_memo = results[0].page_content.replace("search_document: ", "")

print(f"질문: {query}")
print(f"가장 관련 있는 메모: {found_memo}")