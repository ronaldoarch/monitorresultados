# Configuração Gunicorn para produção

bind = "0.0.0.0:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Hooks para inicializar monitor automaticamente
def on_starting(server):
    """Executado quando Gunicorn inicia"""
    import app_vps
    app_vps.inicializar_monitor_automatico()

def when_ready(server):
    """Executado quando Gunicorn está pronto"""
    import app_vps
    # Garantir que monitor está rodando
    if not app_vps.monitor_iniciado:
        app_vps.inicializar_monitor_automatico()
