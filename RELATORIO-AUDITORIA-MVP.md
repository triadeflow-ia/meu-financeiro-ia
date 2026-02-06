# Relatório de Auditoria – MVP Gestão Financeira Inteligente

**Objetivo:** Documento para um agente de IA ou equipe entender o que já foi feito e o que falta no projeto.

**Data do relatório:** Fevereiro 2026  
**Projeto:** meu-financeiro-ia (full-stack: React + FastAPI + Supabase)

---

## 1. Visão geral do que foi pedido vs. entregue

| Área | Pedido | Status |
|------|--------|--------|
| Stack | Backend Python (FastAPI), Frontend React, Supabase | ✅ Implementado |
| Banco | Tabelas `clientes` e `transacoes` | ✅ Schema criado e documentado |
| Santander | Conexão mTLS (privada.key + .crt), extrato, match PIX | ✅ Implementado |
| Webhook WhatsApp | Receber mensagens, OpenAI (texto/áudio), cadastrar cliente / baixa manual | ✅ Implementado |
| Webhook WhatsApp – resposta | Enviar resposta de volta ao WhatsApp (Z-API send-text) | ✅ Implementado |
| Dashboard | Dark mode, KPIs, tabela, badges, botões Sincronizar e Exportar | ✅ Implementado |
| Dashboard – CRUD clientes | Botão Novo Cliente, modal, Editar/Excluir na tabela | ✅ Implementado |
| UX | Skeleton ao carregar, Toast após ações | ✅ Implementado |

---

## 2. O que já está feito (entregue)

### 2.1 Backend (Python / FastAPI)

- **Estrutura:** `backend/app/` com `main.py`, `db.py`, `config.py`, `models/schemas.py`, `routers/`, `api/`.
- **conexao_banco.py** (raiz de `backend/`):
  - Lê certificados de `backend/certs/` (`privada.key` e Santander, ex.: `santander.crt` ou `santander.pem`).
  - Expõe `obter_cliente_santander()` e `obter_cliente_santander_async()` para mTLS com a API do Santander.
- **Rotas disponíveis:**
  - **Clientes:**  
    `GET /api/clientes`, `GET /api/clientes/dashboard`, `GET /api/clientes/export/contabilidade`,  
    `GET /api/clientes/{id}`, `POST /api/clientes`, `PATCH /api/clientes/{id}`, `DELETE /api/clientes/{id}`.
  - **Bank:** `POST /api/bank/sync` – mTLS, extrato PIX, match com clientes, inserção em `transacoes` com anti-duplicidade por `hash_bancario`.
  - **Santander (legado):** `POST /api/santander/sincronizar` – alternativa ao bank/sync.
  - **Webhook:** `POST /api/webhook/whatsapp` – recebe JSON da **Z-API**; usa GPT-4o para extrair intenção; cadastra cliente ou baixa manual; **envia a resposta de volta ao WhatsApp via Z-API send-text** quando `ZAPI_BASE_URL` está configurado.
- **Lógica de negócio:**
  - **app/api/bank_sync.py:** orquestra mTLS, busca PIX, match por valor + nome, inserção em `transacoes`.
  - **app/routers/webhook.py:** extração de texto/áudio do payload Z-API (`body["text"]["message"]`, etc.), áudio (Whisper), interpretação OpenAI, cadastro/baixa; **envio Z-API** via `_enviar_zapi_text(phone, message)` com header `Client-Token` opcional.
  - **app/santander_api.py:** URL configurável via `SANTANDER_EXTRATO_URL`, normalização para match.
  - **app/db.py:** cliente REST Supabase (JWT ou chave `sb_` com header `apikey`).
- **Variáveis de ambiente (backend/.env):**
  - Obrigatórias: `SUPABASE_URL`, `SUPABASE_KEY`.
  - Webhook/OpenAI: `OPENAI_API_KEY`.
  - Z-API (resposta no WhatsApp): `ZAPI_BASE_URL` (base da instância, sem `/send-text`), `ZAPI_CLIENT_TOKEN` (opcional, header Client-Token).
  - Opcionais: `SANTANDER_EXTRATO_URL`, `CERT_KEY_FILE`, `CERT_FILE`.
- **Scripts de teste:**  
  `testar_conexao.py` (Supabase), `testar_openai.py` (OpenAI), **`testar_webhook_zapi.py`** (simula payload Z-API e testa webhook + envio; use `PORT=8000` ou `PORT=8001`).
- **requirements.txt:** FastAPI, uvicorn, httpx, python-dotenv, pydantic, pydantic-settings, openai, certifi, starlette.

### 2.2 Banco de dados (Supabase)

- **Schema em `supabase/schema.sql`:**
  - **clientes:** id (uuid), nome, documento_cpf_cnpj, valor_mensalidade, dia_vencimento (1–28), status_ativo, created_at, updated_at.
  - **transacoes:** id, cliente_id (FK), valor, data_pagamento, status_nota_fiscal (pendente/emitida/cancelada), hash_bancario, created_at; constraint unique(cliente_id, data_pagamento).
  - Índices em status_ativo, nome, cliente_id, data_pagamento, hash_bancario.
- **Migração:** `supabase/migrations/001_clientes_transacoes.sql` para quem já tinha tabela `clientes` antiga.
- **Configuração:** Projeto Supabase com URL e service_role no .env; schema executado no SQL Editor do painel.

### 2.3 Frontend (React + Vite + Tailwind)

- **Estrutura:** `frontend/src/` com `App.tsx`, `Dashboard.tsx`, `Toast.tsx`, `main.tsx`, `index.css`; Tailwind + PostCSS configurados.
- **Dashboard (Dark Mode):**
  - Cards de KPI: Total Recebido, Notas a Emitir, Clientes Inadimplentes (`GET /api/clientes/dashboard`).
  - Tabela de clientes: Nome, Documento, Mensalidade, Vencimento (dia), Status (badges Pago/Pendente/Atrasado), **coluna Ações (Editar / Excluir)**.
  - **Botão "+ Novo Cliente":** abre modal com formulário (Nome, CPF/CNPJ, Valor Mensalidade, Dia Vencimento); envia `POST /api/clientes`; atualiza lista após sucesso.
  - **Editar:** abre o mesmo modal com dados do cliente; envia `PATCH /api/clientes/{id}`; atualiza lista.
  - **Excluir:** confirmação; envia `DELETE /api/clientes/{id}`; atualiza lista.
  - Botão **Sincronizar Santander:** `POST /api/bank/sync`, loading e Toast.
  - Botão **Exportar para Contabilidade:** `GET /api/clientes/export/contabilidade`, download CSV.
- **UX:** Skeleton na tabela e nos KPIs; Toast (sucesso/erro, auto-dismiss 5s); lista de clientes recarregada após criar/editar/excluir.
- **Proxy:** Vite envia `/api` para `http://localhost:8000`.
- **Dependências:** React 18, Vite 5, Tailwind 3. Componentes com Tailwind (sem shadcn/ui instalado via CLI).

### 2.4 Integrações

- **Santander Sandbox:** mTLS implementado; URL e formato do extrato podem precisar de ajuste conforme documentação oficial.
- **OpenAI:** GPT-4o no webhook; Whisper para áudio quando o payload trouxer áudio.
- **Z-API:** Envio da resposta do webhook via `POST {ZAPI_BASE_URL}/send-text` com body `{ "phone", "message" }` e header opcional `Client-Token`; extração de número do payload (phone/participantPhone, ignorando fromMe).

---

## 3. O que falta ou pode ser melhorado

### 3.1 Frontend

- **shadcn/ui:** Não instalado via CLI; para padrão shadcn completo, usar `npx shadcn@latest init` e componentes (Button, Card, Dialog, etc.).
- **Atualização em tempo real:** Dados carregados ao montar e após cada ação; não há polling nem Supabase Realtime para refletir alterações feitas por outros canais (ex.: cadastro via WhatsApp).
- **Dashboard.css:** Arquivo existe; o Dashboard usa principalmente Tailwind e pode tornar o CSS parcialmente redundante.

### 3.2 Backend

- **URL/contrato da API Santander:** Validar com a documentação do Santander Sandbox e ajustar `_normalizar_transacoes` e a URL se necessário.
- **Autenticação da API:** Rotas abertas; não há JWT, API key ou login. Para produção, recomenda-se middleware (API key ou Auth com Supabase).
- **Testes automatizados:** Não há pytest (unitários/integração); apenas scripts manuais.
- **Rota santander/sincronizar:** Duplicada em relação a `bank/sync`; pode ser removida ou mantida por compatibilidade.

### 3.3 Banco de dados (Supabase)

- **RLS (Row Level Security):** Não habilitado; com service_role o acesso é total. Para multi-tenant ou anon key no front, definir políticas RLS.
- **Campo `updated_at` em clientes:** Existe no schema; não há trigger ou lógica no backend para atualizá-lo automaticamente.
- **Emissão de notas:** Apenas status na tabela e KPI “Notas a Emitir”; não há fluxo de “emitir nota” nem integração com NF-e.

### 3.4 DevOps / Ambiente

- **Deploy:** Não há Dockerfile, docker-compose nem instruções de deploy (ex.: Vercel/Railway).
- **Variáveis em produção:** Configurar SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, ZAPI_BASE_URL (e ZAPI_CLIENT_TOKEN se necessário); certificados e SANTANDER_EXTRATO_URL se usar Santander.
- **Certificados Santander:** Em `backend/certs/` (privada.key e .crt/.pem); pasta no .gitignore.

### 3.5 Documentação e produto

- **README.md:** Descreve estrutura, configuração e funcionalidades.
- **Documentação da API:** Swagger em `http://localhost:8000/docs` com o backend rodando.
- **Emissão de notas fiscais:** Sem integração com provedor de NF-e.

---

## 4. Resumo para o agente de IA

- **Já feito:** Projeto full-stack com FastAPI (clientes CRUD, dashboard, bank/sync mTLS, webhook WhatsApp com GPT-4o e **resposta via Z-API send-text**), Supabase (schema clientes + transacoes), frontend React (Dashboard dark, KPIs, tabela com badges, **CRUD de clientes na UI** – Novo Cliente, Editar, Excluir –, Skeleton, Toast, Sincronizar e Exportar CSV). Scripts de teste: Supabase, OpenAI e webhook Z-API.
- **Principais lacunas:** (1) Validar/ajustar URL e formato da API Santander; (2) Proteção de rotas (auth) e, se desejado, RLS no Supabase; (3) Testes automatizados (pytest); (4) Deploy (ex.: Docker); (5) Atualização em tempo real ou polling no frontend; (6) Fluxo de emissão de notas.
- **Arquivos chave:**
  - Backend: `backend/app/main.py`, `backend/app/api/bank_sync.py`, `backend/app/routers/clientes.py`, `backend/app/routers/webhook.py`, `backend/conexao_banco.py`, `backend/app/santander_api.py`, `backend/app/db.py`.
  - Frontend: `frontend/src/Dashboard.tsx`, `frontend/src/App.tsx`, `frontend/src/Toast.tsx`.
  - Banco: `supabase/schema.sql`.
  - Config: `backend/.env`, `backend/.env.example`.
  - Teste webhook: `backend/testar_webhook_zapi.py` (variável `PORT` opcional para URL do backend).

---

## 5. Checklist rápido de verificação

| Item | Como verificar |
|------|----------------|
| Backend com webhook | `POST http://127.0.0.1:8000/api/webhook/whatsapp` com payload Z-API retorna 200 e `{"ok": true, "resposta": "..."}`. |
| Z-API envio | Com `ZAPI_BASE_URL` e `ZAPI_CLIENT_TOKEN` no .env, o mesmo POST acima dispara envio para o número do payload. |
| Dashboard CRUD | Clicar em "+ Novo Cliente", preencher e salvar; na tabela, Editar (modal pré-preenchido) e Excluir (com confirmação). |
| Lista atualiza | Após criar/editar/excluir cliente, a tabela e os KPIs são recarregados. |
| Teste webhook | `cd backend`, `python testar_webhook_zapi.py` (ou `PORT=8001` se o backend estiver na 8001). |

---

*Fim do relatório de auditoria.*
