from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.database.database import Base


class Atendimento(Base):
    __tablename__ = "atendimentos"

    id = Column(Integer, primary_key=True, index=True)
    telefone = Column(String(30), nullable=False, index=True)
    mensagem = Column(Text, nullable=False)
    intencao = Column(String(50), nullable=False, index=True)
    resposta = Column(Text, nullable=False)
    confianca = Column(Float, nullable=False)
    status = Column(String(30), nullable=False, default="registrado")
    protocolo = Column(String(40), nullable=True, unique=True, index=True)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)