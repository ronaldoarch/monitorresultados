# Monitor Automático com Watchdog

## Visão Geral

O sistema agora inclui um **watchdog** que garante que o monitor sempre esteja rodando automaticamente, mesmo após erros ou reinicializações do servidor.

## Como Funciona

### 1. Monitor Principal
- Executa em uma thread separada (`monitor_loop`)
- Verifica resultados a cada 60 segundos (configurável via `MONITOR_INTERVALO`)
- Continua rodando mesmo após erros (até 5 erros consecutivos antes de pausar)

### 2. Watchdog
- Executa em uma thread separada (`watchdog_loop`)
- Verifica a cada 30 segundos se o monitor está rodando
- **Reinicia automaticamente** o monitor se detectar que ele parou
- Garante que o monitor sempre esteja ativo

### 3. Tratamento de Erros Robusto
- O monitor não para completamente após erros
- Após 5 erros consecutivos, aguarda 60 segundos antes de continuar
- Logs detalhados de todos os erros para diagnóstico

## Configuração

### Variáveis de Ambiente

```bash
# Ativar/desativar início automático (padrão: true)
MONITOR_AUTO_START=true

# Intervalo de verificação em segundos (padrão: 60)
MONITOR_INTERVALO=60
```

### No Docker/Coolify

Adicione estas variáveis nas configurações do serviço:

```yaml
environment:
  MONITOR_AUTO_START: "true"
  MONITOR_INTERVALO: "60"
```

## Endpoints de Monitoramento

### 1. Status do Sistema
```http
GET /api/status
```

Retorna informações completas sobre o sistema:
```json
{
  "monitor_rodando": true,
  "monitor_iniciado": true,
  "thread_ativa": true,
  "watchdog_ativo": true,
  "total_resultados": 225,
  "ultima_verificacao": "2026-01-15T23:12:00-03:00",
  "auto_start": true,
  "intervalo": 60
}
```

### 2. Status do Monitor
```http
GET /api/monitor/status
```

Retorna status específico do monitor:
```json
{
  "monitor_rodando": true,
  "monitor_iniciado": true,
  "thread_ativa": true,
  "watchdog_ativo": true,
  "verificar_disponivel": true,
  "auto_start": true,
  "intervalo": 60
}
```

### 3. Health Check (Recomendado)
```http
GET /api/monitor/health
```

**Este é o endpoint mais importante!** Ele:
- Verifica se o monitor está rodando
- **Reinicia automaticamente** se detectar que parou
- Retorna status detalhado

```json
{
  "monitor_ativo": true,
  "monitor_iniciado": true,
  "watchdog_ativo": true,
  "auto_start": true,
  "intervalo": 60,
  "status": "ok",
  "mensagem": "Monitor ativo"
}
```

## Monitoramento Externo

### Usando Cron ou Agendador

Configure um cron job para chamar o health check periodicamente:

```bash
# Verificar a cada 5 minutos
*/5 * * * * curl -s https://seu-dominio.com/api/monitor/health > /dev/null
```

### Usando Uptime Robot ou Similar

Configure um monitor HTTP que chama:
```
https://seu-dominio.com/api/monitor/health
```

- Intervalo: 5 minutos
- Espera: `"status": "ok"`
- Se não receber "ok", o próprio endpoint tentará reiniciar o monitor

## Inicialização Automática

O monitor é iniciado automaticamente em 3 momentos:

1. **Quando o módulo é carregado** (via `inicializar_monitor_automatico()`)
2. **Quando Gunicorn inicia** (via hook `on_starting`)
3. **Quando Gunicorn está pronto** (via hook `when_ready`)

O watchdog também é iniciado automaticamente junto com o monitor.

## Logs

### Monitor Principal
```
🔄 Monitor Bicho Certo iniciado (verifica a cada 60s)
✅ Bicho Certo: 3 novos resultados encontrados!
❌ Erro no monitor (tentativa 1/5): Connection timeout
```

### Watchdog
```
🔍 Watchdog do monitor iniciado (verifica a cada 30s)
⚠️  Monitor parou! Reiniciando automaticamente...
✅ Monitor Bicho Certo iniciado em thread separada (intervalo: 60s)
```

## Solução de Problemas

### Monitor não está iniciando

1. Verifique logs:
```bash
docker logs seu-container | grep -i monitor
```

2. Verifique variáveis de ambiente:
```bash
docker exec seu-container env | grep MONITOR
```

3. Force reinicialização via API:
```bash
curl -X GET https://seu-dominio.com/api/monitor/health
```

### Monitor para após alguns minutos

1. Verifique se o watchdog está ativo:
```bash
curl https://seu-dominio.com/api/monitor/status
```

2. Se `watchdog_ativo` for `false`, o watchdog pode ter parado. O health check deve reiniciá-lo.

3. Verifique logs de erro para identificar problemas recorrentes.

### Monitor reinicia constantemente

Isso pode indicar um problema mais sério:

1. Verifique logs de erro:
```bash
docker logs seu-container | grep -i "erro\|error"
```

2. Verifique recursos do servidor (memória, CPU):
```bash
docker stats seu-container
```

3. Aumente o intervalo se necessário:
```bash
MONITOR_INTERVALO=120  # 2 minutos
```

## Vantagens do Sistema

✅ **Zero intervenção manual** - Monitor sempre ativo  
✅ **Auto-recuperação** - Reinicia automaticamente após erros  
✅ **Monitoramento externo** - Health check endpoint para serviços externos  
✅ **Logs detalhados** - Facilita diagnóstico de problemas  
✅ **Configurável** - Intervalos e comportamento via variáveis de ambiente  

## Próximos Passos

Após fazer deploy:

1. Configure um monitor externo chamando `/api/monitor/health` a cada 5 minutos
2. Monitore os logs nas primeiras horas para garantir que tudo está funcionando
3. Ajuste `MONITOR_INTERVALO` conforme necessário

O sistema agora é **completamente autônomo** e não requer intervenção manual! 🚀
