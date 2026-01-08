# 🎯 Opção B - Integração com Endpoint PHP (RECOMENDADO)

## ✅ Por Que Esta Opção?

- ✅ Usa sistema existente do painel
- ✅ Mais simples de configurar
- ✅ Endpoint PHP já faz tudo
- ✅ Menos código para manter

## 🚀 Quick Start (3 Passos)

### 1. Configurar URL

```bash
# Opção A: Via script
./configurar_opcao_b.sh

# Opção B: Manualmente
export ENDPOINT_PHP="https://lotbicho.com/backend/scraper/processar-resultados-completo.php"
```

### 2. Iniciar Servidor

```bash
python3 integracao_endpoint_php.py --auto --intervalo 5 --port 5001
```

### 3. Testar

```bash
curl http://localhost:5001/api/resultados
```

**Pronto!** 🎉

## 📡 Endpoints Disponíveis

- `GET /api/resultados` - Lista resultados (processa antes)
- `POST /api/resultados/processar` - Força processamento
- `GET /api/status` - Status do sistema
- `POST /api/processamento/start` - Iniciar automático
- `GET /api/processamento/status` - Status do processamento

## 🔄 Como Funciona

```
Frontend → Python API → Endpoint PHP → Processa Tudo → Retorna
```

O endpoint PHP faz:
1. Busca resultados
2. Salva em games
3. Sincroniza com extractions
4. Liquida apostas
5. Retorna resultados

## 📖 Documentação Completa

Veja `PASSO_A_PASSO_OPCAO_B.md` para guia detalhado.

