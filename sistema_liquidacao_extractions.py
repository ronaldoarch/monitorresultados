#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Liquidação com Extrações (Extractions)
Adaptado para trabalhar com extrações pré-criadas e horários de fechamento
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Aposta, Resultado, Liquidacao, Usuario, Transacao, Extracao
from monitor_selenium import carregar_resultados

# Mapeamento de loterias do painel para o sistema
MAPEAMENTO_LOTERIAS = {
    'PT Rio de Janeiro': 'PT RIO',
    'PT Rio': 'PT RIO',
    'Look Goiás': 'LOOK GOIÁS',
    'Look': 'LOOK GOIÁS',
    'Loteria Nacional': 'LOTERIA NACIONAL',
    'PT Band': 'PT BAND',
    'PT São Paulo': 'PT BAND',
    'Lotece': 'LOTECE',
    'PT Lotep': 'PT LOTEP',
    'PT Bahia': 'PT BAHIA',
    'Maluca Bahia': 'MALUCA BAHIA',
    'Abaese': 'ABAESE',
    'Aval': 'AVAL',
    # Adicione mais conforme necessário
}

def mapear_loteria_painel_para_sistema(loteria_painel):
    """Mapeia nome da loteria do painel para o sistema"""
    return MAPEAMENTO_LOTERIAS.get(loteria_painel, loteria_painel.upper())

class SistemaLiquidacaoExtractions:
    def __init__(self, database_url='sqlite:///apostas.db'):
        """Inicializa sistema de liquidação com extrações"""
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def encontrar_extracao_ativa(self, loteria, horario):
        """Encontra extração ativa para uma loteria e horário"""
        session = self.Session()
        try:
            # Mapear loteria
            loteria_sistema = mapear_loteria_painel_para_sistema(loteria)
            
            # Buscar extração
            extracao = session.query(Extracao).filter(
                and_(
                    Extracao.loteria == loteria_sistema,
                    Extracao.horario == horario,
                    Extracao.status.in_(['aberta', 'fechada'])  # Ainda não sorteada
                )
            ).order_by(Extracao.id.desc()).first()
            
            return extracao
        finally:
            session.close()
    
    def listar_extracoes_disponiveis(self):
        """Lista extrações disponíveis para apostas"""
        session = self.Session()
        try:
            agora = datetime.utcnow()
            
            # Buscar extrações abertas ou fechadas (mas não sorteadas)
            extracoes = session.query(Extracao).filter(
                Extracao.status.in_(['aberta', 'fechada'])
            ).order_by(Extracao.close_time.asc()).all()
            
            resultado = []
            for e in extracoes:
                # Calcular se está aberta
                esta_aberta = agora < e.close_time
                minutos_para_fechar = int((e.close_time - agora).total_seconds() / 60) if esta_aberta else 0
                
                resultado.append({
                    'id': e.id,
                    'loteria': e.loteria,
                    'horario': e.horario,
                    'close_time': e.close_time.isoformat(),
                    'real_close_time': e.real_close_time.isoformat(),
                    'status': e.status,
                    'esta_aberta': esta_aberta,
                    'fecha_em_timestamp': int(e.close_time.timestamp()),
                    'minutos_para_fechar': minutos_para_fechar if esta_aberta else 0
                })
            
            return resultado
        finally:
            session.close()
    
    def criar_aposta_com_extracao(self, usuario_id, extraction_id, numero, animal, valor, tipo_aposta='grupo', multiplicador=18.0):
        """Cria aposta vinculada a uma extração"""
        session = self.Session()
        
        try:
            # Verificar se extração existe e está aberta
            extracao = session.query(Extracao).get(extraction_id)
            if not extracao:
                raise ValueError("Extração não encontrada")
            
            agora = datetime.utcnow()
            if agora >= extracao.close_time:
                raise ValueError(f"Extração já fechou. Fechou em {extracao.close_time}")
            
            # Verificar saldo do usuário
            usuario = session.query(Usuario).get(usuario_id)
            if not usuario:
                raise ValueError("Usuário não encontrado")
            
            if usuario.saldo < valor:
                raise ValueError("Saldo insuficiente")
            
            # Criar aposta
            aposta = Aposta(
                usuario_id=usuario_id,
                extraction_id=extraction_id,
                numero=numero,
                animal=animal,
                valor=valor,
                loteria=extracao.loteria,  # Para exibição
                horario=extracao.horario,  # Para exibição
                tipo_aposta=tipo_aposta,
                multiplicador=multiplicador,
                status='pendente'
            )
            session.add(aposta)
            
            # Debitar saldo
            usuario.saldo -= valor
            
            # Criar transação
            transacao = Transacao(
                usuario_id=usuario_id,
                tipo='aposta',
                valor=-valor,
                descricao=f'Aposta #{aposta.id} - {numero} {animal}',
                status='concluida'
            )
            session.add(transacao)
            
            session.commit()
            
            print(f"✅ Aposta criada: #{aposta.id} - Extração #{extraction_id} - R$ {valor:.2f}")
            return aposta.id
            
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao criar aposta: {e}")
            raise
        finally:
            session.close()
    
    def processar_resultado_por_extracao(self, resultado_dict, extraction_id):
        """Processa resultado de uma extração específica"""
        session = self.Session()
        
        try:
            # Verificar se extração existe
            extracao = session.query(Extracao).get(extraction_id)
            if not extracao:
                print(f"⚠️  Extração {extraction_id} não encontrada")
                return 0
            
            # Verificar se já tem resultado para esta extração
            resultado_existente = session.query(Resultado).filter_by(
                extraction_id=extraction_id
            ).first()
            
            if resultado_existente and resultado_existente.processado:
                print(f"⚠️  Resultado da extração {extraction_id} já foi processado")
                return 0
            
            # Criar ou atualizar resultado
            if resultado_existente:
                resultado = resultado_existente
            else:
                resultado = Resultado(
                    extraction_id=extraction_id,
                    numero=resultado_dict['numero'],
                    animal=resultado_dict['animal'],
                    loteria=extracao.loteria,
                    horario=extracao.horario,
                    timestamp=datetime.fromisoformat(resultado_dict['timestamp'].replace('Z', '+00:00'))
                )
                session.add(resultado)
                session.flush()
            
            # Buscar apostas desta extração
            apostas = session.query(Aposta).filter_by(
                extraction_id=extraction_id,
                status='pendente'
            ).all()
            
            print(f"📊 Processando {len(apostas)} apostas da extração {extraction_id}")
            
            liquidadas = 0
            
            for aposta in apostas:
                ganhou = False
                valor_ganho = 0.0
                
                # Verificar se ganhou
                if aposta.numero == resultado.numero:
                    ganhou = True
                    valor_ganho = aposta.valor * aposta.multiplicador
                elif aposta.animal.lower() == resultado.animal.lower():
                    ganhou = True
                    valor_ganho = aposta.valor * aposta.multiplicador
                
                # Atualizar status
                if ganhou:
                    aposta.status = 'ganhou'
                    aposta.data_liquidacao = datetime.utcnow()
                    
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
                    
                    print(f"✅ Aposta #{aposta.id}: GANHOU! R$ {valor_ganho:.2f}")
                else:
                    aposta.status = 'perdeu'
                    aposta.data_liquidacao = datetime.utcnow()
                    print(f"❌ Aposta #{aposta.id}: Perdeu")
                
                # Criar liquidação
                liquidacao = Liquidacao(
                    aposta_id=aposta.id,
                    resultado_id=resultado.id,
                    valor_aposta=aposta.valor,
                    valor_ganho=valor_ganho,
                    status='concluida'
                )
                session.add(liquidacao)
                
                liquidadas += 1
            
            # Marcar resultado como processado
            resultado.processado = True
            
            # Marcar extração como sorteada e liquidada
            extracao.status = 'liquidada'
            
            session.commit()
            
            print(f"✅ {liquidadas} apostas liquidadas para extração {extraction_id}")
            return liquidadas
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"❌ Erro ao processar resultado: {e}")
            return 0
        finally:
            session.close()
    
    def processar_resultados_monitor(self):
        """Processa resultados do monitor e liquida por extração"""
        print("🔄 Verificando resultados do monitor para liquidar...")
        
        # Carregar resultados do monitor
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        if not resultados:
            print("ℹ️  Nenhum resultado encontrado")
            return 0
        
        session = self.Session()
        total_liquidado = 0
        
        try:
            # Para cada resultado do monitor
            for resultado_dict in resultados:
                loteria = resultado_dict['loteria']
                horario = resultado_dict.get('horario', 'N/A')
                
                # Mapear loteria
                loteria_sistema = mapear_loteria_painel_para_sistema(loteria)
                
                # Buscar extração correspondente
                extracao = session.query(Extracao).filter(
                    and_(
                        Extracao.loteria == loteria_sistema,
                        Extracao.horario == horario,
                        Extracao.status.in_(['fechada', 'sorteada'])  # Já fechou, aguardando resultado
                    )
                ).order_by(Extracao.id.desc()).first()
                
                if extracao:
                    print(f"📌 Encontrada extração {extracao.id} para {loteria} {horario}")
                    liquidadas = self.processar_resultado_por_extracao(resultado_dict, extracao.id)
                    total_liquidado += liquidadas
                else:
                    print(f"⚠️  Nenhuma extração encontrada para {loteria} {horario}")
        
        finally:
            session.close()
        
        print(f"✅ Total: {total_liquidado} apostas liquidadas")
        return total_liquidado

if __name__ == '__main__':
    # Teste
    sistema = SistemaLiquidacaoExtractions()
    sistema.processar_resultados_monitor()

