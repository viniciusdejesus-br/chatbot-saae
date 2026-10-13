import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes.chatbot import router as chatbot_router
from app.api.routes.protocolos import router as protocolos_router
from app.database.database import Base, engine, get_db
from app.models.atendimento import Atendimento  # Registra o modelo no metadata.

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot SAAE CordeirÃ³polis",
    description="Sistema de atendimento inteligente do SAAE de CordeirÃ³polis/SP",
    version="2.2.0",
)


@app.on_event("startup")
def criar_tabelas():
    # Cria tabelas ausentes, sem apagar os registros existentes.
    Base.metadata.create_all(bind=engine)


app.include_router(chatbot_router, prefix="/chatbot")
app.include_router(protocolos_router, prefix="/protocolos")


@app.get("/")
def root():
    return {
        "sistema": "Chatbot SAAE CordeirÃ³polis",
        "status": "online",
        "ia": "Ollama",
    }


@app.get("/status")
def status(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Falha ao verificar a conexÃ£o com o PostgreSQL")
        raise HTTPException(
            status_code=503,
            detail="Banco de dados indisponÃ­vel.",
        ) from None

    return {
        "status": "online",
        "ia": "Ollama",
        "banco": "online",
    }