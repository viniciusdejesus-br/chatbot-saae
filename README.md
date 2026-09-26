# Chatbot SAAE Cordeirópolis

Projeto inicial para desenvolvimento no VS Code, baseado no TCC do chatbot inteligente de atendimento ao cliente do SAAE de Cordeirópolis/SP.

## Stack
- Python 3.10+
- FastAPI
- PostgreSQL
- SQLAlchemy
- n8n
- WhatsApp (integração preparada)

## Como executar

1. Instale Python 3.10+.
2. Crie/abra esta pasta no VS Code.
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Copie `.env.example` para `.env` e ajuste os dados.
5. Execute:

```bash
uvicorn app.main:app --reload
```

6. Acesse:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

O código é uma base inicial do protótipo. A integração real com WhatsApp, IA e infraestrutura externa ainda deve ser configurada.
