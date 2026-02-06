"""
Cliente da API de Extrato do Santander Sandbox.
Usa conexao_banco para mTLS com certificados.
"""
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Permite importar conexao_banco quando o app roda a partir de backend/
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(_backend_dir))

load_dotenv()

SANTANDER_EXTRATO_URL = os.getenv(
    "SANTANDER_EXTRATO_URL",
    "https://api.sandbox.santander.com.br/extrato/v1",
)


async def buscar_extrato(conta: str | None = None, dias: int = 7):
    """
    Busca extrato no Santander Sandbox.
    Retorna lista de transações (descrição, valor, data, eh_pix).
    """
    try:
        from conexao_banco import obter_cliente_santander_async
    except ImportError:
        return []

    try:
        client = obter_cliente_santander_async()
    except FileNotFoundError:
        return []

    url = SANTANDER_EXTRATO_URL.rstrip("/")
    if conta:
        url = f"{url}/contas/{conta}/extrato"
    else:
        url = f"{url}/extrato"
    params = {"dias": dias}

    try:
        async with client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
        return _normalizar_transacoes(data)
    except Exception:
        return []


def _normalizar_transacoes(data):
    """
    Normaliza resposta da API para lista com: descricao, valor, data, eh_pix.
    Ajuste conforme o JSON real retornado pelo Santander Sandbox.
    """
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = data.get("transacoes", data.get("lancamentos", data.get("itens", [])))
    else:
        items = []

    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        desc = item.get("descricao") or item.get("historico") or item.get("descricaoTransacao") or ""
        valor = item.get("valor") or item.get("valorLancamento") or 0
        data_str = item.get("data") or item.get("dataLancamento") or item.get("dataTransacao") or ""
        tipo = (item.get("tipo") or item.get("tipoTransacao") or "").upper()
        eh_pix = "PIX" in tipo or "PIX" in (desc or "").upper()
        hash_bancario = item.get("hash") or item.get("id") or item.get("hashBancario") or ""
        out.append({
            "descricao": str(desc).strip(),
            "valor": float(valor) if valor else 0,
            "data": data_str,
            "eh_pix": eh_pix,
            "hash_bancario": str(hash_bancario) if hash_bancario else None,
        })
    return out
