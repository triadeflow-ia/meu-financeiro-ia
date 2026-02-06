# Erro 400 ao cadastrar cliente (Supabase)

Se o webhook da Z-API retornar **500** e nos logs aparecer:

`Client error '400 Bad Request' for url '...supabase.co/rest/v1/clientes'`

significa que o **Supabase rejeitou o INSERT** na tabela `clientes`. As causas mais comuns:

---

## 1. Tabela com estrutura diferente

A tabela `clientes` no seu projeto Supabase precisa ter **exatamente** estas colunas (nomes em minúsculo):

| Coluna              | Tipo              | Obrigatório |
|---------------------|-------------------|-------------|
| `id`                | uuid (default)    | não (gerado) |
| `nome`              | text              | sim |
| `documento_cpf_cnpj`| text              | não |
| `valor_mensalidade` | numeric(12,2)     | sim |
| `dia_vencimento`    | smallint (1–28)   | sim |
| `status_ativo`      | boolean (default true) | não |
| `created_at`        | timestamptz (default now()) | não |
| `updated_at`        | timestamptz (default now()) | não |

**O que fazer:** No Supabase, abra **SQL Editor** e execute o conteúdo do arquivo **`supabase/schema.sql`** do projeto. Se a tabela já existir com outro formato, você pode:

- **Opção A:** Apagar a tabela `clientes` (e `transacoes` se existir) e rodar o `schema.sql` de novo, **ou**
- **Opção B:** Ajustar a tabela com `ALTER TABLE` para ter as colunas acima (nomes e tipos iguais).

---

## 2. RLS (Row Level Security) bloqueando

Se **Row Level Security** estiver ativo na tabela `clientes` e não houver política que permita INSERT com a chave que você usa (`SUPABASE_KEY`), o Supabase pode devolver 400 ou 403.

**O que fazer:** No painel do Supabase, em **Table Editor** → tabela `clientes` → **Policies**. Ou use uma chave **service_role** em `SUPABASE_KEY` (a service_role ignora RLS). Nunca exponha a service_role no frontend; use só no backend (Railway).

---

## 3. Ver a mensagem exata do Supabase

Depois do ajuste no código, em novos erros o webhook passa a responder **200** com uma mensagem do tipo:

`Erro ao cadastrar no banco: <mensagem do Supabase>`

Assim você vê no WhatsApp ou nos logs qual foi o motivo (coluna inexistente, tipo errado, etc.) e pode corrigir a tabela de acordo.
