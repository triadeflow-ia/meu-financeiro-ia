-- Validação no banco: garantir valores não negativos
-- Execute no SQL Editor do Supabase (tabelas já existentes)

-- clientes: mensalidade não pode ser negativa
ALTER TABLE public.clientes
  DROP CONSTRAINT IF EXISTS clientes_valor_mensalidade_non_negative;
ALTER TABLE public.clientes
  ADD CONSTRAINT clientes_valor_mensalidade_non_negative
  CHECK (valor_mensalidade >= 0);

-- transacoes: valor do pagamento não pode ser negativo
ALTER TABLE public.transacoes
  DROP CONSTRAINT IF EXISTS transacoes_valor_non_negative;
ALTER TABLE public.transacoes
  ADD CONSTRAINT transacoes_valor_non_negative
  CHECK (valor >= 0);
