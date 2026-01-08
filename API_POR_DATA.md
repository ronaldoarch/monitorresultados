# 📅 API - Resultados por Data

## 🎯 Novos Endpoints para Filtrar por Data

A API agora suporta agrupamento e filtragem de resultados por data!

---

## 📋 Endpoints Disponíveis

### 1. `/api/resultados/por-data` ⭐ NOVO
Retorna resultados **agrupados por data**.

**Exemplo de resposta:**
```json
{
  "por_data": {
    "05/01/2026": [
      {
        "numero": "9498",
        "animal": "Vaca",
        "loteria": "Look Goiás",
        "estado": "GO",
        "horario": "11:20",
        "posicao": 1,
        "colocacao": "1°",
        "data_extração": "05/01/2026"
      }
    ],
    "04/01/2026": [
      {
        "numero": "4369",
        "animal": "Porco",
        "loteria": "PT Rio de Janeiro",
        "estado": "RJ",
        "horario": "14:30",
        "posicao": 1,
        "colocacao": "1°",
        "data_extração": "04/01/2026"
      }
    ]
  },
  "estatisticas": {
    "05/01/2026": 376,
    "04/01/2026": 250
  },
  "total_resultados": 626,
  "total_datas": 2,
  "ultima_verificacao": "2026-01-05T19:40:00"
}
```

---

### 2. `/api/resultados/data/<data>` ⭐ NOVO
Retorna resultados de uma **data específica**.

**Formatos aceitos:**
- `DD-MM-YYYY` → `/api/resultados/data/05-01-2026`
- `DD/MM/YYYY` → `/api/resultados/data/05/01/2026`

**Exemplo de resposta (`/api/resultados/data/05-01-2026`):**
```json
{
  "data": "05/01/2026",
  "resultados": [
    {
      "numero": "9498",
      "animal": "Vaca",
      "loteria": "Look Goiás",
      "estado": "GO",
      "horario": "11:20",
      "posicao": 1,
      "colocacao": "1°",
      "data_extração": "05/01/2026"
    }
  ],
  "por_estado": {
    "GO": [...],
    "RJ": [...],
    "SP": [...]
  },
  "por_loteria": {
    "Look Goiás_11:20": [...],
    "PT Rio de Janeiro_14:30": [...]
  },
  "total": 376,
  "estados": 8,
  "loterias": 36
}
```

---

### 3. `/api/resultados/estado/<estado>/data/<data>` ⭐ NOVO
Retorna resultados de um **estado e data específicos**.

**Exemplos:**
- `/api/resultados/estado/RJ/data/05-01-2026` → Rio de Janeiro em 05/01/2026
- `/api/resultados/estado/GO/data/05/01/2026` → Goiás em 05/01/2026
- `/api/resultados/estado/SP/data/05-01-2026` → São Paulo em 05/01/2026

**Exemplo de resposta:**
```json
{
  "estado": "RJ",
  "data": "05/01/2026",
  "resultados": [
    {
      "numero": "4369",
      "animal": "Porco",
      "loteria": "PT Rio de Janeiro",
      "estado": "RJ",
      "horario": "14:30",
      "posicao": 1,
      "colocacao": "1°",
      "data_extração": "05/01/2026"
    }
  ],
  "por_loteria": {
    "PT Rio de Janeiro_14:30": [...],
    "Maluquinha RJ_16h": [...]
  },
  "total": 48,
  "loterias": 3
}
```

---

## 💻 Exemplos de Uso

### JavaScript (Frontend)

```javascript
// Buscar resultados agrupados por data
fetch('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-data')
  .then(res => res.json())
  .then(data => {
    console.log('Resultados por data:', data.por_data);
    console.log('Estatísticas:', data.estatisticas);
    
    // Mostrar resultados de hoje
    const hoje = new Date().toLocaleDateString('pt-BR');
    const resultadosHoje = data.por_data[hoje] || [];
    console.log(`Resultados de hoje: ${resultadosHoje.length}`);
  });

// Buscar resultados de uma data específica
const data = '05-01-2026'; // ou '05/01/2026'
fetch(`https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/data/${data}`)
  .then(res => res.json())
  .then(data => {
    console.log(`Total de resultados em ${data.data}: ${data.total}`);
    data.resultados.forEach(r => {
      console.log(`${r.colocacao} - ${r.numero} ${r.animal}`);
    });
  });

// Buscar resultados de um estado em uma data específica
const estado = 'RJ';
const data = '05-01-2026';
fetch(`https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${estado}/data/${data}`)
  .then(res => res.json())
  .then(data => {
    console.log(`RJ em ${data.data}: ${data.total} resultados`);
  });
```

### Python

```python
import requests
from datetime import datetime

# Buscar resultados por data
response = requests.get('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-data')
data = response.json()

# Mostrar estatísticas
print("Resultados por data:")
for data_str, total in data['estatisticas'].items():
    print(f"  {data_str}: {total} resultados")

# Buscar resultados de uma data específica
hoje = datetime.now().strftime('%d-%m-%Y')
response = requests.get(f'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/data/{hoje}')
data_hoje = response.json()

print(f"\nResultados de hoje ({data_hoje['data']}): {data_hoje['total']}")
for r in data_hoje['resultados']:
    print(f"  {r['colocacao']} - {r['numero']} {r['animal']} ({r['loteria']} {r['horario']})")
```

### cURL

```bash
# Todos os resultados agrupados por data
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-data

# Resultados de uma data específica
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/data/05-01-2026

# Resultados do RJ em uma data específica
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/RJ/data/05-01-2026

# Resultados de Goiás em uma data específica
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/GO/data/05/01/2026
```

---

## 🎨 Exemplo de Interface com Filtro por Data

```html
<!DOCTYPE html>
<html>
<head>
    <title>Resultados por Data</title>
</head>
<body>
    <h1>Resultados</h1>
    
    <div>
        <label>Data:</label>
        <input type="date" id="filtro-data" onchange="carregarResultados()">
    </div>
    
    <div>
        <label>Estado:</label>
        <select id="filtro-estado" onchange="carregarResultados()">
            <option value="">Todos</option>
            <option value="RJ">Rio de Janeiro</option>
            <option value="SP">São Paulo</option>
            <option value="GO">Goiás</option>
        </select>
    </div>
    
    <div id="resultados"></div>
    
    <script>
        function formatarDataParaAPI(data) {
            // Converter YYYY-MM-DD para DD-MM-YYYY
            const partes = data.split('-');
            return `${partes[2]}-${partes[1]}-${partes[0]}`;
        }
        
        async function carregarResultados() {
            const dataInput = document.getElementById('filtro-data').value;
            const estado = document.getElementById('filtro-estado').value;
            
            let url = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados';
            
            if (dataInput && estado) {
                const data = formatarDataParaAPI(dataInput);
                url = `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${estado}/data/${data}`;
            } else if (dataInput) {
                const data = formatarDataParaAPI(dataInput);
                url = `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/data/${data}`;
            } else if (estado) {
                url = `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${estado}`;
            }
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                
                let html = `<h2>${data.total || 0} resultados</h2>`;
                
                if (data.por_loteria) {
                    Object.entries(data.por_loteria).forEach(([chave, grupo]) => {
                        html += `<h3>${chave}</h3>`;
                        grupo.forEach(r => {
                            html += `<p>${r.colocacao} - ${r.numero} ${r.animal}</p>`;
                        });
                    });
                } else if (data.resultados) {
                    data.resultados.forEach(r => {
                        html += `<p>${r.colocacao} - ${r.numero} ${r.animal} (${r.loteria} ${r.horario})</p>`;
                    });
                }
                
                document.getElementById('resultados').innerHTML = html;
            } catch (error) {
                console.error('Erro:', error);
            }
        }
        
        // Definir data de hoje por padrão
        document.getElementById('filtro-data').valueAsDate = new Date();
        carregarResultados();
    </script>
</body>
</html>
```

---

## 📊 Combinações de Filtros Disponíveis

| Endpoint | Descrição |
|----------|-----------|
| `/api/resultados` | Todos os resultados |
| `/api/resultados/por-estado` | Agrupados por estado |
| `/api/resultados/por-data` | Agrupados por data |
| `/api/resultados/estado/<estado>` | Filtrado por estado |
| `/api/resultados/data/<data>` | Filtrado por data |
| `/api/resultados/estado/<estado>/data/<data>` | Filtrado por estado E data |

---

## ✅ Checklist

- [x] Endpoint `/api/resultados/por-data` criado
- [x] Endpoint `/api/resultados/data/<data>` criado
- [x] Endpoint `/api/resultados/estado/<estado>/data/<data>` criado
- [x] Suporte a formatos DD-MM-YYYY e DD/MM/YYYY
- [x] Extração automática de data de `data_extração` ou `timestamp`

---

✅ **API atualizada com filtros por data!**

