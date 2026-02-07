# Prompt para Google AI Studio – Integração com o Backend

Copie o bloco abaixo e cole no chat do **Google AI Studio** quando for criar ou ajustar o frontend. O assistente usará essas informações para integrar a interface com a API do backend.

---

## Bloco para colar no Google AI Studio

```
Você vai construir (ou ajustar) um frontend que consome uma API REST real. Use EXATAMENTE o backend abaixo.

## Backend disponível

- **URL base da API:** `https://meu-financeiro-ia-production.up.railway.app`
- **Prefixo das rotas:** `/api`
- **Documentação interativa:** `https://meu-financeiro-ia-production.up.railway.app/docs`
- Todas as requisições devem ser em **JSON** (Content-Type: application/json quando houver body).
- Se o backend estiver configurado com API Key em produção, será necessário enviar o header: **X-API-KEY** com o valor que o dono do backend informar. Se não informar API Key, faça as chamadas sem esse header.

## Endpoints disponíveis

### 1) Listar clientes
- **GET** `https://meu-financeiro-ia-production.up.railway.app/api/clientes`
- Resposta: array de objetos com: id, nome, documento_cpf_cnpj, valor_mensalidade, dia_vencimento, status_ativo, status_pagamento (string: "pago" | "pendente" | "atrasado").

### 2) KPIs do dashboard
- **GET** `https://meu-financeiro-ia-production.up.railway.app/api/clientes/dashboard`
- Resposta: { "total_recebido": number, "notas_a_emitir": number, "clientes_inadimplentes": number }.

### 3) Obter um cliente por ID
- **GET** `https://meu-financeiro-ia-production.up.railway.app/api/clientes/{id}`
- Substitua {id} pelo UUID do cliente.
- Resposta: mesmo formato de um item da listagem.

### 4) Criar cliente
- **POST** `https://meu-financeiro-ia-production.up.railway.app/api/clientes`
- Body (JSON): { "nome": string (obrigatório), "documento_cpf_cnpj": string | null (opcional), "valor_mensalidade": number (obrigatório), "dia_vencimento": number 1–28 (obrigatório), "status_ativo": boolean (opcional, default true) }.
- Resposta: objeto do cliente criado (com id e status_pagamento).

### 5) Atualizar cliente
- **PATCH** `https://meu-financeiro-ia-production.up.railway.app/api/clientes/{id}`
- Body (JSON): qualquer subconjunto de { "nome", "documento_cpf_cnpj", "valor_mensalidade", "dia_vencimento", "status_ativo" }. Apenas os campos enviados são atualizados.
- Resposta: objeto do cliente atualizado.

### 6) Excluir cliente
- **DELETE** `https://meu-financeiro-ia-production.up.railway.app/api/clientes/{id}`
- Resposta: status 204 sem body.

### 7) Exportar CSV para contabilidade
- **GET** `https://meu-financeiro-ia-production.up.railway.app/api/clientes/export/contabilidade`
- Resposta: arquivo CSV (Content-Disposition: attachment; filename=contabilidade.csv). Trate como download (blob ou link de download).

### 8) Sincronizar Santander (extrato bancário)
- **POST** `https://meu-financeiro-ia-production.up.railway.app/api/bank/sync`
- Sem body. Resposta (JSON): { "message": string, "transacoes_extrato": number, "matches_criados": number }.

### 9) Health check (testar se o backend está no ar)
- **GET** `https://meu-financeiro-ia-production.up.railway.app/health`
- Resposta: { "status": "ok" }.

## CORS
O backend já aceita requisições de origens diferentes (CORS configurado). Se o front rodar em outro domínio e der erro de CORS, o dono do backend pode adicionar a origem nas variáveis de ambiente (CORS_ORIGINS) do Railway.

## Resumo para você (assistente)
- Use a URL base acima para todas as chamadas.
- GET para listar e obter dados; POST para criar e para bank/sync; PATCH para editar; DELETE para excluir.
- Sempre envie Content-Type: application/json nos POST e PATCH, e body em JSON.
- Trate erros pelos status HTTP (401, 404, 500) e, quando vier body JSON de erro, use o campo "detail" para mensagem.
- O frontend que você gerar deve permitir: ver lista de clientes, ver KPIs (total recebido, notas a emitir, inadimplentes), criar cliente, editar cliente, excluir cliente e, se fizer sentido na UI, botões para “Sincronizar Santander” e “Exportar CSV”.
```

---

## Uso

1. Abra o **Google AI Studio** (ou o produto onde você está criando o front).
2. Cole o **bloco inteiro** (de “Você vai construir…” até “…Exportar CSV”) no prompt/chat.
3. Peça, por exemplo: “Gere o código do frontend (HTML/JS ou React) que usa essa API” ou “Ajuste a tela de clientes para usar esses endpoints”.
4. Se o backend usar **API Key**, adicione no prompt: “O header **X-API-KEY** deve ser enviado em todas as requisições para /api/ com o valor: [COLOQUE_AQUI_O_VALOR].”

Se quiser, posso adaptar esse prompt para outro formato (ex.: só endpoints, ou em inglês).
