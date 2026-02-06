-- Gestão Financeira Inteligente - Schema Supabase
-- Execute no SQL Editor do Supabase

-- clientes: id, nome, documento_cpf_cnpj, valor_mensalidade, dia_vencimento, status_ativo
create table if not exists public.clientes (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  documento_cpf_cnpj text,
  valor_mensalidade numeric(12, 2) not null,
  dia_vencimento smallint not null check (dia_vencimento >= 1 and dia_vencimento <= 28),
  status_ativo boolean not null default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- transacoes: id, cliente_id, valor, data_pagamento, status_nota_fiscal, hash_bancario
create table if not exists public.transacoes (
  id uuid primary key default gen_random_uuid(),
  cliente_id uuid not null references public.clientes(id) on delete restrict,
  valor numeric(12, 2) not null,
  data_pagamento date not null,
  status_nota_fiscal text not null default 'pendente' check (status_nota_fiscal in ('pendente', 'emitida', 'cancelada')),
  hash_bancario text,
  created_at timestamptz default now(),
  unique(cliente_id, data_pagamento)
);

create index if not exists idx_clientes_status_ativo on public.clientes (status_ativo);
create index if not exists idx_clientes_nome on public.clientes (nome);
create index if not exists idx_transacoes_cliente_id on public.transacoes (cliente_id);
create index if not exists idx_transacoes_data_pagamento on public.transacoes (data_pagamento);
create index if not exists idx_transacoes_hash_bancario on public.transacoes (hash_bancario);

-- Comentários
comment on table public.clientes is 'Clientes com mensalidade e dia de vencimento';
comment on table public.transacoes is 'Pagamentos recebidos; hash_bancario evita duplicidade no match';
