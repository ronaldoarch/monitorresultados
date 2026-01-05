# 📍 API - Resultados por Estado

## 🎯 Novos Endpoints

A API agora suporta agrupamento e filtragem de resultados por estado!

---

## 📋 Endpoints Disponíveis

### 1. `/api/resultados` (Atualizado)
Retorna todos os resultados, agora **incluindo o campo `estado`** em cada resultado.

**Exemplo de resposta:**
```json
{
  "resultados": [
    {
      "numero": "9498",
      "animal": "Vaca",
      "loteria": "Look Goiás",
      "estado": "GO",
      "horario": "11:20",
      "posicao": 1,
      "colocacao": "1°",
      "timestamp": "2026-01-05T17:00:00",
      "data_extração": "05/01/2026"
    },
    {
      "numero": "4369",
      "animal": "Porco",
      "loteria": "PT Rio de Janeiro",
      "estado": "RJ",
      "horario": "14:30",
      "posicao": 1,
      "colocacao": "1°",
      "timestamp": "2026-01-05T17:00:00",
      "data_extração": "05/01/2026"
    }
  ],
  "ultima_verificacao": "2026-01-05T17:00:00"
}
```

---

### 2. `/api/resultados/por-estado` ⭐ NOVO
Retorna resultados **agrupados por estado**.

**Exemplo de resposta:**
```json
{
  "por_estado": {
    "RJ": [
      {
        "numero": "4369",
        "animal": "Porco",
        "loteria": "PT Rio de Janeiro",
        "estado": "RJ",
        "horario": "14:30",
        "posicao": 1,
        "colocacao": "1°"
      }
    ],
    "GO": [
      {
        "numero": "9498",
        "animal": "Vaca",
        "loteria": "Look Goiás",
        "estado": "GO",
        "horario": "11:20",
        "posicao": 1,
        "colocacao": "1°"
      }
    ],
    "SP": [
      {
        "numero": "3364",
        "animal": "Leão",
        "loteria": "PT-SP/Bandeirantes",
        "estado": "SP",
        "horario": "13:40",
        "posicao": 1,
        "colocacao": "1°"
      }
    ]
  },
  "estatisticas": {
    "RJ": 45,
    "GO": 36,
    "SP": 48,
    "BA": 12,
    "PB": 10,
    "CE": 10,
    "BR": 140
  },
  "total_resultados": 301,
  "total_estados": 7,
  "ultima_verificacao": "2026-01-05T17:00:00"
}
```

---

### 3. `/api/resultados/estado/<estado>` ⭐ NOVO
Retorna resultados de um **estado específico**.

**Exemplos:**
- `/api/resultados/estado/RJ` → Resultados do Rio de Janeiro
- `/api/resultados/estado/GO` → Resultados de Goiás
- `/api/resultados/estado/SP` → Resultados de São Paulo
- `/api/resultados/estado/BA` → Resultados da Bahia
- `/api/resultados/estado/BR` → Resultados nacionais (Loteria Nacional, Federal)

**Exemplo de resposta (`/api/resultados/estado/GO`):**
```json
{
  "estado": "GO",
  "resultados": [
    {
      "numero": "9498",
      "animal": "Vaca",
      "loteria": "Look Goiás",
      "estado": "GO",
      "horario": "11:20",
      "posicao": 1,
      "colocacao": "1°"
    },
    {
      "numero": "9481",
      "animal": "Touro",
      "loteria": "Look Goiás",
      "estado": "GO",
      "horario": "14:20",
      "posicao": 1,
      "colocacao": "1°"
    }
  ],
  "por_loteria": {
    "Look Goiás_11:20": [
      {
        "numero": "9498",
        "animal": "Vaca",
        "loteria": "Look Goiás",
        "estado": "GO",
        "horario": "11:20",
        "posicao": 1,
        "colocacao": "1°"
      }
    ],
    "Look Goiás_14:20": [
      {
        "numero": "9481",
        "animal": "Touro",
        "loteria": "Look Goiás",
        "estado": "GO",
        "horario": "14:20",
        "posicao": 1,
        "colocacao": "1°"
      }
    ]
  },
  "total": 36,
  "loterias": 3
}
```

---

## 🗺️ Mapeamento de Estados

O sistema identifica automaticamente o estado baseado no nome da loteria:

| Loteria | Estado |
|---------|--------|
| PT Rio de Janeiro | RJ |
| PT-SP/Bandeirantes | SP |
| PT Bahia | BA |
| PT Paraiba/Lotep | PB |
| Look Goiás | GO |
| Lotece | CE |
| Maluca Bahia | BA |
| Loteria Nacional | BR |
| Loteria Federal | BR |

**Estados suportados:**
- `RJ` - Rio de Janeiro
- `SP` - São Paulo
- `GO` - Goiás
- `BA` - Bahia
- `PB` - Paraíba
- `CE` - Ceará
- `MG` - Minas Gerais
- `PR` - Paraná
- `SC` - Santa Catarina
- `RS` - Rio Grande do Sul
- `BR` - Nacional (Loteria Nacional, Federal)

---

## 💻 Exemplos de Uso

### JavaScript (Frontend)

```javascript
// Buscar todos os resultados por estado
fetch('http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-estado')
  .then(res => res.json())
  .then(data => {
    console.log('Resultados por estado:', data.por_estado);
    console.log('Estatísticas:', data.estatisticas);
    
    // Mostrar resultados do RJ
    const resultadosRJ = data.por_estado.RJ || [];
    resultadosRJ.forEach(r => {
      console.log(`${r.colocacao} - ${r.numero} ${r.animal} (${r.loteria} ${r.horario})`);
    });
  });

// Buscar resultados de um estado específico
fetch('http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/GO')
  .then(res => res.json())
  .then(data => {
    console.log(`Total de resultados em ${data.estado}: ${data.total}`);
    data.resultados.forEach(r => {
      console.log(`${r.colocacao} - ${r.numero} ${r.animal}`);
    });
  });
```

### Python

```python
import requests

# Buscar resultados por estado
response = requests.get('http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-estado')
data = response.json()

# Mostrar estatísticas
print("Estatísticas por estado:")
for estado, total in data['estatisticas'].items():
    print(f"  {estado}: {total} resultados")

# Buscar resultados do RJ
rj_data = requests.get('http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/RJ').json()
print(f"\nResultados do RJ: {rj_data['total']}")
for r in rj_data['resultados']:
    print(f"  {r['colocacao']} - {r['numero']} {r['animal']} ({r['loteria']} {r['horario']})")
```

### cURL

```bash
# Todos os resultados agrupados por estado
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-estado

# Resultados do Rio de Janeiro
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/RJ

# Resultados de Goiás
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/GO

# Resultados nacionais
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/BR
```

---

## 🎨 Exemplo de Interface

```html
<!DOCTYPE html>
<html>
<head>
    <title>Resultados por Estado</title>
</head>
<body>
    <h1>Resultados por Estado</h1>
    
    <select id="estadoSelect">
        <option value="">Todos os estados</option>
        <option value="RJ">Rio de Janeiro</option>
        <option value="SP">São Paulo</option>
        <option value="GO">Goiás</option>
        <option value="BA">Bahia</option>
        <option value="PB">Paraíba</option>
        <option value="CE">Ceará</option>
        <option value="BR">Nacional</option>
    </select>
    
    <div id="resultados"></div>
    
    <script>
        const estadoSelect = document.getElementById('estadoSelect');
        const resultadosDiv = document.getElementById('resultados');
        
        estadoSelect.addEventListener('change', async () => {
            const estado = estadoSelect.value;
            
            if (!estado) {
                // Mostrar todos agrupados
                const res = await fetch('/api/resultados/por-estado');
                const data = await res.json();
                
                resultadosDiv.innerHTML = '<h2>Resultados por Estado</h2>';
                for (const [estado, resultados] of Object.entries(data.por_estado)) {
                    resultadosDiv.innerHTML += `<h3>${estado} (${resultados.length})</h3>`;
                    resultados.forEach(r => {
                        resultadosDiv.innerHTML += `<p>${r.colocacao} - ${r.numero} ${r.animal} (${r.loteria} ${r.horario})</p>`;
                    });
                }
            } else {
                // Mostrar apenas do estado selecionado
                const res = await fetch(`/api/resultados/estado/${estado}`);
                const data = await res.json();
                
                resultadosDiv.innerHTML = `<h2>Resultados de ${data.estado} (${data.total})</h2>`;
                data.resultados.forEach(r => {
                    resultadosDiv.innerHTML += `<p>${r.colocacao} - ${r.numero} ${r.animal} (${r.loteria} ${r.horario})</p>`;
                });
            }
        });
        
        // Carregar inicialmente
        estadoSelect.dispatchEvent(new Event('change'));
    </script>
</body>
</html>
```

---

## ✅ Checklist

- [x] Campo `estado` adicionado a todos os resultados
- [x] Endpoint `/api/resultados/por-estado` criado
- [x] Endpoint `/api/resultados/estado/<estado>` criado
- [x] Mapeamento automático de loterias para estados
- [x] Suporte a estados: RJ, SP, GO, BA, PB, CE, MG, PR, SC, RS, BR

---

✅ **API atualizada e pronta para uso!**

