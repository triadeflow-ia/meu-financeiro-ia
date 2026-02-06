# Backend - Python 3.11 + Uvicorn
FROM python:3.11-slim

WORKDIR /app

# Dependências do sistema (opcional, para certificados/SSL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código da aplicação
COPY app ./app
COPY conexao_banco.py .

# Variáveis de ambiente são injetadas em runtime (docker-compose env_file / environment)
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Railway (e outros clouds) injetam PORT em runtime
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
