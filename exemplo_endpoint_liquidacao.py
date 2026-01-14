#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Endpoint Flask para Liquidação Avançada
Integra com sistema de liquidação usando regras completas
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado
import os

app = Flask(__name__)
CORS(app)

# Inicializar sistema de liquidação
sistema = SistemaLiquidacaoAvancado(
    database_url=os.getenv('DATABASE_URL', 'sqlite:///apostas.db'),
    api_url=os.getenv('BICHO_CERTO_API', 'http://localhost:8000')
)

@app.route('/api/liquidar/automatico', methods=['POST'])
def liquidar_automatico():
    """
    Endpoint para liquidação automática de todas as apostas pendentes.
    
    Returns:
        {
            "sucesso": true,
            "apostas_liquidadas": 10,
            "mensagem": "10 apostas liquidadas"
        }
    """
    try:
        total = sistema.processar_liquidacao_automatica()
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

@app.route('/api/liquidar/aposta/<int:aposta_id>', methods=['POST'])
def liquidar_aposta_especifica(aposta_id):
    """
    Endpoint para liquidar uma aposta específica.
    
    Body (JSON):
        {
            "loteria": "PT Rio de Janeiro",
            "horario": "09:30"
        }
    
    Returns:
        {
            "ganhou": true,
            "acertos": 1,
            "valor_ganho": 25.71,
            "detalhes": {...}
        }
    """
    try:
        data = request.get_json() or {}
        loteria = data.get('loteria')
        horario = data.get('horario')
        
        if not loteria or not horario:
            return jsonify({
                'sucesso': False,
                'erro': 'loteria e horario são obrigatórios'
            }), 400
        
        resultado = sistema.liquidar_aposta_especifica(
            aposta_id=aposta_id,
            loteria=loteria,
            horario=horario
        )
        
        if 'erro' in resultado:
            return jsonify({
                'sucesso': False,
                'erro': resultado['erro']
            }), 404
        
        return jsonify({
            'sucesso': True,
            **resultado
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/liquidar/sorteio', methods=['POST'])
def liquidar_sorteio():
    """
    Endpoint para liquidar todas as apostas de um sorteio específico.
    
    Body (JSON):
        {
            "loteria": "PT Rio de Janeiro",
            "horario": "09:30"
        }
    
    Returns:
        {
            "sucesso": true,
            "apostas_liquidadas": 5
        }
    """
    try:
        data = request.get_json() or {}
        loteria = data.get('loteria')
        horario = data.get('horario')
        
        if not loteria or not horario:
            return jsonify({
                'sucesso': False,
                'erro': 'loteria e horario são obrigatórios'
            }), 400
        
        # Buscar resultados
        dados = sistema.buscar_resultados_organizados(loteria=loteria, horario=horario)
        resultados = dados.get('organizados', {}).get(loteria, {}).get(horario, [])
        
        if not resultados:
            return jsonify({
                'sucesso': False,
                'erro': 'Resultado não encontrado para este sorteio'
            }), 404
        
        # Processar liquidação
        total = sistema.processar_liquidacao_por_sorteio(
            loteria=loteria,
            horario=horario,
            resultados_api=resultados
        )
        
        return jsonify({
            'sucesso': True,
            'apostas_liquidadas': total
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/resultados/organizados', methods=['GET'])
def api_resultados_organizados():
    """
    Proxy para API de resultados organizados.
    Útil se você quiser adicionar autenticação ou cache.
    """
    try:
        dados = sistema.buscar_resultados_organizados()
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'erro': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Status do sistema de liquidação"""
    try:
        # Testar conexão com API
        dados = sistema.buscar_resultados_organizados()
        total_tabelas = len(dados.get('organizados', {}))
        
        return jsonify({
            'status': 'operacional',
            'api_conectada': True,
            'total_tabelas': total_tabelas
        })
    except Exception as e:
        return jsonify({
            'status': 'erro',
            'api_conectada': False,
            'erro': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
