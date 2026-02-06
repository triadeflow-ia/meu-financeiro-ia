"""
Rota de sincronização com o Santander.
Delega para app.api.bank_sync a autenticação mTLS, busca de extrato PIX e match com Supabase.
"""
from fastapi import APIRouter, HTTPException

from app.api.bank_sync import sincronizar_santander_com_supabase

router = APIRouter()


@router.post("/sync")
async def bank_sync(dias: int = 30):
    """
    Busca o extrato de PIX no Santander (certificados privada.key + .crt em backend/certs/).
    Para cada entrada PIX, verifica se existe cliente correspondente no Supabase (valor + nome).
    Se houver match, insere na tabela transacoes.
    """
    try:
        return await sincronizar_santander_com_supabase(dias=dias)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail="Certificados Santander não encontrados. Coloque privada.key e o .crt em backend/certs/.",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao sincronizar com Santander: {e}")
