# Dockerfile para a aplicação Aluga_Ai
FROM python:3.13-slim

# Define o diretório de trabalho
WORKDIR /app

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    sqlite3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/media

# Cria diretórios necessários para media e arquivos estáticos coletados
RUN mkdir -p /app/media 

# Expõe a porta da aplicação
EXPOSE 8000

# Script de entrada para executar migrações e iniciar servidor
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8000"]
