# Resumo de Comparação de Horários - Tabela vs API

## Tabela de Extrações Fornecida

### LOTECE (4 extrações)
- **10:26** → Close: **11:00** ✓
- **13:25** → Close: **14:00** ✓
- **19:10** → Close: **19:40** ✓
- **15:26** → Close: **15:40** ✓

### LOTEP (4 extrações)
- **10:35** → Close: **10:45** ✓
- **12:35** → Close: **12:45** ✓
- **15:35** → Close: **15:45** ✓
- **17:51** → Close: **18:05** ✓

### LOOK (8 extrações)
- **11:05** → Close: **11:20** ✓
- **14:05** → Close: **14:20** ✓
- **16:05** → Close: **16:20** ✓
- **18:05** → Close: **18:20** ✓
- **21:05** → Close: **21:20** ✓
- **09:05** → Close: **09:20** ✓
- **23:10** → Close: **23:20** ✓
- **07:05** → Close: **07:20** ✓

### PARA TODOS (2 extrações)
- **09:35** → Close: **09:45** ✓
- **20:20** → Close: **20:40** ✓

### PT RIO (6 extrações)
- **11:10** → Close: **11:20** ✓
- **14:10** → Close: **14:20** ✓
- **16:10** → Close: **16:20** ✓
- **18:10** → Close: **18:20** ✓
- **21:10** → Close: **21:20** ✓
- **09:10** → Close: **09:20** ✓

### NACIONAL (8 extrações)
- **07:45** → Close: **08:00** ✓
- **09:45** → Close: **10:00** ✓
- **11:45** → Close: **12:00** ✓
- **14:45** → Close: **15:00** ✓
- **16:45** → Close: **17:00** ✓
- **20:45** → Close: **21:00** ✓
- **22:45** → Close: **23:00** ✓
- **01:51** → Close: **02:00** ✓

### PT BAHIA (5 extrações)
- **10:03** → Close: **10:20** ✓
- **12:03** → Close: **12:20** ✓
- **15:03** → Close: **15:20** ✓
- **18:43** → Close: **19:00** ✓
- **21:03** → Close: **21:20** ✓

### FEDERAL (1 extração)
- **19:50** → Close: **20:00** ✓

### PT SP (4 extrações)
- **10:11** → Close: **10:00** ⚠️ (Close antes do Real Close)
- **13:11** → Close: **13:15** ✓
- **17:11** → Close: **17:15** ✓
- **20:11** → Close: **20:15** ✓

### PT SP (Band) (1 extração)
- **15:11** → Close: **15:15** ✓

---

## Mapeamento de Nomes

A API pode retornar nomes diferentes. Mapeamento necessário:

| Nome na Tabela | Nome na API (possíveis variações) |
|----------------|-----------------------------------|
| LOTECE | Lotece |
| LOTEP | PT Paraiba/Lotep |
| LOOK | Look Goiás |
| PT RIO | PT Rio de Janeiro, PT-RJ |
| NACIONAL | Loteria Nacional |
| PT BAHIA | PT Bahia |
| FEDERAL | FEDERAL |
| PT SP | PT SP |
| PT SP (Band) | PT-SP/Bandeirantes |
| PARA TODOS | Para Todos, PARA TODOS |

---

## Formato de Horários

A API pode retornar horários em diferentes formatos:
- `09:30` (padrão HH:MM)
- `09h30` (com 'h')
- `0930` (sem separador)
- `9h30` (sem zero à esquerda)

**Normalização necessária:** Converter todos para formato `HH:MM` (ex: `09:30`)

---

## Como Usar o Script de Comparação

```bash
# Comparar com API local
python3 comparar_horarios.py

# Comparar com API remota
python3 comparar_horarios.py https://seu-dominio.com/api/resultados/organizados
```

O script irá:
1. Buscar horários da API
2. Normalizar nomes de loterias
3. Normalizar formatos de horários
4. Comparar com a tabela fornecida
5. Gerar relatório detalhado

---

## Observações Importantes

1. **PT SP 10:11**: O Close Time (10:00) é ANTES do Real Close Time (10:11). Isso pode ser um erro na tabela ou uma característica especial desta extração.

2. **Horários podem variar**: A API retorna os horários como aparecem no site bichocerto.com, que podem ter pequenas variações de formato.

3. **Loterias podem ter múltiplos nomes**: É necessário mapear corretamente os nomes da API para os nomes da tabela.

4. **Horários extras**: A API pode retornar horários que não estão na tabela (extrações antigas ou desativadas).

5. **Horários faltando**: Alguns horários da tabela podem não aparecer na API se não houver resultados recentes.

---

## Próximos Passos

1. Executar o script `comparar_horarios.py` com a URL real da API
2. Analisar os resultados da comparação
3. Ajustar o mapeamento de nomes se necessário
4. Verificar se há horários que precisam ser adicionados ou removidos
5. Documentar discrepâncias encontradas
