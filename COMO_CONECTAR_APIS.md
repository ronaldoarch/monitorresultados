# 🔌 Como Conectar as APIs no Seu Site

Guia prático para integrar o Livro dos Sonhos e Monitor Deu no Poste no seu site.

## 🌐 URLs das APIs

### Livro dos Sonhos
```
https://esoo4kg0sk0w08k4g00c0c8w.agenciamidas.com/api/v1
```

### Monitor Deu no Poste
```
https://ok8c08cc8cw0cksg0w4c4ocw.agenciamidas.com/api
```

---

## 📖 Livro dos Sonhos - Endpoints

### 1. Interpretar Sonho
**POST** `/api/v1/interpretar`

```javascript
const API_LIVRO_SONHOS = 'https://esoo4kg0sk0w08k4g00c0c8w.agenciamidas.com/api/v1';

async function interpretarSonho(sonho) {
    const response = await fetch(`${API_LIVRO_SONHOS}/interpretar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sonho: sonho })
    });
    
    const data = await response.json();
    
    if (data.sucesso && data.encontrado) {
        return data.dados;
    }
    
    return null;
}

// Uso
const resultado = await interpretarSonho('leão');
console.log('Animal:', resultado.animal);
console.log('Grupo:', resultado.grupo);
console.log('Números:', resultado.numeros);
```

### 2. Sonhos Populares
**GET** `/api/v1/sonhos/populares`

```javascript
async function carregarSonhosPopulares() {
    const response = await fetch(`${API_LIVRO_SONHOS}/sonhos/populares?limite=30`);
    const data = await response.json();
    return data.sonhos || [];
}
```

### 3. Status
**GET** `/api/v1/status`

```javascript
async function verificarStatusLivroSonhos() {
    const response = await fetch(`${API_LIVRO_SONHOS}/status`);
    return await response.json();
}
```

---

## 🎰 Monitor Deu no Poste - Endpoints

### 1. Obter Resultados
**GET** `/api/resultados`

```javascript
const API_MONITOR = 'https://ok8c08cc8cw0cksg0w4c4ocw.agenciamidas.com/api';

async function obterResultados() {
    const response = await fetch(`${API_MONITOR}/resultados`);
    const data = await response.json();
    return data.resultados || [];
}
```

### 2. Status do Monitor
**GET** `/api/status`

```javascript
async function obterStatusMonitor() {
    const response = await fetch(`${API_MONITOR}/status`);
    return await response.json();
}
```

### 3. Forçar Verificação
**POST** `/api/verificar-agora`

```javascript
async function verificarAgora() {
    const response = await fetch(`${API_MONITOR}/verificar-agora`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}
```

---

## 💻 Exemplo Completo de Integração

### HTML + JavaScript

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Integração APIs - Livro dos Sonhos + Monitor</title>
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
        
        <!-- MONITOR -->
        <div class="card">
            <h2>🎰 Resultados</h2>
            <button onclick="carregarResultados()">Carregar Resultados</button>
            <button onclick="verificarAgora()">Verificar Agora</button>
            <div id="resultadosMonitor" class="resultado"></div>
        </div>
    </div>
    
    <script>
        // ============================================
        // CONFIGURAÇÃO DAS APIs
        // ============================================
        const API_LIVRO_SONHOS = 'https://esoo4kg0sk0w08k4g00c0c8w.agenciamidas.com/api/v1';
        const API_MONITOR = 'https://ok8c08cc8cw0cksg0w4c4ocw.agenciamidas.com/api';
        
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
                    headers: {
                        'Content-Type': 'application/json'
                    },
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
                        <p>Dezena: ${dados.numeros.dezena}</p>
                        <p>Centena: ${dados.numeros.centena}</p>
                        <p>Milhar: ${dados.numeros.milhar}</p>
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
        async function carregarResultados() {
            const resultadosDiv = document.getElementById('resultadosMonitor');
            resultadosDiv.innerHTML = 'Carregando...';
            
            try {
                const response = await fetch(`${API_MONITOR}/resultados`);
                const data = await response.json();
                
                if (data.resultados && data.resultados.length > 0) {
                    let html = `<h3>📊 ${data.total_resultados || 0} Resultados</h3>`;
                    
                    // Mostrar últimos 10 resultados
                    data.resultados.slice(0, 10).forEach(r => {
                        html += `
                            <div style="margin: 10px 0; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 5px;">
                                <strong>${r.numero}</strong> - ${r.animal} (${r.loteria || 'N/A'})
                            </div>
                        `;
                    });
                    
                    resultadosDiv.innerHTML = html;
                } else {
                    resultadosDiv.innerHTML = '<p>Nenhum resultado encontrado.</p>';
                }
            } catch (error) {
                resultadosDiv.innerHTML = '<p style="color: #ef4444;">Erro ao carregar resultados</p>';
                console.error('Erro:', error);
            }
        }
        
        async function verificarAgora() {
            const resultadosDiv = document.getElementById('resultadosMonitor');
            resultadosDiv.innerHTML = 'Verificando...';
            
            try {
                const response = await fetch(`${API_MONITOR}/verificar-agora`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const data = await response.json();
                
                if (data.sucesso) {
                    resultadosDiv.innerHTML = `<p>✅ ${data.mensagem}</p>`;
                    setTimeout(carregarResultados, 2000);
                } else {
                    resultadosDiv.innerHTML = `<p style="color: #ef4444;">Erro: ${data.erro || data.mensagem}</p>`;
                }
            } catch (error) {
                resultadosDiv.innerHTML = '<p style="color: #ef4444;">Erro ao verificar</p>';
                console.error('Erro:', error);
            }
        }
        
        // Carregar resultados ao iniciar
        carregarResultados();
    </script>
</body>
</html>
```

---

## 🔄 Fluxo Completo de Integração

### 1. Usuário Informa Sonho → Criar Aposta

```javascript
// Passo 1: Interpretar sonho
const interpretacao = await interpretarSonho('leão');

if (interpretacao) {
    // Passo 2: Criar aposta no seu sistema
    const aposta = {
        usuario_id: usuarioId,
        numero: interpretacao.numeros.dezena,
        animal: interpretacao.animal,
        grupo: interpretacao.grupo,
        valor: 10.0,
        loteria: "PT Rio de Janeiro",
        horario: "11:00"
    };
    
    // Salvar no seu banco de dados
    await criarAposta(aposta);
}
```

### 2. Monitorar Resultados → Liquidar Apostas

```javascript
// Verificar resultados periodicamente
setInterval(async () => {
    const resultados = await obterResultados();
    
    // Para cada resultado, verificar apostas
    resultados.forEach(resultado => {
        liquidarApostas(resultado);
    });
}, 60000); // A cada 1 minuto

async function liquidarApostas(resultado) {
    // Buscar apostas pendentes que correspondem
    const apostas = await buscarApostasPendentes({
        numero: resultado.numero,
        animal: resultado.animal,
        loteria: resultado.loteria
    });
    
    // Liquidar cada aposta
    apostas.forEach(aposta => {
        if (aposta.numero === resultado.numero || 
            aposta.animal === resultado.animal) {
            // Ganhou!
            const valorGanho = aposta.valor * aposta.multiplicador;
            atualizarSaldo(aposta.usuario_id, valorGanho);
            atualizarAposta(aposta.id, {
                status: 'ganhou',
                valor_ganho: valorGanho
            });
        } else {
            // Perdeu
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
$API_LIVRO_SONHOS = 'https://esoo4kg0sk0w08k4g00c0c8w.agenciamidas.com/api/v1';
$API_MONITOR = 'https://ok8c08cc8cw0cksg0w4c4ocw.agenciamidas.com/api';

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
    echo "Dezena: " . $interpretacao['numeros']['dezena'] . "\n";
}

$resultados = obterResultados();
foreach ($resultados as $resultado) {
    echo "Resultado: " . $resultado['numero'] . " - " . $resultado['animal'] . "\n";
}
?>
```

---

## 🔒 CORS

Ambas as APIs estão configuradas com CORS habilitado, então você pode fazer requisições diretamente do navegador sem problemas.

---

## ✅ Teste Rápido

### Testar Livro dos Sonhos:
```bash
curl -X POST https://esoo4kg0sk0w08k4g00c0c8w.agenciamidas.com/api/v1/interpretar \
  -H "Content-Type: application/json" \
  -d '{"sonho": "leão"}'
```

### Testar Monitor:
```bash
curl https://ok8c08cc8cw0cksg0w4c4ocw.agenciamidas.com/api/resultados
```

---

## 🎯 Próximos Passos

1. **Integrar no seu site**: Use os exemplos acima
2. **Criar sistema de apostas**: Use os dados do Livro dos Sonhos
3. **Liquidar automaticamente**: Use os resultados do Monitor
4. **Testar**: Verifique se tudo está funcionando

Tudo pronto para integração! 🚀
