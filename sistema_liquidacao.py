#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Liquidação Automática de Apostas
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Adicionar ao path
sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Aposta, Resultado, Liquidacao, Usuario, Transacao
from monitor_selenium import carregar_resultados

class SistemaLiquidacao:
    def __init__(self, database_url='sqlite:///apostas.db'):
        """Inicializa sistema de liquidação"""
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def processar_resultado(self, resultado_dict):
        """Processa um resultado e liquida apostas relacionadas"""
        session = self.Session()
        
        try:
            # Verificar se resultado já existe
            resultado_existente = session.query(Resultado).filter_by(
                numero=resultado_dict['numero'],
                animal=resultado_dict['animal'],
                loteria=resultado_dict['loteria'],
                horario=resultado_dict.get('horario', 'N/A')
            ).first()
            
            if resultado_existente and resultado_existente.processado:
                print(f"⚠️  Resultado {resultado_dict['numero']} já foi processado")
                return 0
            
            # Criar ou atualizar resultado
            if resultado_existente:
                resultado = resultado_existente
            else:
                resultado = Resultado(
                    numero=resultado_dict['numero'],
                    animal=resultado_dict['animal'],
                    loteria=resultado_dict['loteria'],
                    horario=resultado_dict.get('horario', 'N/A'),
                    timestamp=datetime.fromisoformat(resultado_dict['timestamp'].replace('Z', '+00:00'))
                )
                session.add(resultado)
                session.flush()
            
            # Buscar apostas pendentes para este resultado
            apostas = session.query(Aposta).filter_by(
                loteria=resultado.loteria,
                horario=resultado.horario,
                status='pendente'
            ).all()
            
            print(f"📊 Processando {len(apostas)} apostas para {resultado.loteria} {resultado.horario}")
            
            liquidadas = 0
            
            for aposta in apostas:
                ganhou = False
                valor_ganho = 0.0
                
                # Verificar se ganhou (número ou animal)
                if aposta.numero == resultado.numero:
                    ganhou = True
                    valor_ganho = aposta.valor * aposta.multiplicador
                elif aposta.animal.lower() == resultado.animal.lower():
                    ganhou = True
                    valor_ganho = aposta.valor * aposta.multiplicador
                
                # Atualizar status da aposta
                if ganhou:
                    aposta.status = 'ganhou'
                    aposta.data_liquidacao = datetime.utcnow()
                    
                    # Atualizar saldo do usuário
                    usuario = session.query(Usuario).get(aposta.usuario_id)
                    if usuario:
                        usuario.saldo += valor_ganho
                        
                        # Criar transação de ganho
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
                
                # Criar registro de liquidação
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
            
            session.commit()
            
            print(f"✅ {liquidadas} apostas liquidadas para resultado {resultado.numero} {resultado.animal}")
            return liquidadas
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"❌ Erro ao processar resultado: {e}")
            return 0
        finally:
            session.close()
    
    def processar_novos_resultados(self):
        """Processa todos os resultados novos do monitor"""
        print("🔄 Verificando novos resultados para liquidar...")
        
        # Carregar resultados do monitor
        dados = carregar_resultados()
        resultados = dados.get('resultados', [])
        
        if not resultados:
            print("ℹ️  Nenhum resultado encontrado")
            return 0
        
        total_liquidado = 0
        
        for resultado_dict in resultados:
            liquidadas = self.processar_resultado(resultado_dict)
            total_liquidado += liquidadas
        
        print(f"✅ Total: {total_liquidado} apostas liquidadas")
        return total_liquidado
    
    def criar_aposta(self, usuario_id, numero, animal, valor, loteria, horario, tipo_aposta='grupo', multiplicador=18.0):
        """Cria uma nova aposta"""
        session = self.Session()
        
        try:
            # Verificar saldo do usuário
            usuario = session.query(Usuario).get(usuario_id)
            if not usuario:
                raise ValueError("Usuário não encontrado")
            
            if usuario.saldo < valor:
                raise ValueError("Saldo insuficiente")
            
            # Criar aposta
            aposta = Aposta(
                usuario_id=usuario_id,
                numero=numero,
                animal=animal,
                valor=valor,
                loteria=loteria,
                horario=horario,
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
            
            print(f"✅ Aposta criada: #{aposta.id} - R$ {valor:.2f}")
            return aposta.id
            
        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao criar aposta: {e}")
            raise
        finally:
            session.close()

if __name__ == '__main__':
    # Teste
    sistema = SistemaLiquidacao()
    sistema.processar_novos_resultados()

