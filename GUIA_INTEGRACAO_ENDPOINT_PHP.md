# 🔗 Guia de Integração com Endpoint PHP

## 📋 Visão Geral

O sistema Python agora se integra com o endpoint PHP do painel que faz **TUDO**:
- ✅ Busca resultados
- ✅ Salva em `games`
- ✅ Sincroniza com `extractions`
- ✅ Liquida apostas pendentes
- ✅ Retorna resultados formatados

## 🚀 Como Usar

### Opção 1: Servidor Python Integrado (Recomendado)

```bash
# Iniciar servidor que chama endpoint PHP
python3 integracao_endpoint_php.py \
  --endpoint-php "https://lotbicho.com/backend/scraper/processar-resultados-completo.php" \
  --auto \
  --intervalo 5 \
  --port 5001
```

Isso vai:
- Iniciar servidor Flask na porta 5001
- Chamar endpoint PHP a cada 5 minutos automaticamente
- Expor API para o frontend

### Opção 2: Usar no app_vps.py Existente

Adicione ao seu `app_vps.py`:

```python
from integracao_endpoint_php import processar_resultados_via_php

@app.route('/api/resultados', methods=['GET'])
def api_resultados():
    """Processa e retorna resultados via PHP"""
    resultado = processar_resultados_via_php()
    
    if resultado['sucesso']:
        return jsonify({
            'resultados': resultado['resultados'],
            'summary': resultado['summary']
        })
    else:
        return jsonify({
            'resultados': [],
            'erro': resultado.get('erro')
        }), 500
```

## 📡 Endpoints Disponíveis

### Processar Resultados

```bash
POST /api/resultados/processar
```

Retorna:
```json
{
  "sucesso": true,
  "resultados": [...],
  "summary": {
    "results_saved": 15,
    "extractions_synced": 12,
    "bets_processed": 5,
    "bets_won": 2,
    "bets_lost": 3
  }
}
```

### Listar Resultados

```bash
GET /api/resultados
```

Processa resultados primeiro, depois retorna.

### Status

```bash
GET /api/status
```

### Processamento Automático

```bash
# Iniciar
POST /api/processamento/start
{
  "intervalo": 5  # minutos
}

# Parar
POST /api/processamento/stop

# Status
GET /api/processamento/status
```

## 🔄 Fluxo Completo

```
┌─────────────────────────────────────┐
│  Frontend (Seu Jogo)                │
│                                     │
│  GET /api/resultados               │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Servidor Python                    │
│  (integracao_endpoint_php.py)      │
│                                     │
│  → POST endpoint PHP                │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Endpoint PHP do Painel             │
│  (processar-resultados-completo.php)│
│                                     │
│  1. Busca resultados                │
│  2. Salva em games                  │
│  3. Sincroniza → extractions        │
│  4. Liquida apostas                 │
│  5. Retorna resultados              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Frontend                            │
│                                     │
│  Recebe e exibe resultados          │
└─────────────────────────────────────┘
```

## 💻 Exemplo de Uso no Frontend

### JavaScript

```javascript
// Processar resultados
async function processarResultados() {
    const response = await fetch('/api/resultados/processar', {
        method: 'POST'
    });
    const data = await response.json();
    
    if (data.sucesso) {
        console.log(`${data.summary.bets_processed} apostas processadas`);
        console.log(`${data.summary.bets_won} ganhas`);
        
        // Exibir resultados
        exibirResultados(data.resultados);
    }
}

// Listar resultados (processa automaticamente)
async function listarResultados() {
    const response = await fetch('/api/resultados');
    const data = await response.json();
    
    // Exibir resultados
    exibirResultados(data.resultados);
}

// Atualizar a cada 5 minutos
setInterval(processarResultados, 5 * 60 * 1000);
```

## ⚙️ Configuração

### Variável de Ambiente

```bash
export ENDPOINT_PHP="https://lotbicho.com/backend/scraper/processar-resultados-completo.php"
python3 integracao_endpoint_php.py --auto
```

### No Código

Edite `integracao_endpoint_php.py`:

```python
ENDPOINT_PHP = 'https://lotbicho.com/backend/scraper/processar-resultados-completo.php'
```

## 🔄 Processamento Automático

### Via API

```bash
# Iniciar (a cada 5 minutos)
curl -X POST http://localhost:5001/api/processamento/start \
  -H "Content-Type: application/json" \
  -d '{"intervalo": 5}'

# Ver status
curl http://localhost:5001/api/processamento/status

# Parar
curl -X POST http://localhost:5001/api/processamento/stop
```

### Via Linha de Comando

```bash
# Iniciar com processamento automático
python3 integracao_endpoint_php.py --auto --intervalo 5
```

## 📊 Exemplo Completo

### app_vps.py Adaptado

```python
from flask import Flask, jsonify
from integracao_endpoint_php import processar_resultados_via_php, iniciar_processamento_automatico

app = Flask(__name__)

@app.route('/api/resultados', methods=['GET'])
def api_resultados():
    """Processa e retorna resultados"""
    resultado = processar_resultados_via_php()
    
    if resultado['sucesso']:
        return jsonify({
            'resultados': resultado['resultados'],
            'summary': resultado['summary']
        })
    else:
        return jsonify({
            'resultados': [],
            'erro': resultado.get('erro')
        }), 500

# Iniciar processamento automático
iniciar_processamento_automatico(intervalo_minutos=5)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

## ✅ Vantagens

1. **Simples**: Um único endpoint PHP faz tudo
2. **Confiável**: Usa sistema existente do painel
3. **Completo**: Busca, salva, sincroniza, liquida
4. **Flexível**: Pode ser chamado manualmente ou automaticamente
5. **Rápido**: Processa tudo em segundos

## 🎯 Próximos Passos

1. ✅ Sistema Python criado
2. ⏳ Configurar URL do endpoint PHP
3. ⏳ Testar processamento
4. ⏳ Integrar com frontend
5. ⏳ Configurar processamento automático

## 🔧 Troubleshooting

### Endpoint PHP não responde?

```python
# Verificar URL
print(f"Endpoint: {ENDPOINT_PHP}")

# Testar manualmente
import requests
response = requests.post(ENDPOINT_PHP, timeout=300)
print(response.json())
```

### Timeout?

Aumente o timeout:

```python
response = requests.post(ENDPOINT_PHP, timeout=600)  # 10 minutos
```

### Erro de conexão?

Verifique:
- URL do endpoint está correta
- Servidor PHP está acessível
- Firewall permite conexão

Tudo pronto para integrar! 🚀

