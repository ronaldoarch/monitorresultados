# 🔧 Troubleshooting - Dashboard sem Dados

## Problema: Dashboard mostra "Nenhum resultado"

### Verificações Rápidas

1. **Verificar se a API está funcionando:**
   ```
   http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/status
   ```

2. **Verificar se resultados.json existe:**
   ```
   http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados
   ```

3. **Verificar logs no Coolify:**
   - No painel Coolify, vá em "View Logs"
   - Procure por erros relacionados a:
     - `resultados.json`
     - `monitor_selenium`
     - `carregar_resultados`

## Soluções

### Solução 1: Criar resultados.json Inicial

Se o arquivo não existe, crie um vazio:

```bash
# No terminal do Coolify ou via SSH
echo '{"resultados": [], "ultima_verificacao": null, "total_resultados": 0}' > resultados.json
```

### Solução 2: Verificar Permissões

O arquivo `resultados.json` precisa ser gravável:

```bash
chmod 666 resultados.json
```

### Solução 3: Executar Monitor Manualmente

Para gerar dados iniciais:

1. No Coolify, vá em "Terminal" ou "Execute Command"
2. Execute:
   ```bash
   python3 monitor_selenium.py --uma-vez
   ```

### Solução 4: Verificar Variáveis de Ambiente

No Coolify, adicione estas variáveis:

```
PYTHONUNBUFFERED=1
FLASK_ENV=production
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### Solução 5: Verificar ChromeDriver

Se o monitor não funciona, pode ser ChromeDriver:

```bash
# Verificar se está instalado
which chromedriver
chromedriver --version

# Se não funcionar, reinstalar
apt-get update
apt-get install -y chromium-chromedriver
```

## Testes

### Teste 1: API Status
```bash
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/status
```

Deve retornar:
```json
{
  "monitor_rodando": false,
  "total_resultados": 0,
  "ultima_verificacao": null,
  "timestamp": "..."
}
```

### Teste 2: API Resultados
```bash
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados
```

### Teste 3: Forçar Verificação
```bash
curl -X POST http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/verificar-agora
```

## Configuração do Monitor Automático

Para o monitor rodar automaticamente, você precisa:

1. **Opção A: Iniciar com monitor**
   - No Dockerfile, o CMD já está configurado para Gunicorn
   - O monitor precisa ser iniciado separadamente

2. **Opção B: Modificar app_vps.py para iniciar monitor**
   - Já está configurado para iniciar com `--monitor`
   - Mas precisa ser chamado corretamente

3. **Opção C: Usar dois containers**
   - Container 1: app_vps.py (servidor web)
   - Container 2: monitor_selenium.py (monitor)

## Solução Rápida: Iniciar Monitor Manualmente

No Coolify, vá em "Execute Command" e rode:

```bash
python3 monitor_selenium.py --uma-vez
```

Isso vai:
1. Verificar todas as URLs
2. Extrair resultados
3. Salvar em `resultados.json`
4. Dashboard vai atualizar automaticamente

## Verificar se Funcionou

Após executar o monitor:

1. Verifique `resultados.json`:
   ```bash
   cat resultados.json
   ```

2. Verifique no dashboard:
   - Recarregue a página
   - Clique em "Atualizar"
   - Deve mostrar resultados

## Próximos Passos

1. ✅ Verificar logs no Coolify
2. ✅ Testar API endpoints
3. ✅ Executar monitor manualmente
4. ✅ Configurar monitor automático (se necessário)

