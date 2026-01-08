#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar extrações no sistema
"""

import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(__file__))

from sistema_liquidacao_extractions import SistemaLiquidacaoExtractions, mapear_loteria_painel_para_sistema
from models import Extracao

def criar_extracao(loteria, horario, minutos_antes_fechar=5, minutos_antes_resultado=0):
    """
    Cria uma extração
    
    Args:
        loteria: Nome da loteria (será mapeado automaticamente)
        horario: Horário do sorteio (ex: "11:30")
        minutos_antes_fechar: Minutos antes do horário que fecha (padrão: 5)
        minutos_antes_resultado: Minutos antes do horário que resultado aparece (padrão: 0)
    """
    sistema = SistemaLiquidacaoExtractions()
    session = sistema.Session()
    
    try:
        # Mapear loteria
        loteria_sistema = mapear_loteria_painel_para_sistema(loteria)
        
        # Parsear horário
        hora, minuto = map(int, horario.split(':'))
        
        # Calcular horários
        hoje = datetime.utcnow().replace(hour=hora, minute=minuto, second=0, microsecond=0)
        real_close_time = hoje + timedelta(minutes=minutos_antes_resultado)
        close_time = real_close_time - timedelta(minutes=minutos_antes_fechar)
        
        # Verificar se já existe
        existente = session.query(Extracao).filter(
            Extracao.loteria == loteria_sistema,
            Extracao.horario == horario,
            Extracao.status.in_(['aberta', 'fechada'])
        ).first()
        
        if existente:
            print(f"⚠️  Extração já existe (ID: {existente.id})")
            return existente.id
        
        # Criar extração
        extracao = Extracao(
            loteria=loteria_sistema,
            horario=horario,
            close_time=close_time,
            real_close_time=real_close_time,
            status='aberta'
        )
        session.add(extracao)
        session.commit()
        
        print(f"✅ Extração criada:")
        print(f"   ID: {extracao.id}")
        print(f"   Loteria: {extracao.loteria}")
        print(f"   Horário: {extracao.horario}")
        print(f"   Fecha em: {extracao.close_time}")
        print(f"   Resultado em: {extracao.real_close_time}")
        
        return extracao.id
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao criar extração: {e}")
        return None
    finally:
        session.close()

def criar_extracoes_diarias(loteria, horarios, minutos_antes_fechar=5):
    """Cria extrações para vários horários de uma loteria"""
    ids = []
    for horario in horarios:
        id_ext = criar_extracao(loteria, horario, minutos_antes_fechar)
        if id_ext:
            ids.append(id_ext)
    return ids

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Criar extração no sistema')
    parser.add_argument('--loteria', required=True, help='Nome da loteria')
    parser.add_argument('--horario', required=True, help='Horário do sorteio (ex: 11:30)')
    parser.add_argument('--minutos-fechar', type=int, default=5, help='Minutos antes que fecha')
    parser.add_argument('--minutos-resultado', type=int, default=0, help='Minutos antes que resultado aparece')
    
    args = parser.parse_args()
    
    criar_extracao(
        args.loteria,
        args.horario,
        args.minutos_fechar,
        args.minutos_resultado
    )

