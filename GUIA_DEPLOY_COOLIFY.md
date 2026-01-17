# 🚀 Guia de Deploy no Coolify

## 📋 Pré-requisitos

1. Conta no Coolify configurada
2. Repositório Git com o código
3. Acesso ao servidor onde o Coolify está rodando

---

## 🔧 Configuração no Coolify

### **1. Criar Nova Aplicação**

1. Acesse seu painel do Coolify
2. Clique em **"New Resource"** → **"Application"**
3. Escolha **"Docker Compose"** ou **"Dockerfile"**

### **2. Configurar Repositório**

- **Repository URL:** URL do seu repositório Git
- **Branch:** `main` (ou a branch que você usa)
- **Dockerfile Path:** `Dockerfile` (ou deixe vazio se estiver na raiz)

### **3. Configurar Variáveis de Ambiente**

No Coolify, adicione as seguintes variáveis de ambiente:

#### **Variáveis Obrigatórias:**

```bash
# Monitor
MONITOR_AUTO_START=true
MONITOR_INTERVALO=60

# Bot de Liquidação
BOT_AUTO_START=true
BOT_DATABASE_URL=sqlite:///apostas.db
```

#### **Variáveis Opcionais (se usar integração com site):**

```bash
# URL da API do seu site (onde o bot vai enviar liquidações)
SITE_API_URL=https://seu-site.com

# Chave de API (opcional, para autenticação)
SITE_API_KEY=sua-chave-secreta-aqui
```

### **4. Configurar Porta**

- **Port:** `8000` (ou a porta que você configurou)
- **Expose Port:** Marque como público se quiser acesso externo

### **5. Configurar Volumes (Opcional)**

Se quiser persistir dados entre reinicializações:

- **Volume:** `/app/data` → Para salvar `resultados.json`
- **Volume:** `/app/apostas.db` → Para salvar banco de dados SQLite

**Ou configure banco de dados externo:**

```bash
BOT_DATABASE_URL=postgresql://user:password@host:5432/apostas
```

### **6. Configurar Health Check (Opcional)**

- **Health Check Path:** `/api/status`
- **Health Check Interval:** `30` segundos

---

## 📝 Arquivo docker-compose.yml (Alternativa)

Se preferir usar Docker Compose diretamente, crie um arquivo `docker-compose.yml`:

```yaml
version: '3.8'

services:
  monitor-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: monitor-bot
    ports:
      - "8000:8000"
    environment:
      - MONITOR_AUTO_START=true
      - MONITOR_INTERVALO=60
      - BOT_AUTO_START=true
      - BOT_DATABASE_URL=sqlite:///apostas.db
      - SITE_API_URL=${SITE_API_URL:-}
      - SITE_API_KEY=${SITE_API_KEY:-}
    volumes:
      - ./data:/app/data
      - ./apostas.db:/app/apostas.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 🔄 Processo de Deploy

### **1. Push para Git**

```bash
git add .
git commit -m "Adicionar bot de liquidação automática"
git push origin main
```

### **2. Deploy no Coolify**

1. No painel do Coolify, clique em **"Deploy"**
2. Aguarde o build e deploy completarem
3. Verifique os logs para garantir que tudo iniciou corretamente

### **3. Verificar se Está Funcionando**

Acesse:
- **Dashboard:** `https://seu-dominio.com/`
- **Painel do Bot:** `https://seu-dominio.com/dashboard-bot`
- **Status API:** `https://seu-dominio.com/api/status`

---

## 🐛 Troubleshooting

### **Problema: Bot não inicia**

**Verificar logs:**
```bash
# No Coolify, vá em "Logs" da aplicação
# Ou via terminal:
docker logs monitor-bot
```

**Verificar variáveis de ambiente:**
- Certifique-se de que `BOT_AUTO_START=true`
- Verifique se `BOT_DATABASE_URL` está correto

### **Problema: Monitor não coleta resultados**

**Verificar:**
1. Logs do monitor
2. Se ChromeDriver está instalado corretamente
3. Se `MONITOR_AUTO_START=true`

### **Problema: Banco de dados não persiste**

**Solução:**
- Configure volume para `/app/apostas.db`
- Ou use banco de dados externo (PostgreSQL)

### **Problema: Porta não está acessível**

**Verificar:**
1. Porta está exposta no Coolify
2. Firewall permite acesso à porta
3. Domínio está configurado corretamente

---

## 📊 Monitoramento

### **Verificar Status:**

```bash
curl https://seu-dominio.com/api/status
```

Resposta esperada:
```json
{
  "monitor_rodando": true,
  "bot_ativo": true,
  "total_resultados": 150,
  ...
}
```

### **Verificar Logs:**

No Coolify:
1. Vá em **"Logs"** da aplicação
2. Filtre por "Bot" ou "Monitor"

---

## 🔐 Segurança

### **Recomendações:**

1. **Use HTTPS:** Configure SSL no Coolify
2. **Proteja API Key:** Não commite `SITE_API_KEY` no Git
3. **Use Variáveis de Ambiente:** Configure no Coolify, não no código
4. **Firewall:** Restrinja acesso se necessário

---

## 🔄 Atualizações

### **Para atualizar:**

1. Faça alterações no código
2. Commit e push para Git
3. No Coolify, clique em **"Redeploy"**
4. Aguarde deploy completar

### **Rollback:**

Se algo der errado:
1. No Coolify, vá em **"Deployments"**
2. Escolha uma versão anterior
3. Clique em **"Redeploy"**

---

## 📞 Suporte

Se tiver problemas:
1. Verifique logs no Coolify
2. Verifique variáveis de ambiente
3. Teste endpoints manualmente
4. Verifique se banco de dados está acessível

---

**Pronto!** Seu bot está deployado no Coolify! 🎉
