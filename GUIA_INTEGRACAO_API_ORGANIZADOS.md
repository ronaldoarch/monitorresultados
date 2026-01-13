# 🚀 Guia Completo: Integração da API de Resultados Organizados

Este guia mostra como integrar a API `/api/resultados/organizados` no seu site e configurar liquidação automática de apostas.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Consumindo a API no Frontend](#consumindo-a-api-no-frontend)
3. [Exibindo Resultados no Site](#exibindo-resultados-no-site)
4. [Liquidação Automática](#liquidação-automática)
5. [Exemplo Completo](#exemplo-completo)

---

## 🎯 Visão Geral

A API `/api/resultados/organizados` retorna resultados organizados por:
- **Tabela (Loteria)**: Ex: "PT Rio de Janeiro", "Look Goiás"
- **Horário**: Ex: "09:30", "11:20", "15h"
- **Limite**: Máximo de 7 posições por sorteio (1° a 7°)

**Endpoint Base:**
```
GET https://seu-monitor.com/api/resultados/organizados
```

---

## 💻 Consumindo a API no Frontend

### Exemplo 1: JavaScript Vanilla (Fetch API)

```javascript
// Função para buscar resultados organizados
async function buscarResultadosOrganizados() {
    try {
        const response = await fetch('https://seu-monitor.com/api/resultados/organizados');
        const data = await response.json();
        
        if (data.organizados) {
            return data.organizados;
        }
        return {};
    } catch (error) {
        console.error('Erro ao buscar resultados:', error);
        return {};
    }
}

// Usar a função
buscarResultadosOrganizados().then(resultados => {
    console.log('Resultados:', resultados);
    exibirResultados(resultados);
});
```

### Exemplo 2: jQuery

```javascript
function buscarResultadosOrganizados() {
    $.ajax({
        url: 'https://seu-monitor.com/api/resultados/organizados',
        method: 'GET',
        dataType: 'json',
        success: function(data) {
            if (data.organizados) {
                exibirResultados(data.organizados);
            }
        },
        error: function(xhr, status, error) {
            console.error('Erro ao buscar resultados:', error);
        }
    });
}

// Chamar a cada 30 segundos
setInterval(buscarResultadosOrganizados, 30000);
```

### Exemplo 3: Axios

```javascript
import axios from 'axios';

async function buscarResultadosOrganizados() {
    try {
        const response = await axios.get('https://seu-monitor.com/api/resultados/organizados');
        return response.data.organizados || {};
    } catch (error) {
        console.error('Erro ao buscar resultados:', error);
        return {};
    }
}

// Usar
buscarResultadosOrganizados().then(resultados => {
    exibirResultados(resultados);
});
```

---

## 🎨 Exibindo Resultados no Site

### Estrutura HTML Base

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resultados do Jogo do Bicho</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        
        .tabela {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .tabela h2 {
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        
        .horario {
            margin-bottom: 25px;
        }
        
        .horario h3 {
            color: #555;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .resultados-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
        }
        
        .resultado-item {
            background: #ecf0f1;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        
        .resultado-item.primeiro {
            border-left-color: #e74c3c;
            background: #fff5f5;
        }
        
        .posicao {
            font-weight: bold;
            color: #e74c3c;
            font-size: 14px;
        }
        
        .numero {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin: 5px 0;
        }
        
        .animal {
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        
        .erro {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Resultados do Jogo do Bicho</h1>
        <div id="loading" class="loading">Carregando resultados...</div>
        <div id="erro" style="display: none;"></div>
        <div id="resultados"></div>
    </div>

    <script>
        const API_URL = 'https://seu-monitor.com/api/resultados/organizados';
        
        // Função para buscar resultados
        async function buscarResultados() {
            try {
                document.getElementById('loading').style.display = 'block';
                document.getElementById('erro').style.display = 'none';
                
                const response = await fetch(API_URL);
                const data = await response.json();
                
                if (data.organizados) {
                    exibirResultados(data.organizados);
                } else {
                    mostrarErro('Nenhum resultado encontrado');
                }
            } catch (error) {
                mostrarErro('Erro ao carregar resultados: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        // Função para exibir resultados
        function exibirResultados(organizados) {
            const container = document.getElementById('resultados');
            container.innerHTML = '';
            
            // Ordenar tabelas alfabeticamente
            const tabelas = Object.keys(organizados).sort();
            
            tabelas.forEach(tabela => {
                const tabelaDiv = document.createElement('div');
                tabelaDiv.className = 'tabela';
                
                const titulo = document.createElement('h2');
                titulo.textContent = tabela;
                tabelaDiv.appendChild(titulo);
                
                // Ordenar horários
                const horarios = Object.keys(organizados[tabela]).sort();
                
                horarios.forEach(horario => {
                    const horarioDiv = document.createElement('div');
                    horarioDiv.className = 'horario';
                    
                    const horarioTitulo = document.createElement('h3');
                    horarioTitulo.textContent = `Horário: ${horario}`;
                    horarioDiv.appendChild(horarioTitulo);
                    
                    const grid = document.createElement('div');
                    grid.className = 'resultados-grid';
                    
                    organizados[tabela][horario].forEach(resultado => {
                        const item = document.createElement('div');
                        item.className = 'resultado-item';
                        if (resultado.posicao === 1) {
                            item.classList.add('primeiro');
                        }
                        
                        item.innerHTML = `
                            <div class="posicao">${resultado.colocacao}</div>
                            <div class="numero">${resultado.numero}</div>
                            <div class="animal">${resultado.animal}</div>
                        `;
                        
                        grid.appendChild(item);
                    });
                    
                    horarioDiv.appendChild(grid);
                    tabelaDiv.appendChild(horarioDiv);
                });
                
                container.appendChild(tabelaDiv);
            });
        }
        
        // Função para mostrar erro
        function mostrarErro(mensagem) {
            const erroDiv = document.getElementById('erro');
            erroDiv.textContent = mensagem;
            erroDiv.style.display = 'block';
        }
        
        // Carregar resultados ao iniciar
        buscarResultados();
        
        // Atualizar a cada 30 segundos
        setInterval(buscarResultados, 30000);
    </script>
</body>
</html>
```

---

## ⚙️ Liquidação Automática

### Opção 1: Endpoint de Liquidação (Recomendado)

Se você tem um sistema de apostas próprio, pode usar o endpoint de liquidação:

```javascript
// Endpoint para liquidar apostas automaticamente
async function liquidarApostas() {
    try {
        const response = await fetch('https://seu-monitor.com/api/resultados/liquidar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.sucesso) {
            console.log(`✅ ${data.apostas_liquidadas} apostas liquidadas`);
            return data;
        } else {
            console.error('Erro na liquidação:', data.erro);
            return null;
        }
    } catch (error) {
        console.error('Erro ao liquidar:', error);
        return null;
    }
}
```

### Opção 2: Liquidação Manual no Backend

Se você quer implementar sua própria lógica de liquidação:

```javascript
// Backend Node.js/Express exemplo
const express = require('express');
const axios = require('axios');
const app = express();

// Endpoint para buscar resultados e liquidar
app.post('/api/liquidar-automatico', async (req, res) => {
    try {
        // 1. Buscar resultados organizados
        const resultadosResponse = await axios.get('https://seu-monitor.com/api/resultados/organizados');
        const resultados = resultadosResponse.data.organizados;
        
        // 2. Processar cada tabela e horário
        let totalLiquidado = 0;
        
        for (const [tabela, horarios] of Object.entries(resultados)) {
            for (const [horario, resultadosSorteio] of Object.entries(horarios)) {
                // 3. Buscar apostas pendentes para este sorteio
                const apostas = await buscarApostasPendentes(tabela, horario);
                
                // 4. Verificar cada aposta contra os resultados
                for (const aposta of apostas) {
                    const ganhou = verificarGanho(aposta, resultadosSorteio);
                    
                    if (ganhou) {
                        await liquidarAposta(aposta, resultadosSorteio);
                        totalLiquidado++;
                    } else {
                        await marcarApostaComoPerdida(aposta);
                    }
                }
            }
        }
        
        res.json({
            sucesso: true,
            apostas_liquidadas: totalLiquidado
        });
    } catch (error) {
        res.status(500).json({
            sucesso: false,
            erro: error.message
        });
    }
});

// Função para verificar se aposta ganhou
function verificarGanho(aposta, resultados) {
    for (const resultado of resultados) {
        // Verificar por número
        if (aposta.numero === resultado.numero) {
            return true;
        }
        // Verificar por animal
        if (aposta.animal.toLowerCase() === resultado.animal.toLowerCase()) {
            return true;
        }
        // Verificar por posição (se aposta especificou posição)
        if (aposta.posicao_esperada && resultado.posicao === aposta.posicao_esperada) {
            return true;
        }
    }
    return false;
}

app.listen(3000, () => {
    console.log('Servidor rodando na porta 3000');
});
```

### Opção 3: Cron Job para Liquidação Automática

**Node.js com node-cron:**

```javascript
const cron = require('node-cron');
const axios = require('axios');

// Executar a cada 1 minuto
cron.schedule('* * * * *', async () => {
    console.log('🔄 Verificando resultados para liquidação...');
    
    try {
        // Buscar resultados
        const response = await axios.get('https://seu-monitor.com/api/resultados/organizados');
        const resultados = response.data.organizados;
        
        // Processar liquidação
        await processarLiquidacao(resultados);
        
        console.log('✅ Liquidação concluída');
    } catch (error) {
        console.error('❌ Erro na liquidação:', error.message);
    }
});

async function processarLiquidacao(resultados) {
    // Sua lógica de liquidação aqui
    for (const [tabela, horarios] of Object.entries(resultados)) {
        for (const [horario, resultadosSorteio] of Object.entries(horarios)) {
            // Processar cada sorteio
            await liquidarSorteio(tabela, horario, resultadosSorteio);
        }
    }
}
```

**Python com schedule:**

```python
import schedule
import time
import requests

def liquidar_automatico():
    print('🔄 Verificando resultados para liquidação...')
    
    try:
        # Buscar resultados
        response = requests.get('https://seu-monitor.com/api/resultados/organizados')
        data = response.json()
        resultados = data.get('organizados', {})
        
        # Processar liquidação
        processar_liquidacao(resultados)
        
        print('✅ Liquidação concluída')
    except Exception as e:
        print(f'❌ Erro na liquidação: {e}')

def processar_liquidacao(resultados):
    for tabela, horarios in resultados.items():
        for horario, resultados_sorteio in horarios.items():
            # Processar cada sorteio
            liquidar_sorteio(tabela, horario, resultados_sorteio)

# Executar a cada 1 minuto
schedule.every(1).minutes.do(liquidar_automatico)

while True:
    schedule.run_pending()
    time.sleep(1)
```

---

## 📝 Exemplo Completo: Frontend + Backend

### Frontend (HTML + JavaScript)

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Resultados e Liquidação</title>
</head>
<body>
    <h1>Resultados do Jogo do Bicho</h1>
    <button onclick="atualizarResultados()">Atualizar Resultados</button>
    <button onclick="liquidarApostas()">Liquidar Apostas</button>
    <div id="resultados"></div>
    <div id="status"></div>

    <script>
        const API_BASE = 'https://seu-monitor.com/api';
        
        async function atualizarResultados() {
            try {
                const response = await fetch(`${API_BASE}/resultados/organizados`);
                const data = await response.json();
                exibirResultados(data.organizados);
            } catch (error) {
                console.error('Erro:', error);
            }
        }
        
        async function liquidarApostas() {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = 'Liquidando...';
            
            try {
                const response = await fetch(`${API_BASE}/resultados/liquidar`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.sucesso) {
                    statusDiv.textContent = `✅ ${data.apostas_liquidadas} apostas liquidadas`;
                } else {
                    statusDiv.textContent = `❌ Erro: ${data.erro}`;
                }
            } catch (error) {
                statusDiv.textContent = `❌ Erro: ${error.message}`;
            }
        }
        
        function exibirResultados(organizados) {
            const div = document.getElementById('resultados');
            div.innerHTML = JSON.stringify(organizados, null, 2);
        }
        
        // Atualizar automaticamente a cada 30 segundos
        setInterval(atualizarResultados, 30000);
        atualizarResultados();
    </script>
</body>
</html>
```

---

## 🔐 Segurança e Boas Práticas

### 1. CORS (Cross-Origin Resource Sharing)

Se seu site estiver em um domínio diferente do monitor, configure CORS:

```python
# No app_vps.py (Flask)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permitir todas as origens
# ou
CORS(app, origins=["https://seusite.com"])  # Permitir apenas seu site
```

### 2. Rate Limiting

Limite requisições para evitar sobrecarga:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/resultados/organizados')
@limiter.limit("10 per minute")
def api_resultados_organizados():
    # ...
```

### 3. Cache

Use cache para reduzir requisições:

```javascript
// Cache simples no frontend
let cacheResultados = null;
let cacheTimestamp = null;
const CACHE_DURATION = 30000; // 30 segundos

async function buscarResultadosComCache() {
    const agora = Date.now();
    
    if (cacheResultados && cacheTimestamp && (agora - cacheTimestamp) < CACHE_DURATION) {
        return cacheResultados;
    }
    
    const resultados = await buscarResultadosOrganizados();
    cacheResultados = resultados;
    cacheTimestamp = agora;
    
    return resultados;
}
```

---

## 📊 Estrutura de Dados Retornada

```json
{
  "organizados": {
    "PT Rio de Janeiro": {
      "09:30": [
        {
          "horario": "09:30",
          "animal": "Camelo",
          "numero": "4732",
          "posicao": 1,
          "colocacao": "1°",
          "estado": "RJ",
          "data_extracao": "13/01/2026",
          "timestamp": "2026-01-13T22:01:40.661260"
        }
        // ... até 7 resultados
      ]
    }
  },
  "estatisticas": {
    "total_tabelas": 18,
    "total_horarios": 38,
    "total_resultados": 194
  },
  "ultima_verificacao": "2026-01-13T22:03:25.593233",
  "fonte": "bichocerto.com"
}
```

---

## 🚀 Próximos Passos

1. **Integrar no seu site**: Use os exemplos acima para exibir resultados
2. **Configurar liquidação**: Escolha uma das opções de liquidação automática
3. **Monitorar**: Configure logs e alertas para acompanhar o funcionamento
4. **Otimizar**: Implemente cache e rate limiting conforme necessário

---

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique a documentação: `API_RESULTADOS_ORGANIZADOS.md`
- Consulte os logs do monitor: `GET /api/status`
- Verifique a última verificação: campo `ultima_verificacao` na resposta
