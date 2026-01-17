# 🗄️ Guia de Banco de Dados - Bot de Liquidação

## 📋 Opções Disponíveis

O bot suporta **duas opções** de banco de dados:

1. **SQLite** (padrão) - Arquivo local, não precisa criar nada
2. **PostgreSQL** - Banco de dados externo, mais robusto para produção

---

## ✅ Opção 1: SQLite (Padrão - Mais Simples)

### **Vantagens:**
- ✅ Não precisa criar banco de dados
- ✅ Não precisa instalar nada
- ✅ Funciona imediatamente
- ✅ Perfeito para testes e pequenos volumes

### **Desvantagens:**
- ⚠️ Arquivo único (pode corromper se houver problemas)
- ⚠️ Não é ideal para múltiplos servidores
- ⚠️ Performance limitada para grandes volumes

### **Como Usar:**

**Não precisa fazer nada!** O bot cria automaticamente o arquivo `apostas.db` na primeira execução.

**Configuração:**
```bash
# Variável de ambiente (opcional, já é o padrão)
BOT_DATABASE_URL=sqlite:///apostas.db
```

**Onde fica o arquivo:**
- No mesmo diretório onde o bot está rodando
- Ou em `/app/apostas.db` se rodar no Docker

**Para persistir no Docker/Coolify:**
Configure um volume:
- **Volume:** `/app/apostas.db` → Salvar em local permanente

---

## 🐘 Opção 2: PostgreSQL (Recomendado para Produção)

### **Vantagens:**
- ✅ Mais robusto e confiável
- ✅ Suporta múltiplos servidores
- ✅ Melhor performance
- ✅ Backup mais fácil
- ✅ Ideal para produção

### **Desvantagens:**
- ⚠️ Precisa criar banco de dados
- ⚠️ Precisa instalar PostgreSQL (ou usar serviço gerenciado)

### **Como Configurar:**

#### **1. Criar Banco de Dados PostgreSQL**

**Opção A: PostgreSQL Local**
```bash
# Instalar PostgreSQL (se ainda não tiver)
sudo apt-get install postgresql postgresql-contrib

# Criar banco de dados
sudo -u postgres psql
CREATE DATABASE apostas;
CREATE USER bot_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE apostas TO bot_user;
\q
```

**Opção B: Serviço Gerenciado (Recomendado)**
- **Supabase** (grátis até certo limite)
- **Railway** (grátis com limites)
- **Render** (grátis com limites)
- **AWS RDS** (pago)
- **DigitalOcean Managed Databases** (pago)

#### **2. Configurar Variável de Ambiente**

**Formato da URL:**
```
postgresql://usuario:senha@host:porta/nome_banco
```

**Exemplos:**

**PostgreSQL Local:**
```bash
BOT_DATABASE_URL=postgresql://bot_user:sua_senha@localhost:5432/apostas
```

**Supabase:**
```bash
BOT_DATABASE_URL=postgresql://postgres:sua_senha@db.xxxxx.supabase.co:5432/postgres
```

**Railway:**
```bash
BOT_DATABASE_URL=postgresql://postgres:sua_senha@containers-us-west-xxx.railway.app:5432/railway
```

**Render:**
```bash
BOT_DATABASE_URL=postgresql://usuario:senha@dpg-xxxxx-a.oregon-postgres.render.com/apostas
```

#### **3. Configurar no Coolify**

No painel do Coolify, adicione a variável:

```bash
BOT_DATABASE_URL=postgresql://usuario:senha@host:porta/nome_banco
```

**⚠️ IMPORTANTE:** Não commite a senha no Git! Use variáveis de ambiente.

#### **4. Instalar Driver PostgreSQL (se necessário)**

O SQLAlchemy já inclui o driver, mas se der erro, adicione ao `requirements_vps.txt`:

```txt
psycopg2-binary>=2.9.0
```

Ou para Python 3.11+:
```txt
psycopg[binary]>=3.1.0
```

---

## 🔄 Migração de SQLite para PostgreSQL

Se você já está usando SQLite e quer migrar:

### **1. Exportar Dados do SQLite:**

```python
# script_migrar.py
import sqlite3
import json

conn = sqlite3.connect('apostas.db')
cursor = conn.cursor()

# Exportar apostas
cursor.execute("SELECT * FROM apostas")
apostas = cursor.fetchall()

# Exportar liquidações
cursor.execute("SELECT * FROM liquidacoes")
liquidacoes = cursor.fetchall()

# Salvar em JSON
with open('backup.json', 'w') as f:
    json.dump({
        'apostas': apostas,
        'liquidacoes': liquidacoes
    }, f)

conn.close()
```

### **2. Importar para PostgreSQL:**

O bot cria as tabelas automaticamente na primeira execução, então:

1. Configure `BOT_DATABASE_URL` para PostgreSQL
2. Inicie o bot (ele cria as tabelas)
3. Importe os dados manualmente se necessário

---

## 📊 Estrutura do Banco de Dados

O bot cria automaticamente estas tabelas:

### **Tabelas Criadas:**

1. **usuarios** - Usuários do sistema
2. **extractions** - Extrações (se usar sistema de extrações)
3. **apostas** - Apostas recebidas
4. **resultados** - Resultados coletados
5. **liquidacoes** - Liquidações processadas
6. **transacoes** - Transações financeiras

### **Ver Estrutura:**

```python
from models import Base
from sqlalchemy import create_engine

engine = create_engine('postgresql://...')
Base.metadata.create_all(engine)
```

---

## 🧪 Testar Conexão

### **Teste Rápido:**

```python
# test_db.py
from bot_liquidacao import BotLiquidacao

# Testar SQLite
bot_sqlite = BotLiquidacao(database_url='sqlite:///teste.db')
print("✅ SQLite OK")

# Testar PostgreSQL
bot_pg = BotLiquidacao(database_url='postgresql://usuario:senha@host:5432/apostas')
print("✅ PostgreSQL OK")
```

---

## 🔐 Segurança

### **Boas Práticas:**

1. **Não commite senhas no Git**
   ```bash
   # ❌ ERRADO
   BOT_DATABASE_URL=postgresql://user:senha123@host/db
   
   # ✅ CERTO - Use variáveis de ambiente
   BOT_DATABASE_URL=${DB_URL}
   ```

2. **Use senhas fortes**
   ```bash
   # Gere senha segura
   openssl rand -base64 32
   ```

3. **Restrinja acesso**
   - Configure firewall do PostgreSQL
   - Use SSL se possível
   - Limite IPs que podem conectar

4. **Backup regular**
   ```bash
   # Backup PostgreSQL
   pg_dump -U usuario -d apostas > backup.sql
   ```

---

## 📝 Exemplo Completo: PostgreSQL no Coolify

### **1. Criar PostgreSQL no Coolify:**

1. No Coolify, vá em **"New Resource"** → **"Database"** → **"PostgreSQL"**
2. Configure:
   - **Nome:** `apostas-db`
   - **Versão:** `15` ou `16`
   - **Senha:** (gerar senha segura)
3. Clique em **"Deploy"**

### **2. Obter URL de Conexão:**

Após criar, o Coolify mostra a URL de conexão:
```
postgresql://postgres:senha@apostas-db:5432/postgres
```

### **3. Configurar na Aplicação:**

Na aplicação do bot, adicione variável:
```bash
BOT_DATABASE_URL=postgresql://postgres:senha@apostas-db:5432/postgres
```

### **4. Deploy:**

O bot criará as tabelas automaticamente na primeira execução!

---

## 🆘 Troubleshooting

### **Erro: "No module named 'psycopg2'"**

**Solução:**
Adicione ao `requirements_vps.txt`:
```txt
psycopg2-binary>=2.9.0
```

### **Erro: "Connection refused"**

**Verificar:**
1. PostgreSQL está rodando?
2. Host e porta estão corretos?
3. Firewall permite conexão?

### **Erro: "Authentication failed"**

**Verificar:**
1. Usuário e senha estão corretos?
2. Usuário tem permissões no banco?

### **Erro: "Database does not exist"**

**Solução:**
Crie o banco de dados primeiro:
```sql
CREATE DATABASE apostas;
```

---

## ✅ Recomendações

### **Para Desenvolvimento/Testes:**
- Use **SQLite** (mais simples)

### **Para Produção:**
- Use **PostgreSQL** (mais robusto)
- Use serviço gerenciado (Supabase, Railway, etc.)
- Configure backups automáticos

---

## 📞 Próximos Passos

1. Escolha SQLite ou PostgreSQL
2. Configure variável `BOT_DATABASE_URL`
3. Deploy no Coolify
4. Verifique se bot criou as tabelas

**Pronto!** Seu banco de dados está configurado! 🎉
