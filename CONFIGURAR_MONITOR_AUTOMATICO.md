# 🔄 Configurar Monitor Automático

Este guia explica como configurar o monitor para iniciar automaticamente quando a aplicação é iniciada.

## 🎯 Problema Resolvido

Anteriormente, o monitor não iniciava automaticamente quando a aplicação era executada com Gunicorn. Agora, o monitor inicia automaticamente quando:

1. ✅ A aplicação é iniciada (Gunicorn ou Flask direto)
2. ✅ O módulo é carregado (com variável de ambiente configurada)
3. ✅ Via hooks do Gunicorn

---

## ⚙️ Configuração

### Opção 1: Variável de Ambiente (Recomendado)

Configure as variáveis de ambiente antes de iniciar a aplicação:

```bash
# Habilitar início automático (padrão: true)
export MONITOR_AUTO_START=true

# Intervalo em segundos (padrão: 60)
export MONITOR_INTERVALO=60
```

### Opção 2: Docker

No seu `Dockerfile` ou `docker-compose.yml`:

```dockerfile
# Dockerfile
ENV MONITOR_AUTO_START=true
ENV MONITOR_INTERVALO=60
```

```yaml
# docker-compose.yml
services:
  monitor:
    environment:
      - MONITOR_AUTO_START=true
      - MONITOR_INTERVALO=60
```

### Opção 3: Systemd Service

No arquivo de serviço systemd:

```ini
[Service]
Environment="MONITOR_AUTO_START=true"
Environment="MONITOR_INTERVALO=60"
```

### Opção 4: Coolify/VPS

No painel do Coolify ou configuração do VPS, adicione as variáveis de ambiente:

```
MONITOR_AUTO_START=true
MONITOR_INTERVALO=60
```

---

## 🚀 Como Funciona

### Inicialização Automática

O monitor é iniciado automaticamente em 3 momentos:

1. **Quando o módulo é importado** (se `MONITOR_AUTO_START=true`):
   ```python
   # Executado automaticamente quando app_vps.py é importado
   if os.getenv('MONITOR_AUTO_START', 'true').lower() == 'true':
       inicializar_monitor_automatico()
   ```

2. **Via hook do Gunicorn `on_starting`**:
   ```python
   def on_starting(server):
       inicializar_monitor_automatico()
   ```

3. **Via hook do Gunicorn `when_ready`**:
   ```python
   def when_ready(server):
       if not monitor_iniciado:
           inicializar_monitor_automatico()
   ```

### Verificação Imediata

O monitor faz uma verificação imediata ao iniciar:

```python
def monitor_loop(intervalo=60):
    # Fazer primeira verificação imediatamente
    novos = verificar()
    if novos > 0:
        logger.info(f"✅ {novos} novos resultados encontrados!")
    
    # Depois verifica a cada intervalo
    while monitor_rodando:
        # ...
```

---

## 📋 Endpoints de Controle

### Verificar Status do Monitor

```bash
GET /api/monitor/status
```

Resposta:
```json
{
  "monitor_rodando": true,
  "monitor_iniciado": true,
  "thread_ativa": true,
  "verificar_disponivel": true
}
```

### Iniciar Monitor Manualmente

```bash
POST /api/monitor/start
Content-Type: application/json

{
  "intervalo": 60
}
```

### Parar Monitor

```bash
POST /api/monitor/stop
```

### Forçar Verificação Imediata

```bash
POST /api/verificar-agora
```

---

## 🔍 Troubleshooting

### Monitor não está iniciando

1. **Verificar variável de ambiente:**
   ```bash
   echo $MONITOR_AUTO_START
   # Deve retornar: true
   ```

2. **Verificar logs:**
   ```bash
   # Ver logs do Gunicorn
   tail -f /var/log/gunicorn.log
   
   # Ou se estiver usando Docker
   docker logs <container_id>
   ```

3. **Verificar se função `verificar` está disponível:**
   ```bash
   curl http://localhost:8000/api/monitor/status
   # Verificar campo "verificar_disponivel"
   ```

4. **Iniciar manualmente via API:**
   ```bash
   curl -X POST http://localhost:8000/api/monitor/start \
     -H "Content-Type: application/json" \
     -d '{"intervalo": 60}'
   ```

### Monitor para após alguns minutos

1. **Verificar se thread está viva:**
   ```bash
   curl http://localhost:8000/api/monitor/status
   ```

2. **Verificar logs de erro:**
   ```bash
   # Procurar por erros no monitor
   grep "Erro no monitor" /var/log/gunicorn.log
   ```

3. **Reiniciar monitor:**
   ```bash
   curl -X POST http://localhost:8000/api/monitor/stop
   curl -X POST http://localhost:8000/api/monitor/start \
     -H "Content-Type: application/json" \
     -d '{"intervalo": 60}'
   ```

### Monitor não encontra resultados

1. **Verificar se monitor está rodando:**
   ```bash
   curl http://localhost:8000/api/monitor/status
   ```

2. **Forçar verificação imediata:**
   ```bash
   curl -X POST http://localhost:8000/api/verificar-agora
   ```

3. **Verificar resultados:**
   ```bash
   curl http://localhost:8000/api/resultados
   ```

---

## 📝 Exemplo de Deploy

### Docker Compose

```yaml
version: '3.8'

services:
  monitor:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONITOR_AUTO_START=true
      - MONITOR_INTERVALO=60
    volumes:
      - ./resultados.json:/app/resultados.json
    restart: unless-stopped
```

### Systemd Service

```ini
[Unit]
Description=Monitor de Resultados Bicho Certo
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/monitorresultados
Environment="MONITOR_AUTO_START=true"
Environment="MONITOR_INTERVALO=60"
ExecStart=/usr/bin/gunicorn --config gunicorn_config.py app_vps:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Script de Inicialização

```bash
#!/bin/bash
# iniciar_monitor.sh

export MONITOR_AUTO_START=true
export MONITOR_INTERVALO=60

gunicorn --config gunicorn_config.py app_vps:app
```

---

## ✅ Checklist de Configuração

- [ ] Variável `MONITOR_AUTO_START=true` configurada
- [ ] Variável `MONITOR_INTERVALO` configurada (padrão: 60)
- [ ] Função `verificar` disponível (módulo `monitor_selenium` importado)
- [ ] Logs sendo monitorados
- [ ] Endpoint `/api/monitor/status` retorna `monitor_rodando: true`
- [ ] Primeira verificação acontece ao iniciar
- [ ] Verificações subsequentes acontecem no intervalo configurado

---

## 🎉 Pronto!

Agora o monitor inicia automaticamente sempre que a aplicação é iniciada, sem necessidade de redeploy manual!

Para verificar se está funcionando:

```bash
# 1. Verificar status
curl http://localhost:8000/api/monitor/status

# 2. Verificar resultados
curl http://localhost:8000/api/resultados

# 3. Verificar última verificação
curl http://localhost:8000/api/status
```
