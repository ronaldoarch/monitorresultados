#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Integração com Site Externo
Gerencia comunicação bidirecional com o site do cliente
"""

import logging
import requests
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from pytz import timezone
    ZoneInfo = lambda tz: timezone(tz)

logger = logging.getLogger(__name__)

class IntegracaoSite:
    """
    Gerencia comunicação bidirecional com site externo
    """
    
    def __init__(self, site_api_url=None, api_key=None, timeout=10):
        self.site_api_url = site_api_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configurar headers padrão
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
        else:
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
    
    def enviar_liquidacao(self, liquidacao_dict):
        """
        Envia liquidação de volta para o site externo
        
        Formato esperado em liquidacao_dict:
        {
            "aposta_id_externo": 123,  # ID original do site
            "aposta_id_bot": 456,      # ID no bot
            "status": "ganhou" | "perdeu",
            "valor_ganho": 180.0,
            "resultado": {
                "numero": "1234",
                "animal": "Cavalo",
                "posicao": 1
            },
            "timestamp": "2026-01-16T11:35:00Z",
            "detalhes": {
                "tipo_aposta": "grupo",
                "acertos": 1,
                "multiplicador": 18.0
            }
        }
        """
        if not self.site_api_url:
            logger.warning("⚠️  Site API URL não configurado. Liquidação não será enviada.")
            return False
        
        try:
            endpoint = f'{self.site_api_url.rstrip("/")}/api/liquidacoes/receber'
            
            response = self.session.post(
                endpoint,
                json=liquidacao_dict,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Liquidação enviada para site: aposta {liquidacao_dict.get('aposta_id_externo')}")
                return True
            else:
                logger.error(f"❌ Erro ao enviar liquidação: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout ao enviar liquidação para site")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Erro de conexão ao enviar liquidação para site")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao enviar liquidação para site: {e}")
            return False
    
    def buscar_apostas_pendentes(self, ultima_verificacao=None):
        """
        Busca apostas pendentes do site (polling)
        Útil como fallback se webhook não funcionar
        
        Retorna lista de apostas ou None em caso de erro
        """
        if not self.site_api_url:
            return []
        
        try:
            endpoint = f'{self.site_api_url.rstrip("/")}/api/apostas/pendentes'
            params = {}
            
            if ultima_verificacao:
                params['ultima_verificacao'] = ultima_verificacao.isoformat()
            
            response = self.session.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('apostas', [])
            else:
                logger.warning(f"⚠️  Erro ao buscar apostas pendentes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"⚠️  Erro ao buscar apostas pendentes do site: {e}")
            return []
    
    def testar_conexao(self):
        """
        Testa conexão com o site externo
        """
        if not self.site_api_url:
            return False
        
        try:
            # Tentar endpoint de health check ou raiz
            endpoint = f'{self.site_api_url.rstrip("/")}/api/health'
            response = self.session.get(endpoint, timeout=5)
            return response.status_code == 200
        except:
            # Se não tiver health check, tentar endpoint de apostas
            try:
                endpoint = f'{self.site_api_url.rstrip("/")}/api/apostas/pendentes'
                response = self.session.get(endpoint, timeout=5)
                return response.status_code in [200, 404]  # 404 também é OK (endpoint pode não existir)
            except:
                return False
