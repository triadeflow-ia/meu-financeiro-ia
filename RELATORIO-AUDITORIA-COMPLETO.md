# Relatório de Auditoria Completo – meu-financeiro-ia

**Data:** 7 de fevereiro de 2026  
**Objetivo:** Documento único para qualquer IA ou equipe entender **tudo** que existe no projeto: estrutura, stack, rotas, banco, integrações, variáveis, deploy, testes e estado atual.

---

## 1. Visão geral

| Item | Valor |
|------|--------|
| **Nome** | meu-financeiro-ia (Gestão Financeira Inteligente) |
| **Tipo** | MVP full-stack |
| **Backend** | Python 3.x, FastAPI, Uvicorn |
| **Frontend** | React 18, Vite 5, TypeScript, Tailwind CSS |
| **Banco** | Supabase (PostgreSQL) |
| **Integrações** | Z-API (WhatsApp), OpenAI (GPT-4o + Whisper), Santander (mTLS, opcional) |
| **Deploy backend** | Railway (`meu-financeiro-ia-production.up.railway.app`) |
| **URL da API** | `https://meu-financeiro-ia-production.up.railway.app/api` |

**O que o sistema faz:**

- Cadastro e listagem de **clientes** (nome, documento, mensalidade, dia de vencimento 1–28, status ativo).
- **Transações** (pagamentos) por cliente, com status de nota fiscal (pendente/emitida/cancelada) e anti-duplicidade por `hash_bancario`.
- **Dashboard:** KPIs (total recebido no mês, notas a emitir, clientes inadimplentes); tabela de clientes com status Pago/Pendente/Atrasado; CRUD completo (Novo, Editar, Excluir); Sincronizar Santander; Exportar CSV para contabilidade.
- **Webhook WhatsApp (Z-API):** recebe mensagens (texto ou áudio), processa com OpenAI (cadastrar cliente ou baixa manual), envia a resposta de volta no WhatsApp via Z-API send-text (dois tokens: URL da instância + Client-Token de segurança da conta).
- **Frontend** com dark mode (zinc-950/900), modal de cliente, Toast, Skeleton, Supabase Realtime opcional.

---

## 2. Estrutura completa do repositório

```
meu-financeiro-ia/
├── backend/                          # API FastAPI
│   ├── app/
│   │   ├── main.py                   # FastAPI app, CORS, inclusão dos routers
│   │   ├── config.py                 # Settings (Pydantic), lê .env
│   │   ├── db.py                     # Cliente REST Supabase (httpx)
│   │   ├── routers/
│   │   │   ├── clientes.py           # CRUD, dashboard, export CSV
│   │   │   ├── webhook.py            # POST /api/webhook/whatsapp (Z-API + OpenAI + send-text)
│   │   │   ├── bank.py               # POST /api/bank/sync (Santander mTLS)
│   │   │   └── santander.py          # POST /api/santander/sincronizar (legado)
│   │   ├── api/
│   │   │   └── bank_sync.py          # Lógica: extrato PIX, match com clientes, inserção transacoes
│   │   ├── models/
│   │   │   └── schemas.py            # ClienteCreate, ClienteUpdate, ClienteResponse, etc.
│   │   ├── middleware/
│   │   │   └── api_key.py            # Exige X-API-KEY em /api/* (exceto webhook) se API_KEY definido
│   │   └── santander_api.py         # mTLS, normalização do extrato Santander
│   ├── conexao_banco.py              # Cliente mTLS Santander (certs em backend/certs/)
│   ├── testar_conexao.py             # Script: testa Supabase (clientes)
│   ├── testar_openai.py              # Script: testa OpenAI (gpt-4o-mini)
│   ├── testar_webhook_zapi.py        # Script: POST simulado para webhook (backend em 8000)
│   ├── requirements.txt              # fastapi, uvicorn, httpx, pydantic, pydantic-settings, openai, etc.
│   ├── Dockerfile                    # Build da API
│   ├── railway.json                  # Deploy: root = backend
│   └── certs/                        # privada.key + certificado Santander (não commitados)
├── frontend/
│   ├── src/
│   │   ├── App.tsx                   # Rotas base API, fetchClientes, fetchDashboardKPIs, createCliente, updateCliente, deleteCliente, bankSync, exportContabilidade
│   │   ├── Dashboard.tsx             # KPIs, tabela clientes, modal CRUD (ModalCliente), Toast, Skeleton, Realtime
│   │   ├── Toast.tsx                 # Componente Toast (sucesso/erro)
│   │   ├── main.tsx                  # React root
│   │   ├── index.css                 # Estilos globais + Tailwind
│   │   ├── Dashboard.css             # (opcional)
│   │   ├── vite-env.d.ts
│   │   └── lib/
│   │       └── supabase.ts           # Cliente Supabase para Realtime (VITE_SUPABASE_*)
│   ├── index.html
│   ├── package.json                  # react, vite, tailwind, typescript, @supabase/supabase-js
│   ├── vite.config.ts                # Proxy /api -> backend
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile                    # Build estático + nginx
├── supabase/
│   ├── schema.sql                    # Definição canônica: clientes + transacoes + índices
│   └── migrations/
│       ├── 001_clientes_transacoes.sql
│       ├── 002_add_missing_columns_clientes.sql
│       ├── 003_recriar_tabelas_do_zero.sql   # DROP + CREATE (cuidado: apaga dados)
│       ├── 004_enable_rls.sql                 # RLS em clientes e transacoes
│       └── 005_add_validation_constraints.sql # CHECK valor_mensalidade >= 0, valor >= 0
├── docs/
│   └── Z-API-INTEGRACAO.md           # Webhook, send-text, dois tokens (URL + Client-Token)
├── .env.example                      # Referência build front (Docker)
├── .gitignore
├── docker-compose.yml                # Backend + front (nginx)
├── README.md                         # Visão geral, configuração, Docker
├── ENV-VARS.md                       # Tabela de variáveis backend/frontend
├── VALIDAR-SOLUCAO.md                # Passo a passo: backend no ar, webhook 200, cadastro, WhatsApp
├── PASSO-A-PASSO-RAILWAY.md          # Configurar Root Directory = backend no Railway
├── DEPLOY-RAILWAY.md
├── PROMPT-INTEGRACAO-GOOGLE-AI-STUDIO.md  # Prompt para outro front (ex.: Google AI Studio) usar esta API
├── RELATORIO-AUDITORIA-MVP.md        # Auditoria anterior (entregas vs pedido)
├── RELATORIO-AUDITORIA-COMPLETO.md   # Este arquivo
├── SUPABASE-400.md                   # Troubleshooting Supabase
└── (outros .md conforme necessário)
```

---

## 3. API Backend – Todas as rotas

| Método | Rota | Descrição | Body (se aplicável) |
|--------|------|-----------|----------------------|
| GET | `/` | Mensagem + link /docs | — |
| GET | `/health` | Healthcheck (Railway) | — |
| GET | `/api/clientes` | Lista todos os clientes com status_pagamento (pago/pendente/atrasado) | — |
| GET | `/api/clientes/dashboard` | KPIs: total_recebido, notas_a_emitir, clientes_inadimplentes | — |
| GET | `/api/clientes/export/contabilidade` | CSV: Data, Cliente, Valor, Documento (StreamingResponse) | — |
| GET | `/api/clientes/{id}` | Um cliente por UUID | — |
| POST | `/api/clientes` | Criar cliente | JSON: nome, documento_cpf_cnpj?, valor_mensalidade, dia_vencimento (1-28), status_ativo? |
| PATCH | `/api/clientes/{id}` | Atualizar cliente (parcial) | JSON: qualquer subconjunto dos campos do cliente |
| DELETE | `/api/clientes/{id}` | Excluir cliente | — (204 sem body) |
| POST | `/api/bank/sync` | Sincronizar Santander (mTLS, extrato, match PIX → transacoes) | — |
| POST | `/api/santander/sincronizar` | Legado Santander | — |
| POST | `/api/webhook/whatsapp` | Webhook Z-API: recebe payload (texto/áudio), OpenAI, cadastra/baixa, envia resposta Z-API send-text | JSON: payload Z-API (phone, text.message, fromMe, etc.) |

**Autenticação:**

- Se `API_KEY` estiver definido no backend: todas as rotas `/api/*` (exceto `/api/webhook/whatsapp`) exigem header **X-API-KEY** com o mesmo valor; caso contrário 401.
- Webhook: se `ZAPI_SECURITY_TOKEN` estiver definido, exige header **X-ZAPI-Security-Token** ou **Client-Token** com esse valor.

---

## 4. Banco de dados (Supabase)

**Tabelas:**

- **clientes:** id (uuid PK), nome (text), documento_cpf_cnpj (text nullable), valor_mensalidade (numeric), dia_vencimento (smallint 1–28), status_ativo (boolean), created_at, updated_at. Constraint: valor_mensalidade >= 0.
- **transacoes:** id (uuid PK), cliente_id (FK clientes), valor (numeric), data_pagamento (date), status_nota_fiscal (pendente|emitida|cancelada), hash_bancario (text), created_at. Unique (cliente_id, data_pagamento). Constraint: valor >= 0.

**Migrações (ordem):** 001 → 002 → 003 (recriar do zero) → 004 (RLS) → 005 (CHECKs).

**Backend:** usa `SUPABASE_URL` e `SUPABASE_KEY` (service_role); service_role ignora RLS.

---

## 5. Variáveis de ambiente

**Backend (Railway / backend/.env):**

- **Obrigatórias:** SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY (para webhook).
- **Z-API (envio no WhatsApp):** ZAPI_BASE_URL **ou** (ZAPI_INSTANCE_ID + ZAPI_INSTANCE_TOKEN); ZAPI_CLIENT_TOKEN = token de **segurança da conta** (aba Segurança), não o token da instância.
- **Opcionais:** API_KEY, ZAPI_SECURITY_TOKEN, CORS_ORIGINS, SANTANDER_EXTRATO_URL; certificados em backend/certs/.

**Frontend (build):**

- VITE_API_URL (URL do backend se front em outro domínio), VITE_API_KEY (se backend usar API_KEY), VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY (Realtime).

Detalhes: **ENV-VARS.md** e **backend/.env.example**.

---

## 6. Frontend – Detalhes

- **App.tsx:** define API_BASE (VITE_API_URL ou /api), apiHeaders (X-API-KEY), exporta fetchClientes, fetchDashboardKPIs, createCliente, updateCliente, deleteCliente, bankSync, exportContabilidade e tipos Cliente, DashboardKPIs, ClientePayload.
- **Dashboard.tsx:** estado (clientes, kpis, loading, modal, editingCliente, modalForm, submitting, deletingId, toast); load(); openNewModal, openEditModal, closeModal; handleSubmitCliente (create/update via App), handleExcluir (deleteCliente); ModalCliente (form Nome, Documento, Valor, Dia 1–28); tabela com Badge de status; Supabase Realtime (canal clientes + transacoes) para atualizar lista sem F5.
- **Build:** `npm run build` (tsc + vite) passa sem erros.

---

## 7. Webhook WhatsApp (resumo)

- **Entrada:** POST /api/webhook/whatsapp com payload Z-API (phone, text.message, fromMe, participantPhone, etc.). Áudio: transcreve com Whisper.
- **Lógica:** OpenAI (GPT-4o) extrai intenção → cadastrar_cliente ou baixa_manual ou resposta livre. Validação (nome, valor >= 0, dia 1–28) antes de inserir.
- **Resposta no WhatsApp:** extração do número de `body.phone` (prioridade) ou participantPhone, normalização com _normalizar_phone; POST para Z-API send-text com header Client-Token (ZAPI_CLIENT_TOKEN = token segurança da conta). URL da Z-API = ZAPI_BASE_URL ou montada com ZAPI_INSTANCE_ID + ZAPI_INSTANCE_TOKEN.

Documentação completa: **docs/Z-API-INTEGRACAO.md**.

---

## 8. Deploy e testes

- **Backend no Railway:** Root Directory = `backend`; variáveis conforme ENV-VARS.md. URL: meu-financeiro-ia-production.up.railway.app.
- **Testes locais:**  
  - `cd backend && python testar_conexao.py` (Supabase)  
  - `cd backend && python testar_openai.py` (OpenAI)  
  - `cd backend && python testar_webhook_zapi.py` (exige backend rodando em 127.0.0.1:8000)
- **Validação em produção:** seguir **VALIDAR-SOLUCAO.md** (health, webhook 200, cadastro via curl, teste real WhatsApp).

---

## 9. Documentos de referência

| Arquivo | Conteúdo |
|---------|----------|
| README.md | Visão geral, estrutura, configuração local, Docker |
| ENV-VARS.md | Variáveis backend e frontend |
| docs/Z-API-INTEGRACAO.md | Webhook Z-API, send-text, dois tokens |
| VALIDAR-SOLUCAO.md | Passo a passo para validar que a solução funciona |
| PASSO-A-PASSO-RAILWAY.md | Configurar Root Directory no Railway |
| PROMPT-INTEGRACAO-GOOGLE-AI-STUDIO.md | Prompt para outro front (ex.: Google AI Studio) consumir esta API |

---

## 10. Estado atual (fev/2026)

- **Backend:** estável; webhook com extração de phone priorizando body.phone; validação no cadastro e na baixa; dois tokens Z-API documentados.
- **Frontend:** CRUD completo; build OK; dark mode; modal e Toast.
- **Banco:** schema e migrações 001–005 aplicáveis; RLS habilitado; CHECKs de valor.
- **Pendências sugeridas:** testes automatizados (pytest); políticas RLS explícitas se front usar anon key; fluxo de emissão de notas (hoje só status e KPI).

---

*Este relatório contém tudo que uma IA ou desenvolvedor precisa para entender o projeto meu-financeiro-ia de ponta a ponta.*
