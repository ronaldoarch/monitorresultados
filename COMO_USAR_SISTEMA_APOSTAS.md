# 🎰 Como Usar o Sistema de Apostas

## 📋 Visão Geral

Sistema completo de apostas com:
- ✅ Monitor automático de resultados
- ✅ Liquidação automática de apostas
- ✅ API REST completa
- ✅ Banco de dados integrado

## 🚀 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements_apostas.txt
```

### 2. Inicializar Banco de Dados

O banco será criado automaticamente na primeira execução (SQLite por padrão).

Para PostgreSQL:
```python
sistema = SistemaLiquidacao('postgresql://user:pass@localhost/apostas')
```

## 🔧 Configuração

### Iniciar Servidor

```bash
# Com monitor automático
python3 app_apostas.py --monitor --intervalo 60 --port 5001

# Sem monitor (apenas API)
python3 app_apostas.py --port 5001
```

### Iniciar Monitor Separadamente

```bash
# Via API
curl -X POST http://localhost:5001/api/monitor/start

# Com intervalo customizado
curl -X POST http://localhost:5001/api/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"intervalo": 120}'
```

## 📡 API Endpoints

### Apostas

#### Criar Aposta
```bash
POST /api/apostas
{
  "usuario_id": 1,
  "numero": "1234",
  "animal": "Cavalo",
  "valor": 10.0,
  "loteria": "PT Rio de Janeiro",
  "horario": "11:00",
  "tipo_aposta": "grupo",
  "multiplicador": 18.0
}
```

#### Ver Aposta
```bash
GET /api/apostas/{id}
```

#### Listar Apostas do Usuário
```bash
GET /api/apostas/usuario/{usuario_id}
```

### Resultados

#### Listar Resultados
```bash
GET /api/resultados
```

#### Forçar Liquidação
```bash
POST /api/resultados/liquidar
```

### Usuários

#### Consultar Saldo
```bash
GET /api/usuarios/{usuario_id}/saldo
```

### Monitor

#### Iniciar Monitor
```bash
POST /api/monitor/start
```

#### Parar Monitor
```bash
POST /api/monitor/stop
```

#### Status do Monitor
```bash
GET /api/monitor/status
```

## 🔄 Fluxo de Funcionamento

### 1. Usuário Faz Aposta
```python
# Via API
POST /api/apostas
{
  "usuario_id": 1,
  "numero": "1234",
  "animal": "Cavalo",
  "valor": 10.0,
  "loteria": "PT Rio de Janeiro",
  "horario": "11:00"
}
```

### 2. Monitor Detecta Resultado
- Monitor verifica a cada X segundos
- Quando encontra novo resultado, processa automaticamente

### 3. Sistema Liquida Apostas
- Busca apostas pendentes para aquele horário/loteria
- Compara número/animal
- Calcula ganho (se houver)
- Atualiza saldo do usuário
- Registra transação

### 4. Frontend Atualiza
- Frontend consulta API
- Mostra resultados em tempo real
- Exibe ganhos/perdas

## 💻 Exemplo de Uso

### Python

```python
import requests

# Criar aposta
response = requests.post('http://localhost:5001/api/apostas', json={
    'usuario_id': 1,
    'numero': '1234',
    'animal': 'Cavalo',
    'valor': 10.0,
    'loteria': 'PT Rio de Janeiro',
    'horario': '11:00'
})
print(response.json())

# Consultar saldo
response = requests.get('http://localhost:5001/api/usuarios/1/saldo')
print(response.json())

# Listar apostas
response = requests.get('http://localhost:5001/api/apostas/usuario/1')
print(response.json())
```

### JavaScript

```javascript
// Criar aposta
fetch('http://localhost:5001/api/apostas', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    usuario_id: 1,
    numero: '1234',
    animal: 'Cavalo',
    valor: 10.0,
    loteria: 'PT Rio de Janeiro',
    horario: '11:00'
  })
})
.then(r => r.json())
.then(data => console.log(data));

// Consultar saldo
fetch('http://localhost:5001/api/usuarios/1/saldo')
  .then(r => r.json())
  .then(data => console.log(data));
```

## 🗄️ Banco de Dados

### Estrutura

- **usuarios**: Usuários do sistema
- **apostas**: Apostas feitas
- **resultados**: Resultados extraídos
- **liquidacoes**: Registro de liquidações
- **transacoes**: Histórico de transações

### Migrar para PostgreSQL

```python
from sistema_liquidacao import SistemaLiquidacao

# SQLite (padrão)
sistema = SistemaLiquidacao('sqlite:///apostas.db')

# PostgreSQL
sistema = SistemaLiquidacao('postgresql://user:pass@localhost/apostas')
```

## 🔐 Segurança

### Implementar:

1. **Autenticação JWT**
2. **Validação de entrada**
3. **Rate limiting**
4. **Criptografia de dados sensíveis**
5. **Logs de auditoria**
6. **Backup regular**

## 📊 Integração com Frontend

### WebSocket (Tempo Real)

Para atualizações em tempo real, adicione WebSocket:

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('connected', {'data': 'Conectado'})

# Quando resultado for processado
socketio.emit('resultado_processado', {
    'numero': resultado.numero,
    'animal': resultado.animal,
    'loteria': resultado.loteria
})
```

### Frontend React/Vue

```javascript
// Conectar WebSocket
const socket = io('http://localhost:5001');

socket.on('resultado_processado', (data) => {
  // Atualizar UI
  atualizarResultados(data);
});
```

## 🚀 Deploy

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements_apostas.txt .
RUN pip install -r requirements_apostas.txt
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app_apostas:app"]
```

### Systemd

```ini
[Unit]
Description=Sistema de Apostas
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/apostas/app_apostas.py --monitor
Restart=always

[Install]
WantedBy=multi-user.target
```

## ✅ Checklist

- [ ] Banco de dados configurado
- [ ] API testada
- [ ] Monitor funcionando
- [ ] Liquidação automática ativa
- [ ] Frontend integrado
- [ ] Segurança implementada
- [ ] Logs configurados
- [ ] Backup configurado

## 🎯 Próximos Passos

1. Integrar com seu frontend existente
2. Adicionar autenticação
3. Configurar WebSocket para tempo real
4. Implementar notificações
5. Adicionar dashboard administrativo

Boa sorte! 🚀

