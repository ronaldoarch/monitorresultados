#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico para Investigar Apostas Não Liquidadas
"""

import sys
import os
import requests
from datetime import datetime
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Aposta, Extracao, Resultado, Liquidacao

def mapear_loteria_api_para_sistema(loteria_api):
    """Mapeia nome da loteria da API para nome do sistema"""
    mapeamento = {
        'Loteria Federal': 'FEDERAL',
        'Federal': 'FEDERAL',
        'PT-SP/Bandeirantes': 'PT SP',
        'PT SP': 'PT SP',
        'PT Bandeirantes': 'PT SP',
        'PT Bahia': 'PT BAHIA',
        'PT BAHIA': 'PT BAHIA',
    }
    
    loteria_upper = loteria_api.upper()
    for key, value in mapeamento.items():
        if key.upper() in loteria_upper:
            return value
    
    return loteria_api.upper()

def normalizar_horario(horario):
    """Normaliza horário para comparação"""
    if not horario:
        return None
    horario = str(horario).strip().lower()
    horario = horario.replace('h', '').replace(':', '').replace(' ', '')
    if len(horario) == 3:
        horario = '0' + horario
    return horario if len(horario) == 4 else None

def diagnosticar_apostas_nao_liquidadas(database_url='sqlite:///apostas.db', api_url=None):
    """Diagnostica por que apostas não foram liquidadas"""
    
    api_url = api_url or os.getenv('BICHO_CERTO_API', 'http://localhost:8000')
    
    engine = create_engine(database_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("=" * 80)
    print("🔍 DIAGNÓSTICO DE APOSTAS NÃO LIQUIDADAS")
    print("=" * 80)
    print()
    
    # 1. Buscar apostas pendentes ou perdidas recentes
    print("1️⃣ Buscando apostas recentes...")
    apostas_recentes = session.query(Aposta).filter(
        Aposta.status.in_(['pendente', 'perdida'])
    ).order_by(Aposta.data_aposta.desc()).limit(10).all()
    
    print(f"   Encontradas {len(apostas_recentes)} apostas recentes")
    print()
    
    # 2. Buscar resultados da API
    print("2️⃣ Buscando resultados da API...")
    try:
        response = requests.get(f"{api_url}/api/resultados/organizados", timeout=10)
        response.raise_for_status()
        dados_api = response.json()
        organizados = dados_api.get('organizados', {})
        print(f"   ✅ API acessível - {len(organizados)} tabelas encontradas")
    except Exception as e:
        print(f"   ❌ Erro ao acessar API: {e}")
        organizados = {}
    
    print()
    
    # 3. Para cada aposta, verificar se há resultado correspondente
    print("3️⃣ Verificando correspondência entre apostas e resultados...")
    print()
    
    for aposta in apostas_recentes:
        print(f"📋 Aposta #{aposta.id}")
        print(f"   Modalidade: {aposta.tipo_aposta}")
        print(f"   Loteria: {aposta.loteria}")
        print(f"   Horário: {aposta.horario}")
        print(f"   Status: {aposta.status}")
        print(f"   Data: {aposta.data_aposta}")
        print(f"   Extraction ID: {aposta.extraction_id}")
        
        # Buscar extração
        extracao = session.query(Extracao).get(aposta.extraction_id)
        if extracao:
            print(f"   Extração: {extracao.loteria} {extracao.horario} (status: {extracao.status})")
        else:
            print(f"   ⚠️  Extração não encontrada!")
        
        # Verificar se há resultado na API
        loteria_sistema = mapear_loteria_api_para_sistema(aposta.loteria)
        horario_norm = normalizar_horario(aposta.horario)
        
        resultado_encontrado = False
        resultados_api = []
        
        for loteria_api, horarios in organizados.items():
            loteria_api_norm = mapear_loteria_api_para_sistema(loteria_api)
            
            if loteria_api_norm == loteria_sistema:
                for horario_api, resultados in horarios.items():
                    horario_api_norm = normalizar_horario(horario_api)
                    
                    if horario_api_norm == horario_norm:
                        resultado_encontrado = True
                        resultados_api = resultados
                        print(f"   ✅ Resultado encontrado na API!")
                        print(f"      Loteria API: {loteria_api}")
                        print(f"      Horário API: {horario_api}")
                        print(f"      Quantidade de resultados: {len(resultados)}")
                        break
                
                if resultado_encontrado:
                    break
        
        if not resultado_encontrado:
            print(f"   ❌ Resultado NÃO encontrado na API")
            print(f"      Procurando por: {loteria_sistema} {horario_norm}")
            print(f"      Loterias disponíveis na API:")
            for loteria_api in organizados.keys():
                print(f"         - {loteria_api}")
        
        # Verificar se há resultado no banco
        if extracao:
            resultado_banco = session.query(Resultado).filter_by(
                extraction_id=extracao.id
            ).first()
            
            if resultado_banco:
                print(f"   ✅ Resultado encontrado no banco!")
                print(f"      Número: {resultado_banco.numero}")
                print(f"      Animal: {resultado_banco.animal}")
                print(f"      Processado: {resultado_banco.processado}")
            else:
                print(f"   ❌ Resultado NÃO encontrado no banco")
        
        # Verificar liquidação
        liquidacao = session.query(Liquidacao).filter_by(
            aposta_id=aposta.id
        ).first()
        
        if liquidacao:
            print(f"   ✅ Liquidação encontrada!")
            print(f"      Status: {liquidacao.status}")
            print(f"      Valor ganho: R$ {liquidacao.valor_ganho:.2f}")
        else:
            print(f"   ❌ Liquidação NÃO encontrada")
        
        print()
        print("-" * 80)
        print()
    
    # 4. Resumo
    print("4️⃣ RESUMO")
    print()
    
    apostas_pendentes = session.query(Aposta).filter_by(status='pendente').count()
    apostas_perdidas = session.query(Aposta).filter_by(status='perdida').count()
    apostas_ganhas = session.query(Aposta).filter_by(status='ganhou').count()
    
    print(f"   Apostas pendentes: {apostas_pendentes}")
    print(f"   Apostas perdidas: {apostas_perdidas}")
    print(f"   Apostas ganhas: {apostas_ganhas}")
    print()
    
    # 5. Verificar monitor
    print("5️⃣ Status do Monitor")
    try:
        response = requests.get(f"{api_url}/api/monitor/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   Monitor rodando: {status.get('monitor_rodando', False)}")
            print(f"   Monitor iniciado: {status.get('monitor_iniciado', False)}")
            print(f"   Thread ativa: {status.get('thread_ativa', False)}")
        else:
            print(f"   ⚠️  Não foi possível verificar status do monitor")
    except Exception as e:
        print(f"   ❌ Erro ao verificar monitor: {e}")
    
    session.close()
    
    print()
    print("=" * 80)
    print("✅ Diagnóstico concluído!")
    print("=" * 80)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnosticar apostas não liquidadas')
    parser.add_argument('--database', default='sqlite:///apostas.db', help='URL do banco de dados')
    parser.add_argument('--api', default=None, help='URL da API de resultados')
    args = parser.parse_args()
    
    diagnosticar_apostas_nao_liquidadas(
        database_url=args.database,
        api_url=args.api
    )
