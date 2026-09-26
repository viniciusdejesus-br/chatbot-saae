from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MensagemEntrada(BaseModel):
    telefone: str
    mensagem: str


@router.post("/mensagem")
def receber_mensagem(dados: MensagemEntrada):
    texto = dados.mensagem.lower().strip()

    if "segunda via" in texto or "fatura" in texto:
        intencao = "segunda_via"
        resposta = "Vamos iniciar a solicitação de segunda via."
    elif "protocolo" in texto:
        intencao = "consulta_protocolo"
        resposta = "Informe o número do seu protocolo."
    elif "vazamento" in texto or "serviço" in texto:
        intencao = "solicitacao_servico"
        resposta = "Vamos registrar sua solicitação de serviço."
    else:
        intencao = "informacao_geral"
        resposta = (
            "Não consegui identificar sua solicitação. "
            "Digite: segunda via, protocolo, vazamento ou atendimento."
        )

    return {
        "telefone": dados.telefone,
        "mensagem": dados.mensagem,
        "intencao": intencao,
        "resposta": resposta,
    }
