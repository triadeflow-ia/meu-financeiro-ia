"""
Teste rápido: conexão com Supabase e tabela clientes.
Funciona com chaves novas (sb_secret_...) e legadas (JWT).
Execute na pasta backend: python testar_conexao.py
"""
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)
from dotenv import load_dotenv
load_dotenv()

def testar():
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_KEY", "")
    if not url:
        print("ERRO: SUPABASE_URL não definido no .env")
        return False
    if not key:
        print("ERRO: SUPABASE_KEY não definido no .env")
        return False
    print("SUPABASE_URL:", url)
    print("SUPABASE_KEY: definida (ok)")

    # Chaves novas (sb_secret_ / sb_publishable_) precisam do header apikey
    usa_apikey_header = key.startswith("sb_")
    rest_url = f"{url}/rest/v1/clientes?select=*&limit=1"

    try:
        import httpx
        headers = {
            "apikey": key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        # Para chaves sb_*, não usar Bearer (API rejeita). Só apikey.
        if not usa_apikey_header:
            headers["Authorization"] = f"Bearer {key}"
        r = httpx.get(rest_url, headers=headers, timeout=10)
        if r.status_code == 401:
            print("ERRO: Invalid API key (chave rejeitada).")
            print("Dica: No painel Supabase, em API Keys, veja a aba 'Legacy API Keys' e use a chave service_role (JWT).")
            return False
        r.raise_for_status()
        data = r.json()
        print("Conexão: OK")
        print("Tabela 'clientes': OK (acesso permitido)")
        print("Registros (amostra):", len(data) if isinstance(data, list) else 0)
        return True
    except httpx.HTTPStatusError as e:
        print("ERRO HTTP:", e.response.status_code, e.response.text[:200])
        return False
    except Exception as e:
        print("ERRO:", e)
        return False

if __name__ == "__main__":
    ok = testar()
    exit(0 if ok else 1)
