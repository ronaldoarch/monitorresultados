# 🔗 Configurar URL do Bot no Seu Site

## 📋 O Que Você Precisa Configurar

Seu site precisa saber **para onde enviar as apostas**. Configure a URL do bot:

---

## ⚙️ Configuração

### **1. Descobrir a URL do Bot**

A URL do bot é o endereço onde você fez deploy no Coolify, por exemplo:
- `https://seu-bot.com`
- `https://bot.seudominio.com`
- `https://monitor-resultados.seudominio.com`

### **2. Configurar no Seu Site**

#### **Opção A: Variável de Ambiente (Recomendado)**

**Node.js/Express:**
```javascript
// .env ou variável de ambiente
BOT_API_URL=https://seu-bot.com/api
```

**PHP:**
```php
// config.php ou .env
define('BOT_API_URL', 'https://seu-bot.com/api');
```

**Python:**
```python
# .env ou variável de ambiente
BOT_API_URL=https://seu-bot.com/api
```

#### **Opção B: Arquivo de Configuração**

**JavaScript:**
```javascript
// config.js
const BOT_API_URL = 'https://seu-bot.com/api';
```

**PHP:**
```php
// config.php
$BOT_API_URL = 'https://seu-bot.com/api';
```

---

## 📝 Exemplo Completo de Integração

### **JavaScript/Node.js:**

```javascript
// config.js
const BOT_API_URL = process.env.BOT_API_URL || 'https://seu-bot.com/api';

// api.js
async function enviarApostaParaBot(aposta) {
    try {
        const response = await fetch(`${BOT_API_URL}/apostas/receber`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                aposta_id_externo: aposta.id.toString(),
                usuario_id: aposta.usuario_id,
                numero: aposta.numero.padStart(4, '0'),
                animal: aposta.animal,
                valor: parseFloat(aposta.valor),
                loteria: aposta.loteria,
                horario: aposta.horario,
                tipo_aposta: aposta.tipo_aposta || 'grupo',
                multiplicador: parseFloat(aposta.multiplicador) || 18.0
            })
        });
        
        const resultado = await response.json();
        
        if (resultado.sucesso) {
            console.log('✅ Aposta enviada para bot:', resultado.aposta_id_bot);
            return resultado;
        } else {
            throw new Error(resultado.erro);
        }
    } catch (error) {
        console.error('❌ Erro ao enviar aposta para bot:', error);
        throw error;
    }
}
```

### **PHP:**

```php
<?php
// config.php
define('BOT_API_URL', 'https://seu-bot.com/api');

// api_bot.php
function enviarApostaParaBot($aposta) {
    $url = BOT_API_URL . '/apostas/receber';
    
    $data = [
        'aposta_id_externo' => (string)$aposta['id'],
        'usuario_id' => $aposta['usuario_id'],
        'numero' => str_pad($aposta['numero'], 4, '0', STR_PAD_LEFT),
        'animal' => $aposta['animal'],
        'valor' => (float)$aposta['valor'],
        'loteria' => $aposta['loteria'],
        'horario' => $aposta['horario'],
        'tipo_aposta' => $aposta['tipo_aposta'] ?? 'grupo',
        'multiplicador' => (float)($aposta['multiplicador'] ?? 18.0)
    ];
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200) {
        $resultado = json_decode($response, true);
        if ($resultado['sucesso']) {
            return $resultado;
        } else {
            throw new Exception($resultado['erro']);
        }
    } else {
        throw new Exception("Erro HTTP: $httpCode");
    }
}
?>
```

---

## ✅ Verificar se Está Funcionando

### **1. Testar Conexão:**

```bash
# Testar se bot está acessível
curl https://seu-bot.com/api/status
```

Deve retornar:
```json
{
  "bot_ativo": true,
  "bot_disponivel": true,
  ...
}
```

### **2. Testar Envio de Aposta:**

```javascript
// Teste simples
const apostaTeste = {
    id: 'TESTE-001',
    usuario_id: 1,
    numero: '1234',
    animal: 'Cavalo',
    valor: 10.0,
    loteria: 'PT RIO',
    horario: '11:30'
};

enviarApostaParaBot(apostaTeste)
    .then(resultado => {
        console.log('✅ Teste OK:', resultado);
    })
    .catch(erro => {
        console.error('❌ Teste falhou:', erro);
    });
```

---

## 🔍 Troubleshooting

### **Erro: "Network error" ou "Connection refused"**

**Verificar:**
1. URL do bot está correta?
2. Bot está rodando? (acesse `/api/status`)
3. Firewall permite conexão?

### **Erro: "404 Not Found"**

**Verificar:**
1. URL está completa? (`https://seu-bot.com/api/apostas/receber`)
2. Endpoint existe? (deve ser `/api/apostas/receber`)

### **Erro: "CORS"**

**Solução:**
O bot já tem CORS habilitado. Se ainda der erro, verifique se a URL está correta.

---

## 📋 Checklist

- [ ] Descobriu a URL do bot (ex: `https://seu-bot.com`)
- [ ] Configurou variável `BOT_API_URL` no site
- [ ] Testou conexão: `curl https://seu-bot.com/api/status`
- [ ] Testou envio de aposta
- [ ] Verificou se aposta aparece no painel: `https://seu-bot.com/dashboard-bot`

---

## 🎯 Resumo

**URL Base do Bot:** `https://seu-bot.com`  
**Endpoint para Enviar Apostas:** `https://seu-bot.com/api/apostas/receber`  
**Endpoint para Receber Liquidações:** `https://seu-site.com/api/liquidacoes/receber`

**Configure no seu site:**
```bash
BOT_API_URL=https://seu-bot.com/api
```

**Pronto!** Agora seu site pode enviar apostas para o bot! 🚀
