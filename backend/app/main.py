"""
MVP Gestão Financeira - API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import clientes, santander, bank, webhook
from app.middleware.api_key import APIKeyMiddleware

app = FastAPI(
    title="Gestão Financeira Inteligente",
    description="API para clientes, transações, Santander (mTLS) e webhook WhatsApp",
    version="0.2.0",
)

app.add_middleware(APIKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(santander.router, prefix="/api/santander", tags=["Santander"])
app.include_router(bank.router, prefix="/api/bank", tags=["Bank"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["Webhook"])


@app.get("/")
def root():
    return {"message": "MVP Gestão Financeira API", "docs": "/docs"}
