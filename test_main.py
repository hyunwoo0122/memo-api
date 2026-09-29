# 서버를 실제로 띄우지 않아도 코드 안에서 API요청을 보낼 볼 수 있게 해주는 FastAPI의 테스트 도구
from fastapi.testclient import TestClient
from main import app

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_register_success(client):
    response = client.post("/register", json={"username": "testuser", "password": "test1234"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_register_duplicate_username(client):
    response = client.post("/register", json={"username": "testuser", "password": "test1234"})
    assert response.status_code == 200
    response = client.post("/register", json={"username": "testuser", "password": "test1234"})
    assert response.status_code == 400
    assert response.json()["detail"] == "이미 존재하는 ID입니다."

def test_login_success(client):
    # 먼저 가입을 해야 Test가 진행이 되니 가입먼저 해서 진행 
    client.post("/register", json={"username": "testuser", "password": "test1234"})
    response = client.post("/login", json={"username": "testuser", "password": "test1234"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    # 먼저 가입을 해야 Test가 진행이 되니 가입먼저 해서 진행 
        client.post("/register", json={"username": "testuser", "password": "test1234"})
        response = client.post("/login", json={"username": "testuser", "password": "test12345"})
        assert response.status_code == 401
        assert response.json()["detail"] == "ID 또는 PW가 올바르지 않습니다."

def test_creat_memo(client, auth_headers):
    response = client.post(
         "/memos",
         json={"title": "회의", "content": "3시 팀 회의"},
         headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "회의"
    assert "id" in data

def test_get_memos_without_token(client):
    response = client.get("/memos")
    assert response.status_code == 401

def test_update_other_users_memo(client, auth_headers, other_auth_headers):
     created = client.post(
          "/memos",
          json={"title": " 내 메모", "content": "비밀"},
          headers=auth_headers,
     )

     memo_id = created.json()["id"]

     response = client.put(
          f"/memos/{memo_id}",
          json = {"title": "바꿔치기", "content": "해킹"},
          headers = other_auth_headers,
     )

     assert response.status_code == 403


def test_delete_other_users_memo(client, auth_headers, other_auth_headers):
    created = client.post(
               "/memos",
               json={"title": " 내 메모", "content": "비밀"},
               headers=auth_headers,
          )
     
    memo_id = created.json()["id"]
     
    response = client.delete(
               f"/memos/{memo_id}",
               headers = other_auth_headers,
          )
     
    assert response.status_code == 403

    remaining = client.get("/memos", headers=auth_headers)
    assert len(remaining.json()) == 1
     
     


