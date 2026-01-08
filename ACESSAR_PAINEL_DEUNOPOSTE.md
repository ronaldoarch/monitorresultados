# 🎯 Como Acessar o Painel do Deu no Poste

## 🌐 URLs de Acesso

### Se o deploy foi feito no mesmo servidor do Bicho Certo:

#### Opção 1: Via Porta Direta
```
http://seu-ip-servidor:8081/
```

#### Opção 2: Via Domínio (se configurado)
```
https://seu-dominio.com:8081/
```

#### Opção 3: Via Subdomínio (se configurado)
```
https://deunoposte.seu-dominio.com/
```

### Se o deploy foi feito no Coolify:

O Coolify geralmente cria uma URL automática. Verifique:

1. **No painel do Coolify:**
   - Vá em seu projeto "monitor-deunoposte"
   - Procure por "URL" ou "Domain"
   - A URL será algo como: `https://monitor-deunoposte-xxxxx.agenciamidas.com`

2. **Ou verifique os logs do deploy:**
   - Os logs mostram a URL onde o serviço está rodando

---

## 📊 Endpoints Disponíveis

### Dashboard Principal
```
GET http://seu-servidor:8081/
```
Interface web com estatísticas e controles.

### API de Resultados
```
GET http://seu-servidor:8081/api/resultados
```
Retorna todos os resultados em JSON.

### Status do Sistema
```
GET http://seu-servidor:8081/api/status
```
Verifica se o monitor está rodando e quantos resultados foram coletados.

### Forçar Verificação
```
POST http://seu-servidor:8081/api/verificar-agora
```
Força uma verificação imediata (sem esperar o intervalo).

### Arquivo JSON Direto
```
GET http://seu-servidor:8081/resultados_deunoposte.json
```
Acessa o arquivo JSON diretamente.

### Controles do Monitor
```
POST http://seu-servidor:8081/api/monitor/start    # Iniciar monitor
POST http://seu-servidor:8081/api/monitor/stop     # Parar monitor
GET  http://seu-servidor:8081/api/monitor/status   # Status do monitor
```

---

## 🔍 Como Descobrir a URL

### 1. Verificar no Coolify

1. Acesse o painel do Coolify
2. Vá em "Projects" ou "Applications"
3. Procure por "monitor-deunoposte" ou o nome do seu projeto
4. Clique no projeto
5. Procure por:
   - **"Domains"** ou **"URLs"**
   - **"Environment"** → variável `PUBLIC_URL`
   - **"Settings"** → informações de acesso

### 2. Verificar Logs do Deploy

No Coolify, vá em "Logs" e procure por mensagens como:
```
🚀 Servidor Deu no Poste iniciando em http://0.0.0.0:8081
📊 Dashboard: http://0.0.0.0:8081/
```

### 3. Verificar Variáveis de Ambiente

No Coolify, vá em "Environment" e procure por:
- `PORT` ou `APP_PORT`
- `PUBLIC_URL` ou `DOMAIN`

### 4. Testar Conectividade

Se você souber o IP do servidor:
```bash
# Testar se a porta está aberta
curl http://IP-DO-SERVIDOR:8081/api/status

# Ou
curl http://IP-DO-SERVIDOR:8081/
```

---

## 🎨 Interface do Dashboard

O dashboard do Deu no Poste mostra:

- **Total de Resultados** coletados
- **Última Verificação** realizada
- **Status do Monitor** (Ativo/Inativo)
- **Lista de Endpoints** disponíveis
- **Botões de Controle**:
  - 🔄 Atualizar Status
  - ⚡ Verificar Agora

---

## 📱 Exemplos de Uso

### Via Navegador

1. Abra seu navegador
2. Digite a URL do servidor na porta 8081
3. Você verá o dashboard com estatísticas

### Via cURL

```bash
# Ver status
curl http://seu-servidor:8081/api/status

# Ver resultados
curl http://seu-servidor:8081/api/resultados

# Forçar verificação
curl -X POST http://seu-servidor:8081/api/verificar-agora
```

### Via JavaScript

```javascript
// Buscar resultados
fetch('http://seu-servidor:8081/api/resultados')
  .then(r => r.json())
  .then(data => {
    console.log('Total:', data.total_resultados);
    console.log('Resultados:', data.resultados);
  });

// Verificar status
fetch('http://seu-servidor:8081/api/status')
  .then(r => r.json())
  .then(data => {
    console.log('Monitor rodando:', data.monitor_rodando);
    console.log('Total resultados:', data.total_resultados);
  });
```

---

## 🔧 Troubleshooting

### Erro 404 ou "Not Found"

- Verifique se o serviço está rodando
- Verifique se a porta 8081 está correta
- Verifique se o firewall permite a porta 8081

### Erro de Conexão

- Verifique se o servidor está acessível
- Verifique se a porta está aberta no firewall
- Teste com `curl` ou `wget` primeiro

### Monitor não está coletando

1. Verifique o status: `GET /api/status`
2. Force uma verificação: `POST /api/verificar-agora`
3. Verifique os logs do servidor
4. Verifique se o monitor está ativo: `GET /api/monitor/status`

---

## 📝 Notas Importantes

1. **Porta 8081**: O monitor Deu no Poste roda na porta 8081 por padrão
2. **HTTPS**: Se usar HTTPS, certifique-se de configurar SSL/TLS no Coolify
3. **Firewall**: A porta 8081 precisa estar aberta no firewall
4. **Proxy Reverso**: Se usar nginx/apache, configure o proxy para a porta 8081

---

## 🚀 Próximos Passos

1. **Acesse o dashboard** e verifique se está funcionando
2. **Force uma verificação** para coletar resultados iniciais
3. **Configure o monitor automático** se ainda não estiver ativo
4. **Monitore os logs** para garantir que está coletando resultados
