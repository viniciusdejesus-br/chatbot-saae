from fastapi import APIRouter
from datetime import datetime
import random

router = APIRouter()


@router.post("/")
def gerar_protocolo():
    numero = f"SAAE-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
    return {
        "protocolo": numero,
        "status": "aberto",
        "mensagem": "Protocolo criado com sucesso."
    }


@router.get("/{protocolo}")
def consultar_protocolo(protocolo: str):
    return {
        "protocolo": protocolo,
        "status": "em análise"
    }
