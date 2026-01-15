# Análise Comparativa: Horários da Tabela vs API

## 📊 Resumo Executivo

Este documento compara os horários da **Tabela de Extrações** fornecida com os horários retornados pela **API `/api/resultados/organizados`**.

---

## 📋 Tabela de Extrações (46 Extrações)

### LOTECE (4 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 10:26 | 11:00 | ✅ Ativa |
| 13:25 | 14:00 | ✅ Ativa |
| 19:10 | 19:40 | ✅ Ativa |
| 15:26 | 15:40 | ✅ Ativa |

**Horários esperados na API:** `11:00`, `14:00`, `19:40`, `15:40`

---

### LOTEP (4 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 10:35 | 10:45 | ✅ Ativa |
| 12:35 | 12:45 | ✅ Ativa |
| 15:35 | 15:45 | ✅ Ativa |
| 17:51 | 18:05 | ✅ Ativa |

**Horários esperados na API:** `10:45`, `12:45`, `15:45`, `18:05`

**Mapeamento API:** `PT Paraiba/Lotep` → `LOTEP`

---

### LOOK (8 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 11:05 | 11:20 | ✅ Ativa |
| 14:05 | 14:20 | ✅ Ativa |
| 16:05 | 16:20 | ✅ Ativa |
| 18:05 | 18:20 | ✅ Ativa |
| 21:05 | 21:20 | ✅ Ativa |
| 09:05 | 09:20 | ✅ Ativa |
| 23:10 | 23:20 | ✅ Ativa |
| 07:05 | 07:20 | ✅ Ativa |

**Horários esperados na API:** `11:20`, `14:20`, `16:20`, `18:20`, `21:20`, `09:20`, `23:20`, `07:20`

**Mapeamento API:** `Look Goiás` → `LOOK`

---

### PARA TODOS (2 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 09:35 | 09:45 | ✅ Ativa |
| 20:20 | 20:40 | ✅ Ativa |

**Horários esperados na API:** `09:45`, `20:40`

**Mapeamento API:** `Para Todos` ou `PARA TODOS` → `PARA TODOS`

---

### PT RIO (6 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 11:10 | 11:20 | ✅ Ativa |
| 14:10 | 14:20 | ✅ Ativa |
| 16:10 | 16:20 | ✅ Ativa |
| 18:10 | 18:20 | ✅ Ativa |
| 21:10 | 21:20 | ✅ Ativa |
| 09:10 | 09:20 | ✅ Ativa |

**Horários esperados na API:** `11:20`, `14:20`, `16:20`, `18:20`, `21:20`, `09:20`

**Mapeamento API:** `PT Rio de Janeiro` ou `PT-RJ` → `PT RIO`

---

### NACIONAL (8 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 07:45 | 08:00 | ✅ Ativa |
| 09:45 | 10:00 | ✅ Ativa |
| 11:45 | 12:00 | ✅ Ativa |
| 14:45 | 15:00 | ✅ Ativa |
| 16:45 | 17:00 | ✅ Ativa |
| 20:45 | 21:00 | ✅ Ativa |
| 22:45 | 23:00 | ✅ Ativa |
| 01:51 | 02:00 | ✅ Ativa |

**Horários esperados na API:** `08:00`, `10:00`, `12:00`, `15:00`, `17:00`, `21:00`, `23:00`, `02:00`

**Mapeamento API:** `Loteria Nacional` → `NACIONAL`

---

### PT BAHIA (5 extrações ativas)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 10:03 | 10:20 | ✅ Ativa |
| 12:03 | 12:20 | ✅ Ativa |
| 15:03 | 15:20 | ✅ Ativa |
| 18:43 | 19:00 | ✅ Ativa |
| 21:03 | 21:20 | ✅ Ativa |

**Horários esperados na API:** `10:20`, `12:20`, `15:20`, `19:00`, `21:20`

**Mapeamento API:** `PT Bahia` → `PT BAHIA`

---

### FEDERAL (1 extração ativa)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 19:50 | 20:00 | ✅ Ativa |

**Horários esperados na API:** `20:00`

**Mapeamento API:** `FEDERAL` → `FEDERAL`

---

### PT SP (4 extrações ativas)
| Real Close | Close Time | Status | Observação |
|------------|------------|--------|------------|
| 10:11 | 10:00 | ✅ Ativa | ⚠️ Close ANTES do Real Close |
| 13:11 | 13:15 | ✅ Ativa | |
| 17:11 | 17:15 | ✅ Ativa | |
| 20:11 | 20:15 | ✅ Ativa | |

**Horários esperados na API:** `10:00`, `13:15`, `17:15`, `20:15`

**Mapeamento API:** `PT SP` → `PT SP`

**⚠️ ATENÇÃO:** O horário `10:00` é ANTES do Real Close `10:11`. Isso pode ser um erro na tabela ou uma característica especial.

---

### PT SP (Band) (1 extração ativa)
| Real Close | Close Time | Status |
|------------|------------|--------|
| 15:11 | 15:15 | ✅ Ativa |

**Horários esperados na API:** `15:15`

**Mapeamento API:** `PT-SP/Bandeirantes` → `PT SP (Band)`

---

## 🔍 Análise de Discrepâncias Esperadas

### 1. Formato de Horários
A API pode retornar horários em diferentes formatos:
- ✅ `09:30` (padrão HH:MM)
- ⚠️ `09h30` (com 'h')
- ⚠️ `0930` (sem separador)
- ⚠️ `9h30` (sem zero à esquerda)

**Solução:** Normalizar todos para `HH:MM` antes de comparar.

### 2. Variações de Nomes
A API pode usar nomes diferentes para as mesmas loterias:

| Tabela | Possíveis Nomes na API |
|--------|------------------------|
| LOTEP | `PT Paraiba/Lotep`, `LOTEP` |
| PT RIO | `PT Rio de Janeiro`, `PT-RJ`, `PT RJ` |
| NACIONAL | `Loteria Nacional`, `Nacional` |
| PARA TODOS | `Para Todos`, `PARA TODOS` |
| PT SP (Band) | `PT-SP/Bandeirantes`, `PT SP Bandeirantes` |

### 3. Horários Extras na API
A API pode retornar horários que não estão na tabela:
- Extrações antigas
- Extrações desativadas recentemente
- Horários de teste

### 4. Horários Faltando na API
Alguns horários da tabela podem não aparecer na API se:
- Não houver resultados recentes para aquele horário
- A extração ainda não aconteceu hoje
- O monitor ainda não coletou dados para aquele horário

---

## 📊 Estatísticas Esperadas

### Total de Extrações Ativas na Tabela: **42**

| Loteria | Extrações | Horários Esperados |
|---------|-----------|-------------------|
| LOTECE | 4 | 4 |
| LOTEP | 4 | 4 |
| LOOK | 8 | 8 |
| PARA TODOS | 2 | 2 |
| PT RIO | 6 | 6 |
| NACIONAL | 8 | 8 |
| PT BAHIA | 5 | 5 |
| FEDERAL | 1 | 1 |
| PT SP | 4 | 4 |
| PT SP (Band) | 1 | 1 |
| **TOTAL** | **43** | **43** |

---

## 🛠️ Como Usar o Script de Comparação

### 1. Executar o Script

```bash
# Com API local
python3 comparar_horarios.py

# Com API remota
python3 comparar_horarios.py https://seu-dominio.com/api/resultados/organizados
```

### 2. Interpretar os Resultados

O script irá gerar:

#### ✅ CORRESPONDENTES
Horários que aparecem tanto na tabela quanto na API com o mesmo formato.

#### ❌ FALTANDO NA API
Horários da tabela que não foram encontrados na API.

**Possíveis causas:**
- Extração ainda não aconteceu hoje
- Monitor não coletou dados ainda
- Nome da loteria diferente (problema de mapeamento)

#### ➕ EXTRAS NA API
Horários na API que não estão na tabela.

**Possíveis causas:**
- Extrações antigas/desativadas
- Horários de teste
- Novas extrações não documentadas

---

## 📝 Checklist de Verificação

- [ ] Executar script de comparação
- [ ] Verificar mapeamento de nomes de loterias
- [ ] Verificar normalização de horários
- [ ] Identificar horários faltando
- [ ] Identificar horários extras
- [ ] Documentar discrepâncias encontradas
- [ ] Ajustar código se necessário

---

## 🔧 Ajustes Necessários no Código

Se houver discrepâncias, pode ser necessário:

1. **Ajustar mapeamento de nomes** em `comparar_horarios.py`:
```python
MAPEAMENTO_LOTERIAS = {
    'PT Paraiba/Lotep': 'LOTEP',
    'PT Rio de Janeiro': 'PT RIO',
    'PT-RJ': 'PT RIO',
    # ... adicionar mais mapeamentos
}
```

2. **Melhorar normalização de horários** em `monitor_selenium.py`:
```python
def normalizar_horario(horario):
    # Converter todos os formatos para HH:MM
    # Ex: "09h30" → "09:30", "0930" → "09:30"
```

3. **Ajustar lógica de agrupamento** em `app_vps.py`:
```python
# Garantir que horários similares sejam agrupados corretamente
# Ex: "09:30" e "9h30" devem ser tratados como iguais
```

---

## 📞 Próximos Passos

1. **Executar comparação** com a URL real da API em produção
2. **Analisar resultados** e identificar padrões
3. **Documentar** todas as discrepâncias encontradas
4. **Implementar correções** se necessário
5. **Validar** após correções

---

## 📄 Arquivos Relacionados

- `comparar_horarios.py` - Script de comparação
- `app_vps.py` - Endpoint `/api/resultados/organizados`
- `monitor_selenium.py` - Coleta e normalização de dados
- `RESUMO_COMPARACAO_HORARIOS.md` - Resumo técnico

---

**Última atualização:** 2026-01-15
