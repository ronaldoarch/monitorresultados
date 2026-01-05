# 🚀 Próximos Passos - Após Configurar Variável

## ✅ Você Já Fez:
- [x] Adicionou variável `ENDPOINT_PHP`

## 📋 O Que Fazer Agora:

### 1. Testar Endpoint PHP

```bash
# Testar se endpoint responde
curl -X POST $ENDPOINT_PHP
```

**Ou se não tiver a variável no terminal:**

```bash
curl -X POST https://lotbicho.com/backend/scraper/processar-resultados-completo.php
```

**Deve retornar JSON com `"success": true`**

---

### 2. Iniciar Servidor

```bash
# Ativar venv (se necessário)
source venv/bin/activate

# Iniciar servidor
python3 integracao_endpoint_php.py --auto --intervalo 5 --port 5001
```

**Isso vai:**
- ✅ Iniciar servidor na porta 5001
- ✅ Chamar endpoint PHP a cada 5 minutos automaticamente
- ✅ Processar resultados

---

### 3. Testar API (Em Outro Terminal)

```bash
# Testar processamento manual
curl -X POST http://localhost:5001/api/resultados/processar

# Listar resultados
curl http://localhost:5001/api/resultados

# Ver status
curl http://localhost:5001/api/status

# Status do processamento automático
curl http://localhost:5001/api/processamento/status
```

---

### 4. Verificar Logs

No terminal onde o servidor está rodando, você deve ver:

```
🚀 Servidor iniciando em http://0.0.0.0:5001
📡 Endpoint PHP: https://lotbicho.com/...
✅ Processamento automático iniciado (a cada 5 minutos)

⏰ [2026-01-05 16:30:00] Processamento automático...
🔄 Chamando endpoint PHP: https://...
✅ 15 resultados salvos
✅ 12 extrações sincronizadas
✅ 5 apostas processadas
💰 2 ganhas, 3 perdidas
```

---

### 5. Integrar com Frontend (Se Necessário)

Se seu frontend precisa acessar a API:

```javascript
// No seu frontend
const API_URL = 'http://seu-servidor:5001/api';

// Processar resultados
async function processarResultados() {
    const response = await fetch(`${API_URL}/resultados/processar`, {
        method: 'POST'
    });
    const data = await response.json();
    
    if (data.sucesso) {
        console.log('Resultados processados:', data.resultados);
        console.log('Resumo:', data.summary);
    }
}

// Listar resultados
async function listarResultados() {
    const response = await fetch(`${API_URL}/resultados`);
    const data = await response.json();
    return data.resultados;
}
```

---

### 6. Deploy no Coolify (Se Ainda Não Fez)

1. **No Coolify, adicionar variável de ambiente:**
   - Nome: `ENDPOINT_PHP`
   - Valor: `https://lotbicho.com/backend/scraper/processar-resultados-completo.php`

2. **Atualizar Dockerfile ou usar app_vps.py:**
   - Se usar `integracao_endpoint_php.py`, atualize o Dockerfile
   - Ou continue usando `app_vps.py` e adicione a rota

3. **Fazer redeploy**

---

## ✅ Checklist de Verificação

- [ ] Endpoint PHP testado e funcionando
- [ ] Servidor Python iniciado
- [ ] API respondendo (teste com curl)
- [ ] Processamento automático ativo
- [ ] Logs mostrando processamento
- [ ] Frontend integrado (se necessário)
- [ ] Deploy no Coolify (se necessário)

---

## 🎯 Comandos Rápidos

```bash
# 1. Testar endpoint
curl -X POST $ENDPOINT_PHP

# 2. Iniciar servidor
python3 integracao_endpoint_php.py --auto --intervalo 5 --port 5001

# 3. Testar API
curl http://localhost:5001/api/resultados

# 4. Ver status
curl http://localhost:5001/api/processamento/status
```

---

## 🔧 Se Algo Não Funcionar

### Endpoint não responde?
```bash
# Verificar URL
echo $ENDPOINT_PHP

# Testar manualmente
curl -v -X POST $ENDPOINT_PHP
```

### Servidor não inicia?
```bash
# Verificar dependências
pip install requests schedule flask flask-cors

# Verificar se porta está livre
lsof -i :5001
```

### API não funciona?
```bash
# Verificar se servidor está rodando
ps aux | grep integracao_endpoint_php

# Verificar logs
# (veja o terminal onde iniciou o servidor)
```

---

## 🎉 Pronto!

Após seguir esses passos, seu sistema estará:
- ✅ Chamando endpoint PHP automaticamente
- ✅ Processando resultados
- ✅ Liquidando apostas
- ✅ Expondo API para frontend

Boa sorte! 🚀

