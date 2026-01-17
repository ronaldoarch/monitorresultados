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
COPY monitor_deunoposte.py .
COPY integracao_endpoint_php.py .
COPY dashboard_mini.html .
COPY dashboard_bot.html .
COPY gunicorn_config.py .
COPY comparar_horarios.py .
COPY reprocessar_separar_loterias.py .
COPY bot_liquidacao.py .
COPY matching_resultados.py .
COPY integracao_site.py .
COPY models.py .

# Criar diretório para resultados
RUN mkdir -p /app/data

# Expor porta
EXPOSE 8000

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Copiar script de inicialização
COPY iniciar_com_monitor.sh .
RUN chmod +x iniciar_com_monitor.sh

# Comando de start: inicia monitor em background + servidor web
CMD ["./iniciar_com_monitor.sh"]

