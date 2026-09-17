import ollama

question = input("질문을 입력하세요: ")

response = ollama.chat(
    model= "llama3.1:8b",
    messages=[
        # 사용자가 보내는 메세지, 실제로 들어가는 메세지
        {"role": "user", "content": question}
        ]
)

print(response["message"]["content"])