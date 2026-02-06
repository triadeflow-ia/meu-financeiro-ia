-- Migração: adicionar colunas novas em clientes se a tabela antiga existir
-- (Execute apenas se você já tinha a tabela clientes com estrutura antiga)

-- Adicionar colunas novas mantendo as antigas para não quebrar
do $$
begin
  if exists (select 1 from information_schema.tables where table_schema = 'public' and table_name = 'clientes') then
    alter table public.clientes add column if not exists documento_cpf_cnpj text;
    alter table public.clientes add column if not exists valor_mensalidade numeric(12, 2);
    alter table public.clientes add column if not exists dia_vencimento smallint;
    alter table public.clientes add column if not exists status_ativo boolean default true;
    -- Preencher valor_mensalidade a partir de valor_esperado se existir
    update public.clientes set valor_mensalidade = valor_esperado where valor_mensalidade is null and valor_esperado is not null;
    update public.clientes set dia_vencimento = 10 where dia_vencimento is null;
    update public.clientes set status_ativo = true where status_ativo is null;
  end if;
end $$;
