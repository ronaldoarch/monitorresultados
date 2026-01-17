# 🔗 URL do Bot - Configuração para Seu Site

## 📋 Sua URL do Bot

**URL Base:** `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com`

**URL da API:** `https://okgkgswwkk8ows0csow0csow0c4gg.agenciamidas.com/api`

---

## ⚙️ Configurar no Seu Site

### **Variável de Ambiente:**

```bash
BOT_API_URL=https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api
```

### **No Código:**

**JavaScript:**
```javascript
const BOT_API_URL = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api';
```

**PHP:**
```php
define('BOT_API_URL', 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api');
```

**Python:**
```python
BOT_API_URL = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api'
```

---

## 📤 Endpoint para Enviar Apostas

```
POST https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/apostas/receber
```

### **Exemplo de Código:**

```javascript
async function enviarApostaParaBot(aposta) {
    const response = await fetch('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/apostas/receber', {
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
    
    return await response.json();
}
```

---

## 📥 Endpoint para Receber Liquidações

No seu site, crie:

```
POST https://seu-site.com/api/liquidacoes/receber
```

O bot vai enviar liquidações para este endpoint quando os resultados saírem.

---

## ✅ Verificar se Está Funcionando

### **1. Testar Status do Bot:**

```bash
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/status
```

### **2. Ver Painel do Bot:**

Acesse: `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/dashboard-bot`

---

## 🎯 Resumo

- **URL Base:** `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com`
- **API:** `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api`
- **Enviar Apostas:** `POST /api/apostas/receber`
- **Painel:** `/dashboard-bot`

**Configure no seu site:**
```bash
BOT_API_URL=https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api
```

Pronto! 🚀
