"""
Teste do webhook WhatsApp + envio Z-API.
Simula um payload Z-API (on-message-received) e verifica a resposta.
Troque TELEFONE_TESTE pelo número que deve receber a mensagem (DDI+DDD+número, só dígitos).
"""
import json
import os
import sys

# Carrega .env
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from dotenv import load_dotenv
load_dotenv()

try:
    import urllib.request
    import urllib.error
except ImportError:
    urllib = None

# Use um número real para receber o WhatsApp (ex.: 5521999999999) ou deixe 5511999999999 para só testar a API
TELEFONE_TESTE = os.getenv("TEST_PHONE", "5511999999999").replace(" ", "").replace("-", "")

# Payload no formato Z-API "on message received" (texto)
payload_zapi = {
    "fromMe": False,
    "phone": TELEFONE_TESTE,
    "participantPhone": None,
    "text": {"message": "Oi, quero só um teste de resposta."},
    "type": "ReceivedCallback",
}

def main():
    port = os.getenv("PORT", "8000")
    url = f"http://127.0.0.1:{port}/api/webhook/whatsapp"
    print(f"Enviando POST para {url}")
    print(f"Telefone no payload: {TELEFONE_TESTE}")
    print("Payload (Z-API):", payload_zapi)
    print("-" * 50)
    try:
        body = json.dumps(payload_zapi).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            status = r.status
            raw = r.read().decode("utf-8")
            data = json.loads(raw) if raw.strip() else {}
        print(f"Status: {status}")
        print(f"Resposta: {data}")
        if data.get("ok") and data.get("resposta"):
            print("\n[OK] Webhook processou e gerou resposta.")
            if os.getenv("ZAPI_BASE_URL"):
                print("ZAPI_BASE_URL está configurado: a resposta foi enviada para o WhatsApp nesse número.")
            else:
                print("ZAPI_BASE_URL não configurado: resposta não foi enviada ao WhatsApp.")
        elif status != 200:
            print("\n[FALHA] Servidor retornou erro.")
        else:
            print("\n[OK] Servidor respondeu (pode não ter mensagem para processar).")
    except urllib.error.URLError as e:
        if "Connection refused" in str(e.reason) or "Errno 10061" in str(e):
            print("[ERRO] Backend não está rodando. Inicie com: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        else:
            print(f"[ERRO] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
