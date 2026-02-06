-- Recriar tabelas do zero (apaga as antigas primeiro)
-- Execute no SQL Editor do Supabase
-- ATENÇÃO: isso apaga todos os dados de clientes e transacoes.

-- 1. Apagar na ordem certa (transacoes depende de clientes)
DROP TABLE IF EXISTS public.transacoes;
DROP TABLE IF EXISTS public.clientes;

-- 2. Criar clientes
CREATE TABLE public.clientes (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  documento_cpf_cnpj text,
  valor_mensalidade numeric(12, 2) not null,
  dia_vencimento smallint not null check (dia_vencimento >= 1 and dia_vencimento <= 28),
  status_ativo boolean not null default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 3. Criar transacoes
CREATE TABLE public.transacoes (
  id uuid primary key default gen_random_uuid(),
  cliente_id uuid not null references public.clientes(id) on delete restrict,
  valor numeric(12, 2) not null,
  data_pagamento date not null,
  status_nota_fiscal text not null default 'pendente' check (status_nota_fiscal in ('pendente', 'emitida', 'cancelada')),
  hash_bancario text,
  created_at timestamptz default now(),
  unique(cliente_id, data_pagamento)
);

-- 4. Índices
CREATE INDEX idx_clientes_status_ativo ON public.clientes (status_ativo);
CREATE INDEX idx_clientes_nome ON public.clientes (nome);
CREATE INDEX idx_transacoes_cliente_id ON public.transacoes (cliente_id);
CREATE INDEX idx_transacoes_data_pagamento ON public.transacoes (data_pagamento);
CREATE INDEX idx_transacoes_hash_bancario ON public.transacoes (hash_bancario);

-- 5. Comentários
COMMENT ON TABLE public.clientes IS 'Clientes com mensalidade e dia de vencimento';
COMMENT ON TABLE public.transacoes IS 'Pagamentos recebidos; hash_bancario evita duplicidade no match';
