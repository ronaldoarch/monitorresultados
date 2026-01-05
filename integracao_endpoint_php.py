#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integração com Endpoint PHP do Painel
Chama o endpoint que faz busca, salvamento, sincronização e liquidação
"""

import requests
import time
import schedule
import threading
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# URL do endpoint PHP do painel
# Configure aqui ou via variável de ambiente ENDPOINT_PHP
ENDPOINT_PHP = os.getenv('ENDPOINT_PHP', 'https://lotbicho.com/backend/scraper/processar-resultados-completo.php')

def processar_resultados_via_php():
    """
    Chama endpoint PHP que faz tudo:
    - Busca resultados
    - Salva em games
    - Sincroniza com extractions
    - Liquida apostas
    - Retorna resultados formatados
    """
    try:
        print(f"🔄 Chamando endpoint PHP: {ENDPOINT_PHP}")
        
        response = requests.post(ENDPOINT_PHP, timeout=300)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('success'):
            summary = data.get('summary', {})
            
            print(f"✅ {summary.get('results_saved', 0)} resultados salvos")
            print(f"✅ {summary.get('extractions_synced', 0)} extrações sincronizadas")
            print(f"✅ {summary.get('bets_processed', 0)} apostas processadas")
            print(f"💰 {summary.get('bets_won', 0)} ganhas, {summary.get('bets_lost', 0)} perdidas")
            
            # Mostrar logs se houver
            if 'output' in data:
                for log in data['output']:
                    print(f"   {log}")
            
            return {
                'sucesso': True,
                'resultados': data.get('resultados', []),
                'summary': summary
            }
        else:
            erro = data.get('error', 'Erro desconhecido')
            print(f"❌ Erro: {erro}")
            return {
                'sucesso': False,
                'erro': erro
            }
            
    except requests.exceptions.Timeout:
        print("❌ Timeout ao chamar endpoint PHP")
        return {
            'sucesso': False,
            'erro': 'Timeout ao processar resultados'
        }
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return {
            'sucesso': False,
            'erro': f'Erro de conexão: {str(e)}'
        }
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return {
            'sucesso': False,
            'erro': str(e)
        }

# ==================== ROTAS DA API ====================

@app.route('/api/resultados/processar', methods=['POST'])
def api_processar_resultados():
    """Endpoint para processar resultados via PHP"""
    resultado = processar_resultados_via_php()
    
    if resultado['sucesso']:
        return jsonify(resultado)
    else:
        return jsonify(resultado), 500

@app.route('/api/resultados', methods=['GET'])
def api_listar_resultados():
    """Lista resultados (processa primeiro se necessário)"""
    # Processar resultados antes de retornar
    resultado = processar_resultados_via_php()
    
    if resultado['sucesso']:
        return jsonify({
            'resultados': resultado['resultados'],
            'summary': resultado['summary']
        })
    else:
        return jsonify({
            'resultados': [],
            'erro': resultado.get('erro')
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """Status do sistema"""
    return jsonify({
        'sistema': 'Integração com Endpoint PHP',
        'endpoint_php': ENDPOINT_PHP,
        'processamento_automatico': processamento_automatico_rodando,
        'timestamp': datetime.now().isoformat()
    })

# ==================== PROCESSAMENTO AUTOMÁTICO ====================

processamento_automatico_rodando = False

def processar_automaticamente():
    """Processa resultados automaticamente"""
    print(f"\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processamento automático...")
    processar_resultados_via_php()

def iniciar_processamento_automatico(intervalo_minutos=5):
    """Inicia processamento automático"""
    global processamento_automatico_rodando
    
    if processamento_automatico_rodando:
        print("⚠️  Processamento automático já está rodando")
        return
    
    processamento_automatico_rodando = True
    
    # Agendar execução
    schedule.every(intervalo_minutos).minutes.do(processar_automaticamente)
    
    print(f"✅ Processamento automático iniciado (a cada {intervalo_minutos} minutos)")
    
    def run_scheduler():
        """Executar scheduler em thread separada"""
        while processamento_automatico_rodando:
            schedule.run_pending()
            time.sleep(1)
    
    # Iniciar em thread separada
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    
    return thread

@app.route('/api/processamento/start', methods=['POST'])
def api_iniciar_processamento():
    """Inicia processamento automático"""
    intervalo = int(request.json.get('intervalo', 5)) if request.json else 5
    
    thread = iniciar_processamento_automatico(intervalo)
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'Processamento automático iniciado (a cada {intervalo} minutos)'
    })

@app.route('/api/processamento/stop', methods=['POST'])
def api_parar_processamento():
    """Para processamento automático"""
    global processamento_automatico_rodando
    processamento_automatico_rodando = False
    schedule.clear()
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Processamento automático parado'
    })

@app.route('/api/processamento/status', methods=['GET'])
def api_status_processamento():
    """Status do processamento automático"""
    return jsonify({
        'rodando': processamento_automatico_rodando,
        'proxima_execucao': schedule.next_run().isoformat() if schedule.jobs else None
    })

@app.route('/')
def index():
    """Dashboard principal"""
    return """
    <html>
    <head><title>Integração com Endpoint PHP</title></head>
    <body>
    <h1>🎰 Integração com Endpoint PHP</h1>
    <h2>Endpoints:</h2>
    <ul>
        <li>POST /api/resultados/processar - Processar resultados</li>
        <li>GET /api/resultados - Listar resultados (processa antes)</li>
        <li>GET /api/status - Status do sistema</li>
        <li>POST /api/processamento/start - Iniciar processamento automático</li>
        <li>POST /api/processamento/stop - Parar processamento automático</li>
        <li>GET /api/processamento/status - Status do processamento</li>
    </ul>
    <h2>Configuração:</h2>
    <p>Endpoint PHP: <code>{}</code></p>
    <p>Para mudar, edite a variável <code>ENDPOINT_PHP</code> no código.</p>
    </body>
    </html>
    """.format(ENDPOINT_PHP)

if __name__ == '__main__':
    from flask import request
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--endpoint-php', help='URL do endpoint PHP')
    parser.add_argument('--auto', action='store_true', help='Iniciar processamento automático')
    parser.add_argument('--intervalo', type=int, default=5, help='Intervalo em minutos')
    
    args = parser.parse_args()
    
    # Configurar endpoint PHP se fornecido
    if args.endpoint_php:
        global ENDPOINT_PHP
        ENDPOINT_PHP = args.endpoint_php
    
    # Iniciar processamento automático se solicitado
    if args.auto:
        iniciar_processamento_automatico(args.intervalo)
    
    print(f"🚀 Servidor iniciando em http://{args.host}:{args.port}")
    print(f"📡 Endpoint PHP: {ENDPOINT_PHP}")
    
    app.run(host=args.host, port=args.port, debug=False)

