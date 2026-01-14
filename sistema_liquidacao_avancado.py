#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Liquidação Avançada com Regras Completas
Integra com API de resultados organizados e aplica todas as regras de liquidação
"""

import sys
import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Adicionar ao path
sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Aposta, Resultado, Liquidacao, Usuario, Transacao
from regras_liquidacao import (
    converter_resultado_api_para_milhares,
    conferir_palpite_completo,
    milhar_para_grupo,
    ANIMAIS_GRUPOS
)

class SistemaLiquidacaoAvancado:
    def __init__(self, database_url='sqlite:///apostas.db', api_url=None):
        """
        Inicializa sistema de liquidação avançado.
        
        Args:
            database_url: URL do banco de dados
            api_url: URL base da API de resultados (ex: https://seu-monitor.com)
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.api_url = api_url or os.getenv('BICHO_CERTO_API', 'http://localhost:8000')
    
    def buscar_resultados_organizados(self, loteria: str = None, horario: str = None) -> Dict:
        """
        Busca resultados organizados da API.
        
        Args:
            loteria: Filtrar por loteria específica (opcional)
            horario: Filtrar por horário específico (opcional)
        
        Returns:
            Dict com resultados organizados
        """
        try:
            url = f"{self.api_url}/api/resultados/organizados"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            organizados = data.get('organizados', {})
            
            # Filtrar se necessário
            if loteria or horario:
                filtrado = {}
                for tab, horarios in organizados.items():
                    if loteria and tab != loteria:
                        continue
                    filtrado[tab] = {}
                    for h, resultados in horarios.items():
                        if horario and h != horario:
                            continue
                        filtrado[tab][h] = resultados
                return {'organizados': filtrado}
            
            return data
        except Exception as e:
            print(f"❌ Erro ao buscar resultados: {e}")
            return {'organizados': {}}
    
    def converter_resultado_para_milhares(self, resultados_api: List[Dict]) -> List[int]:
        """Converte resultados da API para lista de milhares."""
        return converter_resultado_api_para_milhares(resultados_api)
    
    def liquidar_aposta_com_regras(
        self,
        aposta: Aposta,
        resultado_milhares: List[int],
        modalidade: str = None,
        pos_from: int = None,
        pos_to: int = None
    ) -> Dict:
        """
        Liquida uma aposta usando as regras completas.
        
        Args:
            aposta: Objeto Aposta do banco
            resultado_milhares: Lista de milhares sorteados
            modalidade: Tipo de modalidade (se None, usa aposta.tipo_aposta)
            pos_from: Posição inicial (se None, usa 1)
            pos_to: Posição final (se None, usa 7)
        
        Returns:
            Dict com resultado da liquidação
        """
        # Usar valores padrão se não fornecidos
        modalidade = modalidade or aposta.tipo_aposta or 'GRUPO'
        pos_from = pos_from or 1
        pos_to = pos_to or 7
        
        # Preparar palpite conforme modalidade
        palpite = {}
        
        if 'GRUPO' in modalidade or modalidade in ['PASSE', 'PASSE_VAI_E_VEM']:
            # Converter animal para grupo
            grupo = self.animal_para_grupo(aposta.animal)
            if modalidade == 'GRUPO':
                palpite['grupos'] = [grupo]
            elif modalidade == 'DUPLA_GRUPO':
                # Se aposta tem múltiplos grupos, usar; senão, usar apenas o grupo do animal
                palpite['grupos'] = [grupo, grupo]  # Ajustar conforme necessário
            elif modalidade in ['PASSE', 'PASSE_VAI_E_VEM']:
                # Passe requer 2 grupos - usar grupo do animal e grupo do número
                grupo_numero = milhar_para_grupo(int(aposta.numero))
                palpite['grupos'] = [grupo, grupo_numero]
            else:
                palpite['grupos'] = [grupo]
        else:
            # Modalidade de número
            palpite['numero'] = aposta.numero
        
        # Conferir palpite
        try:
            resultado = conferir_palpite_completo(
                resultado_milhares=resultado_milhares,
                modalidade=modalidade,
                palpite=palpite,
                pos_from=pos_from,
                pos_to=pos_to,
                valor_por_palpite=aposta.valor,
                divisao_tipo='all'
            )
            
            return {
                'ganhou': resultado['prize']['hits'] > 0,
                'acertos': resultado['prize']['hits'],
                'valor_ganho': resultado['totalPrize'],
                'detalhes': resultado
            }
        except Exception as e:
            print(f"❌ Erro ao conferir aposta #{aposta.id}: {e}")
            return {
                'ganhou': False,
                'acertos': 0,
                'valor_ganho': 0.0,
                'erro': str(e)
            }
    
    def animal_para_grupo(self, animal: str) -> int:
        """Converte nome do animal para número do grupo (1-25)."""
        animal_lower = animal.lower().strip()
        for grupo, nome_animal in ANIMAIS_GRUPOS.items():
            if nome_animal.lower() == animal_lower:
                return grupo
        # Se não encontrar, tentar usar número do animal diretamente
        try:
            return int(animal)
        except ValueError:
            return 1  # Default para Avestruz
    
    def processar_liquidacao_por_sorteio(
        self,
        loteria: str,
        horario: str,
        resultados_api: List[Dict]
    ) -> int:
        """
        Processa liquidação para um sorteio específico.
        
        Args:
            loteria: Nome da loteria
            horario: Horário do sorteio
            resultados_api: Lista de resultados da API para este sorteio
        
        Returns:
            Número de apostas liquidadas
        """
        session = self.Session()
        liquidadas = 0
        
        try:
            # Converter resultados para milhares
            resultado_milhares = self.converter_resultado_para_milhares(resultados_api)
            
            if not resultado_milhares:
                print(f"⚠️  Nenhum resultado válido para {loteria} {horario}")
                return 0
            
            # Buscar apostas pendentes para este sorteio
            apostas = session.query(Aposta).filter(
                and_(
                    Aposta.loteria == loteria,
                    Aposta.horario == horario,
                    Aposta.status == 'pendente'
                )
            ).all()
            
            print(f"📊 Processando {len(apostas)} apostas para {loteria} {horario}")
            
            for aposta in apostas:
                # Liquidar aposta com regras
                resultado_liquidacao = self.liquidar_aposta_com_regras(
                    aposta=aposta,
                    resultado_milhares=resultado_milhares,
                    modalidade=aposta.tipo_aposta,
                    pos_from=1,
                    pos_to=7
                )
                
                # Atualizar status da aposta
                if resultado_liquidacao['ganhou']:
                    aposta.status = 'ganhou'
                    aposta.data_liquidacao = datetime.utcnow()
                    valor_ganho = resultado_liquidacao['valor_ganho']
                    
                    # Atualizar saldo do usuário
                    usuario = session.query(Usuario).get(aposta.usuario_id)
                    if usuario:
                        usuario.saldo += valor_ganho
                        
                        # Criar transação de ganho
                        transacao = Transacao(
                            usuario_id=usuario.id,
                            tipo='ganho',
                            valor=valor_ganho,
                            descricao=f'Ganho na aposta #{aposta.id} - {aposta.numero} {aposta.animal} ({resultado_liquidacao["acertos"]} acertos)',
                            status='concluida'
                        )
                        session.add(transacao)
                    
                    print(f"✅ Aposta #{aposta.id}: GANHOU! R$ {valor_ganho:.2f} ({resultado_liquidacao['acertos']} acertos)")
                else:
                    aposta.status = 'perdeu'
                    aposta.data_liquidacao = datetime.utcnow()
                    print(f"❌ Aposta #{aposta.id}: Perdeu")
                
                # Criar registro de liquidação
                liquidacao = Liquidacao(
                    aposta_id=aposta.id,
                    resultado_id=None,  # Não temos resultado_id aqui
                    valor_aposta=aposta.valor,
                    valor_ganho=resultado_liquidacao.get('valor_ganho', 0.0),
                    status='concluida'
                )
                session.add(liquidacao)
                
                liquidadas += 1
            
            session.commit()
            print(f"✅ {liquidadas} apostas liquidadas para {loteria} {horario}")
            return liquidadas
            
        except SQLAlchemyError as e:
            session.rollback()
            print(f"❌ Erro ao processar liquidação: {e}")
            return 0
        finally:
            session.close()
    
    def processar_liquidacao_automatica(self) -> int:
        """
        Processa liquidação automática usando resultados da API organizados.
        
        Returns:
            Total de apostas liquidadas
        """
        print("🔄 Iniciando liquidação automática...")
        
        # Buscar resultados organizados
        dados = self.buscar_resultados_organizados()
        organizados = dados.get('organizados', {})
        
        if not organizados:
            print("ℹ️  Nenhum resultado encontrado")
            return 0
        
        total_liquidado = 0
        
        # Processar cada loteria e horário
        for loteria, horarios in organizados.items():
            for horario, resultados in horarios.items():
                if not resultados:
                    continue
                
                liquidadas = self.processar_liquidacao_por_sorteio(
                    loteria=loteria,
                    horario=horario,
                    resultados_api=resultados
                )
                total_liquidado += liquidadas
        
        print(f"✅ Total: {total_liquidado} apostas liquidadas")
        return total_liquidado
    
    def liquidar_aposta_especifica(
        self,
        aposta_id: int,
        loteria: str,
        horario: str
    ) -> Dict:
        """
        Liquida uma aposta específica buscando resultado da API.
        
        Args:
            aposta_id: ID da aposta
            loteria: Nome da loteria
            horario: Horário do sorteio
        
        Returns:
            Dict com resultado da liquidação
        """
        session = self.Session()
        
        try:
            aposta = session.query(Aposta).get(aposta_id)
            if not aposta:
                return {'erro': 'Aposta não encontrada'}
            
            # Buscar resultados para este sorteio
            dados = self.buscar_resultados_organizados(loteria=loteria, horario=horario)
            resultados = dados.get('organizados', {}).get(loteria, {}).get(horario, [])
            
            if not resultados:
                return {'erro': 'Resultado não encontrado para este sorteio'}
            
            # Converter e liquidar
            resultado_milhares = self.converter_resultado_para_milhares(resultados)
            resultado_liquidacao = self.liquidar_aposta_com_regras(
                aposta=aposta,
                resultado_milhares=resultado_milhares,
                modalidade=aposta.tipo_aposta
            )
            
            return resultado_liquidacao
            
        finally:
            session.close()

if __name__ == '__main__':
    # Teste
    sistema = SistemaLiquidacaoAvancado(api_url='http://localhost:8000')
    sistema.processar_liquidacao_automatica()
