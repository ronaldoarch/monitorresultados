# 🚀 Deploy do Monitor Deu no Poste no Coolify

## 📋 Passo a Passo Completo

### 1. Criar Novo Projeto no Coolify

1. Acesse o painel do Coolify
2. Vá em **"Projects"** ou **"Applications"**
3. Clique em **"+ New Project"** ou **"Add Application"**
4. Escolha **"GitHub"** como fonte

### 2. Configurar Repositório

- **Repository**: `ronaldoarch/monitorresultados`
- **Branch**: `main`
- **Name**: `monitor-deunoposte` (ou outro nome de sua preferência)

### 3. Configurar Build

#### Opção A: Usar Dockerfile (Recomendado)

Crie um `Dockerfile.deunoposte` no repositório:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app_deunoposte.py .
COPY monitor_deunoposte.py .

# Criar diretório para resultados
RUN mkdir -p /app/data

# Expor porta
EXPOSE 8081

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Comando de start
CMD ["gunicorn", "--bind", "0.0.0.0:8081", "--workers", "2", "--timeout", "120", "app_deunoposte:app"]
```

No Coolify:
- **Dockerfile Path**: `Dockerfile.deunoposte`
- **Build Command**: (deixe vazio)
- **Start Command**: (deixe vazio - usa Dockerfile)

#### Opção B: Build Manual

- **Build Command**:
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```bash
  python3 app_deunoposte.py --monitor --intervalo 300 --port 8081
  ```

### 4. Configurar Porta

- **Port**: `8081`
- **Expose Port**: `8081`

### 5. Variáveis de Ambiente (Opcional)

Se necessário, adicione:
- `PYTHONUNBUFFERED=1`
- `FLASK_ENV=production`

### 6. Deploy

1. Clique em **"Deploy"** ou **"Save & Deploy"**
2. Aguarde o build e deploy (pode levar alguns minutos)
3. Acompanhe os logs em tempo real

### 7. Verificar Deploy

Após o deploy, você terá uma URL como:
```
https://monitor-deunoposte-xxxxx.agenciamidas.com
```

Ou acesse diretamente pela porta:
```
http://147.93.147.33:8081/
```

---

## 🔍 Verificar se Está Funcionando

### 1. Ver Logs no Coolify

Procure por:
```
✅ Monitor Deu no Poste carregado com sucesso
🚀 Servidor Deu no Poste iniciando em http://0.0.0.0:8081
```

### 2. Testar Endpoints

```bash
# Status
curl https://monitor-deunoposte-xxxxx.agenciamidas.com/api/status

# Resultados
curl https://monitor-deunoposte-xxxxx.agenciamidas.com/api/resultados

# Dashboard
# Abra no navegador: https://monitor-deunoposte-xxxxx.agenciamidas.com/
```

### 3. Forçar Primeira Verificação

```bash
curl -X POST https://monitor-deunoposte-xxxxx.agenciamidas.com/api/verificar-agora
```

---

## 📊 Resumo da Configuração

| Item | Valor |
|------|-------|
| **Repositório** | `ronaldoarch/monitorresultados` |
| **Branch** | `main` |
| **Porta** | `8081` |
| **Arquivo Principal** | `app_deunoposte.py` |
| **Dockerfile** | `Dockerfile.deunoposte` (se usar) |
| **Monitor Automático** | Sim (via `--monitor`) |
| **Intervalo** | 300 segundos (5 minutos) |

---

## 🎯 Estrutura Final

Após deploy bem-sucedido:

### Monitor Bicho Certo (Projeto 1)
```
https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/
Porta: 8000
Arquivo: app_vps.py
```

### Monitor Deu no Poste (Projeto 2)
```
https://monitor-deunoposte-xxxxx.agenciamidas.com/
Porta: 8081
Arquivo: app_deunoposte.py
```

---

## ✅ Vantagens de Dois Projetos Separados

1. **Independência**: Cada monitor pode ser reiniciado sem afetar o outro
2. **Escalabilidade**: Pode escalar cada um separadamente
3. **Monitoramento**: Logs e métricas separados
4. **Manutenção**: Mais fácil de debugar e manter
5. **Configuração**: Cada um com suas próprias variáveis de ambiente

---

## 🔧 Troubleshooting

### Build Falha?

1. Verifique se `requirements.txt` está no repositório
2. Verifique se `app_deunoposte.py` e `monitor_deunoposte.py` estão no repositório
3. Verifique os logs do build no Coolify

### Porta não acessível?

1. Verifique se a porta `8081` está configurada
2. Verifique firewall do Coolify
3. Teste localmente primeiro

### Monitor não inicia?

1. Verifique logs: `View Logs` no Coolify
2. Verifique se o monitor está ativo: `GET /api/monitor/status`
3. Force verificação: `POST /api/verificar-agora`

---

## 📝 Notas Importantes

1. **Mesmo Repositório**: Ambos os projetos apontam para o mesmo repositório GitHub
2. **Arquivos Diferentes**: Cada projeto usa um arquivo Python diferente
3. **Portas Diferentes**: Cada projeto roda em uma porta diferente
4. **Deploy Independente**: Cada projeto pode ser deployado independentemente

---

## 🚀 Próximos Passos

1. ✅ Criar projeto no Coolify
2. ✅ Configurar repositório e porta
3. ✅ Fazer deploy
4. ✅ Verificar se está funcionando
5. ✅ Configurar domínio (opcional)
6. ✅ Configurar SSL/HTTPS (opcional)

Boa sorte com o deploy! 🎉
