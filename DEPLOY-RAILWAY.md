# Deploy no Railway

Guia para colocar o **backend** (e opcionalmente o frontend) no Railway. Com o backend online, a Z-API chama o webhook sem ngrok.

---

## 1. Backend no Railway

### 1.1 Conectar o repositório

1. Acesse [railway.app](https://railway.app) e entre na sua conta.
2. **New Project** → **Deploy from GitHub repo**.
3. Escolha o repositório do projeto (ex.: `meu-financeiro-ia`).
4. Railway cria um serviço. Clique nele para abrir as configurações.

### 1.2 Definir raiz e build

1. Em **Settings** do serviço:
   - **Root Directory:** `backend`
   - **Builder:** **Dockerfile** (Railway usa o `backend/Dockerfile`).
2. **Deploy** será disparado automaticamente após o primeiro push ou ao conectar.

### 1.3 Variáveis de ambiente

Em **Variables** do serviço, adicione as mesmas que você usa no `backend/.env`:

| Variável | Obrigatório | Exemplo |
|----------|-------------|---------|
| `SUPABASE_URL` | Sim | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Sim | `eyJ...` (service_role) |
| `OPENAI_API_KEY` | Sim (para webhook) | `sk-proj-...` |
| `ZAPI_BASE_URL` | Sim (para responder no WhatsApp) | `https://api.z-api.io/instances/XXX/token/YYY` |
| `ZAPI_CLIENT_TOKEN` | Opcional | Token da Z-API |
| `API_KEY` | Opcional (segurança) | Chave para header X-API-KEY |
| `ZAPI_SECURITY_TOKEN` | Opcional (validar webhook) | Token que a Z-API envia no header |

Não é necessário definir `PORT`; o Railway define automaticamente.

### 1.4 Domínio público

1. Em **Settings** do serviço, vá em **Networking** / **Generate Domain**.
2. Railway gera uma URL tipo: `https://meu-financeiro-backend-production-xxxx.up.railway.app`

### 1.5 Webhook na Z-API

Use a URL do Railway + rota do webhook:

```
https://SUA-URL-RAILWAY.up.railway.app/api/webhook/whatsapp
```

Exemplo:

```
https://meu-financeiro-backend-production-a1b2.up.railway.app/api/webhook/whatsapp
```

Configure essa URL no painel da Z-API em **Webhook** / **Ao receber mensagem**.

---

## 2. Frontend no Railway (opcional)

Se quiser o Dashboard também no Railway:

1. **New Service** no mesmo projeto → **Deploy from GitHub** (mesmo repo).
2. **Root Directory:** `frontend`.
3. **Builder:** **Dockerfile** (usa o `frontend/Dockerfile`).
4. Em **Variables**, defina as **build** (Build Variables / durante o build):
   - `VITE_API_KEY` (mesmo valor do `API_KEY` do backend)
   - `VITE_SUPABASE_URL`
   - `VITE_SUPABASE_ANON_KEY`
5. **Generate Domain** para o serviço do frontend.

O frontend em Docker usa Nginx e faz proxy de `/api` para o backend. Para isso funcionar no Railway, você tem duas opções:

- **A)** Colocar backend e frontend no mesmo projeto e usar **Railway Private Network**: no `frontend/nginx.conf`, em vez de `http://backend:8000`, usar a **URL interna do serviço backend** (Railway mostra algo como `http://backend.railway.internal:PORT` ou a URL do serviço). Como no Railway cada serviço tem sua própria URL pública, o Nginx do frontend não resolve o nome `backend` por padrão. Nesse caso, o mais simples é o frontend chamar a **URL pública do backend** nas requisições (ex.: `VITE_API_URL=https://xxx.up.railway.app`) e não usar proxy no Nginx para `/api`.
- **B)** Deixar o front só no Railway servindo os arquivos estáticos, e no build apontar as chamadas de API para a URL pública do backend (variável `VITE_API_URL` ou similar no frontend).

Para manter o guia simples: **só o backend no Railway já resolve o webhook.** O frontend você pode continuar rodando local (`npm run dev`) e apontando o proxy para a URL do Railway, ou depois configuramos o front com `VITE_API_URL` para a URL do backend no Railway.

---

## 3. Resumo rápido

1. **New Project** → Deploy from GitHub → repo do projeto.
2. Serviço do **backend**: Root = `backend`, Builder = Dockerfile.
3. **Variables**: colar `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `ZAPI_BASE_URL`, etc.
4. **Generate Domain** no serviço do backend.
5. Copiar a URL e configurar na Z-API: `https://SUA-URL/api/webhook/whatsapp`.

Depois disso, as mensagens do WhatsApp passam a ser recebidas e respondidas pelo backend **online**, sem ngrok.
