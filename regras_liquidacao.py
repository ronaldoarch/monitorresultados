#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Regras de Liquidação - Jogo do Bicho
Implementação completa das regras de liquidação conforme especificação
"""

from typing import List, Dict, Tuple, Optional
from itertools import permutations
from collections import Counter

# ============================================================================
# TABELA DE GRUPOS E DEZENAS
# ============================================================================

# Mapeamento de animais para grupos (1-25)
ANIMAIS_GRUPOS = {
    1: "Avestruz", 2: "Águia", 3: "Burro", 4: "Borboleta",
    5: "Cachorro", 6: "Cabra", 7: "Carneiro", 8: "Camelo",
    9: "Cobra", 10: "Coelho", 11: "Cavalo", 12: "Elefante",
    13: "Galo", 14: "Gato", 15: "Jacaré", 16: "Leão",
    17: "Macaco", 18: "Porco", 19: "Pavão", 20: "Peru",
    21: "Touro", 22: "Tigre", 23: "Urso", 24: "Veado",
    25: "Vaca"
}

def dezena_para_grupo(dezena: int) -> int:
    """
    Converte uma dezena (00-99) para o grupo correspondente (1-25).
    Cada grupo = 4 dezenas consecutivas
    Grupo 25 termina em 00 (inclui 97, 98, 99, 00)
    """
    if dezena == 0:
        return 25  # 00 pertence ao grupo 25 (Vaca)
    return ((dezena - 1) // 4) + 1

def milhar_para_grupo(milhar: int) -> int:
    """Extrai a dezena de um milhar e retorna o grupo."""
    dezena = milhar % 100  # Últimos 2 dígitos
    return dezena_para_grupo(dezena)

def grupos_no_resultado(resultados_milhar: List[int], pos_from: int, pos_to: int) -> List[int]:
    """Converte uma lista de milhares em grupos para um intervalo de posições."""
    grupos = []
    for i in range(pos_from - 1, min(pos_to, len(resultados_milhar))):
        grupos.append(milhar_para_grupo(resultados_milhar[i]))
    return grupos

def grupo_para_dezenas(grupo: int) -> List[int]:
    """Retorna as dezenas de um grupo (1-25)."""
    if grupo < 1 or grupo > 25:
        raise ValueError(f"Grupo inválido: {grupo}")
    
    if grupo == 25:
        return [97, 98, 99, 0]  # 00 = 0
    
    start = (grupo - 1) * 4 + 1
    return [start, start + 1, start + 2, start + 3]

# ============================================================================
# PERMUTAÇÕES DISTINTAS (PARA MODALIDADES INVERTIDAS)
# ============================================================================

def contar_permutacoes_distintas(numero: str) -> int:
    """Conta quantas permutações distintas existem para um número."""
    from itertools import permutations
    seen = set()
    digits = list(numero)
    
    for perm in permutations(digits):
        perm_str = ''.join(perm)
        if perm_str not in seen:
            seen.add(perm_str)
    
    return len(seen)

def gerar_permutacoes_distintas(numero: str) -> List[str]:
    """Gera todas as permutações distintas de um número."""
    from itertools import permutations
    seen = set()
    digits = list(numero)
    
    for perm in permutations(digits):
        perm_str = ''.join(perm)
        if perm_str not in seen:
            seen.add(perm_str)
    
    return sorted(list(seen))

# ============================================================================
# TABELA DE ODDS (MULTIPLICADORES)
# ============================================================================

ODDS_TABLE = {
    'DEZENA': {
        (1, 1): 60, (1, 3): 60, (1, 5): 60, (1, 7): 60,
    },
    'CENTENA': {
        (1, 1): 600, (1, 3): 600, (1, 5): 600, (1, 7): 600,
    },
    'MILHAR': {
        (1, 1): 5000, (1, 3): 5000, (1, 5): 5000,
    },
    'MILHAR_INVERTIDA': {
        (1, 1): 200, (1, 3): 200, (1, 5): 200,
    },
    'CENTENA_INVERTIDA': {
        (1, 1): 600, (1, 3): 600, (1, 5): 600, (1, 7): 600,
    },
    'DEZENA_INVERTIDA': {
        (1, 1): 60, (1, 3): 60, (1, 5): 60, (1, 7): 60,
    },
    'GRUPO': {
        (1, 1): 18, (1, 3): 18, (1, 5): 18, (1, 7): 18,
    },
    'DUPLA_GRUPO': {
        (1, 1): 180, (1, 3): 180, (1, 5): 180, (1, 7): 180,
    },
    'TERNO_GRUPO': {
        (1, 1): 1800, (1, 3): 1800, (1, 5): 1800, (1, 7): 1800,
    },
    'QUADRA_GRUPO': {
        (1, 1): 5000, (1, 3): 5000, (1, 5): 5000, (1, 7): 5000,
    },
    'PASSE': {
        (1, 2): 300,  # Fixo 1º-2º
    },
    'PASSE_VAI_E_VEM': {
        (1, 2): 150,  # Fixo 1º-2º
    },
    'MILHAR_CENTENA': {
        (1, 1): 3300, (1, 3): 3300, (1, 5): 3300,
    },
}

def buscar_odd(modalidade: str, pos_from: int, pos_to: int) -> float:
    """Busca a odd (multiplicador) de uma modalidade para um intervalo de posições."""
    modalidade_odds = ODDS_TABLE.get(modalidade)
    if not modalidade_odds:
        raise ValueError(f"Modalidade não encontrada: {modalidade}")
    
    # Para passe, sempre usar 1-2
    if modalidade in ['PASSE', 'PASSE_VAI_E_VEM']:
        return modalidade_odds.get((1, 2), 0)
    
    # Buscar intervalo exato ou usar padrão
    pos_key = (pos_from, pos_to)
    if pos_key in modalidade_odds:
        return modalidade_odds[pos_key]
    
    # Tentar intervalo padrão 1-5
    return modalidade_odds.get((1, 5), 0)

# ============================================================================
# CÁLCULO DE UNIDADES E VALORES
# ============================================================================

def calcular_unidades(qtd_combinacoes: int, pos_from: int, pos_to: int) -> int:
    """Calcula o número de unidades de aposta."""
    qtd_posicoes = pos_to - pos_from + 1
    return qtd_combinacoes * qtd_posicoes

def calcular_valor_unitario(valor_por_palpite: float, unidades: int) -> float:
    """Calcula o valor unitário de uma aposta."""
    if unidades == 0:
        return 0
    return valor_por_palpite / unidades

def calcular_valor_por_palpite(valor_digitado: float, qtd_palpites: int, divisao_tipo: str) -> float:
    """Calcula o valor por palpite baseado no tipo de divisão."""
    if divisao_tipo == 'each':
        return valor_digitado
    else:
        if qtd_palpites == 0:
            return 0
        return valor_digitado / qtd_palpites

# ============================================================================
# CONFERÊNCIA DE RESULTADOS
# ============================================================================

def conferir_numero(
    resultado: List[int],
    numero_apostado: str,
    modalidade: str,
    pos_from: int,
    pos_to: int
) -> Tuple[int, float]:
    """
    Confere um palpite de número (dezena, centena, milhar) contra resultado.
    Retorna: (acertos, prêmio_total)
    """
    invertida = 'INVERTIDA' in modalidade
    combinations = [numero_apostado]
    
    if invertida:
        combinations = gerar_permutacoes_distintas(numero_apostado)
    
    hits = 0
    numero_digits = len(numero_apostado)
    
    for pos in range(pos_from - 1, min(pos_to, len(resultado))):
        premio = resultado[pos]
        premio_str = str(premio).zfill(4)
        
        # Extrair os últimos N dígitos conforme modalidade
        if numero_digits == 2:
            premio_relevante = premio_str[-2:]  # Dezena
        elif numero_digits == 3:
            premio_relevante = premio_str[-3:]  # Centena
        else:
            premio_relevante = premio_str  # Milhar
        
        # Verificar se alguma combinação bate
        if premio_relevante in combinations:
            hits += 1
    
    return hits, 0.0  # Prêmio será calculado depois

def conferir_grupo_simples(
    resultado: List[int],
    grupo_apostado: int,
    pos_from: int,
    pos_to: int
) -> Tuple[int, float]:
    """Confere um palpite de grupo simples."""
    grupos = grupos_no_resultado(resultado, pos_from, pos_to)
    hits = 1 if grupo_apostado in grupos else 0
    return hits, 0.0

def conferir_dupla_grupo(
    resultado: List[int],
    grupos_apostados: List[int],
    pos_from: int,
    pos_to: int
) -> Tuple[int, float]:
    """Confere um palpite de dupla de grupo."""
    if len(grupos_apostados) != 2:
        raise ValueError('Dupla de grupo deve ter exatamente 2 grupos')
    
    grupos = grupos_no_resultado(resultado, pos_from, pos_to)
    grupos_set = set(grupos)
    
    grupo1_presente = grupos_apostados[0] in grupos_set
    grupo2_presente = grupos_apostados[1] in grupos_set
    
    hits = 1 if (grupo1_presente and grupo2_presente) else 0
    return hits, 0.0

def conferir_terno_grupo(
    resultado: List[int],
    grupos_apostados: List[int],
    pos_from: int,
    pos_to: int
) -> Tuple[int, float]:
    """Confere um palpite de terno de grupo."""
    if len(grupos_apostados) != 3:
        raise ValueError('Terno de grupo deve ter exatamente 3 grupos')
    
    grupos = grupos_no_resultado(resultado, pos_from, pos_to)
    grupos_set = set(grupos)
    
    todos_presentes = all(g in grupos_set for g in grupos_apostados)
    hits = 1 if todos_presentes else 0
    return hits, 0.0

def conferir_quadra_grupo(
    resultado: List[int],
    grupos_apostados: List[int],
    pos_from: int,
    pos_to: int
) -> Tuple[int, float]:
    """Confere um palpite de quadra de grupo."""
    if len(grupos_apostados) != 4:
        raise ValueError('Quadra de grupo deve ter exatamente 4 grupos')
    
    grupos = grupos_no_resultado(resultado, pos_from, pos_to)
    grupos_set = set(grupos)
    
    todos_presentes = all(g in grupos_set for g in grupos_apostados)
    hits = 1 if todos_presentes else 0
    return hits, 0.0

def conferir_passe(
    resultado: List[int],
    grupo1: int,
    grupo2: int,
    vai_e_vem: bool = False
) -> Tuple[int, float]:
    """Confere um palpite de passe (1º → 2º)."""
    if len(resultado) < 2:
        return 0, 0.0
    
    grupo1_resultado = milhar_para_grupo(resultado[0])
    grupo2_resultado = milhar_para_grupo(resultado[1])
    
    hits = 0
    
    if vai_e_vem:
        # Aceita ambas as ordens
        if (grupo1_resultado == grupo1 and grupo2_resultado == grupo2) or \
           (grupo1_resultado == grupo2 and grupo2_resultado == grupo1):
            hits = 1
    else:
        # Ordem exata
        if grupo1_resultado == grupo1 and grupo2_resultado == grupo2:
            hits = 1
    
    return hits, 0.0

# ============================================================================
# CONVERSÃO DE RESULTADOS DA API
# ============================================================================

def converter_resultado_api_para_milhares(resultados_api: List[Dict]) -> List[int]:
    """
    Converte resultados da API organizados para lista de milhares.
    
    Args:
        resultados_api: Lista de resultados no formato da API:
            [{"numero": "4732", "posicao": 1, ...}, ...]
    
    Returns:
        Lista de milhares (inteiros) ordenados por posição
    """
    # Ordenar por posição
    resultados_ordenados = sorted(resultados_api, key=lambda x: x.get('posicao', 0))
    
    # Converter números para inteiros
    milhares = []
    for resultado in resultados_ordenados:
        numero_str = resultado.get('numero', '0000')
        try:
            milhar = int(numero_str)
            milhares.append(milhar)
        except ValueError:
            # Se não conseguir converter, usar 0
            milhares.append(0)
    
    return milhares

# ============================================================================
# FUNÇÃO PRINCIPAL DE CONFERÊNCIA
# ============================================================================

def conferir_palpite_completo(
    resultado_milhares: List[int],
    modalidade: str,
    palpite: Dict,
    pos_from: int,
    pos_to: int,
    valor_por_palpite: float,
    divisao_tipo: str = 'all'
) -> Dict:
    """
    Confere um palpite completo contra um resultado.
    
    Args:
        resultado_milhares: Lista de milhares sorteados (índice 0 = 1º prêmio)
        modalidade: Tipo de modalidade (GRUPO, DEZENA, CENTENA, etc.)
        palpite: Dict com 'grupos' ou 'numero'
        pos_from: Posição inicial (1-indexed)
        pos_to: Posição final (1-indexed)
        valor_por_palpite: Valor apostado
        divisao_tipo: 'all' ou 'each'
    
    Returns:
        Dict com cálculo, prêmio e total
    """
    # Calcular unidades e valor unitário
    if 'GRUPO' in modalidade:
        qtd_grupos = len(palpite.get('grupos', []))
        qtd_posicoes = pos_to - pos_from + 1
        combinations = 1
        units = combinations * qtd_posicoes
        unit_value = calcular_valor_unitario(valor_por_palpite, units)
        
        # Conferir resultado
        if modalidade == 'GRUPO':
            hits, _ = conferir_grupo_simples(resultado_milhares, palpite['grupos'][0], pos_from, pos_to)
        elif modalidade == 'DUPLA_GRUPO':
            hits, _ = conferir_dupla_grupo(resultado_milhares, palpite['grupos'], pos_from, pos_to)
        elif modalidade == 'TERNO_GRUPO':
            hits, _ = conferir_terno_grupo(resultado_milhares, palpite['grupos'], pos_from, pos_to)
        elif modalidade == 'QUADRA_GRUPO':
            hits, _ = conferir_quadra_grupo(resultado_milhares, palpite['grupos'], pos_from, pos_to)
        else:
            raise ValueError(f"Modalidade de grupo não suportada: {modalidade}")
    
    elif modalidade in ['PASSE', 'PASSE_VAI_E_VEM']:
        if not palpite.get('grupos') or len(palpite['grupos']) != 2:
            raise ValueError('Passe requer exatamente 2 grupos')
        
        combinations = 1
        units = 1  # Fixo 1º-2º
        unit_value = valor_por_palpite
        
        vai_e_vem = modalidade == 'PASSE_VAI_E_VEM'
        hits, _ = conferir_passe(resultado_milhares, palpite['grupos'][0], palpite['grupos'][1], vai_e_vem)
    
    else:
        # Modalidade de número
        if not palpite.get('numero'):
            raise ValueError('Modalidade de número requer um número')
        
        numero = palpite['numero']
        invertida = 'INVERTIDA' in modalidade
        
        qtd_posicoes = pos_to - pos_from + 1
        combinations = contar_permutacoes_distintas(numero) if invertida else 1
        units = combinations * qtd_posicoes
        unit_value = calcular_valor_unitario(valor_por_palpite, units)
        
        hits, _ = conferir_numero(resultado_milhares, numero, modalidade, pos_from, pos_to)
    
    # Buscar odd e calcular prêmio
    odd = buscar_odd(modalidade, pos_from, pos_to)
    premio_unidade = odd * unit_value
    total_prize = hits * premio_unidade
    
    return {
        'calculation': {
            'combinations': combinations,
            'positions': pos_to - pos_from + 1,
            'units': units,
            'unitValue': unit_value,
        },
        'prize': {
            'hits': hits,
            'prizePerUnit': premio_unidade,
            'totalPrize': total_prize,
        },
        'totalPrize': total_prize,
        'odd': odd,
    }
