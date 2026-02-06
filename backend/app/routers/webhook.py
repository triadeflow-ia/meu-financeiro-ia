"""
Webhook WhatsApp (Z-API).
Processa áudio ou texto com OpenAI: cadastrar cliente ou dar baixa manual.
Envia a resposta de volta ao WhatsApp via Z-API send-text quando ZAPI_BASE_URL está configurado.
Aceita também payload no formato Evolution API para compatibilidade.
"""
import os
import re
import base64
import tempfile
import logging
from datetime import date
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from openai import OpenAI
import httpx

from app.db import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)
client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "")

# Payload genérico (Z-API principal; formato Evolution aceito opcionalmente)
class WebhookWhatsAppBody(BaseModel):
    pass  # aceita qualquer JSON

SYSTEM_PROMPT = """Você é um assistente de gestão financeira. Extraia dados do texto do usuário e responda APENAS com um JSON válido (sem markdown, sem explicação).

Ações possíveis:

1) CADASTRAR CLIENTE: quando o usuário pedir para cadastrar/registrar um cliente, extraia:
   - nome (obrigatório)
   - documento_cpf_cnpj: CPF ou CNPJ se mencionado (apenas números ou string)
   - valor_mensalidade: número (ex: 500, 150.00)
   - dia_vencimento: número de 1 a 28 (dia do mês)
   Exemplo de texto: "Cadastrar cliente João Silva, CPF 123, mensalidade 500, vencimento dia 10"
   Resposta: {"cadastrar_cliente": {"nome": "João Silva", "documento_cpf_cnpj": "123", "valor_mensalidade": 500, "dia_vencimento": 10}}

2) BAIXA MANUAL: quando o usuário quiser dar baixa em pagamento: nome ou documento do cliente, valor opcional, data opcional.
   Resposta: {"baixa_manual": {"nome_ou_documento": "...", "valor": número ou null, "data_pagamento": "YYYY-MM-DD" ou null}}

3) Outros: responda com {"resposta": "sua mensagem em texto"}.

Regras: Responda somente o JSON. dia_vencimento entre 1 e 28. valor_mensalidade sempre número. Se algo não for dito, use null ou valor padrão (dia_vencimento 10, valor_mensalidade 0)."""


def _extrair_texto_payload_evolution(body: dict) -> str:
    """Extrai texto ou áudio do payload no formato Evolution API (compatibilidade)."""
    try:
        data = body.get("data", body)
        event = data.get("event", "")
        if event == "messages.upsert":
            msg = (data.get("messages") or [{}])[0]
            if not msg:
                return ""
            if msg.get("message", {}).get("audioMessage"):
                return "__AUDIO__"
            return (msg.get("message", {}).get("conversation") or msg.get("message", {}).get("extendedTextMessage", {}).get("text") or "").strip()
        return ""
    except Exception:
        return ""


def _extrair_texto_zapi(body: dict) -> str:
    """
    Extrai texto ou áudio do payload Z-API (webhook on-message-received).
    Doc: atributo text.message na raiz para mensagem de texto.
    """
    try:
        if body.get("audio"):
            return "__AUDIO__"
        # Doc Z-API: "text.message" (string) = mensagem de texto
        text_node = body.get("text")
        if isinstance(text_node, dict) and text_node.get("message"):
            return (text_node["message"] or "").strip()
        # Fallbacks
        msg = body.get("message", body.get("payload", {}))
        if isinstance(msg, dict) and msg.get("audio"):
            return "__AUDIO__"
        if isinstance(msg, dict):
            return (msg.get("text") or msg.get("body") or "").strip()
        return ""
    except Exception:
        return ""


def _extrair_phone_resposta(body: dict) -> str | None:
    """
    Extrai o número/chat para enviar a resposta.
    Doc Z-API (on-message-received): phone = "Phone number or group that sent the message" (raiz do payload).
    Em grupo: phone = "5544999999999-group"; em direto: phone = "5544999999999".
    Ignora mensagens fromMe.
    """
    try:
        if body.get("fromMe") is True:
            return None
        # Doc Z-API: campo "phone" na raiz; fallbacks para outros formatos
        phone = (
            body.get("phone")  # oficial: "Phone number or group that sent the message"
            or body.get("participantPhone")  # em grupo: quem enviou; para responder ao grupo use phone
            or body.get("senderPhone")
            or body.get("from")
            or (body.get("data") or {}).get("phone")
            or (body.get("payload") or {}).get("phone")
        )
        if not phone:
            return None
        phone_str = str(phone).strip()
        if "@" in phone_str:
            phone_str = phone_str.split("@")[0]
        # Grupo: doc envia "5544999999999-group"; send-text aceita group ID
        if "-group" in phone_str or body.get("isGroup"):
            return phone_str if len(phone_str) >= 10 else None
        # Direto: doc send-text = "only send numbers without formatting or a mask"
        digits = re.sub(r"\D", "", phone_str)
        return digits if len(digits) >= 10 else None
    except Exception:
        return None


def _get_zapi_base_url() -> str:
    """Base da Z-API (sem /send-text). Usa ZAPI_BASE_URL ou monta com ZAPI_INSTANCE_ID + ZAPI_INSTANCE_TOKEN."""
    base = (os.getenv("ZAPI_BASE_URL") or "").strip().rstrip("/")
    if base:
        return base
    instance_id = (os.getenv("ZAPI_INSTANCE_ID") or "").strip()
    instance_token = (os.getenv("ZAPI_INSTANCE_TOKEN") or "").strip()
    if instance_id and instance_token:
        return f"https://api.z-api.io/instances/{instance_id}/token/{instance_token}"
    return ""


def _enviar_zapi_text(phone: str, message: str) -> bool:
    """
    Envia texto via Z-API send-text (doc: developer.z-api.io/en/message/send-message-text).
    POST {base}/send-text | Header: Client-Token (obrigatório se ativado) | Body: {"phone": "...", "message": "..."}.
    """
    base = _get_zapi_base_url()
    if not base or not phone or not message:
        if not base:
            logger.warning("Z-API: base URL vazia. Defina ZAPI_BASE_URL ou ZAPI_INSTANCE_ID + ZAPI_INSTANCE_TOKEN no Railway.")
        return False
    url = f"{base}/send-text"
    headers = {"Content-Type": "application/json"}
    client_token = (os.getenv("ZAPI_CLIENT_TOKEN") or "").strip()
    if client_token:
        headers["Client-Token"] = client_token
    else:
        logger.warning("Z-API: ZAPI_CLIENT_TOKEN não definido. Doc exige header Client-Token (Account security token). Defina no Railway.")
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.post(url, json={"phone": phone, "message": message}, headers=headers)
            if r.status_code != 200:
                logger.warning("Z-API send-text falhou: status=%s body=%s", r.status_code, r.text[:200])
            return r.status_code == 200
    except Exception as e:
        logger.warning("Z-API send-text exceção: %s", e)
        return False


def _transcrever_audio(b64_ogg: str) -> str:
    if not client_openai.api_key:
        return ""
    try:
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(base64.b64decode(b64_ogg))
            path = f.name
        with open(path, "rb") as f:
            transcript = client_openai.audio.transcriptions.create(model="whisper-1", file=f)
        os.unlink(path)
        return (transcript.text or "").strip()
    except Exception:
        return ""


def _openai_interpretar(texto: str) -> dict:
    if not texto or not client_openai.api_key:
        return {"resposta": "Configure OPENAI_API_KEY no .env para processar mensagens."}
    try:
        r = client_openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texto},
            ],
            temperature=0.2,
        )
        content = (r.choices[0].message.content or "").strip()
        # Remove blocos de código markdown se vierem
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        if content.startswith("{"):
            import json
            return json.loads(content)
        return {"resposta": content}
    except Exception as e:
        return {"resposta": f"Erro ao processar: {e}"}


def _cadastrar_cliente(payload: dict) -> str:
    """Valida os dados e insere no Supabase. Retorna mensagem de sucesso ou erro."""
    nome = (payload.get("nome") or "").strip()
    if not nome:
        return "Nome obrigatório."
    if len(nome) > 255:
        return "Nome muito longo."
    try:
        valor = float(payload.get("valor_mensalidade", 0))
    except (TypeError, ValueError):
        valor = 0.0
    if valor < 0:
        return "Valor da mensalidade não pode ser negativo."
    try:
        dia = int(payload.get("dia_vencimento", 10))
    except (TypeError, ValueError):
        dia = 10
    if dia < 1 or dia > 28:
        return "Dia de vencimento deve ser entre 1 e 28."
    doc = (payload.get("documento_cpf_cnpj") or "").strip() or None
    if doc is not None and len(doc) > 20:
        return "CPF/CNPJ muito longo."
    row = {
        "nome": nome,
        "documento_cpf_cnpj": doc,
        "valor_mensalidade": round(float(valor), 2),
        "dia_vencimento": int(dia),
        "status_ativo": True,
    }
    supabase = get_supabase()
    try:
        supabase.table("clientes").insert(row).execute()
    except httpx.HTTPStatusError as e:
        try:
            body = e.response.json()
            msg = body.get("message") or body.get("details") or e.response.text or str(e)
        except Exception:
            msg = e.response.text or str(e)
        return f"Erro ao cadastrar no banco: {msg}"
    return (
        f"✅ _Cadastro confirmado!_\n\n"
        f"Cliente *{nome}* foi registrado com sucesso.\n"
        f"• Mensalidade: R$ {valor:.2f}\n"
        f"• Vencimento: dia {dia}\n\n"
        f"Qualquer dúvida, é só chamar."
    )


def _baixa_manual(payload: dict) -> str:
    supabase = get_supabase()
    nome_ou_doc = (payload.get("nome_ou_documento") or "").strip()
    if not nome_ou_doc:
        return "Informe o nome ou documento do cliente."
    valor = payload.get("valor")
    data_pag = payload.get("data_pagamento") or str(date.today())
    r = supabase.table("clientes").select("id, nome, valor_mensalidade, documento_cpf_cnpj").execute()
    clientes = r.data or []
    candidatos = [c for c in clientes if nome_ou_doc.lower() in (c.get("nome") or "").lower() or c.get("documento_cpf_cnpj") == nome_ou_doc]
    if not candidatos:
        return f"Cliente não encontrado: {nome_ou_doc}"
    if len(candidatos) > 1:
        return f"Vários clientes encontrados. Especifique: {[c.get('nome') for c in candidatos]}"
    c = candidatos[0]
    valor_final = float(valor) if valor is not None else float(c.get("valor_mensalidade", 0))
    if valor_final < 0:
        return "Valor do pagamento não pode ser negativo."
    supabase.table("transacoes").insert({
        "cliente_id": c["id"],
        "valor": valor_final,
        "data_pagamento": data_pag,
        "status_nota_fiscal": "pendente",
        "hash_bancario": None,
    }).execute()
    return (
        f"✅ _Baixa confirmada!_\n\n"
        f"Pagamento de *{c.get('nome')}* registrado: R$ {valor_final:.2f} em {data_pag}."
    )


def _validar_token_webhook(request: Request) -> None:
    """Exige 401 se ZAPI_SECURITY_TOKEN estiver definido e o header não bater."""
    expected = (os.getenv("ZAPI_SECURITY_TOKEN") or "").strip()
    if not expected:
        return
    # Z-API pode enviar Client-Token ou você pode configurar um header customizado (ex.: X-ZAPI-Security-Token)
    received = (
        (request.headers.get("X-ZAPI-Security-Token") or request.headers.get("Client-Token") or "").strip()
    )
    if received != expected:
        raise HTTPException(status_code=401, detail="Token de segurança do webhook inválido ou ausente")


@router.post("/whatsapp")
async def webhook_whatsapp(request: Request):
    """
    Recebe mensagens do WhatsApp (Z-API). Processa áudio (Whisper) ou texto com OpenAI:
    cadastrar cliente ou baixa manual. Resposta enviada de volta via Z-API send-text.
    Se ZAPI_SECURITY_TOKEN estiver no .env, exige header X-ZAPI-Security-Token ou Client-Token com o mesmo valor.
    """
    _validar_token_webhook(request)
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Body JSON inválido")

    texto = (
        _extrair_texto_zapi(body)
        or _extrair_texto_payload_evolution(body)
        or (body.get("message") or body.get("text") or "").strip()
    )
    if not texto:
        return {"ok": True, "message": "Nenhuma mensagem para processar"}

    if texto == "__AUDIO__":
        # Z-API ou formato compatível: áudio em body.message.audio ou data.messages[0].message.audioMessage
        try:
            data = body.get("data", body)
            msg = (data.get("messages") or [{}])[0]
            audio = (msg.get("message") or {}).get("audioMessage") or (body.get("message") or {}).get("audio")
            if audio:
                b64 = audio.get("audio") or audio.get("data") or body.get("audio")
                if b64:
                    texto = _transcrever_audio(b64)
        except Exception:
            pass
        if not texto:
            return {"ok": True, "message": "Áudio não transcrito"}

    resultado = _openai_interpretar(texto)
    resposta = resultado.get("resposta", "")

    if "cadastrar_cliente" in resultado:
        try:
            resposta = _cadastrar_cliente(resultado["cadastrar_cliente"])
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                msg = body.get("message") or body.get("details") or e.response.text
            except Exception:
                msg = e.response.text or str(e)
            resposta = f"Erro ao cadastrar cliente: {msg}"
    elif "baixa_manual" in resultado:
        try:
            resposta = _baixa_manual(resultado["baixa_manual"])
        except httpx.HTTPStatusError as e:
            try:
                body = e.response.json()
                msg = body.get("message") or body.get("details") or e.response.text
            except Exception:
                msg = e.response.text or str(e)
            resposta = f"Erro ao dar baixa: {msg}"

    # Envio da resposta de volta ao WhatsApp via Z-API send-text
    phone = _extrair_phone_resposta(body)
    if not phone and resposta:
        # Log para debug: Z-API envia "phone" na raiz (ex.: "5544999999999"); em grupo pode vir "phone": "55...-group"
        logger.warning(
            "Webhook: número não encontrado no payload. Campos do body: phone=%s participantPhone=%s from=%s senderPhone=%s isGroup=%s type=%s keys=%s",
            body.get("phone"),
            body.get("participantPhone"),
            body.get("from"),
            body.get("senderPhone"),
            body.get("isGroup"),
            body.get("type"),
            list(body.keys()),
        )
    if phone and resposta:
        logger.info("Webhook: enviando resposta ao WhatsApp para phone=%s (resposta com %d chars)", phone[:10] + "..." if len(phone) > 10 else phone, len(resposta))
        ok = _enviar_zapi_text(phone, resposta)
        if not ok:
            logger.warning(
                "Webhook: falha ao enviar resposta ao WhatsApp (phone=%s). Confira no Railway: ZAPI_BASE_URL ou ZAPI_INSTANCE_ID+ZAPI_INSTANCE_TOKEN e ZAPI_CLIENT_TOKEN (obrigatório na Z-API).",
                phone[:8] + "..." if len(phone) > 8 else phone,
            )

    return {"ok": True, "resposta": resposta}
