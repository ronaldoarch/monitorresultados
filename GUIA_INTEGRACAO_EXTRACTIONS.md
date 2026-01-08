# 🎯 Guia de Integração com Sistema de Extrações

## 📋 Como Funciona

### Sistema Baseado em Extrações

1. **Extração Pré-Criada**: Cada sorteio é uma "extraction" no banco
2. **Horário de Fechamento**: `close_time` - quando apostas fecham
3. **Horário do Resultado**: `real_close_time` - quando resultado é divulgado
4. **Vinculação**: Cada aposta DEVE ter `extraction_id`

### Fluxo Completo

```
1. Sistema cria extração (pré-criada)
   ↓
2. Usuário faz aposta → Vinculada a extraction_id
   ↓
3. Horário de fechamento chega → Apostas fecham
   ↓
4. Monitor detecta resultado no horário correto
   ↓
5. Sistema liquida APENAS apostas daquela extração
   ↓
6. Resultado aparece no painel
```

## 🔧 O Que Você Precisa Fazer

### 1. Criar Extrações no Banco

As extrações devem ser criadas ANTES das apostas. Exemplo:

```python
from sistema_liquidacao_extractions import SistemaLiquidacaoExtractions
from models import Extracao
from datetime import datetime, timedelta

sistema = SistemaLiquidacaoExtractions()
session = sistema.Session()

# Criar extração
extracao = Extracao(
    loteria='PT RIO',  # Nome no sistema (mapeado)
    horario='11:30',
    close_time=datetime(2026, 1, 5, 11, 25),  # Fecha 5 min antes
    real_close_time=datetime(2026, 1, 5, 11, 30),  # Resultado às 11:30
    status='aberta'
)
session.add(extracao)
session.commit()
```

### 2. Modificar Frontend para Buscar Extrações

**ANTES de mostrar formulário de aposta:**

```javascript
// Buscar extrações disponíveis
async function carregarExtracoesDisponiveis() {
    const response = await fetch('/api/extracoes-disponiveis');
    const data = await response.json();
    
    // Filtrar apenas as abertas
    const abertas = data.extracoes.filter(e => e.esta_aberta);
    
    // Popular dropdown de extrações
    const select = document.getElementById('extracao-select');
    select.innerHTML = abertas.map(e => `
        <option value="${e.id}">
            ${e.loteria} ${e.horario} - Fecha em ${e.minutos_para_fechar} min
        </option>
    `).join('');
    
    return abertas;
}
```

### 3. Validar Antes de Apostar

```javascript
async function fazerAposta(dados) {
    // 1. Buscar extração selecionada
    const extractionId = document.getElementById('extracao-select').value;
    const extracoes = await carregarExtracoesDisponiveis();
    const extracao = extracoes.find(e => e.id == extractionId);
    
    // 2. Validar se está aberta
    if (!extracao || !extracao.esta_aberta) {
        alert('Extração já fechou!');
        return;
    }
    
    // 3. Validar horário
    const agora = Date.now() / 1000;
    if (agora >= extracao.fecha_em_timestamp) {
        alert('Extração já fechou!');
        return;
    }
    
    // 4. Criar aposta COM extraction_id
    const resultado = await fetch('/api/apostas', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            usuario_id: getUsuarioLogado().id,
            extraction_id: extractionId, // ✅ CRÍTICO
            numero: dados.numero,
            animal: dados.animal,
            valor: dados.valor,
            loteria: extracao.loteria,  // Para exibição
            horario: extracao.horario   // Para exibição
        })
    });
    
    return resultado.json();
}
```

### 4. Monitor Processa por Extração

O monitor já está adaptado para:
- Buscar resultado do monitor
- Encontrar extração correspondente (por loteria + horário)
- Liquidar APENAS apostas daquela extração
- Não liquidar com resultados de outras extrações

## 📊 Mapeamento de Loterias

O sistema mapeia automaticamente:

| Painel | Sistema |
|--------|---------|
| PT Rio de Janeiro | PT RIO |
| Look Goiás | LOOK GOIÁS |
| Loteria Nacional | LOTERIA NACIONAL |
| PT Band | PT BAND |
| ... | ... |

**Adicione mais no arquivo `sistema_liquidacao_extractions.py`:**

```python
MAPEAMENTO_LOTERIAS = {
    'PT Rio de Janeiro': 'PT RIO',
    'Sua Loteria': 'NOME_NO_SISTEMA',
    # ...
}
```

## 🔄 Fluxo de Liquidação

### Passo a Passo:

1. **Monitor detecta resultado**:
   ```
   Resultado: PT Rio de Janeiro, 11:30, 1234 Cavalo
   ```

2. **Sistema busca extração**:
   ```python
   # Mapeia: PT Rio de Janeiro → PT RIO
   # Busca: loteria='PT RIO', horario='11:30'
   extracao = encontrar_extracao('PT RIO', '11:30')
   ```

3. **Liquida APENAS apostas desta extração**:
   ```python
   apostas = buscar_apostas(extraction_id=extracao.id)
   # NÃO pega apostas de outras extrações!
   ```

4. **Processa cada aposta**:
   - Compara número/animal
   - Calcula ganho
   - Atualiza saldo
   - Marca como liquidada

## ✅ Checklist de Implementação

### Backend:
- [ ] Extrações sendo criadas no banco
- [ ] `app_apostas_extractions.py` rodando
- [ ] Monitor ativo e processando
- [ ] Mapeamento de loterias correto

### Frontend:
- [ ] Buscar extrações antes de apostar
- [ ] Validar se extração está aberta
- [ ] Enviar `extraction_id` ao criar aposta
- [ ] Mostrar informações da extração (fecha em X min)
- [ ] Exibir resultados por extração

### Testes:
- [ ] Criar extração de teste
- [ ] Fazer aposta vinculada à extração
- [ ] Verificar que monitor detecta resultado
- [ ] Confirmar liquidação apenas da extração correta
- [ ] Verificar que resultados aparecem

## 🎯 Exemplo Completo

### Criar Extração (Backend)

```python
from sistema_liquidacao_extractions import SistemaLiquidacaoExtractions
from models import Extracao
from datetime import datetime

sistema = SistemaLiquidacaoExtractions()
session = sistema.Session()

# Criar extração para PT Rio 11:30
extracao = Extracao(
    loteria='PT RIO',
    horario='11:30',
    close_time=datetime(2026, 1, 5, 11, 25),  # Fecha 5 min antes
    real_close_time=datetime(2026, 1, 5, 11, 30),
    status='aberta'
)
session.add(extracao)
session.commit()
print(f"Extração criada: ID {extracao.id}")
```

### Fazer Aposta (Frontend)

```javascript
// 1. Buscar extrações
const extracoes = await fetch('/api/extracoes-disponiveis').then(r => r.json());

// 2. Encontrar extração desejada
const extracao = extracoes.extracoes.find(e => 
    e.loteria === 'PT RIO' && e.horario === '11:30'
);

// 3. Validar
if (!extracao.esta_aberta) {
    alert('Extração já fechou!');
    return;
}

// 4. Criar aposta
const resultado = await fetch('/api/apostas', {
    method: 'POST',
    body: JSON.stringify({
        usuario_id: 1,
        extraction_id: extracao.id, // ✅ CRÍTICO
        numero: '1234',
        animal: 'Cavalo',
        valor: 10.0
    })
});
```

### Monitor Processa

```python
# Monitor detecta: PT Rio de Janeiro, 11:30, 1234 Cavalo
# Sistema:
# 1. Mapeia: PT Rio de Janeiro → PT RIO
# 2. Busca extração: loteria='PT RIO', horario='11:30'
# 3. Encontra extraction_id=1
# 4. Busca apostas: extraction_id=1
# 5. Liquida APENAS essas apostas
# 6. NÃO toca em apostas de outras extrações
```

## ⚠️ Pontos Críticos

1. **SEMPRE usar `extraction_id`** ao criar aposta
2. **Validar horário de fechamento** antes de permitir aposta
3. **Mapear loterias corretamente** (painel → sistema)
4. **Monitor busca por loteria + horário** para encontrar extração
5. **Liquidação é por extração**, não por loteria genérica

## 🚀 Próximos Passos

1. Criar extrações no banco (script ou manual)
2. Modificar frontend para buscar extrações
3. Validar antes de apostar
4. Testar criação de aposta com `extraction_id`
5. Verificar liquidação automática
6. Confirmar que resultados aparecem corretamente

Tudo pronto para integrar! 🎯

