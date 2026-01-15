#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reprocessar resultados existentes e separar PT Paraíba e Lotep
"""

import json
import sys
import os
from datetime import datetime
import re

def separar_pt_paraiba_lotep(loteria_nome, horario, contexto=''):
    """
    Separa PT Paraíba e Lotep baseado no horário e contexto.
    Horários Lotep: 09:45, 10:45, 12:45, 15:45, 18:45
    Horários PT Paraíba: 09:00, 20:00 (e outros)
    """
    if loteria_nome != "PT Paraiba/Lotep":
        return loteria_nome
    
    # Normalizar horário
    horario_str = str(horario or '').replace('h', ':').replace('H', ':')
    contexto_lower = str(contexto).lower()
    
    # Horários específicos do Lotep
    horarios_lotep = ['09:45', '10:45', '12:45', '15:45', '18:45', '9:45', '10:45', '12:45', '15:45', '18:45']
    
    # Verificar se o contexto menciona "lotep" explicitamente
    if 'lotep' in contexto_lower:
        return "Lotep"
    
    # Verificar se o contexto menciona "pt paraíba" ou "pt paraiba" explicitamente
    if 'pt paraíba' in contexto_lower or 'pt paraiba' in contexto_lower:
        return "PT Paraíba"
    
    # Verificar horário
    for h_lotep in horarios_lotep:
        if h_lotep in horario_str or horario_str.startswith(h_lotep.split(':')[0]):
            # Verificar se é realmente Lotep (horários terminam em :45)
            if ':45' in horario_str or horario_str.endswith('45'):
                return "Lotep"
    
    # Se não conseguir identificar pelo horário, verificar padrões comuns
    # PT Paraíba geralmente tem horários redondos (09:00, 20:00)
    if horario_str:
        try:
            partes = horario_str.split(':')
            if len(partes) >= 2:
                minutos = partes[1].strip()
                if minutos == '00' or minutos == '0':
                    return "PT Paraíba"
                elif minutos == '45':
                    return "Lotep"
        except:
            pass
    
    # Default: manter como está (será separado depois se necessário)
    return "PT Paraíba"  # Default para PT Paraíba

def reprocessar_resultados(arquivo='resultados.json'):
    """Reprocessa resultados existentes separando PT Paraíba e Lotep"""
    
    print(f"📂 Carregando {arquivo}...")
    
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"❌ Arquivo {arquivo} não encontrado!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return False
    
    resultados = dados.get('resultados', [])
    total_antes = len(resultados)
    
    if total_antes == 0:
        print("ℹ️  Nenhum resultado encontrado para reprocessar.")
        return True
    
    print(f"📊 Total de resultados antes: {total_antes}")
    
    # Contadores
    pt_paraiba_antes = sum(1 for r in resultados if r.get('loteria') == 'PT Paraiba/Lotep')
    separados_pt = 0
    separados_lotep = 0
    mantidos = 0
    
    # Reprocessar cada resultado
    for resultado in resultados:
        loteria_original = resultado.get('loteria', '')
        
        if loteria_original == 'PT Paraiba/Lotep':
            horario = resultado.get('horario', '')
            contexto = resultado.get('texto_completo', '') or resultado.get('numero', '') + ' ' + resultado.get('animal', '')
            
            # Separar usando a função
            loteria_nova = separar_pt_paraiba_lotep(loteria_original, horario, contexto)
            
            # Atualizar resultado
            resultado['loteria'] = loteria_nova
            
            if loteria_nova == 'PT Paraíba':
                separados_pt += 1
            elif loteria_nova == 'Lotep':
                separados_lotep += 1
            else:
                mantidos += 1
        else:
            mantidos += 1
    
    # Criar backup
    backup_file = f"{arquivo}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"💾 Criando backup: {backup_file}")
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    # Salvar resultados reprocessados
    print(f"💾 Salvando resultados reprocessados...")
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    pt_paraiba_depois = sum(1 for r in resultados if r.get('loteria') == 'PT Paraíba')
    lotep_depois = sum(1 for r in resultados if r.get('loteria') == 'Lotep')
    pt_lotep_depois = sum(1 for r in resultados if r.get('loteria') == 'PT Paraiba/Lotep')
    
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DE REPROCESSAMENTO")
    print("="*60)
    print(f"Total de resultados: {total_antes}")
    print(f"\nAntes:")
    print(f"  - PT Paraiba/Lotep: {pt_paraiba_antes}")
    print(f"\nDepois:")
    print(f"  - PT Paraíba: {pt_paraiba_depois} ({separados_pt} separados)")
    print(f"  - Lotep: {lotep_depois} ({separados_lotep} separados)")
    print(f"  - PT Paraiba/Lotep (mantidos): {pt_lotep_depois}")
    print(f"  - Outras loterias: {mantidos - pt_lotep_depois}")
    print("="*60)
    
    if separados_pt > 0 or separados_lotep > 0:
        print(f"\n✅ Reprocessamento concluído!")
        print(f"   {separados_pt + separados_lotep} resultados separados com sucesso.")
    else:
        print(f"\nℹ️  Nenhum resultado precisou ser separado.")
    
    return True

if __name__ == '__main__':
    arquivo = sys.argv[1] if len(sys.argv) > 1 else 'resultados.json'
    sucesso = reprocessar_resultados(arquivo)
    sys.exit(0 if sucesso else 1)
