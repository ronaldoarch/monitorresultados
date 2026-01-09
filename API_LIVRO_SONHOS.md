# 📖 API Livro dos Sonhos - Documentação de Integração

API REST para integração do sistema de interpretação de sonhos no seu site.

## 🎨 Design

O sistema utiliza a paleta de cores do **Barão do Bicho**:
- **Verde Escuro**: `#0d4f1c` (background)
- **Verde Claro**: `#4ade80` (destaques e botões)
- **Dourado**: `#fbbf24` (accent e números)
- **Branco**: `#ffffff` (texto)

## 🔌 Endpoints Disponíveis

### Base URL
```
http://seu-servidor:8082/api/v1
```

---

## 📡 Endpoints

### 1. Interpretar Sonho

**POST** `/api/v1/interpretar`

Interpreta um sonho e retorna palpites completos.

#### Request
```json
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

#### Exemplo de Uso (JavaScript)
```javascript
async function interpretarSonho(sonho) {
  const response = await fetch('http://seu-servidor:8082/api/v1/interpretar', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ sonho: sonho })
  });
  
  const data = await response.json();
  
  if (data.sucesso && data.encontrado) {
    console.log('Animal:', data.dados.animal);
    console.log('Grupo:', data.dados.grupo);
    console.log('Números:', data.dados.numeros);
  }
}
```

---

### 2. Listar Sonhos Populares

**GET** `/api/v1/sonhos/populares`

Retorna lista de sonhos populares do dicionário.

#### Query Parameters
- `limite` (opcional): Número máximo de sonhos (padrão: 50)

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
    },
    {
      "sonho": "dinheiro",
      "animal": "Porco",
      "grupo": 18,
      "significado": "Prosperidade financeira"
    }
  ]
}
```

#### Exemplo de Uso (JavaScript)
```javascript
async function carregarSonhosPopulares() {
  const response = await fetch('http://seu-servidor:8082/api/v1/sonhos/populares?limite=30');
  const data = await response.json();
  
  if (data.sucesso) {
    data.sonhos.forEach(sonho => {
      console.log(`${sonho.sonho} -> ${sonho.animal} (Grupo ${sonho.grupo})`);
    });
  }
}
```

---

### 3. Buscar Sonho Específico

**GET** `/api/v1/sonhos/buscar`

Busca um sonho específico no dicionário.

#### Query Parameters
- `sonho` (obrigatório): O sonho a buscar

#### Request
```
GET /api/v1/sonhos/buscar?sonho=leão
```

#### Response (Encontrado)
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

#### Response (Não Encontrado)
```json
{
  "sucesso": false,
  "encontrado": false,
  "mensagem": "Sonho não encontrado"
}
```

---

### 4. Status da API

**GET** `/api/v1/status`

Verifica o status da API e lista endpoints disponíveis.

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

## 🔧 Exemplo de Integração Completa

### HTML + JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>Livro dos Sonhos - Integração</title>
    <style>
        body {
            background: #0d4f1c;
            color: white;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        input, textarea {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 2px solid #4ade80;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }
        button {
            background: #4ade80;
            color: #0d4f1c;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-weight: bold;
            cursor: pointer;
        }
        .resultado {
            margin-top: 20px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            border: 2px solid #4ade80;
        }
        .numero {
            display: inline-block;
            padding: 10px 20px;
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
    <div class="container">
        <h1>📖 Livro dos Sonhos</h1>
        
        <input type="text" id="sonhoInput" placeholder="Digite seu sonho...">
        <button onclick="interpretar()">Interpretar</button>
        
        <div id="resultado" class="resultado" style="display: none;"></div>
    </div>
    
    <script>
        const API_BASE = 'http://seu-servidor:8082/api/v1';
        
        async function interpretar() {
            const sonho = document.getElementById('sonhoInput').value.trim();
            
            if (!sonho) {
                alert('Por favor, digite um sonho!');
                return;
            }
            
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
                    exibirResultado(data.dados);
                } else {
                    alert(data.mensagem || 'Sonho não encontrado');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Erro ao interpretar sonho');
            }
        }
        
        function exibirResultado(dados) {
            const resultadoDiv = document.getElementById('resultado');
            resultadoDiv.style.display = 'block';
            
            resultadoDiv.innerHTML = `
                <h2>🎯 ${dados.animal}</h2>
                <p><strong>Grupo:</strong> ${dados.grupo}</p>
                <p><strong>Significado:</strong> ${dados.significado}</p>
                
                <h3>Números Sugeridos:</h3>
                <div class="numero">Grupo: ${dados.numeros.grupo}</div>
                <div class="numero">Dezena: ${dados.numeros.dezena}</div>
                <div class="numero">Centena: ${dados.numeros.centena}</div>
                <div class="numero">Milhar: ${dados.numeros.milhar}</div>
            `;
        }
    </script>
</body>
</html>
```

---

## 🎨 Cores para Integração

Use estas cores no seu site para manter consistência visual:

```css
/* Cores Barão do Bicho */
--verde-escuro: #0d4f1c;
--verde-claro: #4ade80;
--dourado: #fbbf24;
--branco: #ffffff;
--preto: #000000;
```

---

## ⚠️ Tratamento de Erros

Todos os endpoints retornam status HTTP apropriados:

- `200` - Sucesso
- `400` - Erro de validação (dados faltando)
- `500` - Erro interno do servidor

Sempre verifique o campo `sucesso` na resposta:

```javascript
if (data.sucesso) {
    // Processar dados
} else {
    // Tratar erro
    console.error(data.erro || data.mensagem);
}
```

---

## 🔒 CORS

A API está configurada com CORS habilitado. Se precisar restringir, configure no servidor Flask.

---

## 📝 Notas

- Todos os endpoints suportam CORS
- As respostas são em JSON
- Timestamps estão em formato ISO 8601
- A API é stateless (sem sessões)

---

## 🚀 Iniciar Servidor

```bash
./iniciar_livro_sonhos.sh
```

Ou manualmente:
```bash
source venv_livro_sonhos/bin/activate
python3 app_livro_sonhos.py --port 8082
```
