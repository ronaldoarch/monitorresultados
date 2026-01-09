# 🚀 Deploy Livro dos Sonhos no Coolify

Guia para fazer deploy do sistema Livro dos Sonhos no Coolify.

## 📋 Pré-requisitos

- Repositório no GitHub com o código
- Acesso ao painel Coolify
- Conta no Coolify configurada

## 🔧 Passo a Passo

### 1. Push do Código para o GitHub

O commit já foi feito. Agora faça o push:

```bash
git push origin main
```

### 2. Criar Novo Projeto no Coolify

1. No painel Coolify, clique em **"Projects +"** ou **"+ Add Resource"**
2. Escolha **"New Application"** ou **"New Project"**
3. Dê um nome: `livro-dos-sonhos` ou `livro-sonhos`

### 3. Conectar Repositório GitHub

1. Na tela de criação, escolha **"Source"** → **"GitHub"**
2. Se ainda não conectou:
   - Clique em **"Connect GitHub"** ou **"Add Source"**
   - Autorize o Coolify a acessar seus repositórios
3. Selecione o repositório: `ronaldoarch/monitorresultados` (ou seu repositório)
4. Escolha o branch: `main`

### 4. Configurar Build

#### Opção A: Usando Dockerfile (Recomendado)

1. **Build Pack**: Escolha **"Dockerfile"**
2. **Dockerfile Path**: `Dockerfile.livro_sonhos`
3. O Coolify detectará automaticamente o Dockerfile

#### Opção B: Build Manual

1. **Build Pack**: Escolha **"Python"**
2. **Build Command**:
   ```bash
   pip install --no-cache-dir --upgrade pip && \
   pip install --no-cache-dir -r requirements.txt && \
   pip install --no-cache-dir gunicorn flask-cors
   ```
3. **Start Command**:
   ```bash
   gunicorn --bind 0.0.0.0:8082 --workers 2 --timeout 120 app_livro_sonhos:app
   ```

### 5. Configurar Variáveis de Ambiente

Em **"Environment Variables"**, adicione:

```
PYTHONUNBUFFERED=1
FLASK_ENV=production
```

### 6. Configurar Porta

1. Em **"Port"** ou **"Exposed Port"**, defina: `8082`
2. O Coolify geralmente detecta automaticamente do Dockerfile

### 7. Configurar Domínio (Opcional)

1. Em **"Domain"** ou **"Custom Domain"**, adicione:
   - Domínio personalizado (se tiver)
   - Ou use o domínio gerado pelo Coolify
   - Exemplo: `livro-sonhos.seudominio.com`

### 8. Recursos Necessários

**Recomendações:**
- **RAM**: Mínimo 256MB (recomendado 512MB)
- **CPU**: 0.5 core é suficiente
- **Disco**: 2GB mínimo

### 9. Deploy

1. Clique em **"Deploy"** ou **"Save & Deploy"**
2. Aguarde o build e deploy (pode levar alguns minutos)
3. Acompanhe os logs em tempo real

### 10. Verificar Deploy

Após o deploy:

1. Acesse a URL fornecida pelo Coolify
2. Teste o painel: `http://seu-servidor:8082/`
3. Teste a API: `http://seu-servidor:8082/api/v1/status`
4. Teste interpretação: `http://seu-servidor:8082/api/v1/interpretar`

## 📝 Estrutura de Arquivos Necessários

Certifique-se de que estes arquivos estão no repositório:

```
.
├── Dockerfile.livro_sonhos    # Dockerfile específico
├── app_livro_sonhos.py        # Aplicação Flask
├── livro_sonhos.py            # Sistema de interpretação
├── requirements.txt           # Dependências Python
└── README_LIVRO_SONHOS.md     # Documentação
```

## 🔍 Verificação Pós-Deploy

### Testar API

```bash
# Status
curl http://seu-servidor:8082/api/v1/status

# Interpretar sonho
curl -X POST http://seu-servidor:8082/api/v1/interpretar \
  -H "Content-Type: application/json" \
  -d '{"sonho": "leão"}'
```

### Testar Interface Web

Acesse no navegador:
```
http://seu-servidor:8082/
```

## 🐛 Troubleshooting

### Build Falha?

1. Verifique os logs no Coolify
2. Certifique-se que `requirements.txt` está no repositório
3. Verifique se todas as dependências estão listadas:
   - flask>=3.0.0
   - flask-cors
   - gunicorn

### Porta não acessível?

1. Verifique se a porta `8082` está configurada
2. Verifique firewall do Coolify
3. Teste localmente primeiro: `curl http://localhost:8082/api/v1/status`

### Erro ao iniciar?

1. Verifique logs: `View Logs` no Coolify
2. Teste manualmente: `python3 app_livro_sonhos.py --port 8082`
3. Verifique se todas as dependências foram instaladas

## 🔄 Atualizações Futuras

Para atualizar:

1. Faça alterações no código
2. Faça commit e push:
   ```bash
   git add .
   git commit -m "Atualização do Livro dos Sonhos"
   git push origin main
   ```
3. No Coolify, clique em **"Redeploy"** ou **"Deploy"**
4. O Coolify detecta mudanças automaticamente (se configurado)

## 📊 Endpoints Disponíveis Após Deploy

```
GET  /                          → Painel Web
POST /api/v1/interpretar        → Interpretar sonho
GET  /api/v1/sonhos/populares   → Listar sonhos populares
GET  /api/v1/sonhos/buscar      → Buscar sonho específico
GET  /api/v1/status             → Status da API
```

## ✅ Checklist de Deploy

- [ ] Código commitado e no GitHub
- [ ] Dockerfile.livro_sonhos criado
- [ ] Projeto criado no Coolify
- [ ] Repositório conectado
- [ ] Porta 8082 configurada
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy executado com sucesso
- [ ] API testada e funcionando
- [ ] Interface web acessível

## 🎯 Integração com Monitor Deu no Poste

Se você também tem o Monitor Deu no Poste rodando:

1. **Monitor Deu no Poste**: Porta `8081`
2. **Livro dos Sonhos**: Porta `8082`

Ambos podem rodar simultaneamente no Coolify como aplicações separadas.

## 💡 Dicas

✅ Use **"Auto Deploy"** para deploy automático a cada push  
✅ Configure **"Health Check"** para monitoramento  
✅ Use **"Backup"** se precisar salvar dados  
✅ Configure **"SSL"** se tiver domínio  
✅ Configure **"Environment Variables"** para diferentes ambientes  

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no Coolify
2. Teste localmente primeiro
3. Verifique se todas as dependências estão instaladas
4. Confirme que a porta está correta

Boa sorte com o deploy! 🚀
