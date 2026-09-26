from fastapi import FastAPI
from app.api.routes.chatbot import router as chatbot_router
from app.api.routes.protocolos import router as protocolos_router

app = FastAPI(
    title="Chatbot SAAE Cordeirópolis",
    description="Protótipo de atendimento automatizado",
    version="1.0.0",
)

app.include_router(chatbot_router, prefix="/chatbot", tags=["Chatbot"])
app.include_router(protocolos_router, prefix="/protocolos", tags=["Protocolos"])


@app.get("/")
def root():
    return {
        "sistema": "Chatbot SAAE Cordeirópolis",
        "status": "online"
    }


@app.get("/status")
def status():
    return {"status": "online"}
