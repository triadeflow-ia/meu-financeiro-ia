from pydantic import BaseModel
from typing import Optional
from datetime import date
from decimal import Decimal


class ClienteBase(BaseModel):
    nome: str
    documento_cpf_cnpj: Optional[str] = None
    valor_mensalidade: float
    dia_vencimento: int  # 1-28
    status_ativo: bool = True


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    documento_cpf_cnpj: Optional[str] = None
    valor_mensalidade: Optional[float] = None
    dia_vencimento: Optional[int] = None
    status_ativo: Optional[bool] = None


class ClienteResponse(ClienteBase):
    id: str
    status_pagamento: str  # "pago" | "pendente" | "atrasado" (calculado)

    class Config:
        from_attributes = True


class TransacaoBase(BaseModel):
    cliente_id: str
    valor: float
    data_pagamento: date
    status_nota_fiscal: str = "pendente"
    hash_bancario: Optional[str] = None


class TransacaoCreate(TransacaoBase):
    pass


class TransacaoResponse(TransacaoBase):
    id: str

    class Config:
        from_attributes = True
