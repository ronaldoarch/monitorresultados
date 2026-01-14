# 🔧 Troubleshooting: Apostas Não Liquidadas

Este guia ajuda a diagnosticar e resolver problemas quando apostas não são liquidadas automaticamente.

## 🔍 Diagnóstico Rápido

### Passo 1: Executar Diagnóstico

```bash
python3 diagnostico_liquidacao.py --api https://seu-monitor.com
```

Este script vai:
- ✅ Listar apostas pendentes/perdidas recentes
- ✅ Verificar se resultados estão na API
- ✅ Verificar se resultados estão no banco
- ✅ Verificar se liquidações foram criadas
- ✅ Verificar status do monitor

### Passo 2: Verificar Resultados na API

```bash
curl https://seu-monitor.com/api/resultados/organizados | jq '.organizados | keys'
```

Verifique se as loterias das suas apostas aparecem:
- `FEDERAL` → Deve aparecer como "Loteria Federal" ou "Federal"
- `PT SP` → Deve aparecer como "PT-SP/Bandeirantes" ou "PT SP"

### Passo 3: Verificar Mapeamento de Loterias

O sistema precisa mapear corretamente os nomes:

| Nome no Sistema | Nome na API |
|-----------------|-------------|
| FEDERAL | Loteria Federal, Federal |
| PT SP | PT-SP/Bandeirantes, PT SP |
| PT BAHIA | PT Bahia |

---

## 🛠️ Soluções Comuns

### Problema 1: Resultado não encontrado na API

**Sintomas:**
- Aposta fica como "pendente"
- Diagnóstico mostra "Resultado NÃO encontrado na API"

**Soluções:**

1. **Verificar se o horário está correto:**
   ```bash
   # Verificar horários disponíveis na API
   curl https://seu-monitor.com/api/resultados/organizados | jq '.organizados."Loteria Federal" | keys'
   ```

2. **Verificar formato do horário:**
   - API pode retornar: `"19:50"`, `"19h50"`, `"1950"`
   - Sistema normaliza para comparação, mas pode haver diferenças

3. **Aguardar coleta do monitor:**
   - O monitor pode não ter coletado o resultado ainda
   - Verificar última verificação: `GET /api/status`

### Problema 2: Mapeamento de Loteria Incorreto

**Sintomas:**
- Resultado existe na API mas com nome diferente
- Aposta não encontra resultado correspondente

**Solução:**

Editar função `mapear_loteria_api_para_sistema` em `diagnostico_liquidacao.py`:

```python
def mapear_loteria_api_para_sistema(loteria_api):
    mapeamento = {
        'Loteria Federal': 'FEDERAL',
        'Federal': 'FEDERAL',
        'PT-SP/Bandeirantes': 'PT SP',
        'PT SP': 'PT SP',
        # Adicionar novos mapeamentos aqui
        'Seu Nome API': 'Seu Nome Sistema',
    }
    # ...
```

### Problema 3: Modalidade Não Suportada

**Sintomas:**
- Aposta tem modalidade diferente (ex: "DUPLA_GRUPO")
- Sistema não consegue processar

**Solução:**

Verificar se a modalidade está implementada em `regras_liquidacao.py`:

```python
# Modalidades suportadas:
- GRUPO
- DUPLA_GRUPO
- TERNO_GRUPO
- QUADRA_GRUPO
- DEZENA
- CENTENA
- MILHAR
- MILHAR_INVERTIDA
- PASSE
- PASSE_VAI_E_VEM
```

### Problema 4: Palpite em Formato Incorreto

**Sintomas:**
- Aposta de DUPLA_GRUPO com números "19-18"
- Sistema não consegue extrair grupos

**Solução:**

O script `liquidar_apostas_especificas.py` tenta extrair grupos de diferentes formatos:
- `"19-18"` → grupos [19, 18]
- `"Camelo"` → grupo 8
- `"8"` → grupo 8

---

## 🔄 Liquidação Manual

Se o diagnóstico mostrar que os resultados existem mas não foram liquidados:

### Opção 1: Liquidar Todas as Apostas Pendentes

```bash
python3 liquidar_apostas_especificas.py --api https://seu-monitor.com
```

### Opção 2: Liquidar Apostas de uma Loteria Específica

```bash
python3 liquidar_apostas_especificas.py \
  --api https://seu-monitor.com \
  --loteria "FEDERAL"
```

### Opção 3: Liquidar Apostas de um Horário Específico

```bash
python3 liquidar_apostas_especificas.py \
  --api https://seu-monitor.com \
  --horario "19:50"
```

---

## 📋 Casos Específicos

### Caso 1: Dupla de Grupo (19-18)

**Aposta:**
- Modalidade: `DUPLA_GRUPO`
- Palpites: `"19-18"`
- Posição: `1º ao 3°`
- Extração: `FEDERAL • 19:50`

**Verificação:**
1. Resultado deve ter grupos 19 e 18 nas posições 1º-3º
2. Ambos grupos devem aparecer (não precisa ser na mesma posição)

**Como conferir manualmente:**
```python
# Resultado: ["7838", "4177", "4858", ...]
# Grupos: [grupo(7838), grupo(4177), grupo(4858), ...]
# Verificar se grupos 19 e 18 estão presentes
```

### Caso 2: Milhar (5638, 8493)

**Aposta:**
- Modalidade: `MILHAR`
- Palpites: `"5638"` e `"8493"`
- Posição: `1º ao 5º`
- Extração: `PT SP • 20:11`

**Verificação:**
1. Resultado deve ter números 5638 ou 8493 nas posições 1º-5º
2. Cada número conta como um acerto separado

**Como conferir manualmente:**
```python
# Resultado: ["0690", "6886", "5188", "1792", "9890", ...]
# Verificar se "5638" ou "8493" aparecem nas primeiras 5 posições
```

---

## 🔍 Verificações Adicionais

### Verificar Status do Monitor

```bash
curl https://seu-monitor.com/api/monitor/status
```

Deve retornar:
```json
{
  "monitor_rodando": true,
  "monitor_iniciado": true,
  "thread_ativa": true
}
```

### Verificar Última Verificação

```bash
curl https://seu-monitor.com/api/status
```

Verifique `ultima_verificacao` - deve ser recente (últimos minutos).

### Forçar Verificação Imediata

```bash
curl -X POST https://seu-monitor.com/api/verificar-agora
```

### Verificar Resultados no Banco

```python
from models import Resultado, Extracao
from sqlalchemy.orm import sessionmaker

session = Session()

# Buscar resultados recentes
resultados = session.query(Resultado).order_by(Resultado.timestamp.desc()).limit(10).all()

for r in resultados:
    print(f"{r.loteria} {r.horario}: {r.numero} {r.animal}")
```

---

## 🚨 Problemas Críticos

### Monitor não está rodando

**Sintoma:** `monitor_rodando: false`

**Solução:**
```bash
# Iniciar monitor manualmente
curl -X POST https://seu-monitor.com/api/monitor/start \
  -H "Content-Type: application/json" \
  -d '{"intervalo": 60}'
```

### API não está acessível

**Sintoma:** Erro de conexão ao acessar API

**Solução:**
1. Verificar se o servidor está rodando
2. Verificar firewall/rede
3. Verificar URL da API

### Banco de dados bloqueado

**Sintoma:** Erro de lock no banco SQLite

**Solução:**
```bash
# Verificar processos usando o banco
lsof apostas.db

# Se necessário, fechar conexões e tentar novamente
```

---

## 📞 Próximos Passos

1. ✅ Execute o diagnóstico: `python3 diagnostico_liquidacao.py`
2. ✅ Analise os resultados
3. ✅ Se resultados existem mas não foram liquidados, execute liquidação manual
4. ✅ Se resultados não existem, verifique monitor e API
5. ✅ Corrija mapeamentos se necessário

---

## 💡 Dicas

- **Sempre execute o diagnóstico primeiro** antes de tentar soluções
- **Mantenha logs** do monitor para identificar problemas
- **Verifique mapeamentos** quando adicionar novas loterias
- **Teste liquidação manual** antes de confiar no automático
