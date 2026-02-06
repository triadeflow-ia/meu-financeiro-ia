# Variáveis de ambiente

**Não commite o arquivo `.env`** (ele contém senhas e chaves). Use os `.env.example` como modelo e preencha os valores no seu `.env` local ou no painel do Railway/Vercel.

---

## Backend (`backend/.env`)

Copie `backend/.env.example` para `backend/.env` e preencha:

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `API_KEY` | Não* | Chave para o header `X-API-KEY` nas rotas `/api/` (exceto webhook). Se definido, o frontend precisa enviar o mesmo valor. |
| `SUPABASE_URL` | Sim | URL do projeto Supabase (ex.: `https://xxx.supabase.co`) |
| `SUPABASE_KEY` | Sim | Chave service_role (ou anon) do Supabase |
| `OPENAI_API_KEY` | Sim (webhook) | Chave da OpenAI para GPT e Whisper |
| `ZAPI_BASE_URL` | Uma das opções* | URL base da instância Z-API, **sem** `/send-text` no final |
| `ZAPI_INSTANCE_ID` | Uma das opções* | ID da instância (ex.: `3EE52809B2674111E65B0A9F1770609E`) – use junto com `ZAPI_INSTANCE_TOKEN` |
| `ZAPI_INSTANCE_TOKEN` | Uma das opções* | Token da instância (ex.: `0979A3F00E3994A164770964`) – use junto com `ZAPI_INSTANCE_ID` |
| `ZAPI_CLIENT_TOKEN` | Não | **Client Token** da Z-API (header Client-Token) – cole o valor que a Z-API mostra na conta |
| `ZAPI_SECURITY_TOKEN` | Não | Se definido, o webhook exige header `X-ZAPI-Security-Token` ou `Client-Token` com este valor |

\* Para envio de resposta no WhatsApp: defina **ou** `ZAPI_BASE_URL` **ou** o par `ZAPI_INSTANCE_ID` + `ZAPI_INSTANCE_TOKEN`. No Railway é prático usar ID e token separados.
| `CORS_ORIGINS` | Se front em outro domínio | URLs do frontend separadas por vírgula (ex.: `https://meu-app.vercel.app`) |
| `SANTANDER_EXTRATO_URL` | Não | URL do extrato Santander sandbox (certificados em `backend/certs/`) |

\* Recomendado em produção.

---

## Frontend (build: Vercel/Railway/Docker)

Use `frontend/.env.example` como base. Variáveis **no build** (ex.: Vercel → Environment Variables):

| Variável | Descrição |
|----------|-----------|
| `VITE_API_KEY` | Mesmo valor do `API_KEY` do backend (se usar) |
| `VITE_API_URL` | URL do backend quando o front está em outro domínio (ex.: `https://xxx.up.railway.app`). Deixe vazio em dev local (proxy). |
| `VITE_SUPABASE_URL` | URL do projeto Supabase |
| `VITE_SUPABASE_ANON_KEY` | Chave anon (pública) do Supabase (Realtime) |

---

## Onde estão os arquivos

| Arquivo | No Git? | Uso |
|---------|---------|-----|
| `backend/.env` | Não (ignorado) | Suas chaves reais – nunca commitar |
| `backend/.env.example` | Sim | Modelo – copiar para `backend/.env` |
| `frontend/.env` | Não (ignorado) | Chaves reais do front – nunca commitar |
| `frontend/.env.example` | Sim | Modelo – copiar para `frontend/.env` ou preencher no painel do deploy |
| `.env.example` (raiz) | Sim | Referência para build Docker do frontend |

Para **Railway** (backend): em Variables do serviço, adicione as variáveis do backend listadas acima.  
Para **Vercel** (frontend): em Environment Variables, adicione as variáveis `VITE_*` do frontend.
