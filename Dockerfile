# Imagem base alternativa (caso python:3.11-slim falhe)
FROM ubuntu:22.04

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar Python e dependências do sistema
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3-pip \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    git \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criar link simbólico para python
RUN ln -s /usr/bin/python3.11 /usr/bin/python

# Copiar e instalar as dependências do projeto
COPY requirements.txt requirements-prod.txt ./
RUN pip3 install --upgrade pip && pip3 install -r requirements-prod.txt

# Copiar o restante do código
COPY . .

# Copiar e dar permissão aos scripts
COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/start.sh /start.sh
RUN chmod +x /entrypoint.sh /start.sh

# Criar diretórios necessários
RUN mkdir -p /app/logs /app/media /app/staticfiles

# Expor porta
EXPOSE 8000
