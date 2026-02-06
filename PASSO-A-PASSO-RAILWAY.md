# Passo a passo: configurar Root Directory no Railway

Siga estes passos **na ordem**. Assim o Railway para de dar erro "could not determine how to build".

---

## 1. Abrir o Railway

1. Abra o navegador e vá em: **https://railway.app**
2. Faça login na sua conta.
3. Clique no **projeto** onde está o deploy do **meu-financeiro-ia** (o que deu erro de build).

---

## 2. Entrar no serviço (backend)

1. No projeto, você vê um ou mais **serviços** (caixinhas/cards).
2. Clique no **serviço** que foi criado quando você conectou o repositório **meu-financeiro-ia**.
3. Esse serviço é o que vamos configurar.

---

## 3. Abrir as configurações (Settings)

1. No topo da tela do serviço, procure a aba ou o menu **"Settings"** (Configurações).
2. Clique em **Settings**.

---

## 4. Achar “Root Directory” ou “Source”

Na página de Settings, role a tela e procure uma das opções:

- **"Root Directory"**, ou  
- **"Source"** (com um campo de texto ao lado), ou  
- **"Build"** → dentro dela, **"Root Directory"** ou **"Working Directory"**.

O campo pode estar vazio ou com um ponto (`.`).

---

## 5. Colocar só a pasta do backend

1. No campo **Root Directory** (ou equivalente), **apague** o que estiver.
2. Digite **exatamente** (sem aspas):  
   **`backend`**
3. Clique em **Save** / **Salvar** (se aparecer), ou saia da tela (às vezes salva sozinho).

Não use barra no início nem no fim. Só: **backend**

---

## 6. Fazer um novo deploy

1. Volte para a aba **"Deployments"** (ou a tela principal do serviço).
2. Clique no botão **"Redeploy"** ou **"Deploy"** (ou nos três pontinhos do último deploy → **Redeploy**).

O Railway vai buildar de novo, agora usando só a pasta **backend**, e o build deve passar.

---

## Resumo em uma frase

**Settings do serviço → Root Directory = `backend` → Salvar → Redeploy.**

---

## Se não achar “Root Directory”

Algumas contas do Railway mostram isso em outro lugar:

1. No **projeto** (não no serviço), clique em **"Settings"** do projeto.
2. Ou no serviço, procure por **"Build"** ou **"Source"** e abra; o campo da pasta costuma estar aí.

Se a interface for em inglês: **Root Directory**, **Source**, **Working Directory** ou **Monorepo root path**.

---

## Depois que o build passar

1. Em **Settings** do mesmo serviço, vá em **Networking** (ou **Public Networking**) e clique em **Generate Domain** para criar a URL pública.
2. Copie a URL (ex.: `https://meu-financeiro-ia-production-xxxx.up.railway.app`).
3. Na Z-API, configure o webhook: **essa URL** + **`/api/webhook/whatsapp`**  
   Exemplo: `https://meu-financeiro-ia-production-xxxx.up.railway.app/api/webhook/whatsapp`
4. Em **Variables** do serviço, adicione as variáveis do `backend/.env` (SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, ZAPI_BASE_URL, etc.) — veja o arquivo **ENV-VARS.md** na raiz do projeto.

Se travar em algum passo, diga em qual (por exemplo: “não acho Root Directory” ou “não acho Redeploy”) que eu te oriento no próximo clique.

---

## Erro depois que o build passou (container sobe mas algo falha)

1. **Confira as variáveis (Variables)**  
   No Railway, aba **Variables** do serviço, verifique se estão definidas: `SUPABASE_URL`, `SUPABASE_KEY`, `OPENAI_API_KEY`, `ZAPI_BASE_URL`. Se alguma faltar, o app pode dar 500 no webhook ou ao listar clientes.

2. **Teste se o backend está no ar**  
   Abra no navegador: **https://meu-financeiro-ia-production.up.railway.app/** (deve retornar JSON) e **https://meu-financeiro-ia-production.up.railway.app/health** (deve retornar `{"status":"ok"}`). Se isso funcionar, o container está rodando; erro no webhook costuma ser variável faltando.

3. **Logs**  
   Mensagens INFO do Uvicorn às vezes aparecem como "error" no Railway (é só a classificação). Erro real costuma ter "Traceback" ou "Defina SUPABASE_URL e SUPABASE_KEY". Nesse caso, preencha **Variables** e faça **Redeploy**.
