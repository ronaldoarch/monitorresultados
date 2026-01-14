#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Liquidar Apostas Específicas Manualmente
Útil quando o sistema automático não está funcionando
"""

import sys
import os
import requests
from datetime import datetime
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Aposta, Extracao, Resultado, Liquidacao, Usuario, Transacao
from sistema_liquidacao_avancado import SistemaLiquidacaoAvancado
from regras_liquidacao import converter_resultado_api_para_milhares, conferir_palpite_completo

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

def animal_para_grupo(animal):
    """Converte animal para grupo"""
    animais_grupos = {
        "Avestruz": 1, "Águia": 2, "Burro": 3, "Borboleta": 4,
        "Cachorro": 5, "Cabra": 6, "Carneiro": 7, "Camelo": 8,
        "Cobra": 9, "Coelho": 10, "Cavalo": 11, "Elefante": 12,
        "Galo": 13, "Gato": 14, "Jacaré": 15, "Leão": 16,
        "Macaco": 17, "Porco": 18, "Pavão": 19, "Peru": 20,
        "Touro": 21, "Tigre": 22, "Urso": 23, "Veado": 24,
        "Vaca": 25
    }
    
    animal_lower = animal.lower().strip()
    for nome, grupo in animais_grupos.items():
        if nome.lower() == animal_lower:
            return grupo
    
    return None

def liquidar_apostas_manualmente(database_url='sqlite:///apostas.db', api_url=None, loteria=None, horario=None):
    """Liquida apostas manualmente buscando resultados da API"""
    
    api_url = api_url or os.getenv('BICHO_CERTO_API', 'http://localhost:8000')
    
    sistema = SistemaLiquidacaoAvancado(database_url=database_url, api_url=api_url)
    session = sistema.Session()
    
    print("=" * 80)
    print("🔄 LIQUIDAÇÃO MANUAL DE APOSTAS")
    print("=" * 80)
    print()
    
    # Buscar resultados da API
    print("1️⃣ Buscando resultados da API...")
    dados = sistema.buscar_resultados_organizados()
    organizados = dados.get('organizados', {})
    
    if not organizados:
        print("   ❌ Nenhum resultado encontrado na API")
        return
    
    print(f"   ✅ {len(organizados)} tabelas encontradas")
    print()
    
    # Buscar apostas pendentes
    print("2️⃣ Buscando apostas pendentes...")
    query = session.query(Aposta).filter_by(status='pendente')
    
    if loteria:
        query = query.filter(Aposta.loteria.like(f'%{loteria}%'))
    if horario:
        query = query.filter(Aposta.horario == horario)
    
    apostas = query.all()
    print(f"   Encontradas {len(apostas)} apostas pendentes")
    print()
    
    if not apostas:
        print("   ℹ️  Nenhuma aposta pendente encontrada")
        return
    
    # Processar cada aposta
    print("3️⃣ Processando liquidação...")
    print()
    
    total_liquidadas = 0
    
    for aposta in apostas:
        print(f"📋 Aposta #{aposta.id}")
        print(f"   Loteria: {aposta.loteria}")
        print(f"   Horário: {aposta.horario}")
        print(f"   Modalidade: {aposta.tipo_aposta}")
        
        # Buscar resultado correspondente na API
        loteria_sistema = mapear_loteria_api_para_sistema(aposta.loteria)
        horario_norm = normalizar_horario(aposta.horario)
        
        resultado_encontrado = False
        resultados_api = []
        loteria_api_encontrada = None
        horario_api_encontrado = None
        
        for loteria_api, horarios in organizados.items():
            loteria_api_norm = mapear_loteria_api_para_sistema(loteria_api)
            
            if loteria_api_norm == loteria_sistema:
                for horario_api, resultados in horarios.items():
                    horario_api_norm = normalizar_horario(horario_api)
                    
                    if horario_api_norm == horario_norm:
                        resultado_encontrado = True
                        resultados_api = resultados
                        loteria_api_encontrada = loteria_api
                        horario_api_encontrado = horario_api
                        break
                
                if resultado_encontrado:
                    break
        
        if not resultado_encontrado:
            print(f"   ❌ Resultado não encontrado na API para {aposta.loteria} {aposta.horario}")
            print()
            continue
        
        print(f"   ✅ Resultado encontrado: {loteria_api_encontrada} {horario_api_encontrado}")
        
        # Converter resultados para milhares
        resultado_milhares = sistema.converter_resultado_para_milhares(resultados_api)
        print(f"   Milhares: {resultado_milhares[:7]}")  # Mostrar primeiros 7
        
        # Preparar palpite conforme modalidade
        try:
            palpite = {}
            modalidade = aposta.tipo_aposta.upper()
            
            if 'GRUPO' in modalidade or modalidade in ['PASSE', 'PASSE_VAI_E_VEM']:
                # Converter para grupos
                if modalidade == 'DUPLA_GRUPO':
                    # Para dupla, precisamos dos grupos dos números apostados
                    # Assumindo que o número contém informação dos grupos
                    grupos = []
                    # Tentar extrair grupos dos números
                    if aposta.numero:
                        # Se número tem formato "19-18", extrair grupos
                        if '-' in aposta.numero:
                            partes = aposta.numero.split('-')
                            for parte in partes:
                                grupo = animal_para_grupo(parte) or int(parte) if parte.isdigit() else None
                                if grupo:
                                    grupos.append(grupo)
                        else:
                            # Tentar usar animal
                            grupo = animal_para_grupo(aposta.animal)
                            if grupo:
                                grupos = [grupo, grupo]  # Duplicar para dupla
                    
                    palpite['grupos'] = grupos[:2] if len(grupos) >= 2 else [grupo, grupo] if grupo else []
                elif modalidade == 'GRUPO':
                    grupo = animal_para_grupo(aposta.animal)
                    palpite['grupos'] = [grupo] if grupo else []
                else:
                    grupo = animal_para_grupo(aposta.animal)
                    palpite['grupos'] = [grupo] if grupo else []
            else:
                # Modalidade de número
                palpite['numero'] = aposta.numero
            
            # Conferir palpite
            resultado_liquidacao = sistema.liquidar_aposta_com_regras(
                aposta=aposta,
                resultado_milhares=resultado_milhares,
                modalidade=modalidade,
                pos_from=1,
                pos_to=7
            )
            
            # Atualizar status da aposta
            if resultado_liquidacao['ganhou']:
                aposta.status = 'ganhou'
                aposta.data_liquidacao = datetime.utcnow()
                valor_ganho = resultado_liquidacao['valor_ganho']
                
                # Atualizar saldo
                usuario = session.query(Usuario).get(aposta.usuario_id)
                if usuario:
                    usuario.saldo += valor_ganho
                    
                    # Criar transação
                    transacao = Transacao(
                        usuario_id=usuario.id,
                        tipo='ganho',
                        valor=valor_ganho,
                        descricao=f'Ganho na aposta #{aposta.id} - {aposta.numero} {aposta.animal}',
                        status='concluida'
                    )
                    session.add(transacao)
                
                print(f"   ✅ GANHOU! R$ {valor_ganho:.2f} ({resultado_liquidacao['acertos']} acertos)")
            else:
                aposta.status = 'perdeu'
                aposta.data_liquidacao = datetime.utcnow()
                print(f"   ❌ Perdeu")
            
            # Criar liquidação
            liquidacao = Liquidacao(
                aposta_id=aposta.id,
                resultado_id=None,
                valor_aposta=aposta.valor,
                valor_ganho=resultado_liquidacao.get('valor_ganho', 0.0),
                status='concluida'
            )
            session.add(liquidacao)
            
            session.commit()
            total_liquidadas += 1
            
        except Exception as e:
            print(f"   ❌ Erro ao liquidar: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
        
        print()
    
    print("=" * 80)
    print(f"✅ Total: {total_liquidadas} apostas liquidadas")
    print("=" * 80)
    
    session.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Liquidar apostas manualmente')
    parser.add_argument('--database', default='sqlite:///apostas.db', help='URL do banco de dados')
    parser.add_argument('--api', default=None, help='URL da API de resultados')
    parser.add_argument('--loteria', default=None, help='Filtrar por loteria')
    parser.add_argument('--horario', default=None, help='Filtrar por horário')
    args = parser.parse_args()
    
    liquidar_apostas_manualmente(
        database_url=args.database,
        api_url=args.api,
        loteria=args.loteria,
        horario=args.horario
    )
