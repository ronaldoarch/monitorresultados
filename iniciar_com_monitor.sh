#!/bin/bash
# Script para iniciar aplicação com monitor automático

echo "🚀 Iniciando aplicação com monitor automático..."

# Iniciar monitor em background
python3 monitor_selenium.py &
MONITOR_PID=$!

# Aguardar um pouco para monitor iniciar
sleep 5

# Iniciar servidor Flask/Gunicorn
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 --config gunicorn_config.py app_vps:app

# Quando servidor parar, parar monitor também
kill $MONITOR_PID 2>/dev/null

