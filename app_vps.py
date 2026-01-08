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

# Configurar logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar monitor Bicho Certo e integração PHP
try:
    from monitor_selenium import verificar, carregar_resultados
except ImportError:
    print("⚠️  Monitor Bicho Certo não encontrado. API funcionará, mas monitor não rodará.")
    verificar = None
    carregar_resultados = lambda: {'resultados': [], 'ultima_verificacao': None}

# Importar monitor Deu no Poste
try:
    from monitor_deunoposte import MonitorDeuNoPoste
    monitor_deunoposte = MonitorDeuNoPoste()
    MONITOR_DEUNOPOSTE_DISPONIVEL = True
    logger.info("✅ Monitor Deu no Poste carregado com sucesso")
except ImportError as e:
    logger.warning(f"⚠️  Monitor Deu no Poste não encontrado: {e}")
    monitor_deunoposte = None
    MONITOR_DEUNOPOSTE_DISPONIVEL = False
except Exception as e:
    logger.error(f"❌ Erro ao inicializar Monitor Deu no Poste: {e}")
    monitor_deunoposte = None
    MONITOR_DEUNOPOSTE_DISPONIVEL = False

# Importar integração com endpoint PHP (opcional)
try:
    from integracao_endpoint_php import processar_resultados_via_php
    INTEGRACAO_PHP_DISPONIVEL = True
except ImportError:
    INTEGRACAO_PHP_DISPONIVEL = False
    processar_resultados_via_php = None

# Variável global para controlar monitor
monitor_rodando = False
monitor_thread = None

def monitor_loop(intervalo=60):
    """Loop do monitor em background - monitora Bicho Certo e Deu no Poste"""
    global monitor_rodando
    monitor_rodando = True
    
    print(f"🔄 Monitor iniciado (verifica a cada {intervalo}s)")
    print(f"   📊 Monitorando: Bicho Certo + Deu no Poste")
    
    while monitor_rodando:
        try:
            # Monitor Bicho Certo
            if verificar:
                novos = verificar()
                if novos > 0:
                    print(f"✅ Bicho Certo: {novos} novos resultados encontrados!")
            
            # Monitor Deu no Poste
            if MONITOR_DEUNOPOSTE_DISPONIVEL and monitor_deunoposte:
                try:
                    logger.info("🔍 Iniciando monitoramento Deu no Poste...")
                    resultados_deunoposte = monitor_deunoposte.monitorar_todos()
                    if resultados_deunoposte:
                        # Salvar resultados do Deu no Poste
                        monitor_deunoposte.salvar_resultados(resultados_deunoposte, "resultados_deunoposte.json")
                        logger.info(f"✅ Deu no Poste: {len(resultados_deunoposte)} resultados coletados!")
                    else:
                        logger.info("⚠️  Deu no Poste: Nenhum resultado encontrado")
                except Exception as e:
                    logger.error(f"❌ Erro no monitor Deu no Poste: {e}", exc_info=True)
            else:
                if not MONITOR_DEUNOPOSTE_DISPONIVEL:
                    logger.debug("ℹ️  Monitor Deu no Poste não disponível")
                    
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
    """API para retornar resultados - combina Bicho Certo + Deu no Poste"""
    todos_resultados = []
    
    # Se integração PHP disponível, usar ela
    if INTEGRACAO_PHP_DISPONIVEL and processar_resultados_via_php:
        try:
            resultado = processar_resultados_via_php()
            if resultado.get('sucesso'):
                resultados = resultado.get('resultados', [])
                # Adicionar estado se não existir
                from monitor_selenium import identificar_estado
                for r in resultados:
                    if 'estado' not in r:
                        r['estado'] = identificar_estado(r.get('loteria', ''))
                    r['fonte'] = r.get('fonte', 'bichocerto.com')
                todos_resultados.extend(resultados)
        except Exception as e:
            logger.warning(f"Erro ao processar via PHP: {e}")
    
    # Adicionar resultados do Bicho Certo
    try:
        dados_bichocerto = carregar_resultados()
        resultados_bichocerto = dados_bichocerto.get('resultados', [])
        # Adicionar estado e fonte se não existir
        from monitor_selenium import identificar_estado
        for r in resultados_bichocerto:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
            r['fonte'] = r.get('fonte', 'bichocerto.com')
        todos_resultados.extend(resultados_bichocerto)
    except Exception as e:
        logger.warning(f"Erro ao carregar Bicho Certo: {e}")
    
    # Adicionar resultados do Deu no Poste
    if MONITOR_DEUNOPOSTE_DISPONIVEL:
        try:
            if os.path.exists('resultados_deunoposte.json'):
                with open('resultados_deunoposte.json', 'r', encoding='utf-8') as f:
                    dados_deunoposte = json.load(f)
                    resultados_deunoposte = dados_deunoposte.get('resultados', [])
                    # Garantir que todos têm fonte
                    for r in resultados_deunoposte:
                        r['fonte'] = r.get('fonte', 'deunoposte.com.br')
                    todos_resultados.extend(resultados_deunoposte)
        except Exception as e:
            logger.warning(f"Erro ao carregar Deu no Poste: {e}")
    
    # Remover duplicatas (mesmo número + animal + loteria + horário)
    resultados_unicos = []
    vistos = set()
    for r in todos_resultados:
        chave = (
            r.get('numero', ''),
            r.get('animal', ''),
            r.get('loteria', ''),
            r.get('horario', ''),
            r.get('fonte', '')
        )
        if chave not in vistos:
            vistos.add(chave)
            resultados_unicos.append(r)
    
    return jsonify({
        'resultados': resultados_unicos,
        'total_resultados': len(resultados_unicos),
        'ultima_verificacao': datetime.now().isoformat(),
        'fontes': {
            'bichocerto': len([r for r in resultados_unicos if r.get('fonte') == 'bichocerto.com']),
            'deunoposte': len([r for r in resultados_unicos if r.get('fonte') == 'deunoposte.com.br'])
        }
    })

@app.route('/api/resultados/por-estado')
def api_resultados_por_estado():
    """API para retornar resultados agrupados por estado"""
    try:
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in resultados:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        
        # Agrupar por estado
        por_estado = {}
        for r in resultados:
            estado = r.get('estado', 'BR')
            if estado not in por_estado:
                por_estado[estado] = []
            por_estado[estado].append(r)
        
        # Estatísticas
        stats = {estado: len(grupo) for estado, grupo in por_estado.items()}
        
        return jsonify({
            'por_estado': por_estado,
            'estatisticas': stats,
            'total_resultados': len(resultados),
            'total_estados': len(por_estado),
            'ultima_verificacao': dados.get('ultima_verificacao')
        })
    except Exception as e:
        return jsonify({
            'por_estado': {},
            'erro': str(e)
        }), 500

@app.route('/api/resultados/estado/<estado>')
def api_resultados_estado(estado):
    """API para retornar resultados de um estado específico"""
    try:
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in resultados:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        
        # Filtrar por estado
        resultados_estado = [r for r in resultados if r.get('estado', '').upper() == estado.upper()]
        
        # Agrupar por loteria e horário
        por_loteria = {}
        for r in resultados_estado:
            chave = f"{r.get('loteria', '?')}_{r.get('horario', '?')}"
            if chave not in por_loteria:
                por_loteria[chave] = []
            por_loteria[chave].append(r)
        
        return jsonify({
            'estado': estado.upper(),
            'resultados': resultados_estado,
            'por_loteria': por_loteria,
            'total': len(resultados_estado),
            'loterias': len(por_loteria)
        })
    except Exception as e:
        return jsonify({
            'estado': estado.upper(),
            'resultados': [],
            'erro': str(e)
        }), 500

@app.route('/api/resultados/por-data')
def api_resultados_por_data():
    """API para retornar resultados agrupados por data"""
    try:
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in resultados:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        
        # Extrair data de cada resultado
        def extrair_data(resultado):
            # Tentar data_extração primeiro (formato DD/MM/YYYY)
            if 'data_extração' in resultado and resultado['data_extração']:
                return resultado['data_extração']
            # Tentar timestamp (formato ISO)
            if 'timestamp' in resultado and resultado['timestamp']:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(resultado['timestamp'].replace('Z', '+00:00'))
                    return dt.strftime('%d/%m/%Y')
                except:
                    pass
            # Fallback: data atual
            from datetime import datetime
            return datetime.now().strftime('%d/%m/%Y')
        
        # Agrupar por data
        por_data = {}
        for r in resultados:
            data = extrair_data(r)
            if data not in por_data:
                por_data[data] = []
            por_data[data].append(r)
        
        # Estatísticas
        stats = {data: len(grupo) for data, grupo in por_data.items()}
        
        return jsonify({
            'por_data': por_data,
            'estatisticas': stats,
            'total_resultados': len(resultados),
            'total_datas': len(por_data),
            'ultima_verificacao': dados.get('ultima_verificacao')
        })
    except Exception as e:
        return jsonify({
            'por_data': {},
            'erro': str(e)
        }), 500

@app.route('/api/resultados/data/<data>')
def api_resultados_data(data):
    """API para retornar resultados de uma data específica (formato: DD-MM-YYYY ou DD/MM/YYYY)"""
    try:
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        # Normalizar formato da data (aceitar DD-MM-YYYY ou DD/MM/YYYY)
        data_normalizada = data.replace('-', '/')
        
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in resultados:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        
        # Função para extrair data do resultado
        def extrair_data(resultado):
            if 'data_extração' in resultado and resultado['data_extração']:
                return resultado['data_extração']
            if 'timestamp' in resultado and resultado['timestamp']:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(resultado['timestamp'].replace('Z', '+00:00'))
                    return dt.strftime('%d/%m/%Y')
                except:
                    pass
            from datetime import datetime
            return datetime.now().strftime('%d/%m/%Y')
        
        # Filtrar por data
        resultados_data = [r for r in resultados if extrair_data(r) == data_normalizada]
        
        # Agrupar por estado
        por_estado = {}
        for r in resultados_data:
            estado = r.get('estado', 'BR')
            if estado not in por_estado:
                por_estado[estado] = []
            por_estado[estado].append(r)
        
        # Agrupar por loteria e horário
        por_loteria = {}
        for r in resultados_data:
            chave = f"{r.get('loteria', '?')}_{r.get('horario', '?')}"
            if chave not in por_loteria:
                por_loteria[chave] = []
            por_loteria[chave].append(r)
        
        return jsonify({
            'data': data_normalizada,
            'resultados': resultados_data,
            'por_estado': por_estado,
            'por_loteria': por_loteria,
            'total': len(resultados_data),
            'estados': len(por_estado),
            'loterias': len(por_loteria)
        })
    except Exception as e:
        return jsonify({
            'data': data,
            'resultados': [],
            'erro': str(e)
        }), 500

@app.route('/api/resultados/estado/<estado>/data/<data>')
def api_resultados_estado_data(estado, data):
    """API para retornar resultados de um estado e data específicos"""
    try:
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        # Normalizar formato da data
        data_normalizada = data.replace('-', '/')
        
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in resultados:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        
        # Função para extrair data do resultado
        def extrair_data(resultado):
            if 'data_extração' in resultado and resultado['data_extração']:
                return resultado['data_extração']
            if 'timestamp' in resultado and resultado['timestamp']:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(resultado['timestamp'].replace('Z', '+00:00'))
                    return dt.strftime('%d/%m/%Y')
                except:
                    pass
            from datetime import datetime
            return datetime.now().strftime('%d/%m/%Y')
        
        # Filtrar por estado e data
        resultados_filtrados = [
            r for r in resultados 
            if r.get('estado', '').upper() == estado.upper() 
            and extrair_data(r) == data_normalizada
        ]
        
        # Agrupar por loteria e horário
        por_loteria = {}
        for r in resultados_filtrados:
            chave = f"{r.get('loteria', '?')}_{r.get('horario', '?')}"
            if chave not in por_loteria:
                por_loteria[chave] = []
            por_loteria[chave].append(r)
        
        return jsonify({
            'estado': estado.upper(),
            'data': data_normalizada,
            'resultados': resultados_filtrados,
            'por_loteria': por_loteria,
            'total': len(resultados_filtrados),
            'loterias': len(por_loteria)
        })
    except Exception as e:
        return jsonify({
            'estado': estado.upper(),
            'data': data,
            'resultados': [],
            'erro': str(e)
        }), 500

@app.route('/api/resultados/processar', methods=['POST'])
def api_processar_resultados():
    """Força processamento de resultados"""
    if INTEGRACAO_PHP_DISPONIVEL and processar_resultados_via_php:
        try:
            resultado = processar_resultados_via_php()
            if resultado.get('sucesso'):
                return jsonify(resultado)
            else:
                return jsonify(resultado), 500
        except Exception as e:
            return jsonify({
                'sucesso': False,
                'erro': str(e)
            }), 500
    else:
        return jsonify({
            'sucesso': False,
            'erro': 'Integração PHP não disponível'
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
    """Força verificação imediata - Bicho Certo + Deu no Poste"""
    total_novos = 0
    mensagens = []
    
    # Verificar Bicho Certo
    if verificar:
        try:
            novos = verificar()
            total_novos += novos
            if novos > 0:
                mensagens.append(f'Bicho Certo: {novos} novos resultados')
        except Exception as e:
            mensagens.append(f'Erro no Bicho Certo: {str(e)}')
    
    # Verificar Deu no Poste
    if MONITOR_DEUNOPOSTE_DISPONIVEL and monitor_deunoposte:
        try:
            resultados_deunoposte = monitor_deunoposte.monitorar_todos()
            if resultados_deunoposte:
                monitor_deunoposte.salvar_resultados(resultados_deunoposte, "resultados_deunoposte.json")
                total_novos += len(resultados_deunoposte)
                mensagens.append(f'Deu no Poste: {len(resultados_deunoposte)} resultados coletados')
        except Exception as e:
            mensagens.append(f'Erro no Deu no Poste: {str(e)}')
    
    if not verificar and not MONITOR_DEUNOPOSTE_DISPONIVEL:
        return jsonify({'erro': 'Nenhum monitor disponível'}), 500
    
    return jsonify({
        'sucesso': True,
        'novos_resultados': total_novos,
        'mensagem': '; '.join(mensagens) if mensagens else 'Nenhum resultado novo',
        'fontes': {
            'bichocerto': verificar is not None,
            'deunoposte': MONITOR_DEUNOPOSTE_DISPONIVEL
        }
    })

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
        dados = carregar_resultados()
        # Se não houver dados, retornar estrutura vazia válida
        if not dados:
            dados = {'resultados': [], 'ultima_verificacao': None, 'total_resultados': 0}
        return jsonify(dados)
    except Exception as e:
        logger.warning(f"Erro ao carregar resultados.json: {e}")
        return jsonify({'resultados': [], 'ultima_verificacao': None, 'total_resultados': 0, 'erro': str(e)})

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

