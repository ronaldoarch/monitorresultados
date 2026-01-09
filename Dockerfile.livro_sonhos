FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn flask-cors

# Copiar código da aplicação
COPY app_livro_sonhos.py .
COPY livro_sonhos.py .

# Expor porta
EXPOSE 8082

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Comando de start
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "2", "--timeout", "120", "app_livro_sonhos:app"]
