# Imagem base
FROM python:3.12-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    git \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar as dependências do projeto
COPY requirements.txt requirements-prod.txt ./
RUN pip install --upgrade pip && pip install -r requirements-prod.txt

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

# Entrypoint e comando padrão
ENTRYPOINT ["/entrypoint.sh"]
CMD ["/start.sh"]
