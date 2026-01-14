# 📸 Guia: Como Funciona a Instantânea na Etapa 4

Este guia explica detalhadamente como funciona o processo de **conversão instantânea** dos resultados da API para o formato usado na liquidação (Etapa 4 do fluxo).

---

## 🎯 O Que É a "Instantânea"?

A **instantânea** é o processo de converter os resultados da API (que vêm em formato JSON com números, animais e posições) para um formato simplificado de **milhares** (números de 4 dígitos) que é usado pelo motor de regras de liquidação.

---

## 📋 Fluxo Completo da Liquidação

```
1. Buscar resultados da API organizados
   ↓
2. Para cada sorteio (loteria + horário):
   ↓
3. Converter resultados para milhares ← INSTANTÂNEA
   ↓
4. Buscar apostas pendentes deste sorteio
   ↓
5. Para cada aposta:
   ↓
6. Aplicar regras conforme modalidade
   ↓
7. Calcular acertos e prêmio
   ↓
8. Atualizar saldo do usuário
   ↓
9. Registrar liquidação
```

A **Etapa 4** é onde acontece a conversão instantânea dos resultados.

---

## 🔄 Como Funciona a Conversão (Etapa 4)

### Entrada: Resultados da API

A API retorna resultados no formato:

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
        },
        {
          "horario": "09:30",
          "animal": "Macaco",
          "numero": "4867",
          "posicao": 3,
          "colocacao": "3°",
          "estado": "RJ",
          "data_extracao": "13/01/2026",
          "timestamp": "2026-01-13T12:30:00"
        }
        // ... até 7 resultados
      ]
    }
  }
}
```

### Processo de Conversão

A função `converter_resultado_api_para_milhares()` extrai apenas os números e os converte para inteiros:

```python
def converter_resultado_api_para_milhares(resultados_api: List[Dict]) -> List[int]:
    """
    Converte resultados da API para lista de milhares.
    
    Args:
        resultados_api: Lista de resultados no formato da API
        
    Returns:
        Lista de milhares (inteiros de 4 dígitos)
    """
    milhares = []
    for resultado in resultados_api:
        numero_str = resultado.get('numero', '')
        if numero_str and len(numero_str) == 4:
            try:
                milhar = int(numero_str)
                milhares.append(milhar)
            except ValueError:
                continue  # Ignorar números inválidos
    return milhares
```

### Saída: Lista de Milhares

Após a conversão, temos:

```python
milhares = [4732, 8775, 4867, 1234, 5678, 9012, 3456]
#           1°    2°    3°    4°    5°    6°    7°
```

---

## 💻 Exemplo Prático Completo

### Passo 1: Buscar Resultados da API

```python
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado

sistema = SistemaLiquidacaoAvancado(
    database_url='sqlite:///apostas.db',
    api_url='https://seu-monitor.com'
)

# Buscar resultados organizados
dados = sistema.buscar_resultados_organizados()
organizados = dados.get('organizados', {})
```

### Passo 2: Iterar sobre Cada Sorteio

```python
# Para cada loteria
for loteria, horarios in organizados.items():
    # Para cada horário
    for horario, resultados_api in horarios.items():
        print(f"Processando: {loteria} {horario}")
        print(f"Resultados recebidos: {len(resultados_api)}")
```

### Passo 3: Criar a Instantânea (Etapa 4)

```python
# Converter resultados da API para milhares
resultado_milhares = sistema.converter_resultado_para_milhares(resultados_api)

print(f"Instantânea criada: {resultado_milhares}")
# Saída: [4732, 8775, 4867, 1234, 5678, 9012, 3456]
```

### Passo 4: Usar a Instantânea na Liquidação

```python
# Buscar apostas pendentes
apostas = session.query(Aposta).filter(
    and_(
        Aposta.loteria == loteria,
        Aposta.horario == horario,
        Aposta.status == 'pendente'
    )
).all()

# Para cada aposta, usar a instantânea
for aposta in apostas:
    resultado_liquidacao = sistema.liquidar_aposta_com_regras(
        aposta=aposta,
        resultado_milhares=resultado_milhares,  # ← Usando a instantânea
        modalidade=aposta.tipo_aposta,
        pos_from=1,
        pos_to=7
    )
```

---

## 🔍 Detalhes Técnicos da Conversão

### 1. Validação de Números

A conversão valida que:
- O número existe no resultado
- O número tem exatamente 4 dígitos
- O número pode ser convertido para inteiro

```python
numero_str = resultado.get('numero', '')
if numero_str and len(numero_str) == 4:
    milhar = int(numero_str)  # Converte "4732" → 4732
```

### 2. Preservação da Ordem

A ordem dos resultados é preservada:
- 1º resultado → primeiro milhar da lista
- 2º resultado → segundo milhar da lista
- E assim por diante...

```python
# Resultados da API (ordenados por posição)
resultados_api = [
    {"numero": "4732", "posicao": 1},  # 1°
    {"numero": "8775", "posicao": 2},  # 2°
    {"numero": "4867", "posicao": 3},  # 3°
]

# Instantânea (mesma ordem)
milhares = [4732, 8775, 4867]  # 1°, 2°, 3°
```

### 3. Limite de Posições

A API retorna no máximo 7 posições por sorteio, então a instantânea terá no máximo 7 milhares:

```python
# Se a API retornar 7 resultados
resultados_api = [
    {"numero": "4732", "posicao": 1},
    {"numero": "8775", "posicao": 2},
    {"numero": "4867", "posicao": 3},
    {"numero": "1234", "posicao": 4},
    {"numero": "5678", "posicao": 5},
    {"numero": "9012", "posicao": 6},
    {"numero": "3456", "posicao": 7},
]

# A instantânea terá 7 milhares
milhares = [4732, 8775, 4867, 1234, 5678, 9012, 3456]
```

---

## 📊 Estrutura de Dados da Instantânea

### Formato

```python
# Tipo: List[int]
# Conteúdo: Lista de milhares (números de 4 dígitos)
# Ordem: Preserva a ordem das posições (1° a 7°)

milhares = [4732, 8775, 4867, 1234, 5678, 9012, 3456]
```

### Índices e Posições

```python
# Índice 0 = 1° prêmio
milhares[0]  # 4732 (1°)

# Índice 1 = 2° prêmio
milhares[1]  # 8775 (2°)

# Índice 2 = 3° prêmio
milhares[2]  # 4867 (3°)

# ... e assim por diante
```

### Acesso por Posição

```python
# Para acessar o 1° prêmio
primeiro_premio = milhares[0]  # 4732

# Para acessar o 2° prêmio
segundo_premio = milhares[1]  # 8775

# Para acessar um intervalo (1° a 3°)
primeiros_tres = milhares[0:3]  # [4732, 8775, 4867]
```

---

## 🎯 Por Que Usar Instantânea?

### Vantagens

1. **Simplicidade**: Formato simples e direto (apenas números)
2. **Performance**: Processamento mais rápido (sem objetos complexos)
3. **Compatibilidade**: Formato esperado pelo motor de regras
4. **Consistência**: Mesma estrutura para todas as modalidades

### Comparação

**Sem Instantânea** (processamento direto):
```python
# Precisaria processar objetos complexos
for resultado in resultados_api:
    numero = resultado.get('numero')
    animal = resultado.get('animal')
    posicao = resultado.get('posicao')
    # ... lógica complexa
```

**Com Instantânea** (processamento simplificado):
```python
# Processa apenas números
for milhar in resultado_milhares:
    # Lógica simples e direta
    grupo = milhar_para_grupo(milhar)
    # ... processamento rápido
```

---

## 🔧 Funções Relacionadas

### 1. `converter_resultado_api_para_milhares()`

```python
from regras_liquidacao import converter_resultado_api_para_milhares

resultados_api = [
    {"numero": "4732", "animal": "Camelo"},
    {"numero": "8775", "animal": "Pavão"},
]

milhares = converter_resultado_api_para_milhares(resultados_api)
# Retorna: [4732, 8775]
```

### 2. `milhar_para_grupo()`

```python
from regras_liquidacao import milhar_para_grupo

milhar = 4732
grupo = milhar_para_grupo(milhar)  # Retorna: 8 (Camelo)
```

### 3. `grupos_no_resultado()`

```python
from regras_liquidacao import grupos_no_resultado

milhares = [4732, 8775, 4867]
grupos = grupos_no_resultado(milhares, pos_from=1, pos_to=3)
# Retorna: [8, 19, 17]  # Camelo, Pavão, Macaco
```

---

## 📝 Exemplo Completo de Uso

```python
#!/usr/bin/env python3
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado
from regras_liquidacao import (
    converter_resultado_api_para_milhares,
    milhar_para_grupo,
    grupos_no_resultado
)

# Inicializar sistema
sistema = SistemaLiquidacaoAvancado(
    database_url='sqlite:///apostas.db',
    api_url='https://seu-monitor.com'
)

# 1. Buscar resultados da API
dados = sistema.buscar_resultados_organizados()
organizados = dados.get('organizados', {})

# 2. Processar cada sorteio
for loteria, horarios in organizados.items():
    for horario, resultados_api in horarios.items():
        print(f"\n{'='*60}")
        print(f"Processando: {loteria} {horario}")
        print(f"{'='*60}")
        
        # 3. Criar instantânea (ETAPA 4)
        resultado_milhares = converter_resultado_api_para_milhares(resultados_api)
        
        print(f"\n📸 INSTANTÂNEA CRIADA:")
        print(f"   Milhares: {resultado_milhares}")
        print(f"   Total: {len(resultado_milhares)} posições")
        
        # 4. Extrair informações da instantânea
        print(f"\n📊 INFORMAÇÕES EXTRAÍDAS:")
        for i, milhar in enumerate(resultado_milhares, 1):
            grupo = milhar_para_grupo(milhar)
            animal = sistema.animal_para_grupo_reverso(grupo)  # Se tiver função reversa
            print(f"   {i}°: {milhar:04d} → Grupo {grupo} ({animal})")
        
        # 5. Usar instantânea para liquidação
        print(f"\n💰 LIQUIDAÇÃO:")
        liquidadas = sistema.processar_liquidacao_por_sorteio(
            loteria=loteria,
            horario=horario,
            resultados_api=resultados_api
        )
        print(f"   Apostas liquidadas: {liquidadas}")
```

---

## ⚠️ Observações Importantes

### 1. Validação de Dados

Sempre valide que a instantânea foi criada corretamente:

```python
milhares = converter_resultado_api_para_milhares(resultados_api)

if not milhares:
    print("⚠️  Nenhum resultado válido encontrado")
    return

if len(milhares) < 7:
    print(f"⚠️  Apenas {len(milhares)} resultados encontrados (esperado: 7)")
```

### 2. Ordem dos Resultados

A ordem é crítica! Certifique-se de que os resultados da API estão ordenados por posição:

```python
# Ordenar por posição antes de converter
resultados_ordenados = sorted(
    resultados_api,
    key=lambda x: x.get('posicao', 0)
)

milhares = converter_resultado_api_para_milhares(resultados_ordenados)
```

### 3. Tratamento de Erros

Trate erros durante a conversão:

```python
try:
    milhares = converter_resultado_api_para_milhares(resultados_api)
except Exception as e:
    print(f"❌ Erro ao criar instantânea: {e}")
    return
```

---

## 🚀 Otimizações

### Cache da Instantânea

Para evitar recriar a instantânea múltiplas vezes:

```python
# Cache por sorteio
cache_instantaneas = {}

def obter_instantanea(loteria, horario, resultados_api):
    chave = f"{loteria}_{horario}"
    
    if chave not in cache_instantaneas:
        cache_instantaneas[chave] = converter_resultado_api_para_milhares(resultados_api)
    
    return cache_instantaneas[chave]
```

### Validação Rápida

```python
def validar_instantanea(milhares):
    """Valida se a instantânea está correta"""
    if not milhares:
        return False
    
    if len(milhares) > 7:
        return False
    
    for milhar in milhares:
        if not (0 <= milhar <= 9999):
            return False
    
    return True
```

---

## 📞 Resumo

A **instantânea na Etapa 4** é o processo de:

1. ✅ Receber resultados da API (formato JSON complexo)
2. ✅ Extrair apenas os números (campo `numero`)
3. ✅ Converter para inteiros (milhares)
4. ✅ Criar lista ordenada por posição
5. ✅ Usar essa lista na liquidação

**Formato de Entrada:**
```json
[
  {"numero": "4732", "animal": "Camelo", "posicao": 1},
  {"numero": "8775", "animal": "Pavão", "posicao": 2}
]
```

**Formato de Saída (Instantânea):**
```python
[4732, 8775]
```

**Uso na Liquidação:**
```python
resultado = conferir_palpite_completo(
    resultado_milhares=[4732, 8775],  # ← Instantânea
    modalidade="GRUPO",
    palpite={"grupos": [8]},
    pos_from=1,
    pos_to=7,
    valor_por_palpite=10.0
)
```

---

## ✅ Pronto!

Agora você entende como funciona a instantânea na Etapa 4! É um processo simples mas essencial para converter os dados da API para o formato usado pelo motor de regras de liquidação.
