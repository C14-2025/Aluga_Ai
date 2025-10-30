# Dockerfile para Django + Python 3.9
FROM python:3.9-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos de requirements
COPY requirements.txt ./

# Instala dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copia todo o código do projeto
COPY . .

# Expõe a porta padrão do Django
EXPOSE 8000

# Comando padrão para rodar o servidor (pode ser alterado no Jenkins)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
