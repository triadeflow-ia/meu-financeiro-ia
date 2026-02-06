"""
Configurações via variáveis de ambiente.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # Santander Sandbox - caminho dos certificados (relativo à pasta backend)
    CERT_DIR: Path = Path(__file__).resolve().parent.parent / "certs"
    CERT_KEY_FILE: str = "privada.key"
    CERT_FILE: str = "santander.crt"  # ou santander.pem - nome do certificado do Santander
    SANTANDER_EXTRATO_URL: str = "https://api.santander.com.br/sandbox/extrato/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
