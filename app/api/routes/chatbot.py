import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.atendimento import Atendimento
from app.services.ia_service import IAService
from app.services.protocolo_service import gerar_numero_protocolo

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chatbot"])
ia = IAService()

INTENCOES_COM_PROTOCOLO = {
    "segunda_via",
    "solicitacao_servico",
    "alteracao_cadastral",
    "reclamacao",
    "elogio",
    "atendimento_humano",
}


class MensagemEntrada(BaseModel):
    telefone: str = Field(min_length=8, max_length=30)
    mensagem: str = Field(min_length=1, max_length=2000)

    @field_validator("telefone")
    @classmethod
    def validar_telefone(cls, valor: str) -> str:
        valor = valor.strip()
        digitos = sum(caractere.isdigit() for caractere in valor)
        if digitos < 8:
            raise ValueError("O telefone deve conter pelo menos 8 dÃ­gitos.")
        if any(not (caractere.isdigit() or caractere in "+()- .") for caractere in valor):
            raise ValueError("O telefone contÃ©m caracteres invÃ¡lidos.")
        return valor

    @field_validator("mensagem")
    @classmethod
    def validar_mensagem(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("A mensagem nÃ£o pode estar vazia.")
        return valor


@router.post("/mensagem")
def receber_mensagem(
    dados: MensagemEntrada,
    db: Session = Depends(get_db),
):
    resultado = ia.classificar(dados.mensagem)
    precisa_protocolo = resultado.intencao in INTENCOES_COM_PROTOCOLO

    atendimento = Atendimento(
        telefone=dados.telefone,
        mensagem=dados.mensagem,
        intencao=resultado.intencao,
        resposta=resultado.resposta,
        confianca=resultado.confianca,
        status="aberto" if precisa_protocolo else "registrado",
    )

    try:
        db.add(atendimento)
        db.flush()  # ObtÃ©m o ID gerado pelo banco antes de formar o protocolo.

        if precisa_protocolo:
            atendimento.protocolo = gerar_numero_protocolo(atendimento.id)
            # Evita afirmar que uma equipe real foi acionada; isso ainda depende da integraÃ§Ã£o operacional.
            atendimento.resposta = (
                "Seu atendimento foi registrado no protÃ³tipo. "
                f"Protocolo: {atendimento.protocolo}. Status: aberto. "
                "O encaminhamento Ã  equipe responsÃ¡vel depende da integraÃ§Ã£o operacional."
            )

        db.commit()
        db.refresh(atendimento)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Falha ao gravar atendimento no banco de dados")
        raise HTTPException(
            status_code=503,
            detail="NÃ£o foi possÃ­vel registrar o atendimento no banco de dados.",
        ) from None

    return {
        "atendimento_id": atendimento.id,
        "telefone": atendimento.telefone,
        "mensagem": atendimento.mensagem,
        "intencao": atendimento.intencao,
        "resposta": atendimento.resposta,
        "confianca": atendimento.confianca,
        "protocolo": atendimento.protocolo,
        "status": atendimento.status,
        "status_registro": "salvo",
        "provedor": "Ollama",
        "modelo": ia.model,
    }