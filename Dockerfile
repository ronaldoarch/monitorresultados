FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema (Chrome e ChromeDriver para Selenium)
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar ChromeDriver
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH="${CHROMEDRIVER_PATH}:${PATH}"

# Copiar arquivos de dependências
COPY requirements_vps.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements_vps.txt

# Copiar código da aplicação
COPY app_vps.py .
COPY monitor_selenium.py .
COPY dashboard_mini.html .
COPY gunicorn_config.py .

# Criar diretório para resultados
RUN mkdir -p /app/data

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Comando de start com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--config", "gunicorn_config.py", "app_vps:app"]

