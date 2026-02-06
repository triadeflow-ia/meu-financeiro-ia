-- Habilitar RLS em clientes e transacoes
-- O backend deve usar a chave service_role no .env (SUPABASE_KEY); ela ignora RLS.
-- Acesso com chave anon fica bloqueado até você criar políticas (ex.: para frontend com Supabase Auth).

ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transacoes ENABLE ROW LEVEL SECURITY;

-- Opcional: políticas para o role 'authenticated' (quando usar Supabase Auth no frontend).
-- Descomente e ajuste quando tiver auth.
-- CREATE POLICY "Usuários autenticados podem ler clientes"
--   ON public.clientes FOR SELECT TO authenticated USING (true);
-- CREATE POLICY "Usuários autenticados podem inserir clientes"
--   ON public.clientes FOR INSERT TO authenticated WITH CHECK (true);
-- CREATE POLICY "Usuários autenticados podem atualizar clientes"
--   ON public.clientes FOR UPDATE TO authenticated USING (true) WITH CHECK (true);
-- CREATE POLICY "Usuários autenticados podem ler transacoes"
--   ON public.transacoes FOR SELECT TO authenticated USING (true);
-- CREATE POLICY "Usuários autenticados podem inserir transacoes"
--   ON public.transacoes FOR INSERT TO authenticated WITH CHECK (true);
