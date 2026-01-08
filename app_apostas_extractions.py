#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API de Apostas com Sistema de Extrações
Adaptado para trabalhar com extrações pré-criadas
"""

import os
import sys
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(__file__))

from sistema_liquidacao_extractions import SistemaLiquidacaoExtractions
from monitor_selenium import verificar, carregar_resultados

app = Flask(__name__)
CORS(app)

# Inicializar sistema
sistema = SistemaLiquidacaoExtractions()

# Monitor
monitor_rodando = False
monitor_thread = None

def monitor_loop(intervalo=60):
    """Loop do monitor que processa liquidações por extração"""
    global monitor_rodando
    monitor_rodando = True
    
    print(f"🔄 Monitor iniciado (verifica a cada {intervalo}s)")
    
    while monitor_rodando:
        try:
            # Verificar novos resultados
            novos = verificar()
            
            if novos > 0:
                print(f"✅ {novos} novos resultados encontrados")
                # Processar liquidações por extração
                sistema.processar_resultados_monitor()
        except Exception as e:
            print(f"❌ Erro no monitor: {e}")
        
        for _ in range(intervalo):
            if not monitor_rodando:
                break
            time.sleep(1)
    
    print("🛑 Monitor encerrado")

# ==================== ROTAS DE EXTRAÇÕES ====================

@app.route('/api/extracoes-disponiveis', methods=['GET'])
def listar_extracoes_disponiveis():
    """Lista extrações disponíveis para apostas"""
    try:
        extracoes = sistema.listar_extracoes_disponiveis()
        return jsonify({
            'sucesso': True,
            'extracoes': extracoes
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/extracoes/<int:extraction_id>', methods=['GET'])
def ver_extracao(extraction_id):
    """Ver detalhes de uma extração"""
    from models import Extracao
    session = sistema.Session()
    try:
        extracao = session.query(Extracao).get(extraction_id)
        if not extracao:
            return jsonify({'erro': 'Extração não encontrada'}), 404
        
        agora = datetime.utcnow()
        esta_aberta = agora < extracao.close_time
        
        return jsonify({
            'id': extracao.id,
            'loteria': extracao.loteria,
            'horario': extracao.horario,
            'close_time': extracao.close_time.isoformat(),
            'real_close_time': extracao.real_close_time.isoformat(),
            'status': extracao.status,
            'esta_aberta': esta_aberta,
            'fecha_em_timestamp': int(extracao.close_time.timestamp())
        })
    finally:
        session.close()

# ==================== ROTAS DE APOSTAS ====================

@app.route('/api/apostas', methods=['POST'])
def criar_aposta():
    """Cria aposta vinculada a uma extração"""
    try:
        data = request.json
        
        # Validar campos obrigatórios
        if not data.get('extraction_id'):
            return jsonify({
                'sucesso': False,
                'erro': 'extraction_id é obrigatório'
            }), 400
        
        aposta_id = sistema.criar_aposta_com_extracao(
            usuario_id=data['usuario_id'],
            extraction_id=data['extraction_id'],
            numero=data['numero'],
            animal=data['animal'],
            valor=float(data['valor']),
            tipo_aposta=data.get('tipo_aposta', 'grupo'),
            multiplicador=float(data.get('multiplicador', 18.0))
        )
        
        return jsonify({
            'sucesso': True,
            'aposta_id': aposta_id,
            'mensagem': 'Aposta criada com sucesso'
        })
    except ValueError as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/apostas/<int:aposta_id>', methods=['GET'])
def ver_aposta(aposta_id):
    """Ver detalhes de uma aposta"""
    from models import Aposta
    session = sistema.Session()
    try:
        aposta = session.query(Aposta).get(aposta_id)
        if not aposta:
            return jsonify({'erro': 'Aposta não encontrada'}), 404
        
        return jsonify({
            'id': aposta.id,
            'extraction_id': aposta.extraction_id,
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
                'extraction_id': a.extraction_id,
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
    """Força liquidação de resultados por extração"""
    try:
        total = sistema.processar_resultados_monitor()
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
    """Inicia monitor"""
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

@app.route('/')
def index():
    """Dashboard principal"""
    return """
    <html>
    <head><title>Sistema de Apostas - Extrações</title></head>
    <body>
    <h1>🎰 Sistema de Apostas com Extrações</h1>
    <h2>Endpoints:</h2>
    <ul>
        <li>GET /api/extracoes-disponiveis - Listar extrações</li>
        <li>GET /api/extracoes/{id} - Ver extração</li>
        <li>POST /api/apostas - Criar aposta (com extraction_id)</li>
        <li>GET /api/apostas/{id} - Ver aposta</li>
        <li>GET /api/apostas/usuario/{id} - Listar apostas</li>
        <li>GET /api/resultados - Listar resultados</li>
        <li>POST /api/resultados/liquidar - Forçar liquidação</li>
        <li>GET /api/usuarios/{id}/saldo - Consultar saldo</li>
    </ul>
    </body>
    </html>
    """

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--monitor', action='store_true')
    parser.add_argument('--intervalo', type=int, default=60)
    args = parser.parse_args()
    
    if args.monitor:
        monitor_thread = threading.Thread(
            target=monitor_loop,
            args=(args.intervalo,),
            daemon=True
        )
        monitor_thread.start()
        print(f"✅ Monitor iniciado automaticamente (intervalo: {args.intervalo}s)")
    
    print(f"🚀 Servidor iniciando em http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=False)

