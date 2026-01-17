#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Liquidação Automática de Apostas
Roda em thread separada, verifica resultados e liquida apostas automaticamente
"""

import os
import sys
import threading
import time
import logging
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from pytz import timezone
    ZoneInfo = lambda tz: timezone(tz)

# Adicionar ao path
sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Aposta, Resultado, Liquidacao, Usuario, Transacao
from monitor_selenium import carregar_resultados
from matching_resultados import MatchingResultados
from integracao_site import IntegracaoSite

logger = logging.getLogger(__name__)

class BotLiquidacao:
    """
    Bot automático de liquidação de apostas
    Roda em thread separada, verifica a cada 120s
    """
    
    def __init__(self, database_url='sqlite:///apostas.db', site_api_url=None, api_key=None):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self.matching = MatchingResultados()
        self.integracao = IntegracaoSite(site_api_url, api_key) if site_api_url else None
        
        self.rodando = False
        self.thread = None
        self.ultima_verificacao_apostas = None
        
        logger.info(f"🤖 Bot de Liquidação inicializado")
        if site_api_url:
            logger.info(f"🔗 Integração com site: {site_api_url}")
    
    def iniciar(self):
        """Inicia bot em thread separada"""
        if self.rodando:
            logger.warning("⚠️  Bot já está rodando")
            return
        
        self.rodando = True
        self.thread = threading.Thread(
            target=self.loop,
            args=(120,),  # Intervalo de 120s
            daemon=True,
            name="BotLiquidacao"
        )
        self.thread.start()
        logger.info("✅ Bot de Liquidação iniciado")
    
    def parar(self):
        """Para bot"""
        self.rodando = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("🛑 Bot de Liquidação parado")
    
    def loop(self, intervalo=120):
        """Loop principal - executa a cada 120s"""
        logger.info(f"🔄 Bot de Liquidação iniciado (verifica a cada {intervalo}s)")
        
        while self.rodando:
            try:
                # 1. Processar liquidação automática
                self.processar_liquidacao_automatica()
                
                # 2. Verificar apostas pendentes do site (polling - opcional)
                if self.integracao:
                    self.verificar_apostas_site()
                    
            except Exception as e:
                logger.error(f"❌ Erro no bot de liquidação: {e}", exc_info=True)
            
            # Aguardar intervalo
            for _ in range(intervalo):
                if not self.rodando:
                    break
                time.sleep(1)
        
        logger.info("🛑 Bot de Liquidação encerrado")
    
    def receber_aposta(self, dados_aposta):
        """
        Recebe aposta do site externo
        
        Formato esperado:
        {
            "aposta_id_externo": 123,
            "usuario_id": 456,
            "numero": "1234",
            "animal": "Cavalo",
            "valor": 10.0,
            "loteria": "PT RIO",
            "horario": "11:30",
            "tipo_aposta": "grupo",
            "multiplicador": 18.0,
            "extraction_id": 789  # Opcional
        }
        """
        session = self.Session()
        try:
            # Verificar se aposta já existe (evitar duplicatas)
            if dados_aposta.get('aposta_id_externo'):
                existente = session.query(Aposta).filter_by(
                    aposta_id_externo=str(dados_aposta['aposta_id_externo'])
                ).first()
                
                if existente:
                    logger.info(f"⚠️  Aposta {dados_aposta['aposta_id_externo']} já existe")
                    return existente.id
            
            # Processar extraction_id primeiro (prioridade)
            extraction_id = dados_aposta.get('extraction_id')
            loteria = dados_aposta.get('loteria', '')
            horario = dados_aposta.get('horario', '')
            
            # Se tiver extraction_id, buscar dados da extração
            if extraction_id:
                from models import Extracao
                extracao = session.query(Extracao).get(extraction_id)
                if extracao:
                    # Usar dados da extração (mais confiável)
                    loteria = extracao.loteria
                    horario = extracao.horario
                else:
                    # Extração não encontrada - tentar usar loteria e horário enviados
                    if not loteria or loteria.strip() == '':
                        loteria = f"Loteria {extraction_id}"
                    if not horario or horario.strip() == '':
                        horario = 'N/A'
            else:
                # Sem extraction_id - processar loteria e horário enviados
                # Se loteria é um número, pode ser ID da extração
                if loteria and str(loteria).isdigit():
                    # Tentar buscar extração pelo ID numérico da loteria
                    try:
                        from models import Extracao
                        extracao = session.query(Extracao).get(int(loteria))
                        if extracao:
                            loteria = extracao.loteria
                            horario = extracao.horario if not horario or horario.strip() == '' else horario
                        else:
                            loteria = f"Loteria {loteria}"
                    except:
                        loteria = f"Loteria {loteria}"
                
                # Se horário ainda está vazio
                if not horario or horario.strip() == '':
                    horario = 'N/A'
            
            # Processar número - pode vir como múltiplos números (ex: "12-13-19" para terno, "17-18" para dupla)
            numero_raw = str(dados_aposta.get('numero', ''))
            numeros_multiplos = None
            
            # Se tiver hífen, é múltiplos números (terno, duque, etc)
            if '-' in numero_raw:
                # Armazenar formato completo para referência
                numeros_multiplos = numero_raw
                # Pegar primeiro número para compatibilidade
                primeiro_numero = numero_raw.split('-')[0].strip()
                numero = primeiro_numero.zfill(4)
            else:
                numero = numero_raw.zfill(4)
            
            # Criar aposta
            aposta = Aposta(
                aposta_id_externo=str(dados_aposta.get('aposta_id_externo', '')),
                usuario_id=dados_aposta['usuario_id'],
                extraction_id=extraction_id,
                numero=numero,
                numeros_multiplos=numeros_multiplos,
                animal=dados_aposta.get('animal', ''),
                valor=float(dados_aposta['valor']),
                loteria=loteria,
                horario=horario,
                tipo_aposta=dados_aposta.get('tipo_aposta', 'grupo'),
                multiplicador=float(dados_aposta.get('multiplicador', 18.0)),
                status='pendente'
            )
            
            session.add(aposta)
            session.commit()
            
            logger.info(f"✅ Aposta recebida: ID {aposta.id} - {aposta.numero} {aposta.animal} - R$ {aposta.valor:.2f}")
            return aposta.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Erro ao receber aposta: {e}")
            raise
        finally:
            session.close()
    
    def verificar_apostas_site(self):
        """Verifica se há novas apostas no site (polling)"""
        if not self.integracao:
            return
        
        try:
            apostas = self.integracao.buscar_apostas_pendentes(self.ultima_verificacao_apostas)
            if apostas:
                logger.info(f"📥 {len(apostas)} novas apostas encontradas via polling")
                for aposta_data in apostas:
                    try:
                        self.receber_aposta(aposta_data)
                    except Exception as e:
                        logger.error(f"Erro ao processar aposta do site: {e}")
            
            self.ultima_verificacao_apostas = datetime.now(ZoneInfo('America/Sao_Paulo'))
        except Exception as e:
            logger.warning(f"⚠️  Erro ao verificar apostas do site: {e}")
    
    def processar_liquidacao_automatica(self):
        """
        Processa liquidação automática:
        1. Carrega resultados da API
        2. Busca apostas pendentes
        3. Faz matching de resultados
        4. Processa liquidação
        5. Envia liquidação para o site
        """
        session = self.Session()
        try:
            # 1. Carregar resultados da API
            dados = carregar_resultados()
            resultados_coletados = dados.get('resultados', [])
            
            if not resultados_coletados:
                return
            
            # 2. Buscar apostas pendentes
            apostas_pendentes = self.matching.buscar_apostas_pendentes(session)
            
            if not apostas_pendentes:
                return
            
            logger.info(f"🔄 Processando {len(apostas_pendentes)} apostas pendentes...")
            
            # 3. Para cada aposta pendente, tentar encontrar resultado
            for aposta in apostas_pendentes:
                try:
                    self.processar_liquidacao_aposta(aposta, resultados_coletados, session)
                except Exception as e:
                    logger.error(f"❌ Erro ao processar aposta {aposta.id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar liquidação automática: {e}", exc_info=True)
        finally:
            session.close()
    
    def processar_liquidacao_aposta(self, aposta, resultados_coletados, session):
        """
        Processa liquidação de uma aposta específica
        """
        # Calcular janela de tempo válida
        # Se tiver extraction_id, usar horários da extração
        # Se não, usar horário da aposta + estimativa
        
        agora = datetime.now(ZoneInfo('America/Sao_Paulo'))
        
        # Se tiver extração, usar horários dela
        if aposta.extraction_id:
            from models import Extracao
            extracao = session.query(Extracao).get(aposta.extraction_id)
            if extracao:
                janela_inicio = extracao.close_time
                janela_fim = extracao.real_close_time + timedelta(hours=1)
            else:
                # Fallback: usar horário da aposta
                janela_inicio = agora - timedelta(hours=2)
                janela_fim = agora + timedelta(hours=1)
        else:
            # Sem extração: usar horário da aposta como referência
            janela_inicio = agora - timedelta(hours=2)
            janela_fim = agora + timedelta(hours=1)
        
        # Buscar resultados candidatos
        candidatos = self.matching.buscar_resultados_candidatos(
            resultados_coletados,
            aposta,
            janela_inicio,
            janela_fim
        )
        
        if not candidatos:
            return  # Nenhum resultado encontrado ainda
        
        # Escolher melhor resultado
        resultado_dict = self.matching.escolher_melhor_resultado(candidatos, aposta)
        
        if not resultado_dict:
            return
        
        # Verificar se aposta ganhou
        ganhou = False
        valor_ganho = 0.0
        
        numero_resultado = str(resultado_dict.get('numero', '')).strip()
        animal_resultado = resultado_dict.get('animal', '').strip().lower()
        numero_aposta = str(aposta.numero).strip()
        animal_aposta = aposta.animal.strip().lower()
        
        # Comparar número
        if numero_resultado == numero_aposta:
            ganhou = True
            valor_ganho = aposta.valor * aposta.multiplicador
        # Comparar animal
        elif animal_resultado == animal_aposta:
            ganhou = True
            valor_ganho = aposta.valor * aposta.multiplicador
        
        # Atualizar status da aposta
        if ganhou:
            aposta.status = 'ganhou'
            aposta.data_liquidacao = agora
            logger.info(f"✅ Aposta {aposta.id}: GANHOU! R$ {valor_ganho:.2f}")
        else:
            aposta.status = 'perdeu'
            aposta.data_liquidacao = agora
            logger.info(f"❌ Aposta {aposta.id}: Perdeu")
        
        session.commit()
        
        # Enviar liquidação para o site
        if self.integracao and aposta.aposta_id_externo:
            liquidacao_dict = {
                'aposta_id_externo': aposta.aposta_id_externo,
                'aposta_id_bot': aposta.id,
                'status': 'ganhou' if ganhou else 'perdeu',
                'valor_ganho': valor_ganho,
                'resultado': {
                    'numero': numero_resultado,
                    'animal': resultado_dict.get('animal', ''),
                    'posicao': resultado_dict.get('posicao', 0)
                },
                'timestamp': agora.isoformat(),
                'detalhes': {
                    'tipo_aposta': aposta.tipo_aposta,
                    'multiplicador': aposta.multiplicador
                }
            }
            
            self.integracao.enviar_liquidacao(liquidacao_dict)
