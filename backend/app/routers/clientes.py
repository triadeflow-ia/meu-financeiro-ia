from datetime import date
from fastapi import APIRouter, HTTPException
from app.db import get_supabase
from app.models.schemas import ClienteCreate, ClienteUpdate, ClienteResponse

router = APIRouter()


def _status_pagamento(cliente_id: str, dia_vencimento: int, transacoes_mes: list) -> str:
    """Calcula status: pago, pendente, atrasado."""
    hoje = date.today()
    tem_pagamento = any(str(t.get("cliente_id")) == str(cliente_id) for t in transacoes_mes)
    if tem_pagamento:
        return "pago"
    # Dia de vencimento neste mês (simplificado: usar dia fixo)
    if dia_vencimento > 28:
        dia_vencimento = 28
    try:
        vencimento = hoje.replace(day=min(dia_vencimento, 28))
    except ValueError:
        vencimento = hoje.replace(day=28)
    if hoje > vencimento:
        return "atrasado"
    return "pendente"


def _row_to_cliente(row: dict, transacoes_mes: list) -> ClienteResponse:
    cid = str(row["id"])
    dia = int(row.get("dia_vencimento") or 10)
    status = _status_pagamento(cid, dia, transacoes_mes)
    return ClienteResponse(
        id=cid,
        nome=row["nome"],
        documento_cpf_cnpj=row.get("documento_cpf_cnpj"),
        valor_mensalidade=float(row.get("valor_mensalidade") or 0),
        dia_vencimento=dia,
        status_ativo=bool(row.get("status_ativo", True)),
        status_pagamento=status,
    )


@router.get("", response_model=list[ClienteResponse])
def listar_clientes():
    try:
        supabase = get_supabase()
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        r_trans = supabase.table("transacoes").select("cliente_id").gte("data_pagamento", str(inicio_mes)).lte("data_pagamento", str(hoje)).execute()
        transacoes_mes = r_trans.data or []
        r = supabase.table("clientes").select("*").order("nome").execute()
        return [_row_to_cliente(row, transacoes_mes) for row in (r.data or [])]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
def dashboard_kpis():
    """KPIs: total_recebido, notas_a_emitir, clientes_inadimplentes."""
    try:
        supabase = get_supabase()
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        # Total recebido no mês
        r_trans = supabase.table("transacoes").select("valor").gte("data_pagamento", str(inicio_mes)).lte("data_pagamento", str(hoje)).execute()
        total_recebido = sum(float(t.get("valor") or 0) for t in (r_trans.data or []))
        # Notas a emitir = transações com status_nota_fiscal = pendente
        r_notas = supabase.table("transacoes").select("id").eq("status_nota_fiscal", "pendente").execute()
        notas_a_emitir = len(r_notas.data or [])
        # Clientes ativos + transações do mês para calcular inadimplentes
        r_clientes = supabase.table("clientes").select("id, dia_vencimento").eq("status_ativo", True).execute()
        r_trans_mes = supabase.table("transacoes").select("cliente_id").gte("data_pagamento", str(inicio_mes)).lte("data_pagamento", str(hoje)).execute()
        pagos = {str(t["cliente_id"]) for t in (r_trans_mes.data or [])}
        inadimplentes = 0
        for c in (r_clientes.data or []):
            cid = str(c["id"])
            if cid in pagos:
                continue
            dia = int(c.get("dia_vencimento") or 28)
            try:
                venc = hoje.replace(day=min(dia, 28))
            except ValueError:
                venc = hoje.replace(day=28)
            if hoje > venc:
                inadimplentes += 1
        return {
            "total_recebido": round(total_recebido, 2),
            "notas_a_emitir": notas_a_emitir,
            "clientes_inadimplentes": inadimplentes,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/contabilidade")
def exportar_contabilidade():
    """CSV para contabilidade: Data, Cliente, Valor, Documento."""
    import csv
    from io import StringIO
    from fastapi.responses import StreamingResponse
    try:
        supabase = get_supabase()
        r_trans = supabase.table("transacoes").select("data_pagamento, valor, cliente_id").order("data_pagamento", asc=False).execute()
        trans = r_trans.data or []
        if not trans:
            return StreamingResponse(
                iter(["Data,Cliente,Valor,Documento\n"]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=contabilidade.csv"},
            )
        cliente_ids = list({t["cliente_id"] for t in trans})
        clientes_map = {}
        r_clientes = supabase.table("clientes").select("id, nome, documento_cpf_cnpj").execute()
        for c in (r_clientes.data or []):
            if str(c["id"]) in [str(cid) for cid in cliente_ids]:
                clientes_map[str(c["id"])] = (c.get("nome") or "", c.get("documento_cpf_cnpj") or "")
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(["Data", "Cliente", "Valor", "Documento"])
        for t in trans:
            nome, doc = clientes_map.get(str(t["cliente_id"]), ("", ""))
            w.writerow([t.get("data_pagamento"), nome, t.get("valor"), doc])
        buf.seek(0)
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=contabilidade.csv"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}", response_model=ClienteResponse)
def obter_cliente(id: str):
    try:
        supabase = get_supabase()
        r = supabase.table("clientes").select("*").eq("id", id).single().execute()
        if not r.data:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        hoje = date.today()
        inicio_mes = hoje.replace(day=1)
        r_trans = supabase.table("transacoes").select("cliente_id").gte("data_pagamento", str(inicio_mes)).lte("data_pagamento", str(hoje)).execute()
        return _row_to_cliente(r.data, r_trans.data or [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ClienteResponse)
def criar_cliente(payload: ClienteCreate):
    try:
        supabase = get_supabase()
        data = {
            "nome": payload.nome,
            "documento_cpf_cnpj": payload.documento_cpf_cnpj,
            "valor_mensalidade": payload.valor_mensalidade,
            "dia_vencimento": min(28, max(1, payload.dia_vencimento)),
            "status_ativo": payload.status_ativo,
        }
        r = supabase.table("clientes").insert(data).select().single().execute()
        return _row_to_cliente(r.data, [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{id}", response_model=ClienteResponse)
def atualizar_cliente(id: str, payload: ClienteUpdate):
    try:
        supabase = get_supabase()
        data = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        if payload.dia_vencimento is not None:
            data["dia_vencimento"] = min(28, max(1, payload.dia_vencimento))
        if not data:
            r = supabase.table("clientes").select("*").eq("id", id).single().execute()
            if not r.data:
                raise HTTPException(status_code=404, detail="Cliente não encontrado")
            r_trans = supabase.table("transacoes").select("cliente_id").gte("data_pagamento", str(date.today().replace(day=1))).lte("data_pagamento", str(date.today())).execute()
            return _row_to_cliente(r.data, r_trans.data or [])
        r = supabase.table("clientes").update(data).eq("id", id).select().single().execute()
        if not r.data:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        r_trans = supabase.table("transacoes").select("cliente_id").gte("data_pagamento", str(date.today().replace(day=1))).lte("data_pagamento", str(date.today())).execute()
        return _row_to_cliente(r.data, r_trans.data or [])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}", status_code=204)
def excluir_cliente(id: str):
    try:
        supabase = get_supabase()
        supabase.table("clientes").delete().eq("id", id).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
