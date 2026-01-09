# 🔌 Guia Completo de Integração via API - Livro dos Sonhos

## 📋 Visão Geral

Este guia mostra como integrar o sistema do Livro dos Sonhos no seu site usando a API REST.

## 🌐 Base URL

```
http://seu-servidor:8082/api/v1
```

Ou se estiver rodando localmente:
```
http://localhost:8082/api/v1
```

---

## 📡 Endpoints Disponíveis

### 1. Interpretar Sonho

**POST** `/api/v1/interpretar`

Interpreta um sonho e retorna palpites completos.

#### Request
```javascript
POST /api/v1/interpretar
Content-Type: application/json

{
  "sonho": "leão"
}
```

#### Response (Sucesso)
```json
{
  "sucesso": true,
  "encontrado": true,
  "dados": {
    "sonho": "leão",
    "animal": "Leão",
    "grupo": 16,
    "significado": "Poder e liderança",
    "numeros": {
      "grupo": 16,
      "dezena": "61",
      "centena": "060",
      "milhar": "1500"
    },
    "sugestoes": {
      "dias": [
        {
          "data": "15/01/2024",
          "dia_semana": "Monday",
          "prioridade": "alta"
        }
      ],
      "horarios": [
        {
          "horario": "09:00",
          "prioridade": "alta"
        }
      ]
    }
  }
}
```

#### Response (Não Encontrado)
```json
{
  "sucesso": false,
  "encontrado": false,
  "mensagem": "Sonho não encontrado no dicionário...",
  "sugestao": "Tente buscar por palavras-chave..."
}
```

---

### 2. Listar Sonhos Populares

**GET** `/api/v1/sonhos/populares`

#### Request
```
GET /api/v1/sonhos/populares?limite=30
```

#### Response
```json
{
  "sucesso": true,
  "total": 30,
  "sonhos": [
    {
      "sonho": "leão",
      "animal": "Leão",
      "grupo": 16,
      "significado": "Poder e liderança"
    }
  ]
}
```

---

### 3. Buscar Sonho Específico

**GET** `/api/v1/sonhos/buscar`

#### Request
```
GET /api/v1/sonhos/buscar?sonho=leão
```

#### Response
```json
{
  "sucesso": true,
  "encontrado": true,
  "dados": {
    "animal": "Leão",
    "grupo": 16,
    "numeros": [61, 62, 63, 64],
    "significado": "Poder e liderança"
  }
}
```

---

### 4. Status da API

**GET** `/api/v1/status`

#### Request
```
GET /api/v1/status
```

#### Response
```json
{
  "sucesso": true,
  "status": "online",
  "versao": "1.0.0",
  "endpoints": {
    "interpretar": "/api/v1/interpretar",
    "sonhos_populares": "/api/v1/sonhos/populares",
    "buscar": "/api/v1/sonhos/buscar",
    "status": "/api/v1/status"
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## 💻 Exemplos de Integração

### JavaScript (Vanilla)

```javascript
// Configuração
const API_BASE = 'http://seu-servidor:8082/api/v1';

// Função para interpretar sonho
async function interpretarSonho(sonho) {
    try {
        const response = await fetch(`${API_BASE}/interpretar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sonho: sonho })
        });
        
        const data = await response.json();
        
        if (data.sucesso && data.encontrado) {
            return data.dados;
        } else {
            throw new Error(data.mensagem || 'Sonho não encontrado');
        }
    } catch (error) {
        console.error('Erro:', error);
        throw error;
    }
}

// Uso
interpretarSonho('leão')
    .then(resultado => {
        console.log('Animal:', resultado.animal);
        console.log('Grupo:', resultado.grupo);
        console.log('Números:', resultado.numeros);
    })
    .catch(error => {
        console.error('Erro:', error);
    });
```

---

### jQuery

```javascript
const API_BASE = 'http://seu-servidor:8082/api/v1';

function interpretarSonho(sonho) {
    return $.ajax({
        url: `${API_BASE}/interpretar`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ sonho: sonho })
    });
}

// Uso
interpretarSonho('leão')
    .done(function(data) {
        if (data.sucesso && data.encontrado) {
            console.log('Animal:', data.dados.animal);
            console.log('Grupo:', data.dados.grupo);
        }
    })
    .fail(function(error) {
        console.error('Erro:', error);
    });
```

---

### Axios

```javascript
import axios from 'axios';

const API_BASE = 'http://seu-servidor:8082/api/v1';

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Interpretar sonho
async function interpretarSonho(sonho) {
    try {
        const response = await fetch(`${API_BASE}/interpretar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sonho: sonho })
        });
        
        const data = await response.json();
        
        if (data.sucesso && data.encontrado) {
            return data.dados;
        } else {
            throw new Error(data.mensagem || 'Sonho não encontrado');
        }
    } catch (error) {
        console.error('Erro:', error);
        throw error;
    }
}

// Uso
interpretarSonho('leão')
    .then(resultado => {
        console.log('Animal:', resultado.animal);
        console.log('Grupo:', resultado.grupo);
    })
    .catch(error => {
        console.error('Erro:', error);
    });
```

---

### PHP

```php
<?php
$apiBase = 'http://seu-servidor:8082/api/v1';

function interpretarSonho($sonho) {
    global $apiBase;
    
    $url = $apiBase . '/interpretar';
    
    $data = json_encode(['sonho' => $sonho]);
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Content-Length: ' . strlen($data)
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200) {
        return json_decode($response, true);
    } else {
        return ['sucesso' => false, 'erro' => 'Erro na requisição'];
    }
}

// Uso
$resultado = interpretarSonho('leão');

if ($resultado['sucesso'] && $resultado['encontrado']) {
    $dados = $resultado['dados'];
    echo "Animal: " . $dados['animal'] . "\n";
    echo "Grupo: " . $dados['grupo'] . "\n";
    echo "Dezena: " . $dados['numeros']['dezena'] . "\n";
} else {
    echo "Erro: " . $resultado['mensagem'];
}
?>
```

---

### Python (Requests)

```python
import requests

API_BASE = 'http://seu-servidor:8082/api/v1'

def interpretar_sonho(sonho):
    url = f'{API_BASE}/interpretar'
    
    response = requests.post(
        url,
        json={'sonho': sonho},
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('sucesso') and data.get('encontrado'):
            return data['dados']
        else:
            raise Exception(data.get('mensagem', 'Sonho não encontrado'))
    else:
        raise Exception(f'Erro HTTP {response.status_code}')

# Uso
try:
    resultado = interpretar_sonho('leão')
    print(f"Animal: {resultado['animal']}")
    print(f"Grupo: {resultado['grupo']}")
    print(f"Dezena: {resultado['numeros']['dezena']}")
except Exception as e:
    print(f"Erro: {e}")
```

---

### React

```jsx
import React, { useState } from 'react';

const API_BASE = 'http://seu-servidor:8082/api/v1';

function LivroSonhos() {
    const [sonho, setSonho] = useState('');
    const [resultado, setResultado] = useState(null);
    const [loading, setLoading] = useState(false);
    const [erro, setErro] = useState(null);
    
    const interpretar = async () => {
        if (!sonho.trim()) {
            setErro('Por favor, digite um sonho');
            return;
        }
        
        setLoading(true);
        setErro(null);
        
        try {
            const response = await fetch(`${API_BASE}/interpretar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sonho: sonho })
            });
            
            const data = await response.json();
            
            if (data.sucesso && data.encontrado) {
                setResultado(data.dados);
            } else {
                setErro(data.mensagem || 'Sonho não encontrado');
            }
        } catch (error) {
            setErro('Erro ao conectar com a API');
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            <input
                type="text"
                value={sonho}
                onChange={(e) => setSonho(e.target.value)}
                placeholder="Digite seu sonho..."
            />
            <button onClick={interpretar} disabled={loading}>
                {loading ? 'Interpretando...' : 'Interpretar'}
            </button>
            
            {erro && <div className="erro">{erro}</div>}
            
            {resultado && (
                <div className="resultado">
                    <h3>{resultado.animal}</h3>
                    <p>Grupo: {resultado.grupo}</p>
                    <p>Dezena: {resultado.numeros.dezena}</p>
                    <p>Centena: {resultado.numeros.centena}</p>
                    <p>Milhar: {resultado.numeros.milhar}</p>
                </div>
            )}
        </div>
    );
}

export default LivroSonhos;
```

---

### Vue.js

```vue
<template>
    <div>
        <input 
            v-model="sonho" 
            placeholder="Digite seu sonho..."
            @keyup.enter="interpretar"
        />
        <button @click="interpretar" :disabled="loading">
            {{ loading ? 'Interpretando...' : 'Interpretar' }}
        </button>
        
        <div v-if="erro" class="erro">{{ erro }}</div>
        
        <div v-if="resultado" class="resultado">
            <h3>{{ resultado.animal }}</h3>
            <p>Grupo: {{ resultado.grupo }}</p>
            <p>Dezena: {{ resultado.numeros.dezena }}</p>
            <p>Centena: {{ resultado.numeros.centena }}</p>
            <p>Milhar: {{ resultado.numeros.milhar }}</p>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            sonho: '',
            resultado: null,
            loading: false,
            erro: null,
            apiBase: 'http://seu-servidor:8082/api/v1'
        };
    },
    methods: {
        async interpretar() {
            if (!this.sonho.trim()) {
                this.erro = 'Por favor, digite um sonho';
                return;
            }
            
            this.loading = true;
            this.erro = null;
            
            try {
                const response = await fetch(`${this.apiBase}/interpretar`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ sonho: this.sonho })
                });
                
                const data = await response.json();
                
                if (data.sucesso && data.encontrado) {
                    this.resultado = data.dados;
                } else {
                    this.erro = data.mensagem || 'Sonho não encontrado';
                }
            } catch (error) {
                this.erro = 'Erro ao conectar com a API';
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

---

## 🔒 CORS

A API está configurada com CORS habilitado, permitindo requisições de qualquer origem. Se precisar restringir, edite o arquivo `app_livro_sonhos.py`:

```python
from flask_cors import CORS

# Permitir apenas domínios específicos
CORS(app, resources={r"/api/*": {"origins": ["https://seusite.com", "https://www.seusite.com"]}})
```

---

## ⚠️ Tratamento de Erros

Sempre verifique o campo `sucesso` na resposta:

```javascript
const response = await fetch(`${API_BASE}/interpretar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sonho: 'leão' })
});

const data = await response.json();

if (data.sucesso) {
    // Processar dados
    console.log(data.dados);
} else {
    // Tratar erro
    console.error(data.erro || data.mensagem);
}
```

---

## 📝 Exemplo Completo HTML

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Integração Livro dos Sonhos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        input, button {
            padding: 10px;
            font-size: 16px;
        }
        .resultado {
            margin-top: 20px;
            padding: 20px;
            background: #f0f0f0;
            border-radius: 5px;
        }
        .erro {
            color: red;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <h1>Livro dos Sonhos - API</h1>
    
    <input type="text" id="sonhoInput" placeholder="Digite seu sonho...">
    <button onclick="interpretar()">Interpretar</button>
    
    <div id="resultado"></div>
    
    <script>
        const API_BASE = 'http://seu-servidor:8082/api/v1';
        
        async function interpretar() {
            const sonho = document.getElementById('sonhoInput').value.trim();
            const resultadoDiv = document.getElementById('resultado');
            
            if (!sonho) {
                resultadoDiv.innerHTML = '<div class="erro">Por favor, digite um sonho!</div>';
                return;
            }
            
            resultadoDiv.innerHTML = '<p>Interpretando...</p>';
            
            try {
                const response = await fetch(`${API_BASE}/interpretar`, {
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
                        <div class="resultado">
                            <h2>${dados.animal}</h2>
                            <p><strong>Grupo:</strong> ${dados.grupo}</p>
                            <p><strong>Significado:</strong> ${dados.significado}</p>
                            <h3>Números Sugeridos:</h3>
                            <p>Dezena: ${dados.numeros.dezena}</p>
                            <p>Centena: ${dados.numeros.centena}</p>
                            <p>Milhar: ${dados.numeros.milhar}</p>
                        </div>
                    `;
                } else {
                    resultadoDiv.innerHTML = `<div class="erro">${data.mensagem || 'Sonho não encontrado'}</div>`;
                }
            } catch (error) {
                resultadoDiv.innerHTML = '<div class="erro">Erro ao conectar com a API</div>';
                console.error('Erro:', error);
            }
        }
        
        // Permitir Enter
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

## 🚀 Testando a API

### Com cURL

```bash
# Interpretar sonho
curl -X POST http://seu-servidor:8082/api/v1/interpretar \
  -H "Content-Type: application/json" \
  -d '{"sonho": "leão"}'

# Listar sonhos populares
curl http://seu-servidor:8082/api/v1/sonhos/populares?limite=10

# Status da API
curl http://seu-servidor:8082/api/v1/status
```

### Com Postman

1. Criar nova requisição POST
2. URL: `http://seu-servidor:8082/api/v1/interpretar`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
```json
{
  "sonho": "leão"
}
```

---

## ✅ Checklist de Integração

- [ ] Configurar URL base da API
- [ ] Testar conexão com `/api/v1/status`
- [ ] Implementar função de interpretação
- [ ] Tratar erros adequadamente
- [ ] Exibir resultados na interface
- [ ] Testar com diferentes sonhos
- [ ] Configurar CORS se necessário

---

## 📞 Suporte

Se tiver problemas na integração:
1. Verifique se o servidor está rodando
2. Teste o endpoint `/api/v1/status`
3. Verifique o console do navegador para erros
4. Confirme que a URL da API está correta
