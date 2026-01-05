#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação completa para VPS
- Servidor web para dashboard
- API para resultados
- Monitor em background
"""

import os
import sys
import json
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, render_template_string, request
from flask_cors import CORS

# Adicionar venv ao path
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.14', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

app = Flask(__name__)
CORS(app)

# Importar monitor
try:
    from monitor_selenium import verificar, carregar_resultados
except ImportError:
    print("⚠️  Monitor não encontrado. API funcionará, mas monitor não rodará.")
    verificar = None
    carregar_resultados = lambda: {'resultados': [], 'ultima_verificacao': None}

# Variável global para controlar monitor
monitor_rodando = False
monitor_thread = None

def monitor_loop(intervalo=60):
    """Loop do monitor em background"""
    global monitor_rodando
    monitor_rodando = True
    
    print(f"🔄 Monitor iniciado (verifica a cada {intervalo}s)")
    
    while monitor_rodando:
        try:
            if verificar:
                novos = verificar()
                if novos > 0:
                    print(f"✅ {novos} novos resultados encontrados!")
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
        
        # Aguardar intervalo
        for _ in range(intervalo):
            if not monitor_rodando:
                break
            time.sleep(1)
    
    print("🛑 Monitor encerrado")

@app.route('/')
def index():
    """Dashboard principal"""
    try:
        with open('dashboard_mini.html', 'r', encoding='utf-8') as f:
            return render_template_string(f.read())
    except:
        # Fallback se não encontrar
        return """
        <html>
        <head><title>Monitor de Resultados</title></head>
        <body>
        <h1>Monitor de Resultados</h1>
        <p><a href="/api/resultados">Ver resultados (JSON)</a></p>
        <p><a href="/api/status">Status do sistema</a></p>
        </body>
        </html>
        """

@app.route('/api/resultados')
def api_resultados():
    """API para retornar resultados"""
    try:
        dados = carregar_resultados()
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'resultados': [],
            'erro': str(e),
            'ultima_verificacao': None
        }), 500

@app.route('/api/status')
def api_status():
    """Status do sistema"""
    dados = carregar_resultados()
    return jsonify({
        'monitor_rodando': monitor_rodando,
        'total_resultados': len(dados.get('resultados', [])),
        'ultima_verificacao': dados.get('ultima_verificacao'),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/verificar-agora', methods=['POST'])
def verificar_agora():
    """Força verificação imediata"""
    if not verificar:
        return jsonify({'erro': 'Monitor não disponível'}), 500
    
    try:
        novos = verificar()
        return jsonify({
            'sucesso': True,
            'novos_resultados': novos,
            'mensagem': f'{novos} novos resultados encontrados' if novos > 0 else 'Nenhum resultado novo'
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/start', methods=['POST'])
def monitor_start():
    """Inicia monitor"""
    global monitor_thread, monitor_rodando
    
    if monitor_rodando:
        return jsonify({'mensagem': 'Monitor já está rodando'}), 400
    
    if not verificar:
        return jsonify({'erro': 'Monitor não disponível'}), 500
    
    intervalo = int(request.json.get('intervalo', 60)) if request.json else 60
    
    monitor_thread = threading.Thread(target=monitor_loop, args=(intervalo,), daemon=True)
    monitor_thread.start()
    
    return jsonify({
        'sucesso': True,
        'mensagem': f'Monitor iniciado (intervalo: {intervalo}s)'
    })

@app.route('/api/monitor/stop', methods=['POST'])
def monitor_stop():
    """Para monitor"""
    global monitor_rodando
    
    if not monitor_rodando:
        return jsonify({'mensagem': 'Monitor não está rodando'}), 400
    
    monitor_rodando = False
    return jsonify({'sucesso': True, 'mensagem': 'Monitor parado'})

@app.route('/api/monitor/status', methods=['GET'])
def monitor_status():
    """Status do monitor"""
    return jsonify({
        'rodando': monitor_rodando,
        'thread_viva': monitor_thread.is_alive() if monitor_thread else False
    })

# Servir arquivos estáticos
@app.route('/resultados.json')
def resultados_json():
    """Serve resultados.json"""
    try:
        return send_from_directory('.', 'resultados.json')
    except:
        return jsonify({'resultados': []}), 404

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, help='Porta do servidor')
    parser.add_argument('--host', default='0.0.0.0', help='Host (0.0.0.0 para VPS)')
    parser.add_argument('--monitor', action='store_true', help='Iniciar monitor automaticamente')
    parser.add_argument('--intervalo', type=int, default=60, help='Intervalo do monitor em segundos')
    args = parser.parse_args()
    
    # Iniciar monitor se solicitado
    if args.monitor and verificar:
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(args.intervalo,),
            daemon=True
        )
        monitor_thread.start()
        print(f"✅ Monitor iniciado automaticamente (intervalo: {args.intervalo}s)")
    
    print(f"🚀 Servidor iniciando em http://{args.host}:{args.port}")
    print(f"📊 Dashboard: http://{args.host}:{args.port}/")
    print(f"🔌 API: http://{args.host}:{args.port}/api/resultados")
    
    app.run(host=args.host, port=args.port, debug=False)

