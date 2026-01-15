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
monitor_iniciado = False

def iniciar_monitor(intervalo=60):
    """Inicia o monitor em uma thread separada"""
    global monitor_thread, monitor_iniciado
    
    if monitor_iniciado:
        logger.warning("⚠️  Monitor já está rodando")
        return
    
    if not verificar:
        logger.warning("⚠️  Função verificar não disponível. Monitor não será iniciado.")
        return
    
    monitor_thread = threading.Thread(
        target=monitor_loop,
        args=(intervalo,),
        daemon=True,
        name="MonitorBichoCerto"
    )
    monitor_thread.start()
    monitor_iniciado = True
    logger.info(f"✅ Monitor Bicho Certo iniciado em thread separada (intervalo: {intervalo}s)")

def monitor_loop(intervalo=60):
    """Loop do monitor em background - apenas Bicho Certo"""
    global monitor_rodando
    monitor_rodando = True
    
    logger.info(f"🔄 Monitor Bicho Certo iniciado (verifica a cada {intervalo}s)")
    
    # Fazer primeira verificação imediatamente
    try:
        if verificar:
            novos = verificar()
            if novos > 0:
                logger.info(f"✅ Bicho Certo: {novos} novos resultados encontrados na primeira verificação!")
    except Exception as e:
        logger.error(f"❌ Erro na primeira verificação: {e}")
    
    while monitor_rodando:
        try:
            if verificar:
                novos = verificar()
                if novos > 0:
                    logger.info(f"✅ Bicho Certo: {novos} novos resultados encontrados!")
        except Exception as e:
            logger.error(f"❌ Erro no monitor: {e}")
        
        # Aguardar intervalo
        for _ in range(intervalo):
            if not monitor_rodando:
                break
            time.sleep(1)
    
    logger.info("🛑 Monitor Bicho Certo encerrado")

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
    """API para retornar resultados do Bicho Certo"""
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
                return jsonify({
                    'resultados': resultados,
                    'summary': resultado.get('summary', {}),
                    'ultima_verificacao': datetime.now().isoformat(),
                    'fonte': 'bichocerto.com'
                })
        except Exception as e:
            logger.warning(f"Erro ao processar via PHP: {e}")
    
    # Fallback para método original
    try:
        dados = carregar_resultados()
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in dados.get('resultados', []):
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        dados['fonte'] = 'bichocerto.com'
        return jsonify(dados)
    except Exception as e:
        return jsonify({
            'resultados': [],
            'erro': str(e),
            'ultima_verificacao': None,
            'fonte': 'bichocerto.com'
        }), 500

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

@app.route('/api/resultados/organizados')
def api_resultados_organizados():
    """API para retornar resultados organizados por tabela (loteria) e horário"""
    try:
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        # Adicionar estado se não existir
        from monitor_selenium import identificar_estado
        for r in resultados:
            if 'estado' not in r:
                r['estado'] = identificar_estado(r.get('loteria', ''))
        
        # Função para extrair data normalizada
        def extrair_data_normalizada(resultado):
            if 'data_extração' in resultado and resultado['data_extração']:
                data = resultado['data_extração']
                if data and str(data).strip():
                    return str(data).strip()
            if 'timestamp' in resultado and resultado['timestamp']:
                try:
                    from datetime import datetime
                    timestamp = resultado['timestamp']
                    if timestamp:
                        dt = datetime.fromisoformat(str(timestamp).replace('Z', '+00:00'))
                        return dt.strftime('%d/%m/%Y')
                except Exception as e:
                    logger.debug(f"Erro ao extrair data do timestamp: {e}")
                    pass
            from datetime import datetime
            return datetime.now().strftime('%d/%m/%Y')
        
        # Organizar por tabela (loteria), horário e data (sorteio específico)
        organizados = {}
        
        for r in resultados:
            loteria = r.get('loteria', 'Desconhecida')
            horario = r.get('horario', 'N/A')
            data = extrair_data_normalizada(r)
            
            # Criar chave única: loteria + horário + data (sorteio específico)
            chave_tabela = loteria
            chave_horario = horario
            
            # Inicializar estrutura se não existir
            if chave_tabela not in organizados:
                organizados[chave_tabela] = {}
            
            if chave_horario not in organizados[chave_tabela]:
                organizados[chave_tabela][chave_horario] = []
            
            # Adicionar resultado formatado
            resultado_formatado = {
                'horario': horario,
                'animal': r.get('animal', ''),
                'numero': r.get('numero', ''),
                'posicao': r.get('posicao', 0),
                'colocacao': r.get('colocacao', ''),
                'estado': r.get('estado', 'BR'),
                'data_extracao': data,
                'timestamp': r.get('timestamp', '')
            }
            
            organizados[chave_tabela][chave_horario].append(resultado_formatado)
        
        # Agrupar por sorteio (mesma data) e limitar a 7 posições por sorteio
        organizados_final = {}
        
        for tabela in organizados:
            organizados_final[tabela] = {}
            
            for horario in organizados[tabela]:
                # Agrupar resultados por data (sorteio)
                resultados_por_data = {}
                for resultado in organizados[tabela][horario]:
                    data = resultado['data_extracao']
                    if data not in resultados_por_data:
                        resultados_por_data[data] = []
                    resultados_por_data[data].append(resultado)
                
                # Para cada sorteio (data), ordenar e limitar a 7 posições
                sorteios_ordenados = []
                for data, resultados_sorteio in resultados_por_data.items():
                    # Ordenar por posição
                    resultados_sorteio.sort(key=lambda x: x.get('posicao', 0))
                    # Limitar a 7 posições (1° a 7°)
                    resultados_sorteio = resultados_sorteio[:7]
                    # Adicionar apenas se tiver resultados válidos (posição 1-7)
                    if resultados_sorteio and resultados_sorteio[0].get('posicao', 0) <= 7:
                        sorteios_ordenados.append({
                            'data': data,
                            'resultados': resultados_sorteio
                        })
                
                # Se houver apenas um sorteio para este horário, usar formato simples
                # Se houver múltiplos sorteios, manter separados por data
                if len(sorteios_ordenados) == 1:
                    # Formato simples: apenas os resultados do sorteio mais recente
                    organizados_final[tabela][horario] = sorteios_ordenados[0]['resultados']
                elif len(sorteios_ordenados) > 1:
                    # Múltiplos sorteios: usar o mais recente (último da lista ordenada)
                    # Ordenar por data (mais recente primeiro)
                    # Tratar casos onde data pode ser None
                    def ordenar_por_data(item):
                        data = item.get('data')
                        if data is None:
                            return ''  # Colocar None no final
                        return data
                    sorteios_ordenados.sort(key=ordenar_por_data, reverse=True)
                    organizados_final[tabela][horario] = sorteios_ordenados[0]['resultados']
        
        # Estatísticas
        total_tabelas = len(organizados_final)
        total_horarios = sum(len(horarios) for horarios in organizados_final.values())
        total_resultados = sum(
            len(resultados) 
            for tabela in organizados_final.values() 
            for resultados in tabela.values()
        )
        
        return jsonify({
            'organizados': organizados_final,
            'estatisticas': {
                'total_tabelas': total_tabelas,
                'total_horarios': total_horarios,
                'total_resultados': total_resultados
            },
            'ultima_verificacao': dados.get('ultima_verificacao'),
            'fonte': 'bichocerto.com'
        })
    except Exception as e:
        logger.error(f"Erro ao organizar resultados: {e}")
        return jsonify({
            'organizados': {},
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

@app.route('/api/monitor/start', methods=['POST'])
def api_monitor_start():
    """Inicia o monitor automaticamente"""
    try:
        intervalo = request.json.get('intervalo', 60) if request.is_json else 60
        iniciar_monitor(intervalo)
        return jsonify({
            'sucesso': True,
            'mensagem': f'Monitor iniciado (intervalo: {intervalo}s)',
            'monitor_rodando': monitor_rodando
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/stop', methods=['POST'])
def api_monitor_stop():
    """Para o monitor"""
    global monitor_rodando, monitor_iniciado
    try:
        monitor_rodando = False
        monitor_iniciado = False
        return jsonify({
            'sucesso': True,
            'mensagem': 'Monitor parado'
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/status', methods=['GET'])
def api_monitor_status():
    """Status do monitor"""
    return jsonify({
        'monitor_rodando': monitor_rodando,
        'monitor_iniciado': monitor_iniciado,
        'thread_ativa': monitor_thread.is_alive() if monitor_thread else False,
        'verificar_disponivel': verificar is not None
    })

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
    """Status do sistema - apenas Bicho Certo"""
    dados = carregar_resultados()
    return jsonify({
        'monitor_rodando': monitor_rodando,
        'total_resultados': len(dados.get('resultados', [])),
        'ultima_verificacao': dados.get('ultima_verificacao'),
        'timestamp': datetime.now().isoformat(),
        'fonte': 'bichocerto.com',
        'monitor_disponivel': verificar is not None
    })

@app.route('/api/verificar-agora', methods=['POST'])
def verificar_agora():
    """Força verificação imediata - apenas Bicho Certo"""
    if not verificar:
        return jsonify({'erro': 'Monitor Bicho Certo não disponível'}), 500
    
    try:
        novos = verificar()
        return jsonify({
            'sucesso': True,
            'novos_resultados': novos,
            'mensagem': f'{novos} novos resultados encontrados' if novos > 0 else 'Nenhum resultado novo',
            'fonte': 'bichocerto.com'
        })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/start', methods=['POST'])
def monitor_start():
    """Inicia monitor"""
    try:
        intervalo = int(request.json.get('intervalo', 60)) if request.is_json and request.json else 60
        iniciar_monitor(intervalo)
    return jsonify({
        'sucesso': True,
            'mensagem': f'Monitor iniciado (intervalo: {intervalo}s)',
            'monitor_rodando': monitor_rodando
    })
    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500

@app.route('/api/monitor/stop', methods=['POST'])
def monitor_stop():
    """Para monitor"""
    global monitor_rodando, monitor_iniciado
    
    if not monitor_rodando:
        return jsonify({
            'sucesso': False,
            'mensagem': 'Monitor não está rodando'
        }), 400
    
    monitor_rodando = False
    monitor_iniciado = False
    return jsonify({
        'sucesso': True,
        'mensagem': 'Monitor parado'
    })

@app.route('/api/monitor/status', methods=['GET'])
def monitor_status():
    """Status do monitor"""
    return jsonify({
        'monitor_rodando': monitor_rodando,
        'monitor_iniciado': monitor_iniciado,
        'thread_ativa': monitor_thread.is_alive() if monitor_thread else False,
        'verificar_disponivel': verificar is not None
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

# Inicialização automática do monitor (quando módulo é carregado)
# Verifica variável de ambiente ou inicia automaticamente
def inicializar_monitor_automatico():
    """Inicializa o monitor automaticamente se configurado"""
    # Verificar variável de ambiente
    auto_start = os.getenv('MONITOR_AUTO_START', 'true').lower() == 'true'
    intervalo = int(os.getenv('MONITOR_INTERVALO', '60'))
    
    if auto_start and verificar:
        logger.info(f"🔄 Iniciando monitor automaticamente (intervalo: {intervalo}s)")
        iniciar_monitor(intervalo)
    else:
        logger.info("ℹ️  Monitor não será iniciado automaticamente (use MONITOR_AUTO_START=true)")

# Hook do Gunicorn para iniciar monitor quando worker é criado
def on_starting(server):
    """Hook executado quando Gunicorn inicia"""
    logger.info("🚀 Gunicorn iniciando...")
    inicializar_monitor_automatico()

def when_ready(server):
    """Hook executado quando Gunicorn está pronto"""
    logger.info("✅ Gunicorn pronto!")
    # Garantir que monitor está rodando
    if not monitor_iniciado:
        inicializar_monitor_automatico()

# Inicializar monitor quando módulo é importado (para desenvolvimento)
if os.getenv('FLASK_ENV') != 'production' or os.getenv('MONITOR_AUTO_START', 'true').lower() == 'true':
    # Pequeno delay para garantir que tudo está carregado
    import atexit
    def iniciar_ao_carregar():
        time.sleep(2)  # Aguardar 2 segundos
        inicializar_monitor_automatico()
    
    # Iniciar em thread separada para não bloquear
    threading.Thread(target=iniciar_ao_carregar, daemon=True).start()

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
        iniciar_monitor(args.intervalo)
    
    print(f"🚀 Servidor iniciando em http://{args.host}:{args.port}")
    print(f"📊 Dashboard: http://{args.host}:{args.port}/")
    print(f"🔌 API: http://{args.host}:{args.port}/api/resultados")
    
    app.run(host=args.host, port=args.port, debug=False)

