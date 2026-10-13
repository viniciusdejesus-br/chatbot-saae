import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.atendimento import Atendimento
from app.services.protocolo_service import gerar_numero_protocolo

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Protocolos"])


class CriarProtocoloEntrada(BaseModel):
    atendimento_id: int = Field(gt=0)


def representar_protocolo(atendimento: Atendimento) -> dict:
    return {
        "protocolo": atendimento.protocolo,
        "atendimento_id": atendimento.id,
        "intencao": atendimento.intencao,
        "status": atendimento.status,
        "criado_em": atendimento.criado_em.isoformat() if atendimento.criado_em else None,
    }


@router.post("/")
def gerar_protocolo(
    dados: CriarProtocoloEntrada,
    db: Session = Depends(get_db),
):
    try:
        atendimento = (
            db.query(Atendimento)
            .filter(Atendimento.id == dados.atendimento_id)
            .first()
        )
        if atendimento is None:
            raise HTTPException(status_code=404, detail="Atendimento nÃ£o encontrado.")

        if atendimento.protocolo is None:
            atendimento.protocolo = gerar_numero_protocolo(atendimento.id)
            atendimento.status = "aberto"
            atendimento.resposta = (
                f"{atendimento.resposta.strip()}\n\n"
                f"Protocolo: {atendimento.protocolo}. Status: aberto."
            )
            db.commit()
            db.refresh(atendimento)
        return representar_protocolo(atendimento)
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Falha ao criar ou recuperar protocolo")
        raise HTTPException(
            status_code=503,
            detail="NÃ£o foi possÃ­vel acessar o banco de dados.",
        ) from None


@router.get("/{protocolo}")
def consultar_protocolo(
    protocolo: str,
    db: Session = Depends(get_db),
):
    try:
        atendimento = (
            db.query(Atendimento)
            .filter(Atendimento.protocolo == protocolo.strip())
            .first()
        )
    except SQLAlchemyError:
        logger.exception("Falha ao consultar protocolo")
        raise HTTPException(
            status_code=503,
            detail="NÃ£o foi possÃ­vel consultar o banco de dados.",
        ) from None

    if atendimento is None:
        raise HTTPException(status_code=404, detail="Protocolo nÃ£o encontrado.")

    return representar_protocolo(atendimento)