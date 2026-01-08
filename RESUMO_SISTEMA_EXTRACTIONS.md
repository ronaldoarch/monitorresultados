# 📋 Resumo - Sistema com Extrações

## ✅ O Que Foi Criado

### Arquivos Principais:

1. **`sistema_liquidacao_extractions.py`** - Sistema de liquidação adaptado
2. **`app_apostas_extractions.py`** - API completa com extrações
3. **`models.py`** - Modelos atualizados com tabela `Extracao`
4. **`script_criar_extracao.py`** - Script para criar extrações
5. **`GUIA_INTEGRACAO_EXTRACTIONS.md`** - Guia completo

## 🎯 Como Funciona Agora

### 1. Extrações Pré-Criadas

Cada sorteio é uma **extraction** no banco com:
- `loteria` - Nome no sistema (ex: "PT RIO")
- `horario` - Horário do sorteio (ex: "11:30")
- `close_time` - Quando fecha para apostas
- `real_close_time` - Quando resultado é divulgado
- `status` - aberta, fechada, sorteada, liquidada

### 2. Apostas Vinculadas

Cada aposta **DEVE** ter:
- `extraction_id` - ID da extração
- Validação de horário de fechamento
- Não pode apostar após `close_time`

### 3. Monitor Inteligente

O monitor:
- Detecta resultado do site
- Mapeia loteria (painel → sistema)
- Busca extração correspondente
- Liquida **APENAS** apostas daquela extração
- **NÃO** liquida com resultados errados

## 🚀 Quick Start

### 1. Criar Extração

```bash
python3 script_criar_extracao.py \
  --loteria "PT Rio de Janeiro" \
  --horario "11:30" \
  --minutos-fechar 5
```

### 2. Iniciar API

```bash
python3 app_apostas_extractions.py --monitor --intervalo 60 --port 5001
```

### 3. Frontend Busca Extrações

```javascript
// Buscar extrações disponíveis
const extracoes = await fetch('/api/extracoes-disponiveis').then(r => r.json());

// Filtrar abertas
const abertas = extracoes.extracoes.filter(e => e.esta_aberta);

// Mostrar para usuário escolher
```

### 4. Criar Aposta

```javascript
// Validar se está aberta
if (!extracao.esta_aberta) {
    alert('Extração já fechou!');
    return;
}

// Criar aposta COM extraction_id
await fetch('/api/apostas', {
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

### 5. Monitor Processa

```
Monitor detecta: PT Rio de Janeiro, 11:30, 1234 Cavalo
    ↓
Mapeia: PT Rio de Janeiro → PT RIO
    ↓
Busca extração: loteria='PT RIO', horario='11:30'
    ↓
Encontra extraction_id=1
    ↓
Busca apostas: extraction_id=1
    ↓
Liquida APENAS essas apostas ✅
```

## 📊 Mapeamento de Loterias

O sistema mapeia automaticamente:

| Painel | Sistema |
|--------|---------|
| PT Rio de Janeiro | PT RIO |
| Look Goiás | LOOK GOIÁS |
| Loteria Nacional | LOTERIA NACIONAL |

**Adicione mais em `sistema_liquidacao_extractions.py`:**

```python
MAPEAMENTO_LOTERIAS = {
    'Sua Loteria': 'NOME_NO_SISTEMA',
}
```

## ✅ Checklist de Implementação

### Backend:
- [x] Sistema de extrações criado
- [x] API adaptada
- [x] Monitor processa por extração
- [ ] Criar extrações no banco
- [ ] Testar liquidação

### Frontend:
- [ ] Buscar extrações antes de apostar
- [ ] Validar horário de fechamento
- [ ] Enviar `extraction_id` ao criar aposta
- [ ] Mostrar informações da extração
- [ ] Exibir resultados por extração

## 🎯 Pontos Críticos

1. ✅ **SEMPRE usar `extraction_id`** ao criar aposta
2. ✅ **Validar `close_time`** antes de permitir aposta
3. ✅ **Mapear loterias** corretamente
4. ✅ **Monitor busca por loteria + horário**
5. ✅ **Liquidação é por extração**, não genérica

## 📖 Documentação

- `GUIA_INTEGRACAO_EXTRACTIONS.md` - Guia completo
- `app_apostas_extractions.py` - API com exemplos
- `sistema_liquidacao_extractions.py` - Lógica de liquidação

## 🚀 Próximos Passos

1. Criar extrações no banco
2. Testar criação de aposta com `extraction_id`
3. Verificar liquidação automática
4. Integrar com frontend
5. Testar fluxo completo

Tudo pronto! 🎯

