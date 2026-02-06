"""
Sincronização Santander: autenticação mTLS, extrato PIX e match com clientes no Supabase.

- Usa os certificados em backend/certs/ (privada.key + .crt do Santander).
- Busca o extrato de PIX via API Balance and Statement.
- Para cada entrada PIX, verifica se existe cliente correspondente (valor + nome).
- Se houver match, insere na tabela transacoes (evitando duplicata por hash_bancario).
"""
from datetime import date, datetime, timedelta
from typing import Any

# Autenticação mTLS: certificados da pasta certs/
def _obter_cliente_mtls_santander():
    """
    Retorna cliente HTTP com autenticação mTLS usando privada.key e certificado .crt
    da pasta backend/certs/. Levanta FileNotFoundError se os arquivos não existirem.
    """
    import sys
    from pathlib import Path
    backend_dir = Path(__file__).resolve().parent.parent.parent
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    from conexao_banco import obter_cliente_santander_async
    return obter_cliente_santander_async()  # valida certs ao montar o client


async def _buscar_extrato_pix(dias: int = 30) -> list[dict[str, Any]]:
    """
    Busca extrato no Santander via mTLS (certificados em certs/).
    Retorna apenas entradas PIX normalizadas: descricao, valor, data, hash_bancario.
    """
    from app.santander_api import buscar_extrato
    raw = await buscar_extrato(dias=dias)
    return [t for t in raw if t.get("eh_pix") and t.get("valor") and float(t["valor"]) > 0]


def _parse_data_pagamento(s: str | None, fallback: date) -> date:
    if not s:
        return fallback
    s = (s or "").strip()[:10]
    for sep in ["-", "/"]:
        if sep in s:
            parts = s.replace("/", "-").split("-")
            if len(parts) >= 3:
                try:
                    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                    if 1 <= m <= 12 and 1 <= d <= 31:
                        return date(y, m, d)
                except (ValueError, TypeError):
                    pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except Exception:
        return fallback


def _normalizar_nome(s: str) -> str:
    """Minúsculo, sem acentos, para match."""
    if not s:
        return ""
    s = s.lower().strip()
    for a, b in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ã", "a"), ("õ", "o"), ("ç", "c")]:
        s = s.replace(a, b)
    return s


def _cliente_corresponde_entrada_pix(
    cliente: dict[str, Any],
    valor_pix: float,
    descricao_pix: str,
) -> bool:
    """True se valor e nome do PIX batem com o cliente."""
    valor_cli = round(float(cliente.get("valor_mensalidade") or 0), 2)
    if round(valor_pix, 2) != valor_cli:
        return False
    nome_cli = _normalizar_nome(cliente.get("nome") or "")
    if not nome_cli:
        return False
    return nome_cli in _normalizar_nome(descricao_pix)


async def sincronizar_santander_com_supabase(dias: int = 30) -> dict[str, Any]:
    """
    1. Autentica no Santander via mTLS (certificados em backend/certs/).
    2. Busca o extrato de PIX.
    3. Para cada entrada PIX, verifica se existe cliente correspondente no Supabase.
    4. Se houver match, insere na tabela transacoes (sem duplicar por hash_bancario).

    Retorna: { "message", "transacoes_extrato", "matches_criados" }.
    Levanta FileNotFoundError se os certificados não existirem.
    """
    from app.db import get_supabase

    # Garante que os certificados existem antes de chamar a API
    _obter_cliente_mtls_santander()

    transacoes_pix = await _buscar_extrato_pix(dias=dias)
    supabase = get_supabase()
    hoje = date.today()
    inicio_periodo = hoje - timedelta(days=90)

    # Transações já existentes (cliente_id + data) e hashes já usados
    r_trans = (
        supabase.table("transacoes")
        .select("cliente_id, data_pagamento, hash_bancario")
        .gte("data_pagamento", str(inicio_periodo))
        .lte("data_pagamento", str(hoje))
        .execute()
    )
    trans_list = r_trans.data or []
    existentes = {(str(t.get("cliente_id")), str(t.get("data_pagamento"))) for t in trans_list}
    hashes_ja_usados = {t.get("hash_bancario") for t in trans_list if t.get("hash_bancario")}

    # Clientes ativos para match
    r_clientes = (
        supabase.table("clientes")
        .select("id, nome, valor_mensalidade, status_ativo")
        .eq("status_ativo", True)
        .execute()
    )
    clientes = list(r_clientes.data or [])

    match_count = 0
    for entrada in transacoes_pix:
        valor = round(float(entrada["valor"]), 2)
        descricao = (entrada.get("descricao") or "")
        hash_bancario = entrada.get("hash_bancario")
        if hash_bancario and hash_bancario in hashes_ja_usados:
            continue
        data_pag = _parse_data_pagamento(entrada.get("data"), hoje)

        for cliente in clientes:
            cid = str(cliente["id"])
            if (cid, str(data_pag)) in existentes:
                continue
            if not _cliente_corresponde_entrada_pix(cliente, valor, descricao):
                continue
            # Match: inserir na tabela transacoes
            supabase.table("transacoes").insert({
                "cliente_id": cid,
                "valor": valor,
                "data_pagamento": str(data_pag),
                "status_nota_fiscal": "pendente",
                "hash_bancario": hash_bancario or None,
            }).execute()
            existentes.add((cid, str(data_pag)))
            if hash_bancario:
                hashes_ja_usados.add(hash_bancario)
            match_count += 1
            break

    return {
        "message": "Sincronização concluída",
        "transacoes_extrato": len(transacoes_pix),
        "matches_criados": match_count,
    }
