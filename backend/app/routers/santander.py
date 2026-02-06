"""
Sincronização com Santander Sandbox: busca extrato e atualiza status dos clientes (Pago/Pendente).
"""
from fastapi import APIRouter, HTTPException
from app.db import get_supabase
from app.santander_api import buscar_extrato

router = APIRouter()


@router.post("/sincronizar")
async def sincronizar_santander():
    """
    Busca o extrato no Santander Sandbox e marca como 'Pago' os clientes
    cujo PIX foi encontrado no extrato (por valor ou identificação).
    """
    try:
        transacoes = await buscar_extrato(dias=30)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Erro ao conectar no Santander: {e}")

    try:
        supabase = get_supabase()
        r = supabase.table("clientes").select("id, nome, valor_esperado, chave_pix, status").execute()
        clientes = r.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar clientes: {e}")

    # PIX encontrados no extrato (valor positivo = entrada)
    pix_valores = {t["valor"] for t in transacoes if t.get("eh_pix") and t.get("valor")}
    pix_valores.update({-t["valor"] for t in transacoes if t.get("eh_pix") and t.get("valor")})

    atualizados = 0
    for c in clientes:
        if c.get("status") == "Pago":
            continue
        valor_esperado = c.get("valor_esperado")
        if valor_esperado is not None and (valor_esperado in pix_valores or -valor_esperado in pix_valores):
            supabase.table("clientes").update({"status": "Pago"}).eq("id", c["id"]).execute()
            atualizados += 1

    return {
        "message": "Sincronização concluída",
        "transacoes_extrato": len(transacoes),
        "clientes_atualizados": atualizados,
        "total_clientes": len(clientes),
    }
