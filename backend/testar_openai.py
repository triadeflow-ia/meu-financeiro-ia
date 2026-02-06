"""Teste rápido: conexão com OpenAI. Rode na pasta backend: python testar_openai.py"""
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
os.chdir(backend_dir)
env_file = backend_dir / ".env"
if not env_file.exists():
    print("ERRO: arquivo .env não encontrado em", backend_dir)
    exit(1)
from dotenv import load_dotenv
load_dotenv(env_file)
key = os.getenv("OPENAI_API_KEY", "").strip()
# Fallback: ler direto do arquivo (caso dotenv não carregue)
if not key:
    for line in open(env_file, encoding="utf-8"):
        raw = line.strip()
        if raw.startswith("OPENAI_API_KEY=") and not raw.startswith("OPENAI_API_KEY=#"):
            key = raw.split("=", 1)[1].strip().strip('"').strip("'")
            break
if not key:
    print("ERRO: OPENAI_API_KEY está vazia no .env")
    print("Dica: Cole a chave após o = na linha OPENAI_API_KEY= e salve o arquivo (Ctrl+S).")
    exit(1)

print("Chamando OpenAI (gpt-4o-mini)...")
try:
    from openai import OpenAI
    client = OpenAI(api_key=key)
    r = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Responda em uma palavra: OK"}],
        max_tokens=5,
    )
    msg = (r.choices[0].message.content or "").strip()
    print("Resposta da IA:", msg)
    print("Conexão OpenAI: OK")
except Exception as e:
    print("Erro:", e)
    exit(1)
