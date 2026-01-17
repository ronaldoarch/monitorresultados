# 🤖 Plano: Bot de Liquidação Automática de Apostas

## 📋 Objetivo

Transformar o monitor do Bicho Certo em um **bot automático** que:
1. ✅ Monitora resultados em tempo real
2. ✅ Identifica o horário correto de apuração (resultado sempre vem em minutos, nunca passa de 1h)
3. ✅ Vincula resultados às extrações corretas
4. ✅ Liquida apostas automaticamente com o resultado exato da extração

---

## 🎯 Resumo Executivo

### **Como Funciona:**

```
┌──────────────────────────────────────────────────────────────┐
│ SEU SITE                                                      │
│ ──────────────────────────────────────────────────────────── │
│ • Usuário faz aposta                                          │
│ • Envia para bot via API/webhook                              │
│ • Recebe liquidação quando resultado sair                     │
└──────────────────────────────────────────────────────────────┘
                        ↓ (POST /api/apostas/receber)
┌──────────────────────────────────────────────────────────────┐
│ BOT - RECEPÇÃO DE APOSTAS                                    │
│ ──────────────────────────────────────────────────────────── │
│ • Recebe aposta do seu site                                  │
│ • Cria registro no banco                                     │
│ • Mostra no painel do bot                                    │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ MONITOR (60s)                                                │
│ ──────────────────────────────────────────────────────────── │
│ • Coleta resultados do site bichocerto.com                 │
│ • Salva em resultados.json                                   │
│ • Roda continuamente em background                           │
└──────────────────────────────────────────────────────────────┘
                        ↓
┌──────────────────────────────────────────────────────────────┐
│ BOT DE LIQUIDAÇÃO (120s)                                     │
│ ──────────────────────────────────────────────────────────── │
│ 1. Carrega resultados.json (garante que está na API)        │
│ 2. Busca apostas pendentes do seu site                       │
│ 3. Faz matching: resultado ↔ aposta                          │
│ 4. Verifica se aposta ganhou                                 │
│ 5. Processa liquidação                                        │
│ 6. Envia liquidação de volta para seu site                   │
│ 7. Atualiza painel do bot                                    │
└──────────────────────────────────────────────────────────────┘
                        ↓ (POST /api/liquidacoes/enviar)
┌──────────────────────────────────────────────────────────────┐
│ SEU SITE                                                     │
│ ──────────────────────────────────────────────────────────── │
│ • Recebe liquidação                                           │
│ • Atualiza saldo do usuário                                  │
│ • Notifica usuário                                            │
└──────────────────────────────────────────────────────────────┘
```

### **Características Principais:**

- ⏱️ **Intervalo Monitor:** 60s (coleta resultados)
- ⏱️ **Intervalo Bot:** 120s (garante que resultado chegou na API)
- ⏱️ **Confirmação:** 120s após vincular antes de liquidar
- 📅 **Janela de Busca:** até 1 hora após `real_close_time` (por segurança)
- ✅ **Resultado sempre vem rápido:** minutos após `real_close_time` (nunca passa de 1h)

### **Estados da Extração:**

```
aberta → fechada → sorteada → liquidada
         ↑          ↑          ↑
    close_time   resultado   liquidação
                 vinculado   processada
```

---

## 🎯 Desafios e Soluções

### **Desafio 1: Identificar o Horário Real de Apuração**

**Problema:**
- O site do Bicho Certo tem horários de apuração que **sempre** aparecem em alguns minutos após o primeiro horário
- **NUNCA passa do prazo de 1 hora** - sempre vem rápido
- Exemplo: Se fecha às 11:00, o resultado pode sair entre 11:00 e 11:05 (geralmente)

**Solução Proposta:**
```
1. Monitor coleta resultados continuamente (a cada 60s)
2. Bot de liquidação verifica a cada 120s (2 minutos) para garantir que resultado chegou na API
3. Para cada resultado coletado:
   - Identificar loteria + horário nominal (ex: "11h")
   - Verificar timestamp do resultado
   - Buscar extrações que:
     * Loteria corresponde
     * Horário nominal corresponde
     * Timestamp do resultado está após close_time
     * Timestamp do resultado está dentro de 1 hora após real_close_time
     * Status = "fechada" ou "sorteada" (mas não "liquidada")
     * Ainda não tem resultado vinculado
4. Vincular resultado à extração correta
5. Aguardar 120s após vincular para garantir estabilidade antes de liquidar
```

---

### **Desafio 2: Vincular Resultado à Extração Correta**

**Problema:**
- Múltiplas extrações podem ter o mesmo horário nominal (ex: "11h" todos os dias)
- Precisamos garantir que o resultado de HOJE seja vinculado à extração de HOJE

**Solução Proposta:**
```
1. Usar data de extração (não apenas horário)
2. Comparar timestamp do resultado com:
   - close_time da extração
   - real_close_time da extração
3. Critérios de matching:
   - Loteria deve corresponder (com normalização)
   - Horário nominal deve corresponder
   - Data do resultado deve estar entre close_time e real_close_time + 1 hora
   - Extração deve estar com status "fechada" ou "sorteada"
   - Extração ainda não deve ter resultado vinculado
```

---

### **Desafio 3: Garantir que Resultado Chegou na API Antes de Liquidar**

**Problema:**
- Resultado pode ser coletado pelo monitor mas ainda não estar disponível na API
- Precisamos garantir estabilidade antes de processar liquidação
- Resultado sempre vem rápido (minutos), mas precisamos confirmar que está na API

**Solução Proposta:**
```
1. Monitor coleta resultados a cada 60s e salva em resultados.json
2. Bot de liquidação verifica a cada 120s (2 minutos):
   - Carrega resultados.json (garante que está na "API")
   - Busca extrações "fechadas" aguardando resultado
   - Para cada extração pendente:
     * Calcula janela: [close_time, real_close_time + 1 hora]
     * Busca resultados dentro da janela
     * Tenta vincular resultado à extração
3. Quando resultado encontrado e vinculado:
   - Marcar extração como "sorteada"
   - Aguardar próximo ciclo (120s) para garantir estabilidade
   - No próximo ciclo, verificar novamente se resultado ainda está vinculado
   - Se confirmado, processar liquidação das apostas
4. Se não encontrado após 1 hora:
   - Log de alerta (não deveria acontecer, mas por segurança)
   - Continuar monitorando
```

---

## 🏗️ Arquitetura Proposta

### **Fluxo Completo:**

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SISTEMA CRIA EXTRAÇÃO (Pré-criada)                       │
│    - Loteria: "PT RIO"                                       │
│    - Horário: "11:30"                                        │
│    - close_time: 2026-01-16 11:25:00                        │
│    - real_close_time: 2026-01-16 11:30:00                   │
│    - Status: "aberta"                                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. USUÁRIO FAZ APOSTA                                       │
│    - Vinculada a extraction_id                              │
│    - Status: "pendente"                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. HORÁRIO DE FECHAMENTO CHEGA                              │
│    - Sistema marca extração como "fechada"                  │
│    - Apostas não podem mais ser criadas                     │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. MONITOR COLETA RESULTADOS (A cada 60s)                  │
│    - Busca resultados no site bichocerto.com                │
│    - Salva em resultados.json                               │
│    - Cada resultado tem:                                    │
│      * loteria, horario, numero, animal                     │
│      * timestamp (quando foi coletado)                      │
│      * data_extracao                                        │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. BOT DE LIQUIDAÇÃO VERIFICA (A cada 120s)                 │
│    - Carrega resultados.json (garante que está na API)     │
│    - Busca extrações "fechadas" aguardando resultado        │
│    - Para cada extração:                                    │
│      * Calcula janela: [close_time, real_close_time + 1h] │
│      * Busca resultados dentro da janela                   │
│      * Tenta vincular resultado à extração                  │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. RESULTADO ENCONTRADO E VINCULADO                         │
│    - Resultado vinculado à extração                         │
│    - Extração marcada como "sorteada"                       │
│    - Aguarda próximo ciclo (120s) para garantir estabilidade│
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. CONFIRMAÇÃO E LIQUIDAÇÃO (Próximo ciclo - 120s depois) │
│    - Verifica se resultado ainda está vinculado             │
│    - Se confirmado, processa liquidação das apostas         │
│    - Atualiza saldos dos usuários                          │
│    - Cria registros de liquidação                          │
│    - Marca extração como "liquidada"                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes Necessários

### **1. Módulo de Matching de Resultados**

```python
class MatchingResultados:
    """
    Responsável por vincular resultados coletados às extrações corretas
    """
    
    def encontrar_extracao_para_resultado(self, resultado_dict):
        """
        Encontra a extração correta para um resultado coletado
        
        Critérios:
        1. Loteria deve corresponder (com normalização)
        2. Horário nominal deve corresponder
        3. Timestamp do resultado deve estar na janela válida
        4. Extração deve estar "fechada" ou "sorteada" (não liquidada)
        5. Extração ainda não deve ter resultado vinculado
        """
        pass
    
    def calcular_janela_tempo(self, extracao):
        """
        Calcula janela de tempo válida para buscar resultado:
        [close_time, real_close_time + 1 hora]
        """
        pass
```

### **2. Módulo de Processamento de Liquidação**

```python
class ProcessadorLiquidacao:
    """
    Processa liquidação após resultado ser vinculado à extração
    """
    
    def processar_liquidacao_extracao(self, extraction_id):
        """
        1. Busca todas apostas da extração com status "pendente"
        2. Compara cada aposta com o resultado
        3. Calcula ganhos conforme tipo de aposta
        4. Atualiza saldos
        5. Cria registros de liquidação
        6. Marca extração como "liquidada"
        """
        pass
```

### **3. Integração com Monitor**

```python
# Bot de liquidação roda em thread separada (120s)
def bot_liquidacao_loop(intervalo=120):
    """
    Loop do bot de liquidação - roda independente do monitor
    Verifica a cada 120s para garantir que resultados chegaram na API
    """
    while bot_rodando:
        try:
            # 1. Carregar resultados da API (resultados.json)
            resultados = carregar_resultados()
            
            # 2. Processar matching e liquidação
            processar_liquidacao_automatica(resultados)
            
        except Exception as e:
            logger.error(f"Erro no bot de liquidação: {e}")
        
        time.sleep(intervalo)

# Monitor continua rodando normalmente (60s)
def monitor_loop(intervalo=60):
    while monitor_rodando:
        verificar()  # Coleta e salva em resultados.json
        time.sleep(intervalo)
```

---

## 📊 Estrutura de Dados

### **Extração (já existe):**
```python
{
    "id": 123,
    "loteria": "PT RIO",
    "horario": "11:30",
    "close_time": "2026-01-16T11:25:00Z",
    "real_close_time": "2026-01-16T11:30:00Z",
    "status": "fechada"  # aberta → fechada → sorteada → liquidada
}
```

### **Resultado Coletado (do monitor):**
```python
{
    "loteria": "PT Rio de Janeiro",
    "horario": "11h",
    "numero": "1234",
    "animal": "Cavalo",
    "timestamp": "2026-01-16T11:32:15-03:00",
    "data_extracao": "16/01/2026"
}
```

### **Resultado Vinculado (no banco):**
```python
{
    "id": 456,
    "extraction_id": 123,  # VINCULADO À EXTRAÇÃO
    "numero": "1234",
    "animal": "Cavalo",
    "loteria": "PT RIO",
    "horario": "11:30",
    "timestamp": "2026-01-16T11:32:15Z",
    "processado": False
}
```

---

## 🎯 Algoritmo de Matching e Liquidação

### **Passo a Passo Detalhado:**

```python
def processar_liquidacao_automatica():
    """
    Executado a cada 120s pelo bot de liquidação
    """
    # 1. Carregar resultados da API (resultados.json)
    dados = carregar_resultados()
    resultados_coletados = dados.get('resultados', [])
    
    # 2. Buscar extrações aguardando resultado
    extracoes_pendentes = buscar_extracoes_pendentes()
    # Status: "fechada" ou "sorteada" (mas não "liquidada")
    # Ainda não tem resultado vinculado
    
    # 3. Para cada extração pendente
    for extracao in extracoes_pendentes:
        # 3.1. Calcular janela de tempo válida
        janela_inicio = extracao.close_time
        janela_fim = extracao.real_close_time + timedelta(hours=1)
        agora = datetime.now(ZoneInfo('America/Sao_Paulo'))
        
        # 3.2. Verificar se estamos dentro da janela
        if agora < janela_inicio:
            continue  # Ainda não chegou no horário de fechamento
        
        if agora > janela_fim:
            logger.warning(f"Extração {extracao.id} passou da janela de tempo")
            continue
        
        # 3.3. Buscar resultados candidatos
        resultados_candidatos = buscar_resultados_candidatos(
            resultados_coletados,
            extracao,
            janela_inicio,
            janela_fim
        )
        
        # 3.4. Se encontrou resultado e ainda não vinculou
        if resultados_candidatos and not extracao.resultado:
            resultado_escolhido = escolher_melhor_resultado(
                resultados_candidatos,
                extracao
            )
            
            # Vincular resultado à extração
            vincular_resultado_a_extracao(resultado_escolhido, extracao)
            logger.info(f"✅ Resultado vinculado à extração {extracao.id}")
        
        # 3.5. Se resultado já está vinculado, verificar liquidação
        elif extracao.resultado:
            # Verificar se já passou tempo suficiente desde vinculação
            tempo_desde_vinculacao = agora - extracao.resultado.timestamp
            
            if tempo_desde_vinculacao >= timedelta(seconds=120):
                # Confirmar que resultado ainda está na API
                if confirmar_resultado_na_api(extracao.resultado):
                    # Processar liquidação
                    processar_liquidacao_extracao(extracao.id)
                    logger.info(f"✅ Liquidação processada para extração {extracao.id}")


def buscar_resultados_candidatos(resultados_coletados, extracao, janela_inicio, janela_fim):
    """
    Busca resultados que podem ser vinculados à extração
    """
    candidatos = []
    
    for resultado in resultados_coletados:
        # 1. Normalizar loteria
        loteria_resultado = normalizar_loteria(resultado.get('loteria', ''))
        loteria_extracao = normalizar_loteria(extracao.loteria)
        
        if loteria_resultado != loteria_extracao:
            continue
        
        # 2. Normalizar horário
        horario_resultado = normalizar_horario(resultado.get('horario', ''))
        horario_extracao = normalizar_horario(extracao.horario)
        
        # Comparar horários (permitir pequena variação)
        if not horarios_compatíveis(horario_resultado, horario_extracao):
            continue
        
        # 3. Verificar timestamp
        timestamp_resultado = parsear_timestamp(resultado.get('timestamp'))
        if not timestamp_resultado:
            continue
        
        # Verificar se está na janela válida
        if janela_inicio <= timestamp_resultado <= janela_fim:
            candidatos.append(resultado)
    
    return candidatos


def vincular_resultado_a_extracao(resultado_dict, extracao):
    """
    Vincula resultado coletado à extração no banco
    """
    session = SistemaLiquidacaoExtractions.Session()
    try:
        # Criar registro Resultado
        resultado = Resultado(
            extraction_id=extracao.id,
            numero=resultado_dict.get('numero', ''),
            animal=resultado_dict.get('animal', ''),
            loteria=extracao.loteria,
            horario=extracao.horario,
            timestamp=parsear_timestamp(resultado_dict.get('timestamp')),
            processado=False
        )
        session.add(resultado)
        
        # Marcar extração como "sorteada"
        extracao.status = 'sorteada'
        
        session.commit()
        logger.info(f"✅ Resultado vinculado à extração {extracao.id}")
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erro ao vincular resultado: {e}")
        raise
    finally:
        session.close()


def processar_liquidacao_extracao(extraction_id):
    """
    Processa liquidação de todas as apostas de uma extração
    """
    sistema = SistemaLiquidacaoExtractions()
    sistema.processar_resultado_por_extracao(extraction_id)
```

---

## ⚙️ Configurações Necessárias

### **1. Janela de Tempo para Matching**

```python
# Configuração: quanto tempo após real_close_time ainda considerar válido?
JANELA_TEMPO_APOS_REAL_CLOSE = timedelta(hours=1)  # 1 hora

# Configuração: quanto tempo antes de close_time considerar resultado?
# (normalmente não, mas pode ser útil para testes)
JANELA_TEMPO_ANTES_CLOSE = timedelta(minutes=0)
```

### **2. Intervalo de Verificação**

```python
# Intervalo do monitor (coleta resultados)
INTERVALO_MONITOR = 60  # segundos (1 minuto)

# Intervalo do bot de liquidação (verifica e processa)
INTERVALO_BOT_LIQUIDACAO = 120  # segundos (2 minutos)
# Garante que resultado chegou na API antes de processar
```

### **3. Normalização de Loterias**

```python
MAPEAMENTO_LOTERIAS = {
    "PT Rio de Janeiro": "PT RIO",
    "PT Paraiba/Lotep": "PT LOTEP",
    "Loteria Nacional": "LOTERIA NACIONAL",
    # ... etc
}
```

---

## 🚨 Tratamento de Erros e Casos Especiais

### **Cenários Problemáticos:**

1. **Resultado não encontrado após 1 hora:**
   - **Não deveria acontecer** (resultado sempre vem rápido)
   - Log de alerta crítico
   - Continuar monitorando (pode ser delay do site)
   - Notificar administrador após 2 horas

2. **Múltiplos resultados candidatos:**
   - Escolher o mais próximo do `real_close_time`
   - Escolher o mais recente (timestamp mais próximo de agora)
   - Log de warning com detalhes
   - Registrar escolha para auditoria

3. **Resultado encontrado antes do `close_time`:**
   - Ignorar completamente (não processar)
   - Log de warning
   - Aguardar até após `close_time` para reprocessar

4. **Resultado duplicado:**
   - Verificar se já existe resultado para extração
   - Se já vinculado, ignorar duplicata
   - Log de info
   - Se não vinculado mas duplicado, escolher o mais completo

5. **Resultado desaparece da API após vinculação:**
   - No ciclo de confirmação (120s depois), verificar se ainda existe
   - Se não existir mais, manter vinculação mas não liquidar ainda
   - Aguardar próximo ciclo para tentar novamente
   - Log de warning

6. **Erro ao processar liquidação:**
   - Rollback da transação
   - Log de erro detalhado
   - Manter extração como "sorteada" (não "liquidada")
   - Tentar novamente no próximo ciclo

---

## 📐 Estrutura de Código Proposta

### **Arquivos a Criar/Modificar:**

```
monitorresultados-main/
├── bot_liquidacao.py              # NOVO: Bot principal de liquidação
├── matching_resultados.py         # NOVO: Lógica de matching
├── integracao_site.py             # NOVO: Integração com seu site
├── dashboard_bot.html              # NOVO: Painel do bot
├── app_vps.py                     # MODIFICAR: Adicionar thread do bot + endpoints
├── sistema_liquidacao_extractions.py  # USAR: Sistema existente
├── models.py                      # USAR: Modelos existentes
└── monitor_selenium.py            # USAR: Funções existentes
```

### **Estrutura do Bot de Liquidação:**

```python
# bot_liquidacao.py
class BotLiquidacao:
    """
    Bot automático de liquidação de apostas
    Roda em thread separada, verifica a cada 120s
    """
    
    def __init__(self, database_url='sqlite:///apostas.db', site_api_url=None):
        self.sistema = SistemaLiquidacaoExtractions(database_url)
        self.matching = MatchingResultados()
        self.integracao = IntegracaoSite(site_api_url)  # NOVO
        self.rodando = False
        self.thread = None
    
    def iniciar(self):
        """Inicia bot em thread separada"""
        pass
    
    def parar(self):
        """Para bot"""
        pass
    
    def loop(self, intervalo=120):
        """Loop principal - executa a cada 120s"""
        while self.rodando:
            try:
                # 1. Processar liquidação automática
                self.processar_liquidacao_automatica()
                
                # 2. Verificar apostas pendentes do site (opcional polling)
                self.verificar_apostas_site()
            except Exception as e:
                logger.error(f"Erro no bot: {e}")
            time.sleep(intervalo)
    
    def processar_liquidacao_automatica(self):
        """
        Processa liquidação automática:
        1. Carrega resultados da API
        2. Busca apostas pendentes
        3. Faz matching de resultados
        4. Processa liquidação
        5. Envia liquidação para o site
        """
        pass
    
    def verificar_apostas_site(self):
        """
        Verifica se há novas apostas no site (polling)
        Ou recebe via webhook (implementado em app_vps.py)
        """
        pass
```

### **Estrutura da Integração com Site:**

```python
# integracao_site.py
class IntegracaoSite:
    """
    Gerencia comunicação bidirecional com seu site
    """
    
    def __init__(self, site_api_url, api_key=None):
        self.site_api_url = site_api_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def receber_aposta(self, dados_aposta):
        """
        Recebe aposta do seu site (chamado via webhook)
        
        Formato esperado:
        {
            "aposta_id": 123,
            "usuario_id": 456,
            "numero": "1234",
            "animal": "Cavalo",
            "valor": 10.0,
            "loteria": "PT RIO",
            "horario": "11:30",
            "tipo_aposta": "grupo",
            "multiplicador": 18.0,
            "extraction_id": 789  # ID da extração no seu sistema
        }
        """
        pass
    
    def enviar_liquidacao(self, liquidacao):
        """
        Envia liquidação de volta para seu site
        
        Formato:
        {
            "aposta_id": 123,  # ID original do seu site
            "status": "ganhou" | "perdeu",
            "valor_ganho": 180.0,
            "resultado": {
                "numero": "1234",
                "animal": "Cavalo"
            },
            "timestamp": "2026-01-16T11:35:00Z"
        }
        """
        pass
    
    def buscar_apostas_pendentes(self):
        """
        Busca apostas pendentes do site (polling)
        Útil como fallback se webhook não funcionar
        """
        pass
```

### **Estrutura do Matching:**

```python
# matching_resultados.py
class MatchingResultados:
    """
    Responsável por vincular resultados coletados às extrações corretas
    """
    
    def buscar_extracoes_pendentes(self, session):
        """Busca extrações aguardando resultado"""
        pass
    
    def buscar_resultados_candidatos(self, resultados, extracao, janela_inicio, janela_fim):
        """Busca resultados que podem ser vinculados à extração"""
        pass
    
    def escolher_melhor_resultado(self, candidatos, extracao):
        """Escolhe o melhor resultado entre candidatos"""
        pass
    
    def vincular_resultado(self, resultado_dict, extracao, session):
        """Vincula resultado à extração no banco"""
        pass
    
    def confirmar_resultado_na_api(self, resultado_banco):
        """Confirma que resultado ainda está na API"""
        pass
    
    def horarios_compatíveis(self, horario1, horario2):
        """Verifica se dois horários são compatíveis"""
        pass
```

---

## 🔄 Fluxo Completo Detalhado

### **Timeline de Execução:**

```
T=0s    → Extração criada (status: "aberta")
T=300s  → Usuário faz aposta (vinculada à extração)
T=600s  → close_time chega → Extração marcada como "fechada"
T=630s  → real_close_time chega → Resultado pode aparecer
T=645s  → Monitor coleta resultado (salva em resultados.json)
T=660s  → Bot verifica (120s) → Encontra resultado → Vincula → Marca como "sorteada"
T=780s  → Bot verifica novamente (120s depois) → Confirma resultado → Processa liquidação
T=780s  → Apostas liquidadas → Saldos atualizados → Extração marcada como "liquidada"
```

### **Estados da Extração:**

```
aberta
  ↓ (close_time chega)
fechada
  ↓ (resultado encontrado e vinculado)
sorteada
  ↓ (liquidação processada)
liquidada
```

### **Estados da Aposta:**

```
pendente
  ↓ (liquidação processada)
ganhou / perdeu
```

---

## 🔗 Integração Bidirecional com Seu Site

### **Fluxo de Integração:**

```
┌─────────────────────────────────────────────────────────────┐
│ SEU SITE                                                    │
│ ─────────────────────────────────────────────────────────── │
│ 1. Usuário faz aposta                                       │
│ 2. Envia para bot via webhook ou API                        │
│ 3. Recebe confirmação de recebimento                       │
└─────────────────────────────────────────────────────────────┘
                        ↓ POST /api/apostas/receber
┌─────────────────────────────────────────────────────────────┐
│ BOT                                                          │
│ ─────────────────────────────────────────────────────────── │
│ 1. Recebe aposta                                            │
│ 2. Valida dados                                             │
│ 3. Salva no banco                                           │
│ 4. Mostra no painel do bot                                  │
│ 5. Retorna confirmação                                      │
└─────────────────────────────────────────────────────────────┘
                        ↓ (aguarda resultado)
┌─────────────────────────────────────────────────────────────┐
│ BOT - LIQUIDAÇÃO                                            │
│ ─────────────────────────────────────────────────────────── │
│ 1. Resultado coletado                                       │
│ 2. Verifica apostas pendentes                               │
│ 3. Compara resultado com apostas                           │
│ 4. Calcula ganhos                                           │
│ 5. Envia liquidação para seu site                           │
│ 6. Atualiza painel do bot                                   │
└─────────────────────────────────────────────────────────────┘
                        ↓ POST /api/liquidacoes/receber
┌─────────────────────────────────────────────────────────────┐
│ SEU SITE                                                    │
│ ─────────────────────────────────────────────────────────── │
│ 1. Recebe liquidação                                        │
│ 2. Atualiza saldo do usuário                                │
│ 3. Notifica usuário                                         │
│ 4. Retorna confirmação                                      │
└─────────────────────────────────────────────────────────────┘
```

### **Endpoints do Bot para Receber Apostas:**

```python
# app_vps.py

@app.route('/api/apostas/receber', methods=['POST'])
def receber_aposta_site():
    """
    Endpoint para receber apostas do seu site
    
    Formato esperado:
    {
        "aposta_id_externo": 123,  # ID da aposta no seu site
        "usuario_id": 456,
        "numero": "1234",
        "animal": "Cavalo",
        "valor": 10.0,
        "loteria": "PT RIO",
        "horario": "11:30",
        "tipo_aposta": "grupo",
        "multiplicador": 18.0,
        "extraction_id": 789,  # ID da extração (opcional)
        "timestamp": "2026-01-16T11:00:00Z"
    }
    """
    try:
        dados = request.json
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['aposta_id_externo', 'usuario_id', 'numero', 
                               'animal', 'valor', 'loteria', 'horario']
        for campo in campos_obrigatorios:
            if campo not in dados:
                return jsonify({
                    'sucesso': False,
                    'erro': f'Campo obrigatório ausente: {campo}'
                }), 400
        
        # Criar aposta no banco do bot
        aposta_id = bot_liquidacao.receber_aposta(dados)
        
        return jsonify({
            'sucesso': True,
            'aposta_id_bot': aposta_id,
            'mensagem': 'Aposta recebida com sucesso'
        })
        
    except Exception as e:
        logger.error(f"Erro ao receber aposta: {e}")
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500
```

### **Como Seu Site Envia Apostas:**

#### **Opção 1: Webhook (Recomendado - Tempo Real)**

```javascript
// No seu site, quando usuário faz aposta:
async function enviarApostaParaBot(aposta) {
    try {
        const response = await fetch('https://seu-bot.com/api/apostas/receber', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer SEU_TOKEN_AQUI'  // Se usar autenticação
            },
            body: JSON.stringify({
                aposta_id_externo: aposta.id,  // ID no seu sistema
                usuario_id: aposta.usuario_id,
                numero: aposta.numero,
                animal: aposta.animal,
                valor: aposta.valor,
                loteria: aposta.loteria,
                horario: aposta.horario,
                tipo_aposta: aposta.tipo_aposta || 'grupo',
                multiplicador: aposta.multiplicador || 18.0,
                extraction_id: aposta.extraction_id,  // Se tiver
                timestamp: new Date().toISOString()
            })
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            console.log('Aposta enviada para bot:', resultado.aposta_id_bot);
            // Salvar aposta_id_bot no seu banco para referência futura
        } else {
            console.error('Erro ao enviar aposta:', resultado.erro);
        }
        
        return resultado;
    } catch (error) {
        console.error('Erro ao enviar aposta para bot:', error);
        throw error;
    }
}
```

#### **Opção 2: Polling (Fallback)**

```python
# No bot, verifica periodicamente se há novas apostas
def verificar_apostas_site(self):
    """
    Busca apostas pendentes do seu site (polling)
    Útil como fallback se webhook não funcionar
    """
    try:
        response = self.integracao.session.get(
            f'{self.site_api_url}/api/apostas/pendentes',
            params={'ultima_verificacao': self.ultima_verificacao_apostas}
        )
        
        if response.status_code == 200:
            apostas = response.json().get('apostas', [])
            for aposta in apostas:
                self.receber_aposta(aposta)
            
            self.ultima_verificacao_apostas = datetime.now()
    except Exception as e:
        logger.error(f"Erro ao buscar apostas do site: {e}")
```

### **Enviar Liquidação de Volta para Seu Site:**

```python
# integracao_site.py

def enviar_liquidacao(self, liquidacao):
    """
    Envia liquidação de volta para seu site
    
    Formato:
    {
        "aposta_id_externo": 123,  # ID original do seu site
        "aposta_id_bot": 456,      # ID no bot (para referência)
        "status": "ganhou" | "perdeu",
        "valor_ganho": 180.0,
        "resultado": {
            "numero": "1234",
            "animal": "Cavalo",
            "posicao": 1
        },
        "timestamp": "2026-01-16T11:35:00Z",
        "detalhes": {
            "tipo_aposta": "grupo",
            "acertos": 1,
            "multiplicador": 18.0
        }
    }
    """
    try:
        response = self.session.post(
            f'{self.site_api_url}/api/liquidacoes/receber',
            json={
                'aposta_id_externo': liquidacao['aposta_id_externo'],
                'aposta_id_bot': liquidacao['aposta_id_bot'],
                'status': liquidacao['status'],
                'valor_ganho': liquidacao['valor_ganho'],
                'resultado': liquidacao['resultado'],
                'timestamp': liquidacao['timestamp'],
                'detalhes': liquidacao.get('detalhes', {})
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"✅ Liquidação enviada para site: aposta {liquidacao['aposta_id_externo']}")
            return True
        else:
            logger.error(f"❌ Erro ao enviar liquidação: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao enviar liquidação para site: {e}")
        return False
```

### **Endpoint no Seu Site para Receber Liquidação:**

```javascript
// No seu site, endpoint para receber liquidação do bot
app.post('/api/liquidacoes/receber', async (req, res) => {
    try {
        const { aposta_id_externo, status, valor_ganho, resultado } = req.body;
        
        // Buscar aposta no seu banco
        const aposta = await buscarAposta(aposta_id_externo);
        
        if (!aposta) {
            return res.status(404).json({ erro: 'Aposta não encontrada' });
        }
        
        // Atualizar status da aposta
        aposta.status = status;
        aposta.valor_ganho = valor_ganho;
        aposta.resultado = resultado;
        aposta.data_liquidacao = new Date();
        
        await salvarAposta(aposta);
        
        // Se ganhou, atualizar saldo do usuário
        if (status === 'ganhou') {
            await atualizarSaldo(aposta.usuario_id, valor_ganho);
            await notificarUsuario(aposta.usuario_id, {
                tipo: 'ganho',
                valor: valor_ganho,
                aposta: aposta
            });
        }
        
        res.json({ sucesso: true, mensagem: 'Liquidação processada' });
        
    } catch (error) {
        console.error('Erro ao receber liquidação:', error);
        res.status(500).json({ erro: 'Erro ao processar liquidação' });
    }
});
```

---

## 📊 Painel do Bot (Dashboard)

### **Funcionalidades do Painel:**

1. **Visualização de Apostas Recebidas:**
   - Lista todas as apostas recebidas do seu site
   - Status: pendente, ganhou, perdeu
   - Filtros por data, loteria, status

2. **Visualização de Liquidações:**
   - Histórico de liquidações processadas
   - Detalhes de cada liquidação
   - Estatísticas de ganhos/perdas

3. **Monitoramento em Tempo Real:**
   - Apostas recebidas em tempo real
   - Liquidações processadas em tempo real
   - Status do bot e monitor

4. **Estatísticas:**
   - Total de apostas recebidas
   - Total de liquidações processadas
   - Taxa de sucesso
   - Valor total liquidado

### **Estrutura do Dashboard:**

```html
<!-- dashboard_bot.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Painel do Bot - Liquidação Automática</title>
    <style>
        /* Estilos do dashboard */
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Cabeçalho -->
        <header>
            <h1>🤖 Bot de Liquidação Automática</h1>
            <div class="status">
                <span class="status-bot">Bot: <span id="status-bot">Ativo</span></span>
                <span class="status-monitor">Monitor: <span id="status-monitor">Ativo</span></span>
            </div>
        </header>
        
        <!-- Estatísticas -->
        <section class="stats">
            <div class="stat-card">
                <h3>Total de Apostas</h3>
                <p id="total-apostas">0</p>
            </div>
            <div class="stat-card">
                <h3>Liquidações Hoje</h3>
                <p id="liquidacoes-hoje">0</p>
            </div>
            <div class="stat-card">
                <h3>Valor Liquidado</h3>
                <p id="valor-liquidado">R$ 0,00</p>
            </div>
        </section>
        
        <!-- Tabela de Apostas -->
        <section class="apostas">
            <h2>Apostas Recebidas</h2>
            <table id="tabela-apostas">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Usuário</th>
                        <th>Número</th>
                        <th>Animal</th>
                        <th>Loteria</th>
                        <th>Horário</th>
                        <th>Valor</th>
                        <th>Status</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody id="tbody-apostas">
                    <!-- Preenchido via JavaScript -->
                </tbody>
            </table>
        </section>
        
        <!-- Tabela de Liquidações -->
        <section class="liquidacoes">
            <h2>Liquidações Processadas</h2>
            <table id="tabela-liquidacoes">
                <thead>
                    <tr>
                        <th>ID Aposta</th>
                        <th>Resultado</th>
                        <th>Status</th>
                        <th>Valor Ganho</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody id="tbody-liquidacoes">
                    <!-- Preenchido via JavaScript -->
                </tbody>
            </table>
        </section>
    </div>
    
    <script>
        // JavaScript para atualizar dashboard em tempo real
        async function atualizarDashboard() {
            // Buscar apostas
            const apostas = await fetch('/api/apostas/todas').then(r => r.json());
            atualizarTabelaApostas(apostas);
            
            // Buscar liquidações
            const liquidacoes = await fetch('/api/liquidacoes/todas').then(r => r.json());
            atualizarTabelaLiquidacoes(liquidacoes);
            
            // Buscar estatísticas
            const stats = await fetch('/api/stats').then(r => r.json());
            atualizarEstatisticas(stats);
        }
        
        // Atualizar a cada 5 segundos
        setInterval(atualizarDashboard, 5000);
        atualizarDashboard(); // Primeira carga
    </script>
</body>
</html>
```

### **Endpoints do Dashboard:**

```python
# app_vps.py

@app.route('/dashboard-bot')
def dashboard_bot():
    """Renderiza painel do bot"""
    return send_from_directory('.', 'dashboard_bot.html')

@app.route('/api/apostas/todas')
def api_apostas_todas():
    """Retorna todas as apostas para o dashboard"""
    session = bot_liquidacao.sistema.Session()
    try:
        apostas = session.query(Aposta).order_by(Aposta.data_aposta.desc()).limit(100).all()
        return jsonify({
            'apostas': [{
                'id': a.id,
                'aposta_id_externo': a.aposta_id_externo,
                'usuario_id': a.usuario_id,
                'numero': a.numero,
                'animal': a.animal,
                'loteria': a.loteria,
                'horario': a.horario,
                'valor': a.valor,
                'status': a.status,
                'data_aposta': a.data_aposta.isoformat()
            } for a in apostas]
        })
    finally:
        session.close()

@app.route('/api/liquidacoes/todas')
def api_liquidacoes_todas():
    """Retorna todas as liquidações para o dashboard"""
    session = bot_liquidacao.sistema.Session()
    try:
        liquidacoes = session.query(Liquidacao).join(Aposta).order_by(
            Liquidacao.data_liquidacao.desc()
        ).limit(100).all()
        return jsonify({
            'liquidacoes': [{
                'aposta_id': l.aposta_id,
                'aposta_id_externo': l.aposta.aposta_id_externo,
                'status': l.aposta.status,
                'valor_ganho': l.valor_ganho,
                'data_liquidacao': l.data_liquidacao.isoformat()
            } for l in liquidacoes]
        })
    finally:
        session.close()

@app.route('/api/stats')
def api_stats():
    """Retorna estatísticas para o dashboard"""
    session = bot_liquidacao.sistema.Session()
    try:
        total_apostas = session.query(Aposta).count()
        liquidacoes_hoje = session.query(Liquidacao).filter(
            func.date(Liquidacao.data_liquidacao) == func.date('now')
        ).count()
        valor_liquidado = session.query(func.sum(Liquidacao.valor_ganho)).filter(
            func.date(Liquidacao.data_liquidacao) == func.date('now')
        ).scalar() or 0
        
        return jsonify({
            'total_apostas': total_apostas,
            'liquidacoes_hoje': liquidacoes_hoje,
            'valor_liquidado': float(valor_liquidado)
        })
    finally:
        session.close()
```

---

## 📝 Próximos Passos (Sem Modificar Código Ainda)

### **Fase 1: Análise e Planejamento** ✅ (Este documento)

### **Fase 2: Implementação**
1. Criar módulo `matching_resultados.py`
   - Funções de matching
   - Normalização de loterias e horários
   - Validação de janelas de tempo

2. Criar módulo `bot_liquidacao.py`
   - Classe BotLiquidacao
   - Loop principal (120s)
   - Integração com sistema existente

3. Modificar `app_vps.py`
   - Adicionar thread do bot
   - Iniciar bot junto com monitor
   - Endpoint de status do bot

4. Testes unitários
   - Testar matching de resultados
   - Testar vinculação de extrações
   - Testar processamento de liquidação

### **Fase 3: Testes Integrados**
1. Testar fluxo completo com dados reais
2. Testar tratamento de erros
3. Testar performance com múltiplas extrações simultâneas
4. Testar cenários de edge cases

### **Fase 4: Monitoramento e Logs**
1. Adicionar logs detalhados em cada etapa
2. Criar dashboard de liquidações
3. Alertas para problemas críticos
4. Métricas de performance

---

## ✅ Decisões Tomadas

1. **Prazo para resultado aparecer:**
   - ✅ Resultado **sempre** vem em alguns minutos (nunca passa de 1 hora)
   - ✅ Janela de busca: até 1 hora após `real_close_time` (por segurança)
   - ✅ Se não aparecer após 1 hora: log de alerta, continuar monitorando

2. **Resultados coletados antes do `close_time`:**
   - ✅ Ignorar completamente (não processar)
   - ✅ Aguardar até após `close_time` para considerar válido

3. **Frequência de verificação:**
   - ✅ Monitor: 60s (coleta resultados)
   - ✅ Bot de liquidação: **120s** (garante que resultado chegou na API)
   - ✅ Após vincular resultado: aguardar 120s antes de liquidar (confirmação)

4. **Identificar horário quando resultado tem apenas "11h":**
   - ✅ Usar função `normalizar_horario()` existente
   - ✅ Comparar com horários das extrações (permitir pequena variação)
   - ✅ Escolher extração com horário mais próximo

5. **Garantir resultado na API:**
   - ✅ Bot carrega `resultados.json` diretamente (garante que está na API)
   - ✅ Aguardar 120s após vinculação antes de liquidar
   - ✅ Verificar novamente no ciclo de confirmação

---

## 📚 Referências

- `sistema_liquidacao_extractions.py` - Sistema atual de liquidação
- `models.py` - Modelos de banco de dados
- `monitor_selenium.py` - Monitor de resultados
- `app_vps.py` - Aplicação principal

---

**Status:** 📋 Planejamento Completo - Aguardando Aprovação para Implementação
