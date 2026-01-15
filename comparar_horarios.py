#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar horários da tabela de extrações com os horários retornados pela API
"""

import json
import requests
from datetime import datetime

# Tabela de extrações fornecida pelo usuário
TABELA_EXTRACOES = {
    'LOTECE': [
        {'real_close': '10:26', 'close': '11:00', 'status': 'Ativa'},
        {'real_close': '13:25', 'close': '14:00', 'status': 'Ativa'},
        {'real_close': '19:10', 'close': '19:40', 'status': 'Ativa'},
        {'real_close': '15:26', 'close': '15:40', 'status': 'Ativa'},
    ],
    'LOTEP': [
        {'real_close': '10:35', 'close': '10:45', 'status': 'Ativa'},
        {'real_close': '12:35', 'close': '12:45', 'status': 'Ativa'},
        {'real_close': '15:35', 'close': '15:45', 'status': 'Ativa'},
        {'real_close': '17:51', 'close': '18:05', 'status': 'Ativa'},
    ],
    'LOOK': [
        {'real_close': '11:05', 'close': '11:20', 'status': 'Ativa'},
        {'real_close': '14:05', 'close': '14:20', 'status': 'Ativa'},
        {'real_close': '16:05', 'close': '16:20', 'status': 'Ativa'},
        {'real_close': '18:05', 'close': '18:20', 'status': 'Ativa'},
        {'real_close': '21:05', 'close': '21:20', 'status': 'Ativa'},
        {'real_close': '09:05', 'close': '09:20', 'status': 'Ativa'},
        {'real_close': '23:10', 'close': '23:20', 'status': 'Ativa'},
        {'real_close': '07:05', 'close': '07:20', 'status': 'Ativa'},
    ],
    'PARA TODOS': [
        {'real_close': '09:35', 'close': '09:45', 'status': 'Ativa'},
        {'real_close': '20:20', 'close': '20:40', 'status': 'Ativa'},
    ],
    'PT RIO': [
        {'real_close': '11:10', 'close': '11:20', 'status': 'Ativa'},
        {'real_close': '14:10', 'close': '14:20', 'status': 'Ativa'},
        {'real_close': '16:10', 'close': '16:20', 'status': 'Ativa'},
        {'real_close': '18:10', 'close': '18:20', 'status': 'Ativa'},
        {'real_close': '21:10', 'close': '21:20', 'status': 'Ativa'},
        {'real_close': '09:10', 'close': '09:20', 'status': 'Ativa'},
    ],
    'NACIONAL': [
        {'real_close': '07:45', 'close': '08:00', 'status': 'Ativa'},
        {'real_close': '09:45', 'close': '10:00', 'status': 'Ativa'},
        {'real_close': '11:45', 'close': '12:00', 'status': 'Ativa'},
        {'real_close': '14:45', 'close': '15:00', 'status': 'Ativa'},
        {'real_close': '16:45', 'close': '17:00', 'status': 'Ativa'},
        {'real_close': '20:45', 'close': '21:00', 'status': 'Ativa'},
        {'real_close': '22:45', 'close': '23:00', 'status': 'Ativa'},
        {'real_close': '01:51', 'close': '02:00', 'status': 'Ativa'},
    ],
    'PT BAHIA': [
        {'real_close': '10:03', 'close': '10:20', 'status': 'Ativa'},
        {'real_close': '12:03', 'close': '12:20', 'status': 'Ativa'},
        {'real_close': '15:03', 'close': '15:20', 'status': 'Ativa'},
        {'real_close': '18:43', 'close': '19:00', 'status': 'Ativa'},
        {'real_close': '21:03', 'close': '21:20', 'status': 'Ativa'},
    ],
    'FEDERAL': [
        {'real_close': '19:50', 'close': '20:00', 'status': 'Ativa'},
    ],
    'PT SP': [
        {'real_close': '10:11', 'close': '10:00', 'status': 'Ativa'},
        {'real_close': '13:11', 'close': '13:15', 'status': 'Ativa'},
        {'real_close': '17:11', 'close': '17:15', 'status': 'Ativa'},
        {'real_close': '20:11', 'close': '20:15', 'status': 'Ativa'},
    ],
    'PT SP (Band)': [
        {'real_close': '15:11', 'close': '15:15', 'status': 'Ativa'},
    ],
}

# Mapeamento de nomes da API para nomes da tabela
MAPEAMENTO_LOTERIAS = {
    'Lotece': 'LOTECE',
    'PT Paraiba/Lotep': 'LOTEP',
    'Look Goiás': 'LOOK',
    'PT Rio de Janeiro': 'PT RIO',
    'PT-RJ': 'PT RIO',
    'Loteria Nacional': 'NACIONAL',
    'PT Bahia': 'PT BAHIA',
    'FEDERAL': 'FEDERAL',
    'PT-SP/Bandeirantes': 'PT SP (Band)',
    'PT SP': 'PT SP',
    'Para Todos': 'PARA TODOS',
    'PARA TODOS': 'PARA TODOS',
}

def normalizar_horario(horario):
    """Normaliza horário para formato HH:MM"""
    if not horario:
        return None
    
    # Remover espaços e converter para string
    horario = str(horario).strip()
    
    # Remover 'h' se existir (ex: "09h" -> "09")
    horario = horario.replace('h', ':')
    
    # Se não tiver ':', adicionar ':00'
    if ':' not in horario:
        if len(horario) == 2:
            horario = f"{horario}:00"
        elif len(horario) == 4:
            horario = f"{horario[:2]}:{horario[2:]}"
    
    # Garantir formato HH:MM
    try:
        partes = horario.split(':')
        if len(partes) == 2:
            hora = partes[0].zfill(2)
            minuto = partes[1].zfill(2)
            return f"{hora}:{minuto}"
    except:
        pass
    
    return horario

def normalizar_loteria(loteria):
    """Normaliza nome da loteria"""
    if not loteria:
        return None
    
    loteria = str(loteria).strip()
    
    # Aplicar mapeamento
    for api_name, tabela_name in MAPEAMENTO_LOTERIAS.items():
        if api_name.lower() in loteria.lower():
            return tabela_name
    
    return loteria.upper()

def buscar_horarios_api(url=None):
    """Busca horários da API"""
    if url is None:
        # Tentar diferentes URLs
        urls_tentativas = [
            'http://localhost:5000/api/resultados/organizados',
            'https://seu-dominio.com/api/resultados/organizados',
        ]
    else:
        urls_tentativas = [url]
    
    for url_tentativa in urls_tentativas:
        try:
            print(f"   Tentando: {url_tentativa}")
            response = requests.get(url_tentativa, timeout=10)
            response.raise_for_status()
            dados = response.json()
            
            horarios_api = {}
            
            if 'organizados' in dados:
                for loteria, horarios in dados['organizados'].items():
                    loteria_norm = normalizar_loteria(loteria)
                    if loteria_norm not in horarios_api:
                        horarios_api[loteria_norm] = []
                    
                    for horario in horarios.keys():
                        horario_norm = normalizar_horario(horario)
                        if horario_norm and horario_norm not in horarios_api[loteria_norm]:
                            horarios_api[loteria_norm].append(horario_norm)
            
            print(f"   ✅ Sucesso!")
            return horarios_api
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro de conexão: {e}")
            continue
        except Exception as e:
            print(f"   ❌ Erro: {e}")
            continue
    
    return {}

def comparar_horarios(url_api=None):
    """Compara horários da tabela com os da API"""
    
    print("=" * 80)
    print("COMPARAÇÃO DE HORÁRIOS - TABELA vs API")
    print("=" * 80)
    print()
    
    # Buscar horários da API
    print("📡 Buscando horários da API...")
    horarios_api = buscar_horarios_api(url_api)
    
    if not horarios_api:
        print("⚠️  Não foi possível buscar dados da API. Tentando ler resultados.json...")
        try:
            with open('resultados.json', 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            horarios_api = {}
            for resultado in dados.get('resultados', []):
                loteria = normalizar_loteria(resultado.get('loteria', ''))
                horario = normalizar_horario(resultado.get('horario', ''))
                
                if loteria and horario:
                    if loteria not in horarios_api:
                        horarios_api[loteria] = []
                    if horario not in horarios_api[loteria]:
                        horarios_api[loteria].append(horario)
        except FileNotFoundError:
            print("⚠️  Arquivo resultados.json não encontrado")
        except Exception as e:
            print(f"❌ Erro ao ler resultados.json: {e}")
    
    print(f"✅ Encontrados {sum(len(h) for h in horarios_api.values())} horários na API")
    print()
    
    # Comparar
    resultados_comparacao = []
    
    for loteria_tabela, extracoes in TABELA_EXTRACOES.items():
        horarios_tabela = [e['close'] for e in extracoes if e['status'] == 'Ativa']
        horarios_api_loteria = horarios_api.get(loteria_tabela, [])
        
        # Ordenar horários
        horarios_tabela.sort()
        horarios_api_loteria.sort()
        
        # Encontrar correspondências
        correspondentes = []
        faltando_api = []
        extras_api = []
        
        for h_tabela in horarios_tabela:
            h_tabela_norm = normalizar_horario(h_tabela)
            encontrado = False
            
            for h_api in horarios_api_loteria:
                h_api_norm = normalizar_horario(h_api)
                if h_tabela_norm == h_api_norm:
                    correspondentes.append((h_tabela, h_api))
                    encontrado = True
                    break
            
            if not encontrado:
                faltando_api.append(h_tabela)
        
        # Encontrar horários extras na API
        for h_api in horarios_api_loteria:
            h_api_norm = normalizar_horario(h_api)
            encontrado = False
            
            for h_tabela in horarios_tabela:
                h_tabela_norm = normalizar_horario(h_tabela)
                if h_tabela_norm == h_api_norm:
                    encontrado = True
                    break
            
            if not encontrado:
                extras_api.append(h_api)
        
        resultados_comparacao.append({
            'loteria': loteria_tabela,
            'horarios_tabela': horarios_tabela,
            'horarios_api': horarios_api_loteria,
            'correspondentes': correspondentes,
            'faltando_api': faltando_api,
            'extras_api': extras_api
        })
    
    # Gerar relatório
    print("=" * 80)
    print("RESUMO DA COMPARAÇÃO")
    print("=" * 80)
    print()
    
    # Primeiro, mostrar TODOS os horários coletados pelo monitor
    print("=" * 80)
    print("📡 HORÁRIOS COLETADOS PELO MONITOR (API)")
    print("=" * 80)
    print()
    
    if horarios_api:
        for loteria_api, horarios in sorted(horarios_api.items()):
            if horarios:
                print(f"📊 {loteria_api}")
                print(f"   Horários: {', '.join(sorted(horarios))}")
                print(f"   Total: {len(horarios)} horário(s)")
                print()
    else:
        print("⚠️  Nenhum horário encontrado na API")
        print()
    
    print("=" * 80)
    print("COMPARAÇÃO: TABELA vs API")
    print("=" * 80)
    print()
    
    total_correspondentes = 0
    total_faltando = 0
    total_extras = 0
    
    for resultado in resultados_comparacao:
        loteria = resultado['loteria']
        correspondentes = resultado['correspondentes']
        faltando = resultado['faltando_api']
        extras = resultado['extras_api']
        
        total_correspondentes += len(correspondentes)
        total_faltando += len(faltando)
        total_extras += len(extras)
        
        print(f"\n📊 {loteria}")
        print("-" * 80)
        
        if correspondentes:
            print(f"✅ CORRESPONDENTES ({len(correspondentes)}):")
            for h_tab, h_api in correspondentes:
                print(f"   Tabela: {h_tab:6} = API: {h_api:6} ✓")
        
        if faltando:
            print(f"❌ FALTANDO NA API ({len(faltando)}):")
            for h in faltando:
                print(f"   {h}")
        
        if extras:
            print(f"➕ EXTRAS NA API ({len(extras)}):")
            for h in extras:
                print(f"   {h}")
        
        if not correspondentes and not faltando and not extras:
            print("⚠️  Nenhum horário encontrado")
    
    print()
    print("=" * 80)
    print("ESTATÍSTICAS GERAIS")
    print("=" * 80)
    print(f"✅ Horários correspondentes: {total_correspondentes}")
    print(f"❌ Horários faltando na API: {total_faltando}")
    print(f"➕ Horários extras na API: {total_extras}")
    print()
    
    # Detalhamento por loteria
    print("=" * 80)
    print("DETALHAMENTO POR LOTERIA")
    print("=" * 80)
    print()
    
    for resultado in resultados_comparacao:
        loteria = resultado['loteria']
        print(f"\n{loteria}:")
        print(f"  Tabela: {len(resultado['horarios_tabela'])} horários")
        print(f"  API:    {len(resultado['horarios_api'])} horários")
        print(f"  Match:  {len(resultado['correspondentes'])} correspondentes")
        
        if resultado['horarios_tabela']:
            print(f"  Horários na tabela: {', '.join(resultado['horarios_tabela'])}")
        if resultado['horarios_api']:
            print(f"  Horários na API:    {', '.join(resultado['horarios_api'])}")
    
    # Mostrar também loterias que estão na API mas não na tabela
    print()
    print("=" * 80)
    print("LOTERIAS APENAS NO MONITOR (não na tabela)")
    print("=" * 80)
    print()
    
    loterias_tabela = set(TABELA_EXTRACOES.keys())
    loterias_api = set(horarios_api.keys())
    apenas_api = loterias_api - loterias_tabela
    
    if apenas_api:
        for loteria in sorted(apenas_api):
            horarios = horarios_api[loteria]
            print(f"📊 {loteria}")
            print(f"   Horários: {', '.join(sorted(horarios))}")
            print(f"   Total: {len(horarios)} horário(s)")
            print()
    else:
        print("✅ Todas as loterias do monitor estão na tabela")
        print()

if __name__ == '__main__':
    import sys
    url_api = sys.argv[1] if len(sys.argv) > 1 else None
    comparar_horarios(url_api)
