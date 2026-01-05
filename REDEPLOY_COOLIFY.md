# 🔄 Passo a Passo - Redeploy no Coolify

## ✅ Sim, Você Precisa Fazer Redeploy!

Para usar a nova integração com endpoint PHP, você precisa fazer redeploy no Coolify.

## 📋 Passo a Passo Completo

### Passo 1: Verificar Código no GitHub

O código já está no GitHub, mas vamos verificar:

```bash
# Verificar último commit
git log --oneline -5
```

Deve aparecer commits com:
- "Adicionar integração com endpoint PHP do painel"
- "Configurar Opção B - Integração com Endpoint PHP"

---

### Passo 2: Fazer Push (Se Houver Mudanças Locais)

```bash
# Verificar se há mudanças
git status

# Se houver mudanças, fazer commit e push
git add .
git commit -m "Atualizações finais"
git push
```

---

### Passo 3: No Painel Coolify

#### 3.1 Acessar Projeto

1. Acesse o painel Coolify: `http://147.93.147.33:8000` (ou sua URL)
2. Vá em **"Projects"**
3. Clique no seu projeto (ex: "monitor-resultados")

#### 3.2 Adicionar Variável de Ambiente

1. No projeto, vá em **"Settings"** ou **"Environment Variables"**
2. Clique em **"Add Environment Variable"** ou **"+ Add"**
3. Adicione:
   - **Name**: `ENDPOINT_PHP`
   - **Value**: `https://lotbicho.com/backend/scraper/processar-resultados-completo.php`
   - **Type**: `Plain` (ou `Secret` se preferir)
4. Clique em **"Save"**

#### 3.3 Verificar Configuração

Verifique se:
- ✅ Repositório está conectado
- ✅ Branch está correto (`main`)
- ✅ Build command está vazio (ou correto)
- ✅ Port está configurada (`8000`)

---

### Passo 4: Fazer Redeploy

#### Opção A: Redeploy Manual

1. No projeto, clique em **"Deployments"** ou **"Deploy"**
2. Clique em **"Redeploy"** ou **"Deploy"**
3. Aguarde o build e deploy (pode levar 2-5 minutos)

#### Opção B: Redeploy Automático (Se Configurado)

Se você tem **"Auto Deploy"** ativado:
- Apenas faça `git push`
- O Coolify detecta automaticamente e faz deploy

---

### Passo 5: Verificar Logs

1. Após o deploy, vá em **"Logs"** ou **"View Logs"**
2. Procure por:
   ```
   🚀 Servidor iniciando
   📡 Endpoint PHP: https://...
   ✅ Processamento automático iniciado
   ```

3. Se aparecer erros, verifique:
   - Variável `ENDPOINT_PHP` está configurada?
   - Endpoint PHP está acessível?
   - Dependências instaladas?

---

### Passo 6: Testar

Após o deploy, teste a API:

```bash
# Testar processamento
curl -X POST http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/processar

# Listar resultados
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados

# Status
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/status
```

---

## 🔧 Configuração do Dockerfile (Se Necessário)

Se quiser usar `integracao_endpoint_php.py` diretamente, atualize o Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY integracao_endpoint_php.py .
COPY requirements_apostas.txt requirements.txt

# Instalar Python
RUN pip install --no-cache-dir -r requirements.txt

# Expor porta
EXPOSE 8000

# Comando de start
CMD ["python3", "integracao_endpoint_php.py", "--auto", "--intervalo", "5", "--port", "8000"]
```

**OU** continue usando `app_vps.py` e adicione a rota de integração.

---

## 📝 Checklist de Redeploy

- [ ] Código no GitHub atualizado
- [ ] Variável `ENDPOINT_PHP` adicionada no Coolify
- [ ] Redeploy iniciado
- [ ] Logs verificados
- [ ] API testada
- [ ] Processamento automático funcionando

---

## 🎯 Resumo Rápido

1. **No Coolify:**
   - Adicionar variável `ENDPOINT_PHP`
   - Clicar em "Redeploy"

2. **Aguardar:**
   - Build (1-2 minutos)
   - Deploy (30 segundos)

3. **Testar:**
   - Verificar logs
   - Testar API
   - Confirmar processamento

---

## ⚠️ Se Der Erro no Deploy

### Erro: Variável não encontrada
- Verificar se `ENDPOINT_PHP` está configurada
- Verificar se está no formato correto

### Erro: Módulo não encontrado
- Verificar se `requirements_apostas.txt` está no repositório
- Verificar se dependências estão instaladas

### Erro: Porta em uso
- Verificar se porta 8000 está livre
- Ou mudar porta no Coolify

---

## 🚀 Próximo Passo Após Deploy

Após o deploy bem-sucedido:

1. Verificar logs no Coolify
2. Testar API externamente
3. Integrar com frontend (se necessário)
4. Monitorar processamento automático

Tudo pronto para redeploy! 🎯

