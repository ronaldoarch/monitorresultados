# 🎯 Guia Completo: Liquidação de Apostas com Regras Avançadas

Este guia mostra como integrar o sistema de liquidação avançado com todas as regras do Jogo do Bicho usando a API de resultados organizados.

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura das Regras](#estrutura-das-regras)
3. [Como Funciona a Liquidação](#como-funciona-a-liquidação)
4. [Integração com a API](#integração-com-a-api)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Configuração e Uso](#configuração-e-uso)

---

## 🎯 Visão Geral

O sistema de liquidação avançado implementa todas as modalidades do Jogo do Bicho:

### Modalidades Suportadas

#### **Modalidades de Grupo:**
- **GRUPO**: Aposta em 1 grupo (animal)
- **DUPLA_GRUPO**: Aposta em 2 grupos simultâneos
- **TERNO_GRUPO**: Aposta em 3 grupos simultâneos
- **QUADRA_GRUPO**: Aposta em 4 grupos simultâneos

#### **Modalidades de Número:**
- **DEZENA**: Últimos 2 dígitos (00-99)
- **CENTENA**: Últimos 3 dígitos (000-999)
- **MILHAR**: Número completo (0000-9999)

#### **Modalidades Invertidas:**
- **DEZENA_INVERTIDA**: Permutações da dezena
- **CENTENA_INVERTIDA**: Permutações da centena
- **MILHAR_INVERTIDA**: Permutações do milhar

#### **Modalidades Especiais:**
- **PASSE**: Grupo do 1º prêmio → Grupo do 2º prêmio (ordem exata)
- **PASSE_VAI_E_VEM**: Grupo do 1º ↔ Grupo do 2º (ambas as ordens)
- **MILHAR_CENTENA**: Combinação milhar + centena

---

## 📐 Estrutura das Regras

### Tabela de Grupos (1-25)

Cada grupo corresponde a 4 dezenas consecutivas:

```
Grupo 1 (Avestruz):  01, 02, 03, 04
Grupo 2 (Águia):     05, 06, 07, 08
...
Grupo 25 (Vaca):     97, 98, 99, 00
```

### Conversão de Resultados

A API retorna resultados no formato:
```json
{
  "numero": "4732",
  "animal": "Camelo",
  "posicao": 1,
  "colocacao": "1°"
}
```

O sistema converte para:
- **Milhar**: `4732` (número completo)
- **Grupo**: `8` (Camelo = grupo 8)
- **Dezena**: `32` (últimos 2 dígitos)
- **Centena**: `732` (últimos 3 dígitos)

### Tabela de Odds (Multiplicadores)

| Modalidade | 1º Prêmio | 1º-3º | 1º-5º | 1º-7º |
|------------|-----------|-------|-------|-------|
| GRUPO | 18x | 18x | 18x | 18x |
| DUPLA_GRUPO | 180x | 180x | 180x | 180x |
| TERNO_GRUPO | 1800x | 1800x | 1800x | 1800x |
| QUADRA_GRUPO | 5000x | 5000x | 5000x | 5000x |
| DEZENA | 60x | 60x | 60x | 60x |
| CENTENA | 600x | 600x | 600x | 600x |
| MILHAR | 5000x | 5000x | 5000x | - |
| MILHAR_INVERTIDA | 200x | 200x | 200x | - |
| PASSE | - | - | - | - |
| PASSE_VAI_E_VEM | - | - | - | - |

*Nota: PASSE e PASSE_VAI_E_VEM sempre usam 1º-2º com odds fixas (300x e 150x respectivamente)*

---

## ⚙️ Como Funciona a Liquidação

### Fluxo de Liquidação

```
1. Buscar resultados da API organizados
   ↓
2. Para cada sorteio (loteria + horário):
   ↓
3. Converter resultados para milhares
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

### Exemplo de Liquidação

**Aposta:**
- Modalidade: `GRUPO`
- Animal: `Camelo` (grupo 8)
- Valor: R$ 10,00
- Posições: 1º-7º

**Resultado:**
- 1º prêmio: `4732` (grupo 8 - Camelo) ✅
- 2º prêmio: `1234` (grupo 9 - Cobra)
- 3º prêmio: `5678` (grupo 20 - Peru)
- ...

**Cálculo:**
- Acertos: 1 (1º prêmio)
- Odd: 18x
- Valor unitário: R$ 10,00 / 7 = R$ 1,43
- Prêmio por unidade: R$ 1,43 × 18 = R$ 25,71
- **Prêmio total: R$ 25,71**

---

## 🔌 Integração com a API

### 1. Buscar Resultados Organizados

```python
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado

# Inicializar sistema
sistema = SistemaLiquidacaoAvancado(
    database_url='sqlite:///apostas.db',
    api_url='https://seu-monitor.com'
)

# Buscar resultados
dados = sistema.buscar_resultados_organizados()
organizados = dados.get('organizados', {})

# Exemplo de estrutura:
# {
#   "PT Rio de Janeiro": {
#     "09:30": [
#       {"numero": "4732", "animal": "Camelo", "posicao": 1, ...},
#       {"numero": "1234", "animal": "Cobra", "posicao": 2, ...},
#       ...
#     ]
#   }
# }
```

### 2. Processar Liquidação Automática

```python
# Processar todas as apostas pendentes
total_liquidadas = sistema.processar_liquidacao_automatica()
print(f"✅ {total_liquidadas} apostas liquidadas")
```

### 3. Liquidar Aposta Específica

```python
# Liquidar uma aposta específica
resultado = sistema.liquidar_aposta_especifica(
    aposta_id=123,
    loteria="PT Rio de Janeiro",
    horario="09:30"
)

if resultado.get('ganhou'):
    print(f"✅ Ganhou! R$ {resultado['valor_ganho']:.2f}")
    print(f"   Acertos: {resultado['acertos']}")
else:
    print("❌ Não ganhou")
```

---

## 💻 Exemplos Práticos

### Exemplo 1: Liquidação Simples (GRUPO)

```python
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado
from regras_liquidacao import converter_resultado_api_para_milhares, conferir_palpite_completo

sistema = SistemaLiquidacaoAvancado()

# Resultado do sorteio
resultados_api = [
    {"numero": "4732", "animal": "Camelo", "posicao": 1},
    {"numero": "1234", "animal": "Cobra", "posicao": 2},
    {"numero": "5678", "animal": "Peru", "posicao": 3},
]

# Converter para milhares
milhares = converter_resultado_api_para_milhares(resultados_api)
# Resultado: [4732, 1234, 5678]

# Conferir aposta de GRUPO
palpite = {"grupos": [8]}  # Grupo 8 = Camelo
resultado = conferir_palpite_completo(
    resultado_milhares=milhares,
    modalidade="GRUPO",
    palpite=palpite,
    pos_from=1,
    pos_to=7,
    valor_por_palpite=10.0
)

print(f"Acertos: {resultado['prize']['hits']}")
print(f"Prêmio: R$ {resultado['totalPrize']:.2f}")
```

### Exemplo 2: Liquidação de DEZENA

```python
# Aposta em dezena 32
palpite = {"numero": "32"}
resultado = conferir_palpite_completo(
    resultado_milhares=[4732, 1234, 5678],
    modalidade="DEZENA",
    palpite=palpite,
    pos_from=1,
    pos_to=7,
    valor_por_palpite=5.0
)

# Verificar se ganhou
if resultado['prize']['hits'] > 0:
    print(f"✅ Ganhou! Dezena 32 apareceu {resultado['prize']['hits']} vez(es)")
    print(f"   Prêmio: R$ {resultado['totalPrize']:.2f}")
```

### Exemplo 3: Liquidação de MILHAR_INVERTIDA

```python
# Aposta em milhar invertido 1234
# Permutações: 1234, 1243, 1324, 1342, 1423, 1432, 2134, 2143, ...
palpite = {"numero": "1234"}
resultado = conferir_palpite_completo(
    resultado_milhares=[4321, 1234, 5678],  # 4321 é permutação de 1234
    modalidade="MILHAR_INVERTIDA",
    palpite=palpite,
    pos_from=1,
    pos_to=5,
    valor_por_palpite=20.0
)

print(f"Permutações distintas: {resultado['calculation']['combinations']}")
print(f"Acertos: {resultado['prize']['hits']}")
```

### Exemplo 4: Liquidação de PASSE

```python
# Aposta em PASSE: Grupo 8 (1º) → Grupo 9 (2º)
palpite = {"grupos": [8, 9]}
resultado = conferir_palpite_completo(
    resultado_milhares=[4732, 1234, 5678],  # Grupo 8, Grupo 9, Grupo 20
    modalidade="PASSE",
    palpite=palpite,
    pos_from=1,
    pos_to=2,  # PASSE sempre usa 1º-2º
    valor_por_palpite=15.0
)

if resultado['prize']['hits'] > 0:
    print("✅ PASSE ganhou! Ordem exata: 8 → 9")
```

### Exemplo 5: Liquidação de DUPLA_GRUPO

```python
# Aposta em dupla de grupos: 8 e 9
palpite = {"grupos": [8, 9]}
resultado = conferir_palpite_completo(
    resultado_milhares=[4732, 1234, 5678],  # Grupo 8, Grupo 9, Grupo 20
    modalidade="DUPLA_GRUPO",
    palpite=palpite,
    pos_from=1,
    pos_to=7,
    valor_por_palpite=25.0
)

if resultado['prize']['hits'] > 0:
    print("✅ DUPLA_GRUPO ganhou! Ambos grupos presentes")
    print(f"   Prêmio: R$ {resultado['totalPrize']:.2f}")
```

---

## 🚀 Configuração e Uso

### 1. Instalar Dependências

```bash
pip install requests sqlalchemy flask flask-cors
```

### 2. Configurar Banco de Dados

O sistema usa SQLAlchemy e cria as tabelas automaticamente. Configure a URL do banco:

```python
# SQLite (desenvolvimento)
sistema = SistemaLiquidacaoAvancado(database_url='sqlite:///apostas.db')

# PostgreSQL (produção)
sistema = SistemaLiquidacaoAvancado(
    database_url='postgresql://user:pass@localhost/apostas'
)
```

### 3. Configurar URL da API

```python
# Via código
sistema = SistemaLiquidacaoAvancado(
    api_url='https://seu-monitor.com'
)

# Via variável de ambiente
import os
os.environ['BICHO_CERTO_API'] = 'https://seu-monitor.com'
sistema = SistemaLiquidacaoAvancado()
```

### 4. Criar Aposta com Modalidade

```python
from models import Aposta, Usuario
from sqlalchemy.orm import sessionmaker

session = sistema.Session()

# Buscar usuário
usuario = session.query(Usuario).get(1)

# Criar aposta de GRUPO
aposta = Aposta(
    usuario_id=usuario.id,
    numero="0000",  # Não usado em GRUPO
    animal="Camelo",  # Grupo 8
    valor=10.0,
    loteria="PT Rio de Janeiro",
    horario="09:30",
    tipo_aposta="GRUPO",  # Modalidade
    status='pendente'
)
session.add(aposta)
session.commit()
```

### 5. Executar Liquidação Automática

#### Opção A: Via Script Python

```python
#!/usr/bin/env python3
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado

sistema = SistemaLiquidacaoAvancado(
    database_url='sqlite:///apostas.db',
    api_url='https://seu-monitor.com'
)

# Executar liquidação
total = sistema.processar_liquidacao_automatica()
print(f"✅ {total} apostas liquidadas")
```

#### Opção B: Via Cron Job

```bash
# Executar a cada 1 minuto
* * * * * /usr/bin/python3 /caminho/para/liquidar.py
```

#### Opção C: Via Endpoint Flask

```python
from flask import Flask, jsonify
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado

app = Flask(__name__)
sistema = SistemaLiquidacaoAvancado()

@app.route('/api/liquidar', methods=['POST'])
def liquidar():
    total = sistema.processar_liquidacao_automatica()
    return jsonify({
        'sucesso': True,
        'apostas_liquidadas': total
    })

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 📊 Estrutura de Dados das Apostas

### Campos Necessários na Tabela `apostas`

```sql
CREATE TABLE apostas (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    numero VARCHAR(4) NOT NULL,        -- Número apostado
    animal VARCHAR(50) NOT NULL,        -- Animal (para grupos)
    valor FLOAT NOT NULL,               -- Valor da aposta
    loteria VARCHAR(100) NOT NULL,      -- Nome da loteria
    horario VARCHAR(10) NOT NULL,       -- Horário do sorteio
    tipo_aposta VARCHAR(20) DEFAULT 'GRUPO',  -- Modalidade
    status VARCHAR(20) DEFAULT 'pendente',     -- pendente, ganhou, perdeu
    data_aposta DATETIME,
    data_liquidacao DATETIME
);
```

### Modalidades e Campos

| Modalidade | Usa `numero` | Usa `animal` | Observações |
|------------|--------------|--------------|-------------|
| GRUPO | Não | Sim | Animal = grupo |
| DUPLA_GRUPO | Não | Sim | Precisa de 2 grupos (ajustar modelo) |
| TERNO_GRUPO | Não | Sim | Precisa de 3 grupos |
| QUADRA_GRUPO | Não | Sim | Precisa de 4 grupos |
| DEZENA | Sim (2 dígitos) | Não | Últimos 2 dígitos |
| CENTENA | Sim (3 dígitos) | Não | Últimos 3 dígitos |
| MILHAR | Sim (4 dígitos) | Não | Número completo |
| DEZENA_INVERTIDA | Sim (2 dígitos) | Não | Permutações |
| CENTENA_INVERTIDA | Sim (3 dígitos) | Não | Permutações |
| MILHAR_INVERTIDA | Sim (4 dígitos) | Não | Permutações |
| PASSE | Não | Sim | Precisa de 2 grupos |
| PASSE_VAI_E_VEM | Não | Sim | Precisa de 2 grupos |

---

## 🔍 Debugging e Logs

### Ativar Logs Detalhados

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Verificar Resultados da API

```python
# Buscar e imprimir resultados
dados = sistema.buscar_resultados_organizados()
import json
print(json.dumps(dados, indent=2, ensure_ascii=False))
```

### Testar Conversão de Resultados

```python
from regras_liquidacao import converter_resultado_api_para_milhares

resultados = [
    {"numero": "4732", "posicao": 1},
    {"numero": "1234", "posicao": 2},
]

milhares = converter_resultado_api_para_milhares(resultados)
print(f"Milhares: {milhares}")  # [4732, 1234]
```

---

## ⚠️ Observações Importantes

### 1. Idempotência

O sistema não liquida a mesma aposta duas vezes. Certifique-se de que:
- Apostas já liquidadas têm `status != 'pendente'`
- Resultados já processados não são reprocessados

### 2. Sincronização

- A API retorna resultados organizados por sorteio único
- Cada sorteio é identificado por `(loteria, horario, data_extracao)`
- Apostas devem estar vinculadas ao sorteio correto

### 3. Posições

- Por padrão, o sistema usa posições 1º-7º
- Você pode especificar outras posições ao liquidar
- PASSE sempre usa 1º-2º

### 4. Validação

- Valide modalidades antes de criar apostas
- Verifique se grupos/números são válidos
- Confirme que a loteria e horário existem na API

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do sistema
2. Teste a API de resultados: `GET /api/resultados/organizados`
3. Verifique se as apostas estão com status correto
4. Confirme que a URL da API está acessível

---

## 🎉 Pronto!

Agora você tem um sistema completo de liquidação com todas as regras do Jogo do Bicho integrado com a API de resultados organizados!
