from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_segunda_via():
    response = client.post(
        "/chatbot/mensagem",
        json={
            "telefone": "19999999999",
            "mensagem": "Preciso da segunda via da minha conta"
        },
    )
    assert response.status_code == 200
    assert response.json()["intencao"] == "segunda_via"
