# Integração Z-API (documentação oficial)

Resumo com base em [developer.z-api.io](https://developer.z-api.io) para webhook **on-message-received** e envio **send-text**.

---

## 1. Webhook: mensagem recebida (on-message-received)

**URL do webhook:** configurada na Z-API (painel ou `PUT .../update-webhook-received`).

**Payload (exemplo texto):**
```json
{
  "phone": "5544999999999",
  "fromMe": false,
  "isGroup": false,
  "type": "ReceivedCallback",
  "text": {
    "message": "texto da mensagem"
  },
  "participantPhone": null
}
```

**Campos usados no backend:**
| Campo | Tipo | Uso |
|-------|------|-----|
| `phone` | string | Número ou ID do grupo que enviou. Direto: `5544999999999`; grupo: `5544999999999-group`. **É o destino da resposta.** |
| `participantPhone` | string \| null | Em grupo, número de quem enviou. Para responder ao grupo, usar `phone`. |
| `fromMe` | boolean | Se `true`, não enviamos resposta. |
| `text.message` | string | Texto da mensagem. |
| `audio` | object | Se existir, mensagem é áudio (audioUrl, etc.). |

**Áudio:** payload traz `audio.audioUrl` (ou base64 conforme doc). O backend usa Whisper para transcrever.

---

## 2. Enviar resposta: send-text

**Método:** `POST`  
**URL:** `https://api.z-api.io/instances/YOUR_INSTANCE/token/YOUR_TOKEN/send-text`

**Header obrigatório (quando ativado na conta):**
| Key | Value |
|-----|--------|
| `Client-Token` | Token de segurança da conta (Account security token) |
| `Content-Type` | `application/json` |

**Body:**
```json
{
  "phone": "5511999999999",
  "message": "Texto da resposta"
}
```

- **phone:** só números, sem máscara (ex.: `5511999999999`). Para grupo, usar o ID do grupo (ex.: formato com `-group` conforme webhook).
- **message:** texto a enviar (aceita formatação WhatsApp e emojis).

**Resposta 200:** `{ "zaapId": "...", "messageId": "..." }`  
**Erro sem Client-Token:** `{ "error": "null not allowed" }`

---

## 3. Os dois tipos de autenticação (doc Z-API)

A Z-API usa **dois** identificadores; os dois são necessários quando o token de segurança da conta está ativado:

| Onde | Nome na doc | O que é | Onde pegar |
|------|-------------|---------|------------|
| **URL** | ID e Token da instância | Identificam a **instância** (sua conexão WhatsApp). Formam a URL: `.../instances/ID/token/TOKEN/send-text` | Painel Z-API → sua instância → Editar (ID da instância + Token da instância) |
| **Header** | Client-Token (Account security token) | Token de **segurança da conta**. Não é o token da instância. | Painel Z-API → **Segurança** → Token de segurança da conta → Configurar / Gerar |

**Importante:** o valor que vai na URL (token da instância) **não** é o mesmo que vai no header `Client-Token`. Se você colocar o token da instância no Client-Token, a API responde 403 "Client-Token ... not allowed".

---

## 4. Variáveis de ambiente (backend)

| Variável | Uso (onde entra) |
|----------|-------------------|
| `ZAPI_BASE_URL` | URL completa da instância **sem** `/send-text`. Ex.: `https://api.z-api.io/instances/ID_INSTANCIA/token/TOKEN_DA_INSTANCIA` → usa **ID + token da instância**. |
| `ZAPI_INSTANCE_ID` + `ZAPI_INSTANCE_TOKEN` | Alternativa: o backend monta a URL com esses dois (id e token **da instância**). |
| `ZAPI_CLIENT_TOKEN` | Header `Client-Token`. Valor = **Token de segurança da conta** (Segurança no painel), **não** o token da instância. |

---

## 5. Referências

- [Send plain text](https://developer.z-api.io/en/message/send-message-text)
- [Webhook on message received](https://developer.z-api.io/en/webhooks/on-message-received)
- [Account security token (Client-Token)](https://developer.z-api.io/en/security/client-token)
