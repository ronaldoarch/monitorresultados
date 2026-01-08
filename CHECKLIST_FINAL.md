# ✅ Checklist Final - O Que Fazer Agora

## 📋 Status Atual

### ✅ Já Criado:
- [x] Monitor de resultados (monitor_selenium.py)
- [x] Sistema de liquidação com extrações
- [x] API de apostas (app_apostas_extractions.py)
- [x] Integração com endpoint PHP (integracao_endpoint_php.py)
- [x] Modelos de banco de dados
- [x] Scripts auxiliares
- [x] Documentação completa

## 🎯 O Que Falta Fazer

### 1. **Escolher Qual Sistema Usar**

Você tem 2 opções:

#### Opção A: Sistema Python Completo (Recomendado se quiser independência)
- Usa: `app_apostas_extractions.py`
- Monitor Python próprio
- Banco de dados Python (SQLite/PostgreSQL)
- **Prós**: Controle total, independente do PHP
- **Contras**: Precisa criar extrações manualmente

#### Opção B: Integração com Endpoint PHP (Recomendado se já tem PHP funcionando)
- Usa: `integracao_endpoint_php.py`
- Chama endpoint PHP que faz tudo
- **Prós**: Usa sistema existente, mais simples
- **Contras**: Depende do endpoint PHP estar funcionando

**Recomendação**: Use **Opção B** se o endpoint PHP já está funcionando.

---

### 2. **Configurar Endpoint PHP**

Se escolher Opção B:

```python
# Editar integracao_endpoint_php.py
ENDPOINT_PHP = 'https://lotbicho.com/backend/scraper/processar-resultados-completo.php'
```

Ou via variável de ambiente:
```bash
export ENDPOINT_PHP="https://lotbicho.com/backend/scraper/processar-resultados-completo.php"
```

---

### 3. **Testar Endpoint PHP**

```bash
# Testar se endpoint responde
curl -X POST https://lotbicho.com/backend/scraper/processar-resultados-completo.php
```

Deve retornar JSON com `success: true`.

---

### 4. **Iniciar Servidor**

#### Se usar Opção B (Endpoint PHP):

```bash
python3 integracao_endpoint_php.py \
  --endpoint-php "https://lotbicho.com/backend/scraper/processar-resultados-completo.php" \
  --auto \
  --intervalo 5 \
  --port 5001
```

#### Se usar Opção A (Sistema Completo):

```bash
# 1. Criar extrações primeiro
python3 script_criar_extracao.py --loteria "PT Rio de Janeiro" --horario "11:30"

# 2. Iniciar servidor
python3 app_apostas_extractions.py --monitor --intervalo 60 --port 5001
```

---

### 5. **Testar API**

```bash
# Testar processamento
curl -X POST http://localhost:5001/api/resultados/processar

# Listar resultados
curl http://localhost:5001/api/resultados

# Status
curl http://localhost:5001/api/status
```

---

### 6. **Integrar com Frontend**

#### Adicionar arquivo JavaScript:

```javascript
// api_frontend.js já está criado, apenas ajustar URL
const API_BASE_URL = 'http://seu-servidor:5001/api';
```

#### Modificar tela de apostas:

```javascript
// Buscar extrações (se usar Opção A)
const extracoes = await fetch('/api/extracoes-disponiveis').then(r => r.json());

// Ou processar resultados (se usar Opção B)
const resultados = await fetch('/api/resultados').then(r => r.json());
```

---

### 7. **Configurar Processamento Automático**

#### Opção 1: Via API

```bash
curl -X POST http://localhost:5001/api/processamento/start \
  -H "Content-Type: application/json" \
  -d '{"intervalo": 5}'
```

#### Opção 2: Via Linha de Comando

```bash
python3 integracao_endpoint_php.py --auto --intervalo 5
```

#### Opção 3: Via Cron (Servidor)

```bash
# Executar a cada 5 minutos
*/5 * * * * curl -X POST http://localhost:5001/api/resultados/processar
```

---

### 8. **Deploy no Coolify**

#### Atualizar Dockerfile (se necessário):

```dockerfile
# Se usar integracao_endpoint_php.py
CMD ["python3", "integracao_endpoint_php.py", "--auto", "--intervalo", "5", "--port", "8000"]
```

#### Ou usar app_vps.py:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app_vps:app"]
```

---

## 🎯 Decisões a Tomar

### 1. Qual sistema usar?
- [ ] Opção A: Sistema Python completo
- [ ] Opção B: Integração com endpoint PHP ⭐ (Recomendado)

### 2. Onde rodar?
- [ ] Coolify (já configurado)
- [ ] VPS tradicional
- [ ] Servidor local

### 3. Processamento automático?
- [ ] Sim, via API (schedule)
- [ ] Sim, via cron
- [ ] Não, apenas manual

---

## 📝 Passos Imediatos

### Se escolher Opção B (Endpoint PHP):

1. ✅ **Configurar URL do endpoint**:
   ```python
   # Editar integracao_endpoint_php.py linha 15
   ENDPOINT_PHP = 'https://lotbicho.com/backend/scraper/processar-resultados-completo.php'
   ```

2. ✅ **Testar endpoint**:
   ```bash
   curl -X POST https://lotbicho.com/backend/scraper/processar-resultados-completo.php
   ```

3. ✅ **Iniciar servidor**:
   ```bash
   python3 integracao_endpoint_php.py --auto --intervalo 5 --port 5001
   ```

4. ✅ **Testar API**:
   ```bash
   curl http://localhost:5001/api/resultados
   ```

5. ✅ **Integrar frontend**:
   - Adicionar `api_frontend.js` ao projeto
   - Modificar tela de apostas
   - Testar criação de aposta

6. ✅ **Deploy no Coolify**:
   - Fazer push no GitHub
   - Redeploy no Coolify
   - Verificar logs

---

### Se escolher Opção A (Sistema Completo):

1. ✅ **Criar extrações**:
   ```bash
   python3 script_criar_extracao.py --loteria "PT Rio de Janeiro" --horario "11:30"
   ```

2. ✅ **Criar usuários**:
   ```bash
   python3 script_criar_usuario.py --nome "Teste" --email "teste@exemplo.com" --saldo 100
   ```

3. ✅ **Iniciar servidor**:
   ```bash
   python3 app_apostas_extractions.py --monitor --intervalo 60 --port 5001
   ```

4. ✅ **Testar criação de aposta**:
   ```bash
   curl -X POST http://localhost:5001/api/apostas \
     -H "Content-Type: application/json" \
     -d '{
       "usuario_id": 1,
       "extraction_id": 1,
       "numero": "1234",
       "animal": "Cavalo",
       "valor": 10.0
     }'
   ```

5. ✅ **Verificar liquidação**:
   - Aguardar monitor processar
   - Verificar saldo do usuário
   - Confirmar que apostas foram liquidadas

---

## 🔍 Verificações Finais

### Backend:
- [ ] Servidor rodando
- [ ] API respondendo
- [ ] Endpoint PHP funcionando (se Opção B)
- [ ] Processamento automático ativo (se configurado)

### Frontend:
- [ ] API conectada
- [ ] Tela de apostas funcionando
- [ ] Resultados aparecendo
- [ ] Saldo atualizando
- [ ] Histórico de apostas funcionando

### Banco de Dados:
- [ ] Extrações criadas (se Opção A)
- [ ] Usuários criados
- [ ] Apostas sendo salvas
- [ ] Liquidações sendo registradas

---

## 🚀 Próximo Passo Recomendado

**Se você já tem o endpoint PHP funcionando:**

1. Configure a URL no `integracao_endpoint_php.py`
2. Teste o endpoint PHP manualmente
3. Inicie o servidor Python
4. Teste a API
5. Integre com o frontend

**Tempo estimado**: 30 minutos

---

## 📞 Arquivos de Referência

- `GUIA_INTEGRACAO_ENDPOINT_PHP.md` - Guia completo Opção B
- `GUIA_INTEGRACAO_EXTRACTIONS.md` - Guia completo Opção A
- `RESUMO_INTEGRACAO_PHP.md` - Resumo rápido
- `integracao_endpoint_php.py` - Código Opção B
- `app_apostas_extractions.py` - Código Opção A

---

## ❓ Dúvidas?

1. **Qual opção escolher?** → Use Opção B se endpoint PHP já funciona
2. **Como testar?** → Use curl ou Postman
3. **Como integrar frontend?** → Veja `GUIA_INTEGRACAO_FRONTEND.md`
4. **Como fazer deploy?** → Veja `DEPLOY_COOLIFY.md`

Tudo está pronto, só falta escolher e configurar! 🎯

