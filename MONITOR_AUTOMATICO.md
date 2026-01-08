# 🔄 Como Configurar Monitor Automático

## ✅ Status Atual

O monitor funcionou perfeitamente! Encontrou **242 resultados**.

Mas ele está rodando **apenas quando você executa manualmente**.

## 🎯 Opções para Automatizar

### Opção 1: Usar API do app_vps.py (Recomendado)

O `app_vps.py` já tem suporte para monitor automático via thread.

**Como ativar:**

1. **Via API** (após deploy):
   ```bash
   curl -X POST http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/monitor/start
   ```

2. **Ou modificar Dockerfile** para iniciar automaticamente:
   - Já atualizei o Dockerfile para usar `iniciar_com_monitor.sh`
   - Faz redeploy no Coolify

### Opção 2: Cron Job no Coolify

No Coolify, configure um "Scheduled Task":

1. Vá em "Settings" → "Scheduled Tasks"
2. Adicione:
   - **Command**: `python3 monitor_selenium.py --uma-vez`
   - **Schedule**: `*/5 * * * *` (a cada 5 minutos)
   - Ou `*/10 * * * *` (a cada 10 minutos)

### Opção 3: Modificar app_vps.py para iniciar monitor automaticamente

Já está configurado! Basta usar:

```bash
python3 app_vps.py --monitor --intervalo 60
```

Isso inicia:
- Servidor web (porta 8000)
- Monitor em background (verifica a cada 60 segundos)

## 🚀 Solução Rápida: Redeploy com Monitor Automático

Atualizei o código para iniciar monitor automaticamente. Faça:

1. **No Coolify:**
   - Vá em seu projeto
   - Clique em **"Redeploy"** ou **"Deploy"**
   - O novo Dockerfile vai iniciar monitor + servidor automaticamente

2. **Ou via API:**
   ```bash
   curl -X POST http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/monitor/start
   ```

## 📊 Verificar se Está Rodando

### Ver status do monitor:
```bash
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/monitor/status
```

Resposta esperada:
```json
{
  "rodando": true,
  "thread_viva": true
}
```

### Ver logs:
No Coolify, vá em "View Logs" e procure por:
- `🔄 Monitor iniciado`
- `✓ X novos resultados encontrados!`

## ⚙️ Configuração de Intervalo

O monitor verifica a cada **60 segundos** por padrão.

Para mudar:

1. **Via API:**
   ```bash
   curl -X POST http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/monitor/start \
     -H "Content-Type: application/json" \
     -d '{"intervalo": 120}'
   ```
   (120 = 2 minutos)

2. **Ou modificar no código:**
   - Edite `app_vps.py`
   - Mude `--intervalo 60` para o valor desejado

## 🎯 Recomendações

- **Intervalo mínimo**: 60 segundos (para não sobrecarregar)
- **Intervalo recomendado**: 120-300 segundos (2-5 minutos)
- **Para produção**: 300 segundos (5 minutos) é ideal

## ✅ Checklist

- [x] Monitor funciona manualmente ✅
- [ ] Monitor configurado para rodar automaticamente
- [ ] Verificar logs após redeploy
- [ ] Testar API de status
- [ ] Confirmar que resultados estão sendo atualizados

## 🔍 Troubleshooting

### Monitor não inicia automaticamente?

1. Verifique logs no Coolify
2. Teste API: `POST /api/monitor/start`
3. Verifique se `monitor_selenium.py` está no container

### Monitor para de funcionar?

1. Verifique logs
2. Reinicie: `POST /api/monitor/stop` → `POST /api/monitor/start`
3. Ou faça redeploy

### Resultados não atualizam?

1. Verifique se monitor está rodando: `GET /api/monitor/status`
2. Force verificação: `POST /api/verificar-agora`
3. Verifique permissões do `resultados.json`

## 🎉 Próximos Passos

1. **Fazer redeploy** no Coolify (com novo Dockerfile)
2. **Verificar logs** para confirmar que monitor iniciou
3. **Aguardar alguns minutos** e verificar se resultados estão atualizando
4. **Monitorar dashboard** para ver novos resultados aparecendo

Tudo pronto! 🚀

