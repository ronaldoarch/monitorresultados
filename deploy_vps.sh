#!/bin/bash
# Script para fazer deploy na VPS

echo "🚀 Preparando deploy para VPS..."

# Verificar se está na VPS
if [ -z "$SSH_CONNECTION" ] && [ "$1" != "--local" ]; then
    echo "⚠️  Este script deve ser executado na VPS"
    echo "💡 Para testar localmente: ./deploy_vps.sh --local"
    exit 1
fi

# Criar diretório da aplicação
APP_DIR="/opt/monitor-resultados"
echo "📁 Criando diretório: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copiar arquivos
echo "📦 Copiando arquivos..."
cp -r monitor_selenium.py app_vps.py dashboard_mini.html resultados.json $APP_DIR/ 2>/dev/null || true
cp requirements_vps.txt $APP_DIR/requirements.txt

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Criar arquivo de configuração systemd
echo "⚙️  Criando serviço systemd..."
sudo tee /etc/systemd/system/monitor-resultados.service > /dev/null <<EOF
[Unit]
Description=Monitor de Resultados - Bicho Certo
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app_vps:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Criar serviço do monitor (opcional - pode rodar junto)
sudo tee /etc/systemd/system/monitor-resultados-monitor.service > /dev/null <<EOF
[Unit]
Description=Monitor de Resultados - Background Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python3 monitor_selenium.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
sudo systemctl daemon-reload

echo ""
echo "✅ Deploy concluído!"
echo ""
echo "📋 Comandos úteis:"
echo "  sudo systemctl start monitor-resultados      # Iniciar servidor"
echo "  sudo systemctl enable monitor-resultados     # Iniciar no boot"
echo "  sudo systemctl status monitor-resultados     # Ver status"
echo "  sudo systemctl restart monitor-resultados    # Reiniciar"
echo ""
echo "🌐 Acesse: http://SEU_IP_VPS:5000"

