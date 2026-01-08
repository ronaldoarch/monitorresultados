#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação Flask para Monitor Deu no Poste
Servidor web separado para monitorar apenas deunoposte.com.br
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar monitor Deu no Poste
try:
    from monitor_deunoposte import MonitorDeuNoPoste
    monitor_deunoposte = MonitorDeuNoPoste()
    MONITOR_DISPONIVEL = True
    logger.info("✅ Monitor Deu no Poste carregado com sucesso")
except ImportError as e:
    logger.warning(f"⚠️  Monitor Deu no Poste não encontrado: {e}")
    monitor_deunoposte = None
    MONITOR_DISPONIVEL = False
except Exception as e:
    logger.error(f"❌ Erro ao inicializar Monitor Deu no Poste: {e}")
    monitor_deunoposte = None
    MONITOR_DISPONIVEL = False

# Variável global para controlar monitor
monitor_rodando = False
monitor_thread = None

def monitor_loop(intervalo=300):
    """Loop do monitor em background - apenas Deu no Poste"""
    global monitor_rodando
    monitor_rodando = True
    
    logger.info(f"🔄 Monitor Deu no Poste iniciado (verifica a cada {intervalo}s)")
    
    while monitor_rodando:
        try:
            if MONITOR_DISPONIVEL and monitor_deunoposte:
                logger.info("🔍 Iniciando monitoramento Deu no Poste...")
                resultados = monitor_deunoposte.monitorar_todos()
                if resultados:
                    # Salvar resultados
                    monitor_deunoposte.salvar_resultados(resultados, "resultados_deunoposte.json")
                    logger.info(f"✅ Deu no Poste: {len(resultados)} resultados coletados!")
                else:
                    logger.info("⚠️  Deu no Poste: Nenhum resultado encontrado")
            else:
                logger.warning("⚠️  Monitor Deu no Poste não disponível")
                    
        except Exception as e:
            logger.error(f"❌ Erro no monitor: {e}", exc_info=True)
        
        # Aguardar intervalo
        for _ in range(intervalo):
            if not monitor_rodando:
                break
            time.sleep(1)
    
    logger.info("🛑 Monitor Deu no Poste encerrado")

@app.route('/')
def index():
    """Dashboard principal"""
    return """
    <html>
    <head>
        <title>Monitor Deu no Poste</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stat-value {
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }
            .endpoints {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .endpoint {
                padding: 10px;
                margin: 5px 0;
                background: #f8f9fa;
                border-left: 4px solid #667eea;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            .btn:hover {
                background: #5568d3;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎰 Monitor Deu no Poste</h1>
            <p>Monitoramento de resultados de deunoposte.com.br</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-resultados">-</div>
                <div>Total de Resultados</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="ultima-verificacao">-</div>
                <div>Última Verificação</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="status-monitor">-</div>
                <div>Status do Monitor</div>
            </div>
        </div>
        
        <div class="endpoints">
            <h2>📡 Endpoints Disponíveis</h2>
            <div class="endpoint">
                <strong>GET</strong> <code>/api/resultados</code> - Todos os resultados
            </div>
            <div class="endpoint">
                <strong>GET</strong> <code>/api/status</code> - Status do sistema
            </div>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/verificar-agora</code> - Forçar verificação
            </div>
            <div class="endpoint">
                <strong>GET</strong> <code>/resultados_deunoposte.json</code> - Arquivo JSON
            </div>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/monitor/start</code> - Iniciar monitor
            </div>
            <div class="endpoint">
                <strong>POST</strong> <code>/api/monitor/stop</code> - Parar monitor
            </div>
            <div class="endpoint">
                <strong>GET</strong> <code>/api/monitor/status</code> - Status do monitor
            </div>
            
            <div style="margin-top: 20px;">
                <button class="btn" onclick="atualizarStatus()">🔄 Atualizar Status</button>
                <button class="btn" onclick="verificarAgora()">⚡ Verificar Agora</button>
            </div>
        </div>
        
        <script>
            async function atualizarStatus() {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    document.getElementById('total-resultados').textContent = data.total_resultados || 0;
                    document.getElementById('ultima-verificacao').textContent = 
                        data.ultima_verificacao ? new Date(data.ultima_verificacao).toLocaleString('pt-BR') : 'N/A';
                    document.getElementById('status-monitor').textContent = 
                        data.monitor_rodando ? '🟢 Ativo' : '🔴 Inativo';
                } catch (error) {
                    console.error('Erro:', error);
                }
            }
            
            async function verificarAgora() {
                try {
                    const response = await fetch('/api/verificar-agora', { method: 'POST' });
                    const data = await response.json();
                    alert(data.mensagem || 'Verificação concluída!');
                    atualizarStatus();
                } catch (error) {
                    console.error('Erro:', error);
                }
            }
            
            // Atualizar status ao carregar
            atualizarStatus();
            setInterval(atualizarStatus, 30000); // Atualizar a cada 30 segundos
        </script>
    </body>
    </html>
    """

@app.route('/api/resultados')
def api_resultados():
    """API para retornar resultados do Deu no Poste"""
    try:
        if os.path.exists('resultados_deunoposte.json'):
            with open('resultados_deunoposte.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                return jsonify(dados)
        else:
            return jsonify({
                'resultados': [],
                'total_resultados': 0,
                'ultima_verificacao': None,
                'fonte': 'deunoposte.com.br',
                'mensagem': 'Nenhum resultado coletado ainda'
            })
    except Exception as e:
        logger.error(f"Erro ao carregar resultados: {e}")
        return jsonify({
            'resultados': [],
            'erro': str(e),
            'ultima_verificacao': None
        }), 500

@app.route('/api/status')
def api_status():
    """Status do sistema"""
    total_resultados = 0
    ultima_verificacao = None
    
    try:
        if os.path.exists('resultados_deunoposte.json'):
            with open('resultados_deunoposte.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
                total_resultados = dados.get('total_resultados', 0)
                ultima_verificacao = dados.get('ultima_verificacao')
    except:
        pass
    
    return jsonify({
        'monitor_rodando': monitor_rodando,
        'monitor_disponivel': MONITOR_DISPONIVEL,
        'total_resultados': total_resultados,
        'ultima_verificacao': ultima_verificacao,
        'timestamp': datetime.now().isoformat(),
        'fonte': 'deunoposte.com.br'
    })

@app.route('/api/verificar-agora', methods=['POST'])
def verificar_agora():
    """Força verificação imediata"""
    if not MONITOR_DISPONIVEL or not monitor_deunoposte:
        return jsonify({
            'sucesso': False,
            'erro': 'Monitor Deu no Poste não disponível'
        }), 500
    
    try:
        logger.info("⚡ Forçando verificação imediata do Deu no Poste...")
        resultados = monitor_deunoposte.monitorar_todos()
        
        if resultados:
            monitor_deunoposte.salvar_resultados(resultados, "resultados_deunoposte.json")
            return jsonify({
                'sucesso': True,
                'total_resultados': len(resultados),
                'mensagem': f'{len(resultados)} resultados coletados do Deu no Poste!'
            })
        else:
            return jsonify({
                'sucesso': True,
                'total_resultados': 0,
                'mensagem': 'Nenhum resultado encontrado'
            })
    except Exception as e:
        logger.error(f"Erro ao verificar: {e}", exc_info=True)
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/start', methods=['POST'])
def monitor_start():
    """Inicia monitor em background"""
    global monitor_rodando, monitor_thread
    
    if monitor_rodando:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Monitor já está rodando'
        })
    
    if not MONITOR_DISPONIVEL:
        return jsonify({
            'sucesso': False,
            'erro': 'Monitor não disponível'
        }), 500
    
    try:
        intervalo = request.json.get('intervalo', 300) if request.json else 300
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(intervalo,),
            daemon=True
        )
        monitor_thread.start()
        
        return jsonify({
            'sucesso': True,
            'mensagem': f'Monitor iniciado (intervalo: {intervalo}s)'
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/stop', methods=['POST'])
def monitor_stop():
    """Para monitor"""
    global monitor_rodando
    
    if not monitor_rodando:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Monitor não está rodando'
        })
    
    monitor_rodando = False
    return jsonify({
        'sucesso': True,
        'mensagem': 'Monitor parado'
    })

@app.route('/api/monitor/status', methods=['GET'])
def monitor_status():
    """Status do monitor"""
    return jsonify({
        'rodando': monitor_rodando,
        'disponivel': MONITOR_DISPONIVEL,
        'thread_viva': monitor_thread is not None and monitor_thread.is_alive() if monitor_thread else False
    })

@app.route('/resultados_deunoposte.json')
def resultados_json():
    """Retorna arquivo JSON de resultados"""
    try:
        return send_from_directory('.', 'resultados_deunoposte.json')
    except:
        return jsonify({
            'resultados': [],
            'ultima_verificacao': None,
            'total_resultados': 0,
            'fonte': 'deunoposte.com.br'
        })

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8081, help='Porta do servidor (padrão: 8081)')
    parser.add_argument('--host', default='0.0.0.0', help='Host (0.0.0.0 para VPS)')
    parser.add_argument('--monitor', action='store_true', help='Iniciar monitor automaticamente')
    parser.add_argument('--intervalo', type=int, default=300, help='Intervalo do monitor em segundos (padrão: 300 = 5 minutos)')
    args = parser.parse_args()
    
    # Iniciar monitor se solicitado
    if args.monitor and MONITOR_DISPONIVEL:
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(args.intervalo,),
            daemon=True
        )
        monitor_thread.start()
        logger.info(f"✅ Monitor Deu no Poste iniciado automaticamente (intervalo: {args.intervalo}s)")
    
    logger.info(f"🚀 Servidor Deu no Poste iniciando em http://{args.host}:{args.port}")
    logger.info(f"📊 Dashboard: http://{args.host}:{args.port}/")
    logger.info(f"🔌 API: http://{args.host}:{args.port}/api/resultados")
    
    app.run(host=args.host, port=args.port, debug=False)
