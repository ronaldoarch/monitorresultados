# 🔗 Guia de Integração - Bot de Liquidação Automática

## 📋 Visão Geral

Este guia mostra como integrar seu site com o bot de liquidação automática. O bot recebe apostas do seu site e envia liquidações de volta quando os resultados saem.

---

## 🚀 Configuração Inicial

### **1. Configurar Variáveis de Ambiente no Bot**

No servidor onde o bot está rodando, configure:

```bash
# URL da API do seu site (onde o bot vai enviar liquidações)
export SITE_API_URL="https://seu-site.com"

# Chave de API (opcional, para autenticação)
export SITE_API_KEY="sua-chave-secreta-aqui"

# Banco de dados (opcional, padrão: sqlite:///apostas.db)
export BOT_DATABASE_URL="sqlite:///apostas.db"

# Iniciar bot automaticamente (padrão: true)
export BOT_AUTO_START="true"
```

### **2. Verificar se Bot Está Rodando**

Acesse: `https://seu-bot.com/api/status`

Você deve ver:
```json
{
  "bot_ativo": true,
  "bot_disponivel": true,
  ...
}
```

---

## 📤 Enviar Apostas para o Bot

### **Endpoint do Bot:**

```
POST https://seu-bot.com/api/apostas/receber
Content-Type: application/json
```

### **Formato da Requisição:**

```json
{
  "aposta_id_externo": "123",        // ID da aposta no seu sistema (obrigatório)
  "usuario_id": 456,                  // ID do usuário (obrigatório)
  "numero": "1234",                   // Número apostado (obrigatório)
  "animal": "Cavalo",                 // Animal apostado (obrigatório)
  "valor": 10.0,                      // Valor da aposta (obrigatório)
  "loteria": "PT RIO",                // Nome da loteria (obrigatório)
  "horario": "11:30",                 // Horário do sorteio (obrigatório)
  "tipo_aposta": "grupo",             // Tipo: grupo, dezena, centena, milhar (opcional)
  "multiplicador": 18.0,              // Multiplicador de ganho (opcional, padrão: 18.0)
  "extraction_id": 789                // ID da extração (opcional)
}
```

### **Resposta de Sucesso:**

```json
{
  "sucesso": true,
  "aposta_id_bot": 456,
  "mensagem": "Aposta recebida com sucesso"
}
```

### **Resposta de Erro:**

```json
{
  "sucesso": false,
  "erro": "Campo obrigatório ausente: numero"
}
```

---

## 💻 Código de Integração (JavaScript)

### **Exemplo Completo:**

```javascript
// config.js - Configuração
const BOT_API_URL = 'https://seu-bot.com/api';
const BOT_API_KEY = 'sua-chave-secreta-aqui'; // Se usar autenticação

// api.js - Função para enviar aposta
async function enviarApostaParaBot(aposta) {
    try {
        const response = await fetch(`${BOT_API_URL}/apostas/receber`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${BOT_API_KEY}` // Se usar autenticação
            },
            body: JSON.stringify({
                aposta_id_externo: aposta.id.toString(), // ID no seu sistema
                usuario_id: aposta.usuario_id,
                numero: aposta.numero.padStart(4, '0'), // Garantir 4 dígitos
                animal: aposta.animal,
                valor: parseFloat(aposta.valor),
                loteria: aposta.loteria,
                horario: aposta.horario,
                tipo_aposta: aposta.tipo_aposta || 'grupo',
                multiplicador: parseFloat(aposta.multiplicador) || 18.0,
                extraction_id: aposta.extraction_id // Se tiver
            })
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            console.log('✅ Aposta enviada para bot:', resultado.aposta_id_bot);
            
            // Salvar aposta_id_bot no seu banco para referência futura
            await salvarApostaIdBot(aposta.id, resultado.aposta_id_bot);
            
            return resultado;
        } else {
            console.error('❌ Erro ao enviar aposta:', resultado.erro);
            throw new Error(resultado.erro);
        }
    } catch (error) {
        console.error('❌ Erro ao enviar aposta para bot:', error);
        throw error;
    }
}

// Exemplo de uso quando usuário faz aposta
async function fazerAposta(usuarioId, numero, animal, valor, loteria, horario) {
    try {
        // 1. Criar aposta no seu sistema
        const aposta = await criarApostaNoSistema({
            usuario_id: usuarioId,
            numero: numero,
            animal: animal,
            valor: valor,
            loteria: loteria,
            horario: horario,
            status: 'pendente'
        });
        
        // 2. Enviar para o bot
        await enviarApostaParaBot({
            id: aposta.id,
            usuario_id: usuarioId,
            numero: numero,
            animal: animal,
            valor: valor,
            loteria: loteria,
            horario: horario
        });
        
        return aposta;
    } catch (error) {
        console.error('Erro ao fazer aposta:', error);
        throw error;
    }
}
```

---

## 📥 Receber Liquidações do Bot

### **Endpoint no Seu Site:**

O bot vai enviar liquidações para:

```
POST https://seu-site.com/api/liquidacoes/receber
Content-Type: application/json
```

### **Formato que o Bot Envia:**

```json
{
  "aposta_id_externo": "123",        // ID original da aposta no seu sistema
  "aposta_id_bot": 456,              // ID da aposta no bot (para referência)
  "status": "ganhou",                // "ganhou" ou "perdeu"
  "valor_ganho": 180.0,              // Valor ganho (0.0 se perdeu)
  "resultado": {
    "numero": "1234",
    "animal": "Cavalo",
    "posicao": 1
  },
  "timestamp": "2026-01-16T11:35:00Z",
  "detalhes": {
    "tipo_aposta": "grupo",
    "multiplicador": 18.0
  }
}
```

### **Código para Receber Liquidação (Node.js/Express):**

```javascript
// routes/liquidacoes.js
app.post('/api/liquidacoes/receber', async (req, res) => {
    try {
        const {
            aposta_id_externo,
            aposta_id_bot,
            status,
            valor_ganho,
            resultado,
            timestamp,
            detalhes
        } = req.body;
        
        // Validar dados
        if (!aposta_id_externo || !status) {
            return res.status(400).json({
                sucesso: false,
                erro: 'Campos obrigatórios ausentes'
            });
        }
        
        // Buscar aposta no seu banco
        const aposta = await buscarApostaPorId(aposta_id_externo);
        
        if (!aposta) {
            return res.status(404).json({
                sucesso: false,
                erro: 'Aposta não encontrada'
            });
        }
        
        // Atualizar status da aposta
        aposta.status = status;
        aposta.valor_ganho = valor_ganho;
        aposta.resultado = resultado;
        aposta.data_liquidacao = new Date(timestamp);
        aposta.aposta_id_bot = aposta_id_bot; // Salvar referência
        
        await salvarAposta(aposta);
        
        // Se ganhou, atualizar saldo do usuário
        if (status === 'ganhou' && valor_ganho > 0) {
            await atualizarSaldo(aposta.usuario_id, valor_ganho);
            
            // Criar transação de ganho
            await criarTransacao({
                usuario_id: aposta.usuario_id,
                tipo: 'ganho',
                valor: valor_ganho,
                descricao: `Ganho na aposta #${aposta.id} - ${resultado.numero} ${resultado.animal}`,
                status: 'concluida'
            });
            
            // Notificar usuário
            await notificarUsuario(aposta.usuario_id, {
                tipo: 'ganho',
                titulo: '🎉 Você ganhou!',
                mensagem: `Parabéns! Você ganhou R$ ${valor_ganho.toFixed(2)} na aposta #${aposta.id}`,
                aposta: aposta
            });
        }
        
        res.json({
            sucesso: true,
            mensagem: 'Liquidação processada com sucesso'
        });
        
    } catch (error) {
        console.error('Erro ao receber liquidação:', error);
        res.status(500).json({
            sucesso: false,
            erro: 'Erro ao processar liquidação'
        });
    }
});
```

### **Código para Receber Liquidação (PHP):**

```php
<?php
// api/liquidacoes/receber.php

header('Content-Type: application/json');

$dados = json_decode(file_get_contents('php://input'), true);

// Validar dados
if (!isset($dados['aposta_id_externo']) || !isset($dados['status'])) {
    http_response_code(400);
    echo json_encode([
        'sucesso' => false,
        'erro' => 'Campos obrigatórios ausentes'
    ]);
    exit;
}

$aposta_id_externo = $dados['aposta_id_externo'];
$status = $dados['status'];
$valor_ganho = floatval($dados['valor_ganho'] ?? 0);
$resultado = $dados['resultado'] ?? [];
$timestamp = $dados['timestamp'] ?? date('c');

try {
    // Buscar aposta no banco
    $aposta = buscarApostaPorId($aposta_id_externo);
    
    if (!$aposta) {
        http_response_code(404);
        echo json_encode([
            'sucesso' => false,
            'erro' => 'Aposta não encontrada'
        ]);
        exit;
    }
    
    // Atualizar aposta
    atualizarAposta($aposta_id_externo, [
        'status' => $status,
        'valor_ganho' => $valor_ganho,
        'resultado' => json_encode($resultado),
        'data_liquidacao' => $timestamp,
        'aposta_id_bot' => $dados['aposta_id_bot'] ?? null
    ]);
    
    // Se ganhou, atualizar saldo
    if ($status === 'ganhou' && $valor_ganho > 0) {
        atualizarSaldo($aposta['usuario_id'], $valor_ganho);
        
        // Criar transação
        criarTransacao([
            'usuario_id' => $aposta['usuario_id'],
            'tipo' => 'ganho',
            'valor' => $valor_ganho,
            'descricao' => "Ganho na aposta #{$aposta_id_externo}",
            'status' => 'concluida'
        ]);
        
        // Notificar usuário (opcional)
        notificarUsuario($aposta['usuario_id'], [
            'tipo' => 'ganho',
            'mensagem' => "Parabéns! Você ganhou R$ " . number_format($valor_ganho, 2, ',', '.')
        ]);
    }
    
    echo json_encode([
        'sucesso' => true,
        'mensagem' => 'Liquidação processada com sucesso'
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'sucesso' => false,
        'erro' => 'Erro ao processar liquidação: ' . $e->getMessage()
    ]);
}
?>
```

---

## 🔍 Verificar Status

### **Painel do Bot:**

Acesse: `https://seu-bot.com/dashboard-bot`

Você verá:
- Total de apostas recebidas
- Liquidações processadas hoje
- Valor total liquidado
- Lista de todas as apostas
- Histórico de liquidações

### **API de Status:**

```javascript
// Verificar status do bot
async function verificarStatusBot() {
    const response = await fetch('https://seu-bot.com/api/status');
    const status = await response.json();
    
    console.log('Bot ativo:', status.bot_ativo);
    console.log('Monitor ativo:', status.monitor_rodando);
    console.log('Total de resultados:', status.total_resultados);
    
    return status;
}
```

---

## 🧪 Testar Integração

### **1. Testar Envio de Aposta:**

```javascript
// Teste simples
const apostaTeste = {
    aposta_id_externo: 'TESTE-001',
    usuario_id: 1,
    numero: '1234',
    animal: 'Cavalo',
    valor: 10.0,
    loteria: 'PT RIO',
    horario: '11:30',
    tipo_aposta: 'grupo',
    multiplicador: 18.0
};

enviarApostaParaBot(apostaTeste)
    .then(resultado => {
        console.log('✅ Teste OK:', resultado);
    })
    .catch(erro => {
        console.error('❌ Teste falhou:', erro);
    });
```

### **2. Verificar se Aposta Foi Recebida:**

Acesse: `https://seu-bot.com/dashboard-bot`

Você deve ver a aposta na lista.

---

## ⚠️ Tratamento de Erros

### **Erros Comuns:**

1. **Bot não está rodando:**
   - Verificar: `https://seu-bot.com/api/status`
   - Verificar logs do bot
   - Reiniciar bot se necessário

2. **Aposta não é recebida:**
   - Verificar formato JSON
   - Verificar campos obrigatórios
   - Verificar logs do bot

3. **Liquidação não chega:**
   - Verificar se endpoint `/api/liquidacoes/receber` está funcionando
   - Verificar logs do bot
   - Verificar se resultado foi coletado

---

## 📞 Suporte

Se tiver problemas:
1. Verificar logs do bot
2. Verificar status: `/api/status`
3. Verificar painel: `/dashboard-bot`
4. Verificar se monitor está coletando resultados

---

**Pronto!** Agora seu site está integrado com o bot de liquidação automática! 🎉
