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

## 3. Variáveis de ambiente (backend)

| Variável | Uso |
|----------|-----|
| `ZAPI_BASE_URL` | URL base **sem** `/send-text`. Ex.: `https://api.z-api.io/instances/ID/token/TOKEN` |
| `ZAPI_INSTANCE_ID` + `ZAPI_INSTANCE_TOKEN` | Alternativa: o backend monta a base com esses dois. |
| `ZAPI_CLIENT_TOKEN` | Token de segurança (header `Client-Token`). Obrigatório se a opção estiver ativada na Z-API. |

---

## 4. Referências

- [Send plain text](https://developer.z-api.io/en/message/send-message-text)
- [Webhook on message received](https://developer.z-api.io/en/webhooks/on-message-received)
- [Account security token (Client-Token)](https://developer.z-api.io/en/security/client-token)
