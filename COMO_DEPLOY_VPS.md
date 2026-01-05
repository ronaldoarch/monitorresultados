# 🚀 Como Fazer Deploy na VPS

## Vantagens da VPS vs Cloudflare Pages

✅ **Aplicação completa** - Não é só estático  
✅ **Monitor automático** - Roda 24/7 em background  
✅ **Sem Git** - Atualizações diretas, sem commit/push  
✅ **API completa** - Endpoints para controle  
✅ **Mais controle** - Você gerencia tudo  
✅ **Custo baixo** - VPS básica custa ~$5/mês  

## Passo a Passo

### 1. Escolher VPS

**Recomendações:**
- **DigitalOcean**: $5/mês (1GB RAM)
- **Linode**: $5/mês
- **Vultr**: $5/mês
- **Hetzner**: €4/mês (mais barato na Europa)

### 2. Conectar na VPS

```bash
ssh root@SEU_IP_VPS
```

### 3. Preparar Sistema

```bash
# Atualizar sistema
apt update && apt upgrade -y  # Ubuntu/Debian
# ou
yum update -y  # CentOS/RHEL

# Instalar dependências
apt install -y python3 python3-pip python3-venv git nginx  # Ubuntu/Debian
# ou
yum install -y python3 python3-pip git nginx  # CentOS/RHEL

# Instalar ChromeDriver (para Selenium)
# Ubuntu/Debian:
apt install -y chromium-chromedriver

# Ou baixar manualmente:
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# ... (ver instruções completas no monitor_selenium.py)
```

### 4. Fazer Upload dos Arquivos

**Opção A: Via Git (Recomendado)**
```bash
# Na VPS
cd /opt
git clone SEU_REPO monitor-resultados
cd monitor-resultados
```

**Opção B: Via SCP (do seu Mac)**
```bash
# Do seu Mac
scp -r monitor_selenium.py app_vps.py dashboard_mini.html resultados.json requirements_vps.txt root@SEU_IP:/opt/monitor-resultados/
```

**Opção C: Via Script**
```bash
# Executar deploy_vps.sh na VPS
./deploy_vps.sh
```

### 5. Configurar Aplicação

```bash
cd /opt/monitor-resultados

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements_vps.txt
```

### 6. Testar Localmente na VPS

```bash
# Rodar servidor
python3 app_vps.py --monitor --intervalo 60

# Em outro terminal, testar:
curl http://localhost:5000/api/status
```

### 7. Configurar como Serviço (Systemd)

```bash
# Criar serviço
sudo nano /etc/systemd/system/monitor-resultados.service
```

Cole:
```ini
[Unit]
Description=Monitor de Resultados - Bicho Certo
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/opt/monitor-resultados
Environment="PATH=/opt/monitor-resultados/venv/bin"
ExecStart=/opt/monitor-resultados/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app_vps:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable monitor-resultados
sudo systemctl start monitor-resultados

# Ver status
sudo systemctl status monitor-resultados
```

### 8. Configurar Nginx (Opcional mas Recomendado)

```bash
sudo nano /etc/nginx/sites-available/monitor-resultados
```

Cole:
```nginx
server {
    listen 80;
    server_name seu-dominio.com;  # ou IP da VPS

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/monitor-resultados /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Configurar SSL (HTTPS) - Opcional

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com
```

## Comandos Úteis

```bash
# Ver logs
sudo journalctl -u monitor-resultados -f

# Reiniciar serviço
sudo systemctl restart monitor-resultados

# Parar serviço
sudo systemctl stop monitor-resultados

# Ver status
sudo systemctl status monitor-resultados

# Ver processos
ps aux | grep gunicorn
```

## API Endpoints

- `GET /` - Dashboard
- `GET /api/resultados` - Retorna todos os resultados
- `GET /api/status` - Status do sistema
- `POST /api/verificar-agora` - Força verificação imediata
- `POST /api/monitor/start` - Inicia monitor
- `POST /api/monitor/stop` - Para monitor
- `GET /api/monitor/status` - Status do monitor

## Monitoramento

### Ver logs em tempo real:
```bash
sudo journalctl -u monitor-resultados -f
```

### Verificar se está rodando:
```bash
curl http://localhost:5000/api/status
```

### Verificar monitor:
```bash
curl http://localhost:5000/api/monitor/status
```

## Troubleshooting

### Porta 5000 não acessível?
```bash
# Verificar firewall
sudo ufw allow 5000
# ou
sudo firewall-cmd --add-port=5000/tcp --permanent
```

### Serviço não inicia?
```bash
# Ver logs
sudo journalctl -u monitor-resultados -n 50

# Verificar permissões
ls -la /opt/monitor-resultados
```

### ChromeDriver não funciona?
```bash
# Verificar versão
chromedriver --version

# Verificar se Chrome está instalado
google-chrome --version
```

## Custo Estimado

- **VPS básica**: $5/mês
- **Domínio (opcional)**: $10/ano
- **Total**: ~$5-6/mês

Muito mais barato e completo que Cloudflare Pages + Workers!

