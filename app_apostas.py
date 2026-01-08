#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API completa para sistema de apostas
Integra monitor de resultados com liquidação automática
"""

import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Adicionar ao path
sys.path.insert(0, os.path.dirname(__file__))

from sistema_liquidacao import SistemaLiquidacao
from monitor_selenium import verificar, carregar_resultados

app = Flask(__name__)
CORS(app)

# Inicializar sistema de liquidação
sistema = SistemaLiquidacao()

# Variável para controlar monitor
monitor_rodando = False
monitor_thread = None

def monitor_loop(intervalo=60):
    """Loop do monitor que também processa liquidações"""
    global monitor_rodando
    monitor_rodando = True
    
    print(f"🔄 Monitor iniciado (verifica a cada {intervalo}s)")
    
    while monitor_rodando:
        try:
            # Verificar novos resultados
            novos = verificar()
            
            if novos > 0:
                print(f"✅ {novos} novos resultados encontrados")
                # Processar liquidações automaticamente
                sistema.processar_novos_resultados()
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
        
        # Aguardar intervalo
        for _ in range(intervalo):
            if not monitor_rodando:
                break
            time.sleep(1)
    
    print("🛑 Monitor encerrado")

# ==================== ROTAS DE APOSTAS ====================

@app.route('/api/apostas', methods=['POST'])
def criar_aposta():
    """Cria uma nova aposta"""
    try:
        data = request.json
        aposta_id = sistema.criar_aposta(
            usuario_id=data['usuario_id'],
            numero=data['numero'],
            animal=data['animal'],
            valor=float(data['valor']),
            loteria=data['loteria'],
            horario=data['horario'],
            tipo_aposta=data.get('tipo_aposta', 'grupo'),
            multiplicador=float(data.get('multiplicador', 18.0))
        )
        return jsonify({
            'sucesso': True,
            'aposta_id': aposta_id,
            'mensagem': 'Aposta criada com sucesso'
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 400

@app.route('/api/apostas/<int:aposta_id>', methods=['GET'])
def ver_aposta(aposta_id):
    """Ver detalhes de uma aposta"""
    from models import Aposta
    from sistema_liquidacao import SistemaLiquidacao
    
    session = sistema.Session()
    try:
        aposta = session.query(Aposta).get(aposta_id)
        if not aposta:
            return jsonify({'erro': 'Aposta não encontrada'}), 404
        
        return jsonify({
            'id': aposta.id,
            'numero': aposta.numero,
            'animal': aposta.animal,
            'valor': aposta.valor,
            'loteria': aposta.loteria,
            'horario': aposta.horario,
            'status': aposta.status,
            'data_aposta': aposta.data_aposta.isoformat() if aposta.data_aposta else None
        })
    finally:
        session.close()

@app.route('/api/apostas/usuario/<int:usuario_id>', methods=['GET'])
def listar_apostas_usuario(usuario_id):
    """Lista apostas de um usuário"""
    from models import Aposta
    
    session = sistema.Session()
    try:
        apostas = session.query(Aposta).filter_by(usuario_id=usuario_id).order_by(Aposta.data_aposta.desc()).all()
        
        return jsonify({
            'apostas': [{
                'id': a.id,
                'numero': a.numero,
                'animal': a.animal,
                'valor': a.valor,
                'loteria': a.loteria,
                'horario': a.horario,
                'status': a.status,
                'data_aposta': a.data_aposta.isoformat() if a.data_aposta else None
            } for a in apostas]
        })
    finally:
        session.close()

# ==================== ROTAS DE RESULTADOS ====================

@app.route('/api/resultados', methods=['GET'])
def listar_resultados():
    """Lista todos os resultados"""
    dados = carregar_resultados()
    return jsonify(dados)

@app.route('/api/resultados/liquidar', methods=['POST'])
def liquidar_resultados():
    """Força liquidação de resultados novos"""
    try:
        total = sistema.processar_novos_resultados()
        return jsonify({
            'sucesso': True,
            'apostas_liquidadas': total,
            'mensagem': f'{total} apostas liquidadas'
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

# ==================== ROTAS DE USUÁRIOS ====================

@app.route('/api/usuarios/<int:usuario_id>/saldo', methods=['GET'])
def consultar_saldo(usuario_id):
    """Consulta saldo de um usuário"""
    from models import Usuario
    
    session = sistema.Session()
    try:
        usuario = session.query(Usuario).get(usuario_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'usuario_id': usuario.id,
            'saldo': usuario.saldo,
            'nome': usuario.nome
        })
    finally:
        session.close()

# ==================== ROTAS DE MONITOR ====================

@app.route('/api/monitor/start', methods=['POST'])
def monitor_start():
    """Inicia monitor com liquidação automática"""
    global monitor_thread, monitor_rodando
    
    if monitor_rodando:
        return jsonify({'mensagem': 'Monitor já está rodando'}), 400
    
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
    monitor_rodando = False
    return jsonify({'sucesso': True, 'mensagem': 'Monitor parado'})

@app.route('/api/monitor/status', methods=['GET'])
def monitor_status():
    """Status do monitor"""
    return jsonify({
        'rodando': monitor_rodando,
        'thread_viva': monitor_thread.is_alive() if monitor_thread else False
    })

# ==================== ROTA PRINCIPAL ====================

@app.route('/')
def index():
    """Dashboard principal"""
    return """
    <html>
    <head><title>Sistema de Apostas - API</title></head>
    <body>
    <h1>🎰 Sistema de Apostas - API</h1>
    <h2>Endpoints Disponíveis:</h2>
    <ul>
        <li>POST /api/apostas - Criar aposta</li>
        <li>GET /api/apostas/{id} - Ver aposta</li>
        <li>GET /api/apostas/usuario/{id} - Listar apostas do usuário</li>
        <li>GET /api/resultados - Listar resultados</li>
        <li>POST /api/resultados/liquidar - Forçar liquidação</li>
        <li>GET /api/usuarios/{id}/saldo - Consultar saldo</li>
        <li>POST /api/monitor/start - Iniciar monitor</li>
        <li>POST /api/monitor/stop - Parar monitor</li>
        <li>GET /api/monitor/status - Status do monitor</li>
    </ul>
    </body>
    </html>
    """

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001, help='Porta do servidor')
    parser.add_argument('--host', default='0.0.0.0', help='Host')
    parser.add_argument('--monitor', action='store_true', help='Iniciar monitor automaticamente')
    parser.add_argument('--intervalo', type=int, default=60, help='Intervalo do monitor')
    args = parser.parse_args()
    
    if args.monitor:
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(args.intervalo,),
            daemon=True
        )
        monitor_thread.start()
        print(f"✅ Monitor iniciado automaticamente (intervalo: {args.intervalo}s)")
    
    print(f"🚀 Servidor de apostas iniciando em http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)

