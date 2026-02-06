# Gestão Financeira Inteligente

MVP full-stack para eliminar trabalho manual de controle de pagamentos e emissão de notas.

**Stack:** React (Vite) + Tailwind CSS · Python (FastAPI) · Supabase (PostgreSQL) · Santander (mTLS) · WhatsApp webhook + OpenAI.

## Estrutura

```
meu-financeiro-ia/
├── backend/                    # FastAPI
│   ├── certs/                  # privada.key + certificado .crt do Santander
│   ├── app/
│   │   ├── routers/            # clientes, bank, webhook, santander
│   │   ├── models/
│   │   ├── db.py
│   │   ├── santander_api.py
│   │   └── main.py
│   ├── conexao_banco.py        # mTLS Santander
│   └── requirements.txt
├── frontend/                   # React + Vite + Tailwind
│   └── src/
│       ├── App.tsx
│       ├── Dashboard.tsx      # Dark mode, KPIs, tabela, ações
│       └── index.css
├── supabase/
│   └── schema.sql              # clientes + transacoes
└── README.md
```

## Banco de Dados (Supabase)

Execute `supabase/schema.sql` no SQL Editor do projeto:

- **clientes:** id, nome, documento_cpf_cnpj, valor_mensalidade, dia_vencimento (1–28), status_ativo
- **transacoes:** id, cliente_id, valor, data_pagamento, status_nota_fiscal, hash_bancario

## Configuração

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
cp .env.example .env
```

No `.env`:

- `SUPABASE_URL` e `SUPABASE_KEY`
- `SANTANDER_EXTRATO_URL` (opcional)
- `OPENAI_API_KEY` (para webhook WhatsApp – áudio/texto)

Em `backend/certs/` coloque **privada.key** e o certificado Santander (ex.: **santander.crt**).

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse **http://localhost:5173**. O proxy envia `/api` para o backend.

Opcional – **Supabase Realtime** (atualização automática ao cadastrar cliente pelo WhatsApp etc.):

1. Crie `frontend/.env` com `VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY` (use a **chave anon** do projeto Supabase, não a service_role).
2. No painel Supabase: **Database** → **Replication** → habilite **Realtime** para as tabelas `clientes` e `transacoes`.

## Funcionalidades

### Backend

- **`POST /api/bank/sync`** – Busca extrato Santander (Balance and Statement) via mTLS; faz **match** por valor e nome no PIX e cria transações (evita duplicata por `hash_bancario`).
- **`POST /api/webhook/whatsapp`** – Recebe mensagens (Evolution API / Z-API); usa OpenAI para áudio (Whisper) e texto; **cadastra cliente** ou **dá baixa manual** conforme a intenção.
- **`GET /api/clientes`** – Lista clientes com **status_pagamento** calculado: `pago`, `pendente`, `atrasado`.
- **`GET /api/clientes/dashboard`** – KPIs: total recebido no mês, notas a emitir, clientes inadimplentes.
- **`GET /api/clientes/export/contabilidade`** – CSV: Data, Cliente, Valor, Documento.

### Frontend (Dark Mode)

- **Cards de KPI:** Total Recebido, Notas a Emitir, Clientes Inadimplentes.
- **Tabela de clientes** com badges: **Verde** = Pago, **Amarelo** = Pendente, **Vermelho** = Atrasado.
- **Sincronizar Santander** – loading durante a sincronização.
- **Exportar para Contabilidade** – download do CSV.

## API

Documentação interativa: **http://localhost:8000/docs**.

## Docker

Build e execução com Docker Compose:

```bash
# Backend: configure backend/.env (SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, etc.)
# Frontend (build): na raiz, crie .env com VITE_API_KEY, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY (veja .env.example)

docker-compose up -d --build
```

- **Frontend (app):** http://localhost (Nginx na porta 80; `/api` é repassado ao backend).
- **Backend (direto):** http://localhost:8000 (útil para `/docs`).

Os containers usam **backend/.env** para variáveis do backend; as variáveis **VITE_*** são usadas em tempo de build do frontend (defina-as na raiz em `.env` ou no ambiente antes de `docker-compose build`).

## Observações

- Ajuste a URL e o formato do extrato em `app/santander_api.py` conforme a documentação do Santander (Balance and Statement).
- Certificados e `.env` não devem ser commitados (veja `.gitignore`).
