# 🚀 Aplicação Completa para VPS

## Por que VPS é Melhor?

✅ **Aplicação completa** - Não é só estático  
✅ **Monitor 24/7** - Roda automaticamente em background  
✅ **Sem Git** - Atualizações diretas, sem commit/push  
✅ **API completa** - Controle total via endpoints  
✅ **Mais barato** - ~$5/mês vs Cloudflare Workers  
✅ **Mais rápido** - Sem esperar deploy  

## Arquivos Criados

- `app_vps.py` - Aplicação Flask completa
- `requirements_vps.txt` - Dependências para VPS
- `deploy_vps.sh` - Script de deploy automático
- `gunicorn_config.py` - Configuração do servidor
- `COMO_DEPLOY_VPS.md` - Guia completo passo a passo

## Quick Start

### 1. Na VPS

```bash
# Instalar dependências do sistema
apt update && apt install -y python3 python3-pip python3-venv nginx

# Fazer upload dos arquivos (via Git ou SCP)
cd /opt
git clone SEU_REPO monitor-resultados
cd monitor-resultados

# Criar venv e instalar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_vps.txt
```

### 2. Testar

```bash
# Rodar servidor
python3 app_vps.py --monitor --intervalo 60

# Em outro terminal, testar:
curl http://localhost:5000/api/status
```

### 3. Configurar como Serviço

```bash
# Usar o script de deploy
./deploy_vps.sh

# Ou manualmente criar serviço systemd
sudo nano /etc/systemd/system/monitor-resultados.service
# (ver COMO_DEPLOY_VPS.md para conteúdo completo)

sudo systemctl enable monitor-resultados
sudo systemctl start monitor-resultados
```

## Funcionalidades

### Dashboard
- Acesse: `http://SEU_IP:5000/`
- Atualização automática a cada 30 segundos
- Filtros por loteria
- Estatísticas em tempo real

### API Endpoints

- `GET /api/resultados` - Todos os resultados
- `GET /api/status` - Status do sistema
- `POST /api/verificar-agora` - Força verificação
- `POST /api/monitor/start` - Inicia monitor
- `POST /api/monitor/stop` - Para monitor
- `GET /api/monitor/status` - Status do monitor

### Monitor Automático

O monitor roda em background e:
- Verifica resultados a cada X segundos (configurável)
- Atualiza `resultados.json` automaticamente
- Dashboard atualiza sozinho (sem recarregar página)
- Logs via systemd: `sudo journalctl -u monitor-resultados -f`

## Comparação: VPS vs Cloudflare

| Recurso | VPS | Cloudflare Pages |
|---------|-----|------------------|
| Aplicação completa | ✅ | ❌ (só estático) |
| Monitor automático | ✅ | ❌ (precisa Git) |
| API | ✅ | ⚠️ (precisa Workers) |
| Custo | $5/mês | Grátis* |
| Controle | ✅ Total | ⚠️ Limitado |
| Deploy | ✅ Instantâneo | ⚠️ 1-2 min |

*Cloudflare Workers tem limites no plano grátis

## Próximos Passos

1. **Escolher VPS**: DigitalOcean, Linode, Vultr, Hetzner
2. **Seguir guia**: `COMO_DEPLOY_VPS.md`
3. **Configurar domínio** (opcional): Nginx + SSL
4. **Monitorar**: `sudo journalctl -u monitor-resultados -f`

## Suporte

Ver `COMO_DEPLOY_VPS.md` para guia completo passo a passo!

