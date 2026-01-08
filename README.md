# 🎰 Monitor de Resultados - Bicho Certo

Sistema completo para monitorar resultados de loterias do site Bicho Certo em tempo real.

## 🚀 Deploy Rápido no Coolify

### Via Painel Web (Recomendado)

1. **Criar Projeto** no Coolify
2. **Conectar GitHub**: `ronaldoarch/monitorresultados`
3. **Branch**: `main`
4. **Port**: `8000`
5. **Deploy**!

O Coolify detecta automaticamente o `Dockerfile` e faz o deploy.

### Configuração Manual

- **Build Command**: (deixe vazio - usa Dockerfile)
- **Start Command**: (deixe vazio - usa Dockerfile)
- **Port**: `8000`

## 📋 Funcionalidades

- ✅ Monitor automático 24/7
- ✅ Dashboard em tempo real
- ✅ API REST completa
- ✅ Extração com Selenium
- ✅ Agrupamento por loteria e horário
- ✅ Atualização automática

## 🔗 Endpoints

- `GET /` - Dashboard
- `GET /api/resultados` - Todos os resultados (JSON)
- `GET /api/status` - Status do sistema
- `POST /api/verificar-agora` - Força verificação

## 📁 Estrutura

```
monitorresultados/
├── app_vps.py              # Aplicação Flask principal
├── monitor_selenium.py      # Monitor com Selenium
├── dashboard_mini.html     # Dashboard frontend
├── requirements_vps.txt    # Dependências Python
├── Dockerfile              # Container Docker
├── gunicorn_config.py      # Configuração Gunicorn
└── DEPLOY_COOLIFY.md       # Guia completo de deploy
```

## 🛠️ Tecnologias

- Python 3.11
- Flask (servidor web)
- Selenium (web scraping)
- Gunicorn (WSGI server)
- BeautifulSoup (parsing HTML)

## 📖 Documentação

- `DEPLOY_COOLIFY.md` - Guia completo para Coolify
- `COMO_DEPLOY_VPS.md` - Guia para VPS tradicional
- `DEPLOY_CLOUDFLARE.md` - Guia para Cloudflare Pages

## 🔧 Requisitos

- Python 3.11+
- Chrome/Chromium
- ChromeDriver
- 512MB RAM mínimo
- 5GB disco

## 📝 Licença

Uso pessoal.
