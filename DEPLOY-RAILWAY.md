# Deploy no Railway

Guia para colocar o **backend** (e opcionalmente o frontend) no Railway. Com o backend online, a Z-API chama o webhook sem ngrok.

---

## 1. Backend no Railway

### 1.1 Conectar o repositório

1. Acesse [railway.app](https://railway.app) e entre na sua conta.
2. **New Project** → **Deploy from GitHub repo**.
3. Escolha o repositório do projeto (ex.: `meu-financeiro-ia`).
4. Railway cria um serviço. Clique nele para abrir as configurações.

### 1.2 Definir raiz e build (obrigatório)

O repositório tem **backend/** e **frontend/** na raiz. O Railway precisa buildar só a pasta do backend:

1. Em **Settings** do serviço do **backend**:
   - **Root Directory:** `backend` ← **defina isso** (sem isso o Railpack tenta buildar a raiz e falha com "could not determine how to build").
   - **Builder:** **Dockerfile** (ou deixe em automático; o `backend/railway.json` força o uso do Dockerfile).
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
| `CORS_ORIGINS` | Necessário se o front estiver em outro domínio | URL do front (ex.: `https://meu-app.vercel.app`) |

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

## 2. Frontend em outro lugar (Vercel, Netlify, etc.)

Se o front **não** estiver no Railway, você pode hospedá-lo na **Vercel** ou **Netlify** e apontar para o backend no Railway.

### 2.1 Deploy do frontend (ex.: Vercel)

1. Acesse [vercel.com](https://vercel.com) (ou Netlify) e conecte o repositório **meu-financeiro-ia**.
2. **Root Directory:** `frontend`.
3. **Build Command:** `npm run build` | **Output:** `dist`.
4. Em **Environment Variables** (variáveis de **build**), adicione:
   - `VITE_API_URL` = **URL do backend no Railway** (ex.: `https://meu-financeiro-backend-production-xxxx.up.railway.app`)
   - `VITE_API_KEY` = mesmo valor do `API_KEY` do backend (se você usa)
   - `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY` (para Realtime, se quiser)
5. Faça o deploy. A Vercel gera uma URL (ex.: `https://meu-financeiro-ia.vercel.app`).

### 2.2 Liberar CORS no backend (Railway)

No Railway, nas **Variables** do serviço do **backend**, adicione:

- `CORS_ORIGINS` = URL do front (ex.: `https://meu-financeiro-ia.vercel.app`)

Se tiver mais de um domínio, use vírgula: `https://app.vercel.app,https://outro.netlify.app`.

Faça um novo deploy do backend no Railway para aplicar. Depois disso, o front na Vercel/Netlify consegue chamar a API no Railway.

---

## 3. Frontend no Railway (opcional)

Se quiser o Dashboard também no Railway:

1. **New Service** no mesmo projeto → **Deploy from GitHub** (mesmo repo).
2. **Root Directory:** `frontend`.
3. **Builder:** **Dockerfile** (usa o `frontend/Dockerfile`).
4. Em **Variables**, defina as **build** (Build Variables / durante o build):
   - `VITE_API_URL` = URL pública do backend no Railway (ex.: `https://xxx.up.railway.app`)
   - `VITE_API_KEY` (mesmo valor do `API_KEY` do backend)
   - `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY`
5. No **backend**, adicione em Variables: `CORS_ORIGINS` = URL do serviço do front no Railway (após gerar domínio).
6. **Generate Domain** para o serviço do frontend.

O frontend em Docker usa Nginx e faz proxy de `/api` para o backend. Para isso funcionar no Railway, você tem duas opções:

- **A)** Colocar backend e frontend no mesmo projeto e usar **Railway Private Network**: no `frontend/nginx.conf`, em vez de `http://backend:8000`, usar a **URL interna do serviço backend** (Railway mostra algo como `http://backend.railway.internal:PORT` ou a URL do serviço). Como no Railway cada serviço tem sua própria URL pública, o Nginx do frontend não resolve o nome `backend` por padrão. Nesse caso, o mais simples é o frontend chamar a **URL pública do backend** nas requisições (ex.: `VITE_API_URL=https://xxx.up.railway.app`) e não usar proxy no Nginx para `/api`.
- **B)** Deixar o front só no Railway servindo os arquivos estáticos, e no build apontar as chamadas de API para a URL pública do backend (variável `VITE_API_URL` ou similar no frontend).

Para manter o guia simples: **só o backend no Railway já resolve o webhook.** O frontend você pode continuar rodando local (`npm run dev`) e apontando o proxy para a URL do Railway, ou depois configuramos o front com `VITE_API_URL` para a URL do backend no Railway.

---

## 4. Resumo rápido

1. **New Project** → Deploy from GitHub → repo do projeto.
2. Serviço do **backend**: Root = `backend`, Builder = Dockerfile.
3. **Variables**: colar `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `ZAPI_BASE_URL`, etc.
4. **Generate Domain** no serviço do backend.
5. Copiar a URL e configurar na Z-API: `https://SUA-URL/api/webhook/whatsapp`.

Depois disso, as mensagens do WhatsApp passam a ser recebidas e respondidas pelo backend **online**, sem ngrok.
