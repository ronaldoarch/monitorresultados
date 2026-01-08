# 🎰 Monitores Separados - Bicho Certo e Deu no Poste

## 📋 Visão Geral

Agora você tem **dois monitores completamente separados**:

1. **Monitor Bicho Certo** (`app_vps.py`) - Porta 8000
2. **Monitor Deu no Poste** (`app_deunoposte.py`) - Porta 8001

Cada um funciona de forma independente!

---

## 🟢 Monitor Bicho Certo

### Arquivo: `app_vps.py`
### Porta padrão: `8000`
### Fonte: `bichocerto.com`

### Como Iniciar:

```bash
# Com monitor automático
python3 app_vps.py --monitor --intervalo 60 --port 8000

# Sem monitor (apenas API)
python3 app_vps.py --port 8000
```

### Endpoints:

- `GET /api/resultados` - Resultados do Bicho Certo
- `GET /api/status` - Status do monitor
- `POST /api/verificar-agora` - Forçar verificação
- `GET /resultados.json` - Arquivo JSON

### URL de Acesso:

```
https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/
```

---

## 🔵 Monitor Deu no Poste

### Arquivo: `app_deunoposte.py`
### Porta padrão: `8001`
### Fonte: `deunoposte.com.br`

### Como Iniciar:

```bash
# Com monitor automático (verifica a cada 5 minutos)
python3 app_deunoposte.py --monitor --intervalo 300 --port 8001

# Sem monitor (apenas API)
python3 app_deunoposte.py --port 8001
```

### Endpoints:

- `GET /api/resultados` - Resultados do Deu no Poste
- `GET /api/status` - Status do monitor
- `POST /api/verificar-agora` - Forçar verificação
- `GET /resultados_deunoposte.json` - Arquivo JSON
- `POST /api/monitor/start` - Iniciar monitor
- `POST /api/monitor/stop` - Parar monitor
- `GET /api/monitor/status` - Status do monitor

### URL de Acesso:

```
http://seu-servidor:8001/
```

---

## 🚀 Deploy Separado

### Opção 1: Dois Containers Docker (Recomendado)

#### Container 1 - Bicho Certo
```dockerfile
# Dockerfile.bichocerto
FROM python:3.11-slim
WORKDIR /app
COPY requirements_vps.txt .
RUN pip install -r requirements_vps.txt
COPY app_vps.py monitor_selenium.py dashboard_mini.html gunicorn_config.py .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app_vps:app"]
```

#### Container 2 - Deu no Poste
```dockerfile
# Dockerfile.deunoposte
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app_deunoposte.py monitor_deunoposte.py .
EXPOSE 8001
CMD ["gunicorn", "--bind", "0.0.0.0:8001", "--workers", "2", "app_deunoposte:app"]
```

### Opção 2: Mesmo Servidor, Portas Diferentes

```bash
# Terminal 1 - Bicho Certo
python3 app_vps.py --monitor --intervalo 60 --port 8000

# Terminal 2 - Deu no Poste
python3 app_deunoposte.py --monitor --intervalo 300 --port 8001
```

### Opção 3: Systemd Services

#### `/etc/systemd/system/monitor-bichocerto.service`
```ini
[Unit]
Description=Monitor Bicho Certo
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/monitor
ExecStart=/usr/bin/python3 app_vps.py --monitor --intervalo 60 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### `/etc/systemd/system/monitor-deunoposte.service`
```ini
[Unit]
Description=Monitor Deu no Poste
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/monitor
ExecStart=/usr/bin/python3 app_deunoposte.py --monitor --intervalo 300 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl enable monitor-bichocerto
sudo systemctl enable monitor-deunoposte
sudo systemctl start monitor-bichocerto
sudo systemctl start monitor-deunoposte
```

---

## 📊 Comparação

| Característica | Bicho Certo | Deu no Poste |
|---------------|-------------|--------------|
| **Arquivo** | `app_vps.py` | `app_deunoposte.py` |
| **Porta** | 8000 | 8001 |
| **Fonte** | bichocerto.com | deunoposte.com.br |
| **Tecnologia** | Selenium | Requests + BeautifulSoup |
| **Intervalo padrão** | 60s | 300s (5 min) |
| **Arquivo JSON** | `resultados.json` | `resultados_deunoposte.json` |
| **Loterias** | 9 URLs | 14 loterias, 100+ URLs |

---

## 🔧 Configuração no Coolify

### Projeto 1: Bicho Certo
- **Nome**: `monitor-bichocerto`
- **Port**: `8000`
- **Build**: Dockerfile existente
- **Start**: `gunicorn --bind 0.0.0.0:8000 app_vps:app`

### Projeto 2: Deu no Poste
- **Nome**: `monitor-deunoposte`
- **Port**: `8001`
- **Build**: Criar novo Dockerfile
- **Start**: `gunicorn --bind 0.0.0.0:8001 app_deunoposte:app`

---

## 📡 Exemplos de Uso

### Acessar Resultados do Bicho Certo:
```bash
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados
```

### Acessar Resultados do Deu no Poste:
```bash
curl http://seu-servidor:8001/api/resultados
```

### Combinar Resultados (se necessário):
```javascript
// No frontend
const [bichocerto, deunoposte] = await Promise.all([
  fetch('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados'),
  fetch('http://seu-servidor:8001/api/resultados')
]);

const todos = [
  ...(await bichocerto.json()).resultados,
  ...(await deunoposte.json()).resultados
];
```

---

## ✅ Vantagens da Separação

1. **Independência**: Cada monitor pode ser reiniciado sem afetar o outro
2. **Escalabilidade**: Pode colocar em servidores diferentes
3. **Manutenção**: Mais fácil de debugar e manter
4. **Recursos**: Cada um usa apenas o necessário
5. **Configuração**: Intervalos e configurações diferentes

---

## 🎯 Próximos Passos

1. **Deploy do Deu no Poste**: Configure o segundo container/serviço
2. **Configurar Proxy Reverso**: Se quiser usar o mesmo domínio com paths diferentes
3. **Monitoramento**: Configure alertas para cada monitor separadamente
