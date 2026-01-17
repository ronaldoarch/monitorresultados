#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Matching de Resultados
Responsável por vincular resultados coletados às extrações/apostas corretas
"""

import logging
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from pytz import timezone
    ZoneInfo = lambda tz: timezone(tz)

logger = logging.getLogger(__name__)

# Importar funções de normalização do monitor
from monitor_selenium import normalizar_loteria, normalizar_horario

def parsear_timestamp(timestamp_str):
    """Converte string de timestamp para datetime"""
    if not timestamp_str:
        return None
    
    try:
        # Tentar formato ISO
        if 'T' in str(timestamp_str):
            # Remover 'Z' e substituir por +00:00 se necessário
            ts = str(timestamp_str).replace('Z', '+00:00')
            return datetime.fromisoformat(ts)
        # Tentar outros formatos se necessário
        return datetime.fromisoformat(str(timestamp_str))
    except Exception as e:
        logger.warning(f"Erro ao parsear timestamp {timestamp_str}: {e}")
        return None

def extrair_data_resultado(resultado_dict):
    """Extrai data do resultado (de data_extracao ou timestamp)"""
    # Tentar data_extracao primeiro (formato DD/MM/YYYY)
    data_extracao = resultado_dict.get('data_extracao', '')
    if data_extracao:
        try:
            partes = data_extracao.split('/')
            if len(partes) == 3:
                dia, mes, ano = partes
                return datetime(int(ano), int(mes), int(dia))
        except Exception as e:
            logger.debug(f"Erro ao parsear data_extracao {data_extracao}: {e}")
    
    # Fallback para timestamp
    timestamp = parsear_timestamp(resultado_dict.get('timestamp'))
    if timestamp:
        return timestamp.date()
    
    return None

def horarios_compatíveis(horario1, horario2, tolerancia_minutos=30):
    """
    Verifica se dois horários são compatíveis
    Permite pequena variação (ex: "11h" pode corresponder a "11:30")
    """
    if not horario1 or not horario2:
        return False
    
    # Normalizar horários
    h1_norm = normalizar_horario(horario1)
    h2_norm = normalizar_horario(horario2)
    
    if not h1_norm or not h2_norm:
        return False
    
    # Comparar diretamente
    if h1_norm == h2_norm:
        return True
    
    # Converter para minutos e comparar com tolerância
    try:
        h1_hora = int(h1_norm[:2])
        h1_min = int(h1_norm[2:])
        h2_hora = int(h2_norm[:2])
        h2_min = int(h2_norm[2:])
        
        minutos1 = h1_hora * 60 + h1_min
        minutos2 = h2_hora * 60 + h2_min
        
        diferenca = abs(minutos1 - minutos2)
        return diferenca <= tolerancia_minutos
    except Exception:
        return False

class MatchingResultados:
    """
    Responsável por vincular resultados coletados às extrações/apostas corretas
    """
    
    def __init__(self):
        self.janela_tempo_apos_real_close = timedelta(hours=1)
        self.janela_tempo_antes_close = timedelta(minutes=0)
    
    def buscar_apostas_pendentes(self, session, loteria=None, horario=None):
        """
        Busca apostas pendentes que aguardam resultado
        """
        from models import Aposta
        
        query = session.query(Aposta).filter(
            Aposta.status == 'pendente'
        )
        
        if loteria:
            query = query.filter(Aposta.loteria == loteria)
        
        if horario:
            query = query.filter(Aposta.horario == horario)
        
        return query.all()
    
    def buscar_resultados_candidatos(self, resultados_coletados, aposta, janela_inicio, janela_fim):
        """
        Busca resultados que podem ser vinculados à aposta
        """
        candidatos = []
        
        # Normalizar loteria da aposta
        loteria_aposta = normalizar_loteria(aposta.loteria)
        
        for resultado in resultados_coletados:
            # 1. Normalizar e comparar loteria
            loteria_resultado = normalizar_loteria(resultado.get('loteria', ''))
            
            if loteria_resultado != loteria_aposta:
                continue
            
            # 2. Comparar horários
            horario_resultado = resultado.get('horario', '')
            horario_aposta = aposta.horario
            
            if not horarios_compatíveis(horario_resultado, horario_aposta):
                continue
            
            # 3. Verificar timestamp
            timestamp_resultado = parsear_timestamp(resultado.get('timestamp'))
            if not timestamp_resultado:
                continue
            
            # Verificar se está na janela válida
            if janela_inicio <= timestamp_resultado <= janela_fim:
                candidatos.append({
                    'resultado': resultado,
                    'timestamp': timestamp_resultado,
                    'proximidade': abs((timestamp_resultado - janela_inicio).total_seconds())
                })
        
        # Ordenar por proximidade (mais próximo do início da janela primeiro)
        candidatos.sort(key=lambda x: x['proximidade'])
        
        return [c['resultado'] for c in candidatos]
    
    def escolher_melhor_resultado(self, candidatos, aposta):
        """
        Escolhe o melhor resultado entre candidatos
        Prioriza: mais próximo do horário da aposta, mais completo
        """
        if not candidatos:
            return None
        
        if len(candidatos) == 1:
            return candidatos[0]
        
        # Se múltiplos candidatos, escolher o mais completo e recente
        melhor = candidatos[0]
        melhor_score = 0
        
        for candidato in candidatos:
            score = 0
            
            # Priorizar resultados com mais campos preenchidos
            campos_preenchidos = sum(1 for v in candidato.values() if v)
            score += campos_preenchidos * 10
            
            # Priorizar resultados mais recentes
            timestamp = parsear_timestamp(candidato.get('timestamp'))
            if timestamp:
                score += timestamp.timestamp()
            
            if score > melhor_score:
                melhor_score = score
                melhor = candidato
        
        return melhor
    
    def confirmar_resultado_na_api(self, resultado_banco, resultados_api):
        """
        Confirma que resultado ainda está na API
        """
        if not resultado_banco:
            return False
        
        # Buscar resultado correspondente na API
        for resultado_api in resultados_api:
            if (resultado_api.get('numero') == resultado_banco.numero and
                resultado_api.get('animal', '').lower() == resultado_banco.animal.lower() and
                normalizar_loteria(resultado_api.get('loteria', '')) == normalizar_loteria(resultado_banco.loteria)):
                return True
        
        return False
