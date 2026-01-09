# 🔌 Integração Completa - Livro dos Sonhos + Monitor Deu no Poste

Guia completo para integrar ambas as APIs no seu site.

## 📋 Visão Geral

Você tem **2 sistemas** que trabalham juntos:

1. **Livro dos Sonhos** (Porta 8082) - Interpreta sonhos e gera palpites
2. **Monitor Deu no Poste** (Porta 8081) - Monitora resultados e liquida apostas

---

## 🌐 URLs das APIs

### Livro dos Sonhos
```
http://seu-servidor:8082/api/v1
```

### Monitor Deu no Poste
```
http://seu-servidor:8081/api
```

---

## 📡 Endpoints Disponíveis

### 📖 Livro dos Sonhos (Porta 8082)

#### 1. Interpretar Sonho
**POST** `/api/v1/interpretar`
```json
{
  "sonho": "leão"
}
```

#### 2. Sonhos Populares
**GET** `/api/v1/sonhos/populares?limite=30`

#### 3. Status
**GET** `/api/v1/status`

---

### 🎰 Monitor Deu no Poste (Porta 8081)

#### 1. Obter Resultados
**GET** `/api/resultados`
Retorna todos os resultados coletados.

#### 2. Status do Sistema
**GET** `/api/status`
Status do monitor e quantidade de resultados.

#### 3. Forçar Verificação
**POST** `/api/verificar-agora`
Força uma verificação imediata de resultados.

#### 4. Controlar Monitor
- **POST** `/api/monitor/start` - Iniciar monitor
- **POST** `/api/monitor/stop` - Parar monitor
- **GET** `/api/monitor/status` - Status do monitor

---

## 💻 Exemplo de Integração Completa

### JavaScript (Vanilla)

```javascript
// ============================================
// CONFIGURAÇÃO DAS APIs
// ============================================
const API_LIVRO_SONHOS = 'http://seu-servidor:8082/api/v1';
const API_MONITOR = 'http://seu-servidor:8081/api';

// ============================================
// LIVRO DOS SONHOS - Interpretar Sonho
// ============================================
async function interpretarSonho(sonho) {
    try {
        const response = await fetch(`${API_LIVRO_SONHOS}/interpretar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sonho: sonho })
        });
        
        const data = await response.json();
        
        if (data.sucesso && data.encontrado) {
            return {
                sucesso: true,
                dados: data.dados
            };
        } else {
            return {
                sucesso: false,
                mensagem: data.mensagem || 'Sonho não encontrado'
            };
        }
    } catch (error) {
        console.error('Erro ao interpretar sonho:', error);
        return {
            sucesso: false,
            mensagem: 'Erro ao conectar com a API'
        };
    }
}

// ============================================
// MONITOR DEU NO POSTE - Obter Resultados
// ============================================
async function obterResultados() {
    try {
        const response = await fetch(`${API_MONITOR}/resultados`);
        const data = await response.json();
        
        return {
            sucesso: true,
            resultados: data.resultados || [],
            total: data.total_resultados || 0,
            ultima_verificacao: data.ultima_verificacao
        };
    } catch (error) {
        console.error('Erro ao obter resultados:', error);
        return {
            sucesso: false,
            resultados: [],
            mensagem: 'Erro ao conectar com a API'
        };
    }
}

// ============================================
// MONITOR - Forçar Verificação
// ============================================
async function verificarResultadosAgora() {
    try {
        const response = await fetch(`${API_MONITOR}/verificar-agora`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        return {
            sucesso: data.sucesso || false,
            mensagem: data.mensagem || 'Verificação concluída',
            total_resultados: data.total_resultados || 0
        };
    } catch (error) {
        console.error('Erro ao verificar resultados:', error);
        return {
            sucesso: false,
            mensagem: 'Erro ao conectar com a API'
        };
    }
}

// ============================================
// MONITOR - Status
// ============================================
async function obterStatusMonitor() {
    try {
        const response = await fetch(`${API_MONITOR}/status`);
        const data = await response.json();
        
        return {
            sucesso: true,
            monitor_rodando: data.monitor_rodando || false,
            total_resultados: data.total_resultados || 0,
            ultima_verificacao: data.ultima_verificacao
        };
    } catch (error) {
        console.error('Erro ao obter status:', error);
        return {
            sucesso: false,
            mensagem: 'Erro ao conectar com a API'
        };
    }
}

// ============================================
// EXEMPLO DE USO COMPLETO
// ============================================

// 1. Usuário informa sonho
async function processarSonho(sonho) {
    // Interpretar sonho
    const interpretacao = await interpretarSonho(sonho);
    
    if (interpretacao.sucesso) {
        const dados = interpretacao.dados;
        
        // Exibir palpites para o usuário
        console.log('Animal:', dados.animal);
        console.log('Grupo:', dados.grupo);
        console.log('Números:', dados.numeros);
        
        // Aqui você pode criar a aposta no seu sistema
        // e depois monitorar os resultados
        
        return dados;
    } else {
        console.error('Erro:', interpretacao.mensagem);
        return null;
    }
}

// 2. Verificar resultados periodicamente
async function verificarResultados() {
    const status = await obterStatusMonitor();
    
    if (status.sucesso) {
        console.log('Monitor rodando:', status.monitor_rodando);
        console.log('Total de resultados:', status.total_resultados);
        
        // Obter resultados
        const resultados = await obterResultados();
        
        if (resultados.sucesso) {
            // Processar resultados e liquidar apostas
            resultados.resultados.forEach(resultado => {
                console.log('Resultado:', resultado.numero, resultado.animal);
                // Aqui você liquidaria as apostas correspondentes
            });
        }
    }
}

// 3. Verificar resultados manualmente
async function verificarAgora() {
    const resultado = await verificarResultadosAgora();
    
    if (resultado.sucesso) {
        console.log('Verificação concluída:', resultado.mensagem);
        console.log('Resultados encontrados:', resultado.total_resultados);
        
        // Atualizar lista de resultados
        await verificarResultados();
    }
}

// ============================================
// EXEMPLO DE INTEGRAÇÃO NO HTML
// ============================================
```

---

## 🎨 Exemplo Completo HTML + JavaScript

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integração Completa - Livro dos Sonhos + Monitor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #0d4f1c;
            color: white;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .card {
            background: rgba(13, 79, 28, 0.9);
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #4ade80;
        }
        input, button {
            padding: 10px;
            margin: 5px;
            border: 2px solid #4ade80;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        button {
            background: #4ade80;
            color: #0d4f1c;
            font-weight: bold;
            cursor: pointer;
        }
        .resultado {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
        }
        .numero {
            display: inline-block;
            padding: 8px 15px;
            margin: 5px;
            background: rgba(251, 191, 36, 0.2);
            border: 2px solid #fbbf24;
            border-radius: 5px;
            color: #fbbf24;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h1>📖 Livro dos Sonhos + 🎰 Monitor Deu no Poste</h1>
    
    <div class="container">
        <!-- LIVRO DOS SONHOS -->
        <div class="card">
            <h2>📖 Interpretar Sonho</h2>
            <input type="text" id="sonhoInput" placeholder="Digite seu sonho...">
            <button onclick="interpretar()">Interpretar</button>
            <div id="resultadoSonho" class="resultado" style="display: none;"></div>
        </div>
        
        <!-- MONITOR DEU NO POSTE -->
        <div class="card">
            <h2>🎰 Resultados</h2>
            <button onclick="verificarAgora()">🔄 Verificar Agora</button>
            <button onclick="carregarResultados()">📊 Carregar Resultados</button>
            <div id="statusMonitor" class="resultado"></div>
            <div id="resultadosMonitor" class="resultado" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        // Configuração
        const API_LIVRO_SONHOS = 'http://192.168.18.175:8082/api/v1';
        const API_MONITOR = 'http://192.168.18.175:8081/api';
        
        // ============================================
        // LIVRO DOS SONHOS
        // ============================================
        async function interpretar() {
            const sonho = document.getElementById('sonhoInput').value.trim();
            const resultadoDiv = document.getElementById('resultadoSonho');
            
            if (!sonho) {
                alert('Por favor, digite um sonho!');
                return;
            }
            
            resultadoDiv.innerHTML = 'Interpretando...';
            resultadoDiv.style.display = 'block';
            
            try {
                const response = await fetch(`${API_LIVRO_SONHOS}/interpretar`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sonho: sonho })
                });
                
                const data = await response.json();
                
                if (data.sucesso && data.encontrado) {
                    const dados = data.dados;
                    resultadoDiv.innerHTML = `
                        <h3>🎯 ${dados.animal}</h3>
                        <p><strong>Grupo:</strong> ${dados.grupo}</p>
                        <p><strong>Significado:</strong> ${dados.significado}</p>
                        <h4>Números Sugeridos:</h4>
                        <div class="numero">Grupo: ${dados.numeros.grupo}</div>
                        <div class="numero">Dezena: ${dados.numeros.dezena}</div>
                        <div class="numero">Centena: ${dados.numeros.centena}</div>
                        <div class="numero">Milhar: ${dados.numeros.milhar}</div>
                    `;
                } else {
                    resultadoDiv.innerHTML = `<p style="color: #ef4444;">${data.mensagem || 'Sonho não encontrado'}</p>`;
                }
            } catch (error) {
                resultadoDiv.innerHTML = '<p style="color: #ef4444;">Erro ao conectar com a API</p>';
                console.error('Erro:', error);
            }
        }
        
        // ============================================
        // MONITOR DEU NO POSTE
        // ============================================
        async function verificarAgora() {
            const statusDiv = document.getElementById('statusMonitor');
            statusDiv.innerHTML = 'Verificando...';
            
            try {
                const response = await fetch(`${API_MONITOR}/verificar-agora`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                const data = await response.json();
                
                if (data.sucesso) {
                    statusDiv.innerHTML = `
                        <p>✅ ${data.mensagem}</p>
                        <p>Resultados encontrados: ${data.total_resultados || 0}</p>
                    `;
                    // Recarregar resultados
                    setTimeout(carregarResultados, 1000);
                } else {
                    statusDiv.innerHTML = `<p style="color: #ef4444;">Erro: ${data.erro || data.mensagem}</p>`;
                }
            } catch (error) {
                statusDiv.innerHTML = '<p style="color: #ef4444;">Erro ao conectar com a API</p>';
                console.error('Erro:', error);
            }
        }
        
        async function carregarResultados() {
            const resultadosDiv = document.getElementById('resultadosMonitor');
            resultadosDiv.innerHTML = 'Carregando...';
            resultadosDiv.style.display = 'block';
            
            try {
                const response = await fetch(`${API_MONITOR}/resultados`);
                const data = await response.json();
                
                if (data.resultados && data.resultados.length > 0) {
                    let html = `<h3>📊 Resultados (${data.total_resultados || 0})</h3>`;
                    
                    // Agrupar por loteria e data
                    const agrupados = {};
                    data.resultados.forEach(r => {
                        const chave = `${r.loteria}_${r.data || 'Sem data'}`;
                        if (!agrupados[chave]) {
                            agrupados[chave] = {
                                loteria: r.loteria,
                                data: r.data || 'Sem data',
                                resultados: []
                            };
                        }
                        agrupados[chave].resultados.push(r);
                    });
                    
                    Object.values(agrupados).forEach(grupo => {
                        html += `
                            <div style="margin: 15px 0; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px;">
                                <strong>${grupo.loteria} - ${grupo.data}</strong>
                                <div style="margin-top: 10px;">
                        `;
                        
                        grupo.resultados.forEach(r => {
                            html += `
                                <div style="margin: 5px 0;">
                                    <span class="numero">${r.numero}</span>
                                    <strong>${r.animal}</strong>
                                    ${r.horario ? ` - ${r.horario}` : ''}
                                </div>
                            `;
                        });
                        
                        html += `</div></div>`;
                    });
                    
                    resultadosDiv.innerHTML = html;
                } else {
                    resultadosDiv.innerHTML = '<p>Nenhum resultado encontrado ainda.</p>';
                }
            } catch (error) {
                resultadosDiv.innerHTML = '<p style="color: #ef4444;">Erro ao carregar resultados</p>';
                console.error('Erro:', error);
            }
        }
        
        // Carregar status ao iniciar
        async function carregarStatus() {
            try {
                const response = await fetch(`${API_MONITOR}/status`);
                const data = await response.json();
                
                const statusDiv = document.getElementById('statusMonitor');
                statusDiv.innerHTML = `
                    <p><strong>Status do Monitor:</strong> ${data.monitor_rodando ? '🟢 Ativo' : '🔴 Inativo'}</p>
                    <p><strong>Total de Resultados:</strong> ${data.total_resultados || 0}</p>
                    ${data.ultima_verificacao ? `<p><strong>Última Verificação:</strong> ${new Date(data.ultima_verificacao).toLocaleString('pt-BR')}</p>` : ''}
                `;
            } catch (error) {
                console.error('Erro ao carregar status:', error);
            }
        }
        
        // Carregar status ao iniciar
        carregarStatus();
        
        // Atualizar status a cada 30 segundos
        setInterval(carregarStatus, 30000);
        
        // Permitir Enter no input
        document.getElementById('sonhoInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                interpretar();
            }
        });
    </script>
</body>
</html>
```

---

## 🔄 Fluxo Completo de Integração

### 1. Usuário Informa Sonho
```javascript
// Usuário digita "leão"
const interpretacao = await interpretarSonho('leão');

// Retorna: { animal: "Leão", grupo: 16, numeros: {...} }
```

### 2. Criar Aposta no Seu Sistema
```javascript
// Com os dados do sonho, criar aposta
const aposta = {
    usuario_id: usuarioId,
    numero: interpretacao.dados.numeros.dezena,
    animal: interpretacao.dados.animal,
    valor: 10.0,
    loteria: "PT Rio de Janeiro",
    horario: "11:00"
};

// Salvar aposta no seu banco de dados
await criarAposta(aposta);
```

### 3. Monitorar Resultados
```javascript
// Verificar resultados periodicamente
setInterval(async () => {
    const resultados = await obterResultados();
    
    // Para cada resultado, verificar se há apostas correspondentes
    resultados.resultados.forEach(resultado => {
        liquidarApostas(resultado);
    });
}, 60000); // A cada 1 minuto
```

### 4. Liquidar Apostas
```javascript
async function liquidarApostas(resultado) {
    // Buscar apostas pendentes que correspondem ao resultado
    const apostas = await buscarApostasPendentes({
        numero: resultado.numero,
        animal: resultado.animal,
        loteria: resultado.loteria,
        horario: resultado.horario
    });
    
    // Para cada aposta, verificar se ganhou
    apostas.forEach(aposta => {
        if (aposta.numero === resultado.numero || 
            aposta.animal === resultado.animal) {
            // Aposta ganhou!
            const valorGanho = aposta.valor * aposta.multiplicador;
            
            // Atualizar saldo do usuário
            atualizarSaldo(aposta.usuario_id, valorGanho);
            
            // Marcar aposta como ganhou
            atualizarAposta(aposta.id, {
                status: 'ganhou',
                valor_ganho: valorGanho
            });
        } else {
            // Aposta perdeu
            atualizarAposta(aposta.id, {
                status: 'perdeu'
            });
        }
    });
}
```

---

## 📝 Exemplo com PHP

```php
<?php
// Configuração
$API_LIVRO_SONHOS = 'http://seu-servidor:8082/api/v1';
$API_MONITOR = 'http://seu-servidor:8081/api';

// Função para fazer requisições
function fazerRequisicao($url, $method = 'GET', $data = null) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    
    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
    }
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    return [
        'code' => $httpCode,
        'data' => json_decode($response, true)
    ];
}

// Interpretar sonho
function interpretarSonho($sonho) {
    global $API_LIVRO_SONHOS;
    $result = fazerRequisicao(
        $API_LIVRO_SONHOS . '/interpretar',
        'POST',
        ['sonho' => $sonho]
    );
    
    if ($result['code'] === 200 && $result['data']['sucesso']) {
        return $result['data']['dados'];
    }
    
    return null;
}

// Obter resultados
function obterResultados() {
    global $API_MONITOR;
    $result = fazerRequisicao($API_MONITOR . '/resultados');
    
    if ($result['code'] === 200) {
        return $result['data']['resultados'] ?? [];
    }
    
    return [];
}

// Exemplo de uso
$interpretacao = interpretarSonho('leão');
if ($interpretacao) {
    echo "Animal: " . $interpretacao['animal'] . "\n";
    echo "Grupo: " . $interpretacao['grupo'] . "\n";
}

$resultados = obterResultados();
foreach ($resultados as $resultado) {
    echo "Resultado: " . $resultado['numero'] . " - " . $resultado['animal'] . "\n";
}
?>
```

---

## ✅ Checklist de Integração

- [ ] Configurar URLs das APIs (Livro dos Sonhos e Monitor)
- [ ] Testar conexão com `/api/v1/status` (Livro dos Sonhos)
- [ ] Testar conexão com `/api/status` (Monitor)
- [ ] Implementar função de interpretação de sonhos
- [ ] Implementar função de obtenção de resultados
- [ ] Criar sistema de apostas no seu banco de dados
- [ ] Implementar liquidação automática de apostas
- [ ] Configurar verificação periódica de resultados
- [ ] Testar fluxo completo: Sonho → Aposta → Resultado → Liquidação

---

## 🚀 Iniciar os Servidores

### Terminal 1 - Livro dos Sonhos
```bash
cd "/Volumes/KNUP/pasta sem título"
./iniciar_livro_sonhos.sh
# Ou: source venv_livro_sonhos/bin/activate && python3 app_livro_sonhos.py --port 8082
```

### Terminal 2 - Monitor Deu no Poste
```bash
cd "/Volumes/KNUP/pasta sem título"
source venv_livro_sonhos/bin/activate  # ou o venv apropriado
python3 app_deunoposte.py --port 8081 --monitor --intervalo 300
```

---

## 📞 Suporte

Se tiver problemas:
1. Verifique se ambos os servidores estão rodando
2. Teste os endpoints de status de cada API
3. Verifique o console do navegador para erros
4. Confirme que as URLs estão corretas
