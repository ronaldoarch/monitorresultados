# 📊 API de Resultados Organizados por Tabela e Horário

## 🎯 Endpoint Principal

```
GET /api/resultados/organizados
```

Retorna resultados do Bicho Certo organizados por **tabela (loteria)** e **horário**, com todos os campos necessários.

---

## 📋 Estrutura da Resposta

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
          "timestamp": "2026-01-13T12:30:00"
        },
        {
          "horario": "09:30",
          "animal": "Pavão",
          "numero": "8775",
          "posicao": 2,
          "colocacao": "2°",
          "estado": "RJ",
          "data_extracao": "13/01/2026",
          "timestamp": "2026-01-13T12:30:00"
        }
      ],
      "11:30": [
        {
          "horario": "11:30",
          "animal": "Macaco",
          "numero": "4867",
          "posicao": 1,
          "colocacao": "1°",
          "estado": "RJ",
          "data_extracao": "13/01/2026",
          "timestamp": "2026-01-13T14:30:00"
        }
      ]
    },
    "PT-SP/Bandeirantes": {
      "14:30": [
        {
          "horario": "14:30",
          "animal": "Cavalo",
          "numero": "1234",
          "posicao": 1,
          "colocacao": "1°",
          "estado": "SP",
          "data_extracao": "13/01/2026",
          "timestamp": "2026-01-13T17:30:00"
        }
      ]
    }
  },
  "estatisticas": {
    "total_tabelas": 2,
    "total_horarios": 3,
    "total_resultados": 4
  },
  "ultima_verificacao": "2026-01-13T21:30:00",
  "fonte": "bichocerto.com"
}
```

---

## 🔍 Campos Retornados

Cada resultado contém:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `horario` | string | Horário do sorteio (ex: "09:30", "11:30") |
| `animal` | string | Nome do animal (ex: "Camelo", "Pavão") |
| `numero` | string | Número de 4 dígitos (ex: "4732") |
| `posicao` | integer | Posição do resultado (1, 2, 3, 4, 5, 6, 7) |
| `colocacao` | string | Colocação formatada (ex: "1°", "2°", "3°") |
| `estado` | string | Sigla do estado (RJ, SP, BA, etc.) |
| `data_extracao` | string | Data da extração (DD/MM/YYYY) |
| `timestamp` | string | Timestamp ISO completo |

---

## 💻 Exemplos de Uso

### JavaScript/Fetch

```javascript
// Buscar resultados organizados
async function buscarResultadosOrganizados() {
  try {
    const response = await fetch('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/organizados');
    const data = await response.json();
    
    // Acessar resultados de uma tabela específica
    const ptRio = data.organizados['PT Rio de Janeiro'];
    
    // Acessar resultados de um horário específico
    const resultados0930 = ptRio['09:30'];
    
    // Iterar sobre os resultados
    resultados0930.forEach(resultado => {
      console.log(`${resultado.colocacao} - ${resultado.numero} - ${resultado.animal}`);
    });
    
    return data;
  } catch (error) {
    console.error('Erro ao buscar resultados:', error);
  }
}
```

### Exibir em Tabela HTML

```javascript
function exibirResultadosOrganizados(data) {
  const container = document.getElementById('resultados');
  
  for (const [tabela, horarios] of Object.entries(data.organizados)) {
    const tabelaDiv = document.createElement('div');
    tabelaDiv.className = 'tabela-resultados';
    tabelaDiv.innerHTML = `<h2>${tabela}</h2>`;
    
    for (const [horario, resultados] of Object.entries(horarios)) {
      const horarioDiv = document.createElement('div');
      horarioDiv.className = 'horario-resultados';
      horarioDiv.innerHTML = `<h3>Horário: ${horario}</h3>`;
      
      const tabelaHTML = document.createElement('table');
      tabelaHTML.innerHTML = `
        <thead>
          <tr>
            <th>Posição</th>
            <th>Número</th>
            <th>Animal</th>
            <th>Horário</th>
          </tr>
        </thead>
        <tbody>
          ${resultados.map(r => `
            <tr>
              <td>${r.colocacao}</td>
              <td>${r.numero}</td>
              <td>${r.animal}</td>
              <td>${r.horario}</td>
            </tr>
          `).join('')}
        </tbody>
      `;
      
      horarioDiv.appendChild(tabelaHTML);
      tabelaDiv.appendChild(horarioDiv);
    }
    
    container.appendChild(tabelaDiv);
  }
}
```

### Python/Requests

```python
import requests

# Buscar resultados organizados
response = requests.get('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/organizados')
data = response.json()

# Acessar resultados de uma tabela específica
pt_rio = data['organizados']['PT Rio de Janeiro']

# Acessar resultados de um horário específico
resultados_0930 = pt_rio['09:30']

# Iterar sobre os resultados
for resultado in resultados_0930:
    print(f"{resultado['colocacao']} - {resultado['numero']} - {resultado['animal']}")
```

### cURL

```bash
# Buscar todos os resultados organizados
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/organizados | jq

# Filtrar apenas PT Rio de Janeiro
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/organizados | \
  jq '.organizados["PT Rio de Janeiro"]'

# Filtrar apenas horário 09:30 do PT Rio
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/organizados | \
  jq '.organizados["PT Rio de Janeiro"]["09:30"]'
```

---

## 📊 Estrutura Hierárquica

```
organizados
├── "PT Rio de Janeiro"
│   ├── "09:30"
│   │   ├── [resultado 1°]
│   │   ├── [resultado 2°]
│   │   └── [resultado 3°]
│   ├── "11:30"
│   │   └── [resultados...]
│   └── "14:30"
│       └── [resultados...]
├── "PT-SP/Bandeirantes"
│   └── "14:30"
│       └── [resultados...]
└── "Look Goiás"
    └── [horários...]
```

---

## ✅ Vantagens

1. **Organização clara**: Separado por tabela e horário
2. **Fácil acesso**: Estrutura hierárquica intuitiva
3. **Ordenado**: Resultados ordenados por posição dentro de cada horário
4. **Completo**: Todos os campos necessários incluídos
5. **Estatísticas**: Informações resumidas no topo

---

## 🔄 Atualização

Os resultados são atualizados automaticamente pelo monitor (a cada 60 segundos). Use o campo `ultima_verificacao` para saber quando foi a última atualização.

---

## 📍 URL de Produção

```
https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/organizados
```
