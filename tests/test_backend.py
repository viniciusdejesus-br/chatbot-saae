import importlib
import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.main as main
from app.database.database import Base, get_db
from app.services.ia_service import ClassificacaoIA

chatbot_routes = importlib.import_module("app.api.routes.chatbot")


@pytest.fixture
def client(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
    )

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(main, "engine", test_engine)
    main.app.dependency_overrides[get_db] = override_get_db

    def fake_classificar(mensagem: str):
        if "vazamento" in mensagem.casefold() or "falta de Ã¡gua" in mensagem.casefold():
            return ClassificacaoIA(
                intencao="solicitacao_servico",
                resposta="Resposta simulada para teste.",
                confianca=0.95,
            )
        return ClassificacaoIA(
            intencao="informacao_geral",
            resposta="Resposta simulada para teste.",
            confianca=0.80,
        )

    monkeypatch.setattr(chatbot_routes.ia, "classificar", fake_classificar)

    try:
        with TestClient(main.app) as test_client:
            yield test_client
    finally:
        main.app.dependency_overrides.clear()
        test_engine.dispose()


def test_solicitacao_salva_e_gera_protocolo(client):
    response = client.post(
        "/chatbot/mensagem",
        json={
            "telefone": "5513999999999",
            "mensagem": "Tem um vazamento de Ã¡gua na minha rua",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status_registro"] == "salvo"
    assert data["intencao"] == "solicitacao_servico"
    assert data["status"] == "aberto"
    assert re.fullmatch(r"SAAE-\d{8}-\d{6}", data["protocolo"])
    assert data["protocolo"] in data["resposta"]

    consulta = client.get(f"/protocolos/{data['protocolo']}")
    assert consulta.status_code == 200
    assert consulta.json()["protocolo"] == data["protocolo"]
    assert consulta.json()["status"] == "aberto"


def test_informacao_geral_nao_gera_protocolo_automaticamente(client):
    response = client.post(
        "/chatbot/mensagem",
        json={"telefone": "5513999999999", "mensagem": "OlÃ¡, gostaria de uma informaÃ§Ã£o"},
    )
    assert response.status_code == 200
    assert response.json()["protocolo"] is None
    assert response.json()["status"] == "registrado"


def test_cria_protocolo_para_atendimento_existente(client):
    registro = client.post(
        "/chatbot/mensagem",
        json={"telefone": "5513999999999", "mensagem": "OlÃ¡, gostaria de uma informaÃ§Ã£o"},
    ).json()

    criado = client.post("/protocolos/", json={"atendimento_id": registro["atendimento_id"]})
    assert criado.status_code == 200
    assert criado.json()["protocolo"].startswith("SAAE-")
    assert criado.json()["status"] == "aberto"

    # A operaÃ§Ã£o Ã© idempotente: nÃ£o cria um segundo protocolo para o mesmo atendimento.
    repetido = client.post("/protocolos/", json={"atendimento_id": registro["atendimento_id"]})
    assert repetido.json()["protocolo"] == criado.json()["protocolo"]


def test_protocolo_inexistente_retorna_404(client):
    response = client.get("/protocolos/SAAE-19000101-999999")
    assert response.status_code == 404


def test_entrada_invalida_retorna_422(client):
    response = client.post(
        "/chatbot/mensagem",
        json={"telefone": "abc", "mensagem": "   "},
    )
    assert response.status_code == 422


def test_status_confirma_banco_de_teste(client):
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json()["banco"] == "online"