# 📊 Como Acessar o Monitor Deu no Poste

## 🎯 Formas de Acessar

### 1. Via API do Servidor (Recomendado)

O monitor do Deu no Poste está integrado ao `app_vps.py` e seus resultados são combinados com os do Bicho Certo.

#### Endpoint Principal - Todos os Resultados
```bash
GET https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados
```

**Resposta:**
```json
{
  "resultados": [
    {
      "loteria": "Deu no Poste",
      "horario": "9h",
      "numero": "6470",
      "animal": "Porco",
      "grupo": 18,
      "premio": "1º",
      "data": "2026-01-08",
      "fonte": "deunoposte.com.br",
      "timestamp": "2026-01-08T14:00:00"
    },
    ...
  ],
  "total_resultados": 150,
  "ultima_verificacao": "2026-01-08T14:00:00",
  "fontes": {
    "bichocerto": 80,
    "deunoposte": 70
  }
}
```

#### Filtrar Apenas Resultados do Deu no Poste
```bash
# Via JavaScript no navegador ou curl
curl "https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados" | \
  jq '.resultados[] | select(.fonte == "deunoposte.com.br")'
```

#### Verificar Status do Monitor
```bash
GET https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/status
```

**Resposta:**
```json
{
  "monitor_rodando": true,
  "ultima_verificacao": "2026-01-08T14:00:00",
  "monitores": {
    "bichocerto": true,
    "deunoposte": true
  }
}
```

#### Forçar Verificação Imediata
```bash
POST https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/verificar-agora
```

**Resposta:**
```json
{
  "sucesso": true,
  "novos_resultados": 15,
  "mensagem": "Bicho Certo: 5 novos resultados; Deu no Poste: 10 resultados coletados",
  "fontes": {
    "bichocerto": true,
    "deunoposte": true
  }
}
```

### 2. Via Arquivo JSON Direto

O monitor salva os resultados em arquivos JSON:

#### Arquivo Específico do Deu no Poste
```bash
GET https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/resultados_deunoposte.json
```

**Estrutura:**
```json
{
  "ultima_verificacao": "2026-01-08T14:00:00",
  "total_resultados": 70,
  "fonte": "deunoposte.com.br",
  "resultados_por_data": {
    "2026-01-08": {
      "data": "2026-01-08",
      "total": 50,
      "resultados": [...]
    }
  },
  "resultados": [...]
}
```

#### Arquivo Combinado (Bicho Certo + Deu no Poste)
```bash
GET https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/resultados.json
```

### 3. Executar o Monitor Manualmente

Se você tem acesso SSH ao servidor:

```bash
# Executar monitor uma vez
python3 monitor_deunoposte.py

# Ou via app_vps.py (força verificação)
python3 app_vps.py --monitor --intervalo 60
```

### 4. Via Dashboard Web

Acesse o dashboard principal:
```
https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/
```

O dashboard mostra todos os resultados combinados. Você pode filtrar por fonte usando o código JavaScript:

```javascript
// Filtrar apenas Deu no Poste
const resultadosDeuNoPoste = resultados.filter(r => r.fonte === 'deunoposte.com.br');
```

## 🔍 Verificar se o Monitor Está Rodando

### 1. Ver Logs do Servidor

No Coolify ou servidor, verifique os logs:

```bash
# Procure por estas mensagens:
✅ Monitor Deu no Poste carregado com sucesso
🔍 Iniciando monitoramento Deu no Poste...
✅ Deu no Poste: X resultados coletados!
```

### 2. Verificar Status via API

```bash
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/status
```

### 3. Verificar Arquivo JSON

```bash
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/resultados_deunoposte.json
```

Se o arquivo existir e tiver dados recentes, o monitor está funcionando.

## 📋 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/resultados` | GET | Todos os resultados (Bicho Certo + Deu no Poste) |
| `/api/resultados/por-estado` | GET | Resultados agrupados por estado |
| `/api/resultados/por-data` | GET | Resultados agrupados por data |
| `/api/status` | GET | Status do sistema e monitores |
| `/api/verificar-agora` | POST | Força verificação imediata |
| `/api/monitor/start` | POST | Inicia monitor em background |
| `/api/monitor/stop` | POST | Para monitor |
| `/api/monitor/status` | GET | Status do monitor |
| `/resultados.json` | GET | Arquivo JSON combinado |
| `/resultados_deunoposte.json` | GET | Arquivo JSON apenas Deu no Poste |

## 🎨 Exemplo de Uso no Frontend

```javascript
// Buscar apenas resultados do Deu no Poste
async function buscarDeuNoPoste() {
  const response = await fetch('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados');
  const data = await response.json();
  
  // Filtrar apenas Deu no Poste
  const deuNoPoste = data.resultados.filter(r => r.fonte === 'deunoposte.com.br');
  
  console.log(`Total: ${deuNoPoste.length} resultados do Deu no Poste`);
  return deuNoPoste;
}

// Agrupar por loteria
function agruparPorLoteria(resultados) {
  const agrupados = {};
  resultados.forEach(r => {
    if (!agrupados[r.loteria]) {
      agrupados[r.loteria] = [];
    }
    agrupados[r.loteria].push(r);
  });
  return agrupados;
}
```

## 🚀 Iniciar Monitor Automaticamente

O monitor já está configurado para iniciar automaticamente quando o servidor inicia (se usar `--monitor`).

Para verificar se está rodando:

```bash
# Via API
curl -X POST https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/monitor/start

# Ver status
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/monitor/status
```

## 📝 Notas Importantes

1. **O monitor roda em background** - não precisa acessar o arquivo `.py` diretamente
2. **Resultados são salvos automaticamente** em `resultados_deunoposte.json`
3. **Monitor verifica a cada 60 segundos** (configurável via `--intervalo`)
4. **Resultados são combinados** com os do Bicho Certo na API principal
5. **Cada resultado tem campo `fonte`** para identificar a origem

## 🔧 Troubleshooting

### Monitor não está rodando?

1. Verifique se o arquivo `monitor_deunoposte.py` está no servidor
2. Verifique os logs do servidor para erros
3. Tente forçar verificação: `POST /api/verificar-agora`
4. Verifique se as dependências estão instaladas (requests, beautifulsoup4)

### Resultados não aparecem?

1. Verifique se o monitor está ativo: `GET /api/status`
2. Verifique o arquivo JSON: `GET /resultados_deunoposte.json`
3. Force uma verificação: `POST /api/verificar-agora`
4. Verifique os logs para erros de conexão
