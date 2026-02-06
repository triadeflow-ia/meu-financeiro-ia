# Como validar que a solução está funcionando

Siga na ordem. Se algum passo falhar, pare e corrija antes do próximo.

---

## 1. Backend no ar (Railway)

No navegador, abra:

| URL | O que deve aparecer |
|-----|----------------------|
| **https://meu-financeiro-ia-production.up.railway.app/** | `{"message":"MVP Gestão Financeira API","docs":"/docs"}` |
| **https://meu-financeiro-ia-production.up.railway.app/health** | `{"status":"ok"}` |

Se as duas responderem assim, o backend está rodando.

---

## 2. Supabase: tabela e coluna

1. No **Supabase** → **Table Editor** → tabela **clientes**.
2. Confira se existe a coluna **status_ativo** (e as demais: nome, documento_cpf_cnpj, valor_mensalidade, dia_vencimento, created_at, updated_at).
3. (Opcional) Adicione uma linha manualmente para testar: nome "Teste", valor_mensalidade 100, dia_vencimento 10, status_ativo true. Salve. Se salvar sem erro, o schema está ok.

---

## 3. Webhook responde 200 (teste com curl)

No **PowerShell** ou **Prompt de Comando**, rode (tudo em uma linha):

```bash
curl -X POST "https://meu-financeiro-ia-production.up.railway.app/api/webhook/whatsapp" -H "Content-Type: application/json" -d "{\"fromMe\":false,\"phone\":\"5511999999999\",\"text\":{\"message\":\"Oi, so um teste\"}}"
```

**Esperado:** resposta HTTP 200 e um JSON com `"ok": true` e `"resposta": "..."`.  
Se aparecer 401, confira **ZAPI_SECURITY_TOKEN** (se estiver definido no Railway, o header precisa bater). Se aparecer 500, veja os logs do Railway.

---

## 4. Cadastro de cliente pelo webhook (curl)

Teste a intenção “cadastrar cliente”:

```bash
curl -X POST "https://meu-financeiro-ia-production.up.railway.app/api/webhook/whatsapp" -H "Content-Type: application/json" -d "{\"fromMe\":false,\"phone\":\"5511999999999\",\"text\":{\"message\":\"Cadastrar cliente Maria Silva, CPF 12345678900, mensalidade 350, vencimento dia 15\"}}"
```

**Esperado:** resposta 200 e algo como `"resposta": "Cliente 'Maria Silva' cadastrado com mensalidade R$ 350.00, vencimento dia 15."`

Depois:

1. No **Supabase** → **Table Editor** → **clientes**, confira se existe a linha da **Maria Silva** (nome, valor_mensalidade 350, dia_vencimento 15, status_ativo true).
2. Se a resposta vier com `"Erro ao cadastrar no banco: ..."`, a mensagem após os dois pontos é o motivo do Supabase (ex.: coluna faltando, tipo errado).

---

## 5. Teste pelo WhatsApp (Z-API)

1. Na **Z-API**, confirme que o webhook está: **https://meu-financeiro-ia-production.up.railway.app/api/webhook/whatsapp**.
2. Envie uma mensagem **do seu celular** para o número conectado à Z-API, por exemplo:
   - *"Oi"* → deve voltar uma resposta genérica.
   - *"Cadastrar cliente João Santos, mensalidade 500, vencimento dia 10"* → deve voltar a confirmação de cadastro e deve aparecer o cliente **João Santos** na tabela **clientes** no Supabase.

Se a resposta chegar no WhatsApp e o cliente aparecer na tabela, o fluxo completo está funcionando.

---

## 6. Resumo rápido

| O que validar | Como |
|----------------|------|
| Backend no ar | GET `/` e `/health` retornam JSON |
| Tabela clientes | Coluna `status_ativo` existe; insert manual funciona |
| Webhook 200 | curl POST com `text.message` → resposta 200 e `ok: true` |
| Cadastro via webhook | curl com “Cadastrar cliente…” → 200 e cliente na tabela |
| Fluxo real | Mensagem no WhatsApp “Cadastrar cliente…” → resposta no WhatsApp + linha em clientes |

Se todos os passos acima derem certo, a solução está funcionando.
