# 🚀 Deploy na VPS Colify

## Repositório GitHub
✅ Código enviado para: https://github.com/ronaldoarch/monitorresultados.git

## Passo a Passo para Deploy na Colify

### 1. Conectar na VPS Colify

```bash
ssh usuario@seu-ip-colify
# ou via painel da Colify
```

### 2. Clonar Repositório

```bash
cd /opt  # ou outro diretório de sua preferência
git clone https://github.com/ronaldoarch/monitorresultados.git
cd monitorresultados
```

### 3. Instalar Dependências do Sistema

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx

# Instalar ChromeDriver (necessário para Selenium)
sudo apt install -y chromium-chromedriver chromium-browser
```

### 4. Configurar Ambiente Python

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install --upgrade pip
pip install -r requirements_vps.txt
```

### 5. Testar Aplicação

```bash
# Rodar servidor de teste
python3 app_vps.py --monitor --intervalo 60

# Em outro terminal, testar:
curl http://localhost:5000/api/status
```

### 6. Configurar como Serviço Systemd

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/monitor-resultados.service
```

Cole o seguinte conteúdo (ajuste o caminho se necessário):

```ini
[Unit]
Description=Monitor de Resultados - Bicho Certo
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/opt/monitorresultados
Environment="PATH=/opt/monitorresultados/venv/bin"
ExecStart=/opt/monitorresultados/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app_vps:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Importante:** Substitua `seu-usuario` pelo seu usuário na VPS e `/opt/monitorresultados` pelo caminho onde clonou o repositório.

### 7. Ativar e Iniciar Serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar para iniciar no boot
sudo systemctl enable monitor-resultados

# Iniciar serviço
sudo systemctl start monitor-resultados

# Verificar status
sudo systemctl status monitor-resultados
```

### 8. Configurar Nginx (Recomendado)

```bash
# Criar configuração
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

### 9. Configurar Firewall

```bash
# Permitir porta 5000 (ou 80 se usar Nginx)
sudo ufw allow 5000
# ou
sudo ufw allow 80
sudo ufw allow 443  # se usar HTTPS
```

## Comandos Úteis

```bash
# Ver logs em tempo real
sudo journalctl -u monitor-resultados -f

# Reiniciar serviço
sudo systemctl restart monitor-resultados

# Parar serviço
sudo systemctl stop monitor-resultados

# Ver status
sudo systemctl status monitor-resultados

# Atualizar código (após git pull)
cd /opt/monitorresultados
git pull
sudo systemctl restart monitor-resultados
```

## Verificar se Está Funcionando

```bash
# Testar API
curl http://localhost:5000/api/status

# Testar dashboard
curl http://localhost:5000/

# Ver processos
ps aux | grep gunicorn
```

## Troubleshooting

### Serviço não inicia?
```bash
# Ver logs detalhados
sudo journalctl -u monitor-resultados -n 50

# Verificar permissões
ls -la /opt/monitorresultados
```

### ChromeDriver não funciona?
```bash
# Verificar versão
chromedriver --version
chromium-browser --version

# Se não funcionar, baixar manualmente
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
# ... seguir instruções do monitor_selenium.py
```

### Porta não acessível?
```bash
# Verificar se está escutando
sudo netstat -tlnp | grep 5000

# Verificar firewall
sudo ufw status
```

## Acessar Dashboard

Após configurar, acesse:
- **Direto**: `http://SEU_IP_COLIFY:5000`
- **Com Nginx**: `http://SEU_IP_COLIFY` ou `http://seu-dominio.com`

## Próximos Passos

1. ✅ Código já está no GitHub
2. ⏳ Clonar na VPS Colify
3. ⏳ Instalar dependências
4. ⏳ Configurar serviço
5. ⏳ Acessar dashboard

Boa sorte com o deploy! 🚀

