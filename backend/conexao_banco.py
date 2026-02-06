"""
Conexão com a API de Extrato do Santander Sandbox usando certificados.
Use os certificados na pasta backend/certs/: privada.key e certificado Santander.
"""
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

# Diretório dos certificados (pasta certs na mesma pasta que este arquivo)
BASE_DIR = Path(__file__).resolve().parent
CERTS_DIR = BASE_DIR / "certs"

# Nomes dos arquivos (ajuste se o certificado do Santander tiver outro nome)
CERT_KEY_FILE = os.getenv("CERT_KEY_FILE", "privada.key")
CERT_FILE = os.getenv("CERT_FILE", "santander.crt")

PATH_KEY = CERTS_DIR / CERT_KEY_FILE
PATH_CERT = CERTS_DIR / CERT_FILE


def _caminhos_certificados():
    """Retorna tupla (caminho_cert, caminho_key) para uso com httpx."""
    if not PATH_KEY.exists():
        raise FileNotFoundError(
            f"Chave privada não encontrada: {PATH_KEY}. "
            "Coloque o arquivo privada.key na pasta backend/certs/"
        )
    if not PATH_CERT.exists():
        # Tenta .pem se .crt não existir
        alt = CERTS_DIR / "santander.pem"
        if alt.exists():
            return (str(alt), str(PATH_KEY))
        raise FileNotFoundError(
            f"Certificado Santander não encontrado: {PATH_CERT} (ou santander.pem). "
            "Coloque o certificado do Santander na pasta backend/certs/"
        )
    return (str(PATH_CERT), str(PATH_KEY))


def obter_cliente_santander():
    """
    Cria um cliente HTTP que usa os certificados para autenticação mTLS
    na API de Extrato do Santander Sandbox.
    """
    cert, key = _caminhos_certificados()
    return httpx.Client(
        cert=(cert, key),
        verify=True,
        timeout=30.0,
    )


def obter_cliente_santander_async():
    """Cliente assíncrono para uso nas rotas FastAPI."""
    cert, key = _caminhos_certificados()
    return httpx.AsyncClient(
        cert=(cert, key),
        verify=True,
        timeout=30.0,
    )


# Cliente Supabase (banco de dados) - será usado pelo app
def obter_supabase():
    """Retorna o client Supabase configurado via SUPABASE_URL e SUPABASE_KEY."""
    from supabase import create_client

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError(
            "Defina SUPABASE_URL e SUPABASE_KEY no arquivo .env"
        )
    return create_client(url, key)
