# 🚀 Deploy no Coolify via Painel Web

## Repositório GitHub
✅ Código disponível em: https://github.com/ronaldoarch/monitorresultados.git

## Passo a Passo no Painel Coolify

### 1. Criar Novo Projeto

1. No painel Coolify, clique em **"Projects +"** ou **"+ Add Resource"**
2. Escolha **"New Project"** ou **"New Application"**
3. Dê um nome: `monitor-resultados`

### 2. Conectar Repositório GitHub

1. Na tela de criação, escolha **"Source"** → **"GitHub"**
2. Se ainda não conectou:
   - Clique em **"Connect GitHub"** ou **"Add Source"**
   - Autorize o Coolify a acessar seus repositórios
3. Selecione o repositório: `ronaldoarch/monitorresultados`
4. Escolha o branch: `main`

### 3. Configurar Build

1. **Build Pack**: Escolha **"Python"** ou **"Dockerfile"** (se tiver)
2. **Build Command**: Deixe vazio ou:
   ```
   pip install -r requirements_vps.txt
   ```
3. **Start Command**: 
   ```
   gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 app_vps:app
   ```
   Ou se preferir com monitor:
   ```
   python3 app_vps.py --monitor --intervalo 60
   ```

### 4. Configurar Variáveis de Ambiente (Opcional)

Se precisar de variáveis, adicione em **"Environment Variables"**:
- `PYTHONUNBUFFERED=1`
- `FLASK_ENV=production`

### 5. Configurar Porta

1. Em **"Port"** ou **"Exposed Port"**, defina: `8000`
2. O Coolify geralmente detecta automaticamente

### 6. Configurar Domínio (Opcional)

1. Em **"Domain"** ou **"Custom Domain"**, adicione:
   - Domínio personalizado (se tiver)
   - Ou use o domínio gerado pelo Coolify

### 7. Recursos Necessários

**Recomendações:**
- **RAM**: Mínimo 512MB (recomendado 1GB)
- **CPU**: 1 core é suficiente
- **Disco**: 5GB mínimo

### 8. Dependências do Sistema

O Coolify geralmente instala automaticamente, mas se precisar:

**No Dockerfile (criar se necessário):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos
COPY requirements_vps.txt .
RUN pip install --no-cache-dir -r requirements_vps.txt

COPY . .

# Expor porta
EXPOSE 8000

# Comando de start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "app_vps:app"]
```

### 9. Deploy

1. Clique em **"Deploy"** ou **"Save & Deploy"**
2. Aguarde o build e deploy (pode levar alguns minutos)
3. Acompanhe os logs em tempo real

### 10. Verificar Deploy

Após o deploy:
1. Acesse a URL fornecida pelo Coolify
2. Ou use o IP: `http://147.93.147.33:8000`
3. Teste o dashboard: `http://147.93.147.33:8000/`
4. Teste a API: `http://147.93.147.33:8000/api/status`

## Configuração Alternativa (Sem Dockerfile)

Se o Coolify não detectar automaticamente:

1. **Build Command**:
   ```bash
   python3 -m venv venv && source venv/bin/activate && pip install -r requirements_vps.txt
   ```

2. **Start Command**:
   ```bash
   source venv/bin/activate && python3 app_vps.py --monitor --intervalo 60
   ```

## Troubleshooting

### Build Falha?

1. Verifique os logs no Coolify
2. Certifique-se que `requirements_vps.txt` está no repositório
3. Verifique se todas as dependências estão listadas

### ChromeDriver não funciona?

1. Adicione no Dockerfile (se usar):
   ```dockerfile
   RUN apt-get install -y chromium chromium-driver
   ```

2. Ou configure variável de ambiente:
   ```
   CHROME_BIN=/usr/bin/chromium
   CHROMEDRIVER_PATH=/usr/bin/chromedriver
   ```

### Porta não acessível?

1. Verifique se a porta `8000` está configurada
2. Verifique firewall do Coolify
3. Teste localmente primeiro: `curl http://localhost:8000/api/status`

### Monitor não inicia?

1. Verifique logs: `View Logs` no Coolify
2. Teste manualmente: `python3 app_vps.py --uma-vez`
3. Verifique se Selenium está funcionando

## Comandos Úteis no Coolify

- **View Logs**: Ver logs em tempo real
- **Restart**: Reiniciar aplicação
- **Settings**: Configurações do projeto
- **Environment**: Variáveis de ambiente
- **Domains**: Configurar domínios

## Estrutura Final

Após deploy bem-sucedido:

```
http://147.93.147.33:8000/          → Dashboard
http://147.93.147.33:8000/api/resultados  → API JSON
http://147.93.147.33:8000/api/status     → Status
```

## Atualizações Futuras

Para atualizar:
1. Faça `git push` no seu repositório
2. No Coolify, clique em **"Redeploy"** ou **"Deploy"**
3. O Coolify detecta mudanças automaticamente (se configurado)

## Dicas

✅ Use **"Auto Deploy"** para deploy automático a cada push  
✅ Configure **"Health Check"** para monitoramento  
✅ Use **"Backup"** para salvar dados importantes  
✅ Configure **"SSL"** se tiver domínio  

Boa sorte com o deploy! 🚀

