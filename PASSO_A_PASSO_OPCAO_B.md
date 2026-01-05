# 🚀 Passo a Passo - Opção B (Endpoint PHP)

## ✅ O Que Vamos Fazer

Configurar o sistema Python para chamar o endpoint PHP do painel que já faz tudo.

## 📋 Passo 1: Configurar URL do Endpoint

### Editar arquivo:

```bash
# Abrir arquivo
nano integracao_endpoint_php.py
```

### Localizar linha 20 e ajustar:

```python
ENDPOINT_PHP = 'https://lotbicho.com/backend/scraper/processar-resultados-completo.php'
```

**Substitua pela URL correta do seu endpoint PHP.**

---

## 📋 Passo 2: Testar Endpoint PHP

```bash
# Testar se endpoint responde
curl -X POST https://lotbicho.com/backend/scraper/processar-resultados-completo.php
```

**Deve retornar JSON com `"success": true`**

Se der erro, verifique:
- URL está correta?
- Endpoint está acessível?
- Precisa de autenticação?

---

## 📋 Passo 3: Instalar Dependências

```bash
# Ativar venv
source venv/bin/activate

# Instalar dependências
pip install requests schedule flask flask-cors
```

---

## 📋 Passo 4: Iniciar Servidor

```bash
python3 integracao_endpoint_php.py \
  --endpoint-php "https://lotbicho.com/backend/scraper/processar-resultados-completo.php" \
  --auto \
  --intervalo 5 \
  --port 5001
```

**Isso vai:**
- ✅ Iniciar servidor na porta 5001
- ✅ Chamar endpoint PHP a cada 5 minutos
- ✅ Processar resultados automaticamente

---

## 📋 Passo 5: Testar API

### Em outro terminal:

```bash
# Testar processamento
curl -X POST http://localhost:5001/api/resultados/processar

# Listar resultados
curl http://localhost:5001/api/resultados

# Status
curl http://localhost:5001/api/status
```

---

## 📋 Passo 6: Integrar com Frontend

### 6.1 Adicionar arquivo JavaScript

Copie `api_frontend.js` para seu projeto frontend e ajuste:

```javascript
const API_BASE_URL = 'http://seu-servidor:5001/api';
// ou
const API_BASE_URL = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api';
```

### 6.2 Modificar tela de apostas

```javascript
// Processar resultados
async function processarResultados() {
    const response = await fetch('/api/resultados/processar', {
        method: 'POST'
    });
    const data = await response.json();
    
    if (data.sucesso) {
        // Exibir resultados
        exibirResultados(data.resultados);
        
        // Mostrar resumo
        console.log(`${data.summary.bets_processed} apostas processadas`);
        console.log(`${data.summary.bets_won} ganhas`);
    }
}

// Atualizar a cada 5 minutos
setInterval(processarResultados, 5 * 60 * 1000);
```

---

## 📋 Passo 7: Deploy no Coolify

### 7.1 Atualizar Dockerfile (se necessário)

Se quiser usar `integracao_endpoint_php.py` no Coolify:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY integracao_endpoint_php.py .
COPY requirements_apostas.txt requirements.txt

# Instalar Python
RUN pip install --no-cache-dir -r requirements.txt

# Variável de ambiente para endpoint PHP
ENV ENDPOINT_PHP="https://lotbicho.com/backend/scraper/processar-resultados-completo.php"

# Expor porta
EXPOSE 8000

# Comando de start
CMD ["python3", "integracao_endpoint_php.py", "--auto", "--intervalo", "5", "--port", "8000"]
```

### 7.2 Fazer Deploy

1. Fazer push no GitHub
2. No Coolify, fazer redeploy
3. Verificar logs

---

## ✅ Verificação Final

### Checklist:

- [ ] Endpoint PHP configurado e testado
- [ ] Servidor Python rodando
- [ ] API respondendo corretamente
- [ ] Processamento automático ativo
- [ ] Frontend integrado
- [ ] Resultados aparecendo
- [ ] Liquidação funcionando

---

## 🎯 Comandos Rápidos

```bash
# Iniciar servidor
python3 integracao_endpoint_php.py --auto --intervalo 5 --port 5001

# Testar
curl http://localhost:5001/api/resultados

# Ver status
curl http://localhost:5001/api/processamento/status

# Parar processamento automático
curl -X POST http://localhost:5001/api/processamento/stop
```

---

## 🔧 Troubleshooting

### Endpoint não responde?
- Verificar URL
- Testar no navegador
- Verificar logs do servidor PHP

### API não funciona?
- Verificar se servidor está rodando
- Verificar porta
- Verificar logs

### Processamento não acontece?
- Verificar status: `GET /api/processamento/status`
- Verificar logs do servidor
- Testar manualmente: `POST /api/resultados/processar`

---

Tudo pronto! Siga os passos acima e estará funcionando! 🚀

