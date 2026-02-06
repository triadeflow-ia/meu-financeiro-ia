-- Se a tabela clientes já existia sem status_ativo (e outras colunas), adicione-as.
-- Execute no SQL Editor do Supabase.

-- status_ativo (obrigatório para o backend)
ALTER TABLE public.clientes
  ADD COLUMN IF NOT EXISTS status_ativo boolean NOT NULL DEFAULT true;

-- created_at e updated_at (se não existirem)
ALTER TABLE public.clientes
  ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now();
ALTER TABLE public.clientes
  ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now();

-- Índice usado pelo schema
CREATE INDEX IF NOT EXISTS idx_clientes_status_ativo ON public.clientes (status_ativo);
CREATE INDEX IF NOT EXISTS idx_clientes_nome ON public.clientes (nome);
