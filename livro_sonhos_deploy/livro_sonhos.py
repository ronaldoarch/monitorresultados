#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de interpretação de sonhos para o jogo do bicho
Livro dos Sonhos - Interpretação de sonhos e geração de palpites
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

class LivroSonhos:
    """Sistema de interpretação de sonhos para apostas"""
    
    # Mapeamento de animais para grupos (1-25)
    ANIMAIS_GRUPOS = {
        "Avestruz": 1, "Águia": 2, "Burro": 3, "Borboleta": 4,
        "Cachorro": 5, "Cabra": 6, "Carneiro": 7, "Camelo": 8,
        "Cobra": 9, "Coelho": 10, "Cavalo": 11, "Elefante": 12,
        "Galo": 13, "Gato": 14, "Jacaré": 15, "Leão": 16,
        "Macaco": 17, "Porco": 18, "Pavão": 19, "Peru": 20,
        "Touro": 21, "Tigre": 22, "Urso": 23, "Veado": 24,
        "Vaca": 25
    }
    
    # Dicionário completo de sonhos e suas interpretações
    SONHOS = {
        # Animais
        "avestruz": {"animal": "Avestruz", "grupo": 1, "numeros": [1, 2, 3, 4], "significado": "Persistência e determinação"},
        "águia": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Visão ampla e liberdade"},
        "burro": {"animal": "Burro", "grupo": 3, "numeros": [9, 10, 11, 12], "significado": "Trabalho e paciência"},
        "borboleta": {"animal": "Borboleta", "grupo": 4, "numeros": [13, 14, 15, 16], "significado": "Transformação e renovação"},
        "cachorro": {"animal": "Cachorro", "grupo": 5, "numeros": [17, 18, 19, 20], "significado": "Lealdade e amizade"},
        "cabra": {"animal": "Cabra", "grupo": 6, "numeros": [21, 22, 23, 24], "significado": "Persistência e independência"},
        "carneiro": {"animal": "Carneiro", "grupo": 7, "numeros": [25, 26, 27, 28], "significado": "Paz e tranquilidade"},
        "camelo": {"animal": "Camelo", "grupo": 8, "numeros": [29, 30, 31, 32], "significado": "Resistência e adaptação"},
        "cobra": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Transformação e renovação"},
        "coelho": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Fertilidade e sorte"},
        "cavalo": {"animal": "Cavalo", "grupo": 11, "numeros": [41, 42, 43, 44], "significado": "Força e liberdade"},
        "elefante": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Sabedoria e memória"},
        "galo": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Atenção e alerta"},
        "gato": {"animal": "Gato", "grupo": 14, "numeros": [53, 54, 55, 56], "significado": "Independência e mistério"},
        "jacar": {"animal": "Jacaré", "grupo": 15, "numeros": [57, 58, 59, 60], "significado": "Paciência e estratégia"},
        "leão": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Poder e liderança"},
        "macaco": {"animal": "Macaco", "grupo": 17, "numeros": [65, 66, 67, 68], "significado": "Inteligência e astúcia"},
        "porco": {"animal": "Porco", "grupo": 18, "numeros": [69, 70, 71, 72], "significado": "Prosperidade e abundância"},
        "pavão": {"animal": "Pavão", "grupo": 19, "numeros": [73, 74, 75, 76], "significado": "Beleza e vaidade"},
        "peru": {"animal": "Peru", "grupo": 20, "numeros": [77, 78, 79, 80], "significado": "Generosidade e celebração"},
        "touro": {"animal": "Touro", "grupo": 21, "numeros": [81, 82, 83, 84], "significado": "Força e determinação"},
        "tigre": {"animal": "Tigre", "grupo": 22, "numeros": [85, 86, 87, 88], "significado": "Coragem e poder"},
        "urso": {"animal": "Urso", "grupo": 23, "numeros": [89, 90, 91, 92], "significado": "Força e proteção"},
        "veado": {"animal": "Veado", "grupo": 24, "numeros": [93, 94, 95, 96], "significado": "Gentileza e graça"},
        "vaca": {"animal": "Vaca", "grupo": 25, "numeros": [97, 98, 99, 0], "significado": "Fertilidade e nutrição"},
        
        # Objetos e situações comuns
        "água": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Purificação e renovação"},
        "dinheiro": {"animal": "Porco", "grupo": 18, "numeros": [69, 70, 71, 72], "significado": "Prosperidade financeira"},
        "ouro": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Riqueza e poder"},
        "casa": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Estabilidade e segurança"},
        "comida": {"animal": "Vaca", "grupo": 25, "numeros": [97, 98, 99, 0], "significado": "Abundância e nutrição"},
        "morte": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Transformação e renovação"},
        "casamento": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Fertilidade e união"},
        "criança": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Inocência e renovação"},
        "fogo": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Paixão e energia"},
        "sangue": {"animal": "Tigre", "grupo": 22, "numeros": [85, 86, 87, 88], "significado": "Vitalidade e força"},
        "dente": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Mudanças e transformação"},
        "cobra": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Transformação e renovação"},
        "peixe": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Fertilidade e abundância"},
        "barco": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Viagem e mudanças"},
        "avião": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Liberdade e elevação"},
        "carro": {"animal": "Cavalo", "grupo": 11, "numeros": [41, 42, 43, 44], "significado": "Movimento e progresso"},
        "escada": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Ascensão e crescimento"},
        "escada subindo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Progresso e sucesso"},
        "escada descendo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Cuidado e atenção"},
        "flor": {"animal": "Borboleta", "grupo": 4, "numeros": [13, 14, 15, 16], "significado": "Beleza e renovação"},
        "árvore": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Crescimento e estabilidade"},
        "chuva": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Purificação e renovação"},
        "sol": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Vitalidade e energia"},
        "lua": {"animal": "Gato", "grupo": 14, "numeros": [53, 54, 55, 56], "significado": "Mistério e intuição"},
        "estrela": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Esperança e elevação"},
        "coração": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Amor e emoção"},
        "anel": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Compromisso e união"},
        "chave": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Solução e abertura"},
        "porta": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Oportunidades e mudanças"},
        "janela": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Visão e perspectiva"},
        "espelho": {"animal": "Gato", "grupo": 14, "numeros": [53, 54, 55, 56], "significado": "Reflexão e autoconhecimento"},
        "relógio": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Tempo e atenção"},
        "telefone": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Comunicação e notícias"},
        "carta": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Mensagens e comunicação"},
        "livro": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Sabedoria e conhecimento"},
        "cadeira": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Estabilidade e descanso"},
        "mesa": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Reunião e comunhão"},
        "cama": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Descanso e intimidade"},
        "roupa": {"animal": "Pavão", "grupo": 19, "numeros": [73, 74, 75, 76], "significado": "Aparência e vaidade"},
        "sapato": {"animal": "Cavalo", "grupo": 11, "numeros": [41, 42, 43, 44], "significado": "Caminho e movimento"},
        "óculos": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Clareza e visão"},
        "cigarro": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Cuidado e atenção"},
        "cigarro apagado": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Fim de ciclo"},
        "cigarro aceso": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Energia e paixão"},
        "pássaro": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Liberdade e elevação"},
        "pássaro voando": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Liberdade e sucesso"},
        "cachorro latindo": {"animal": "Cachorro", "grupo": 5, "numeros": [17, 18, 19, 20], "significado": "Alerta e proteção"},
        "gato miando": {"animal": "Gato", "grupo": 14, "numeros": [53, 54, 55, 56], "significado": "Intuição e mistério"},
        "cavalo correndo": {"animal": "Cavalo", "grupo": 11, "numeros": [41, 42, 43, 44], "significado": "Velocidade e progresso"},
        "leão rugindo": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Poder e autoridade"},
        "cobra mordendo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Traição e cuidado"},
        "peixe nadando": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Fertilidade e abundância"},
        "abelha": {"animal": "Borboleta", "grupo": 4, "numeros": [13, 14, 15, 16], "significado": "Trabalho e prosperidade"},
        "formiga": {"animal": "Burro", "grupo": 3, "numeros": [9, 10, 11, 12], "significado": "Trabalho e persistência"},
        "rato": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Fertilidade e renovação"},
        "cobra grande": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Transformação profunda"},
        "cobra pequena": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Mudanças sutis"},
        "cobra venenosa": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Perigo e cuidado"},
        "cobra matando": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Fim de ciclo"},
        "cobra comendo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Transformação e renovação"},
        "cobra engolindo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Absorção e transformação"},
        "cobra rastejando": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Movimento e mudança"},
        "cobra subindo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Ascensão e crescimento"},
        "cobra descendo": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Cuidado e atenção"},
        "cobra na água": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Purificação e renovação"},
        "cobra na terra": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Transformação e renovação"},
        "cobra no ar": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Liberdade e elevação"},
        "cobra no fogo": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Paixão e energia"},
        "cobra no sol": {"animal": "Leão", "grupo": 16, "numeros": [61, 62, 63, 64], "significado": "Vitalidade e energia"},
        "cobra na lua": {"animal": "Gato", "grupo": 14, "numeros": [53, 54, 55, 56], "significado": "Mistério e intuição"},
        "cobra nas estrelas": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Esperança e elevação"},
        "cobra no coração": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Amor e emoção"},
        "cobra no anel": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Compromisso e união"},
        "cobra na chave": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Solução e abertura"},
        "cobra na porta": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Oportunidades e mudanças"},
        "cobra na janela": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Visão e perspectiva"},
        "cobra no espelho": {"animal": "Gato", "grupo": 14, "numeros": [53, 54, 55, 56], "significado": "Reflexão e autoconhecimento"},
        "cobra no relógio": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Tempo e atenção"},
        "cobra no telefone": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Comunicação e notícias"},
        "cobra na carta": {"animal": "Galo", "grupo": 13, "numeros": [49, 50, 51, 52], "significado": "Mensagens e comunicação"},
        "cobra no livro": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Sabedoria e conhecimento"},
        "cobra na cadeira": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Estabilidade e descanso"},
        "cobra na mesa": {"animal": "Elefante", "grupo": 12, "numeros": [45, 46, 47, 48], "significado": "Reunião e comunhão"},
        "cobra na cama": {"animal": "Coelho", "grupo": 10, "numeros": [37, 38, 39, 40], "significado": "Descanso e intimidade"},
        "cobra na roupa": {"animal": "Pavão", "grupo": 19, "numeros": [73, 74, 75, 76], "significado": "Aparência e vaidade"},
        "cobra no sapato": {"animal": "Cavalo", "grupo": 11, "numeros": [41, 42, 43, 44], "significado": "Caminho e movimento"},
        "cobra nos óculos": {"animal": "Águia", "grupo": 2, "numeros": [5, 6, 7, 8], "significado": "Clareza e visão"},
        "cobra no cigarro": {"animal": "Cobra", "grupo": 9, "numeros": [33, 34, 35, 36], "significado": "Cuidado e atenção"},
    }
    
    def __init__(self):
        """Inicializa o sistema de interpretação de sonhos"""
        pass
    
    def normalizar_texto(self, texto: str) -> str:
        """Normaliza o texto para busca (remove acentos, lowercase, etc)"""
        texto = texto.lower().strip()
        # Remove acentos básicos
        texto = texto.replace("á", "a").replace("à", "a").replace("ã", "a").replace("â", "a")
        texto = texto.replace("é", "e").replace("ê", "e")
        texto = texto.replace("í", "i").replace("î", "i")
        texto = texto.replace("ó", "o").replace("ô", "o").replace("õ", "o")
        texto = texto.replace("ú", "u").replace("û", "u")
        texto = texto.replace("ç", "c")
        return texto
    
    def buscar_sonho(self, sonho: str) -> Optional[Dict]:
        """Busca um sonho no dicionário"""
        sonho_normalizado = self.normalizar_texto(sonho)
        
        # Busca exata primeiro (normalizando chaves também)
        for chave, valor in self.SONHOS.items():
            chave_normalizada = self.normalizar_texto(chave)
            if chave_normalizada == sonho_normalizado:
                return valor.copy()
        
        # Busca exata sem normalização (caso já esteja normalizado)
        if sonho_normalizado in self.SONHOS:
            return self.SONHOS[sonho_normalizado].copy()
        
        # Busca parcial (contém) - normalizando chaves
        for chave, valor in self.SONHOS.items():
            chave_normalizada = self.normalizar_texto(chave)
            if chave_normalizada in sonho_normalizado or sonho_normalizado in chave_normalizada:
                return valor.copy()
        
        # Busca por palavras-chave
        palavras = sonho_normalizado.split()
        for palavra in palavras:
            # Busca exata normalizada
            for chave, valor in self.SONHOS.items():
                chave_normalizada = self.normalizar_texto(chave)
                if chave_normalizada == palavra:
                    return valor.copy()
            # Busca exata sem normalização
            if palavra in self.SONHOS:
                return self.SONHOS[palavra].copy()
        
        return None
    
    def interpretar_sonho(self, sonho: str) -> Dict:
        """Interpreta um sonho e retorna informações completas"""
        resultado = self.buscar_sonho(sonho)
        
        if resultado:
            # Adiciona informações extras
            resultado["sonho_original"] = sonho
            resultado["encontrado"] = True
            
            # Gera números de dezena, centena e milhar baseados no grupo
            grupo = resultado["grupo"]
            dezena = grupo * 4 - 3  # Primeiro número do grupo
            centena_base = (grupo - 1) * 4
            milhar_base = (grupo - 1) * 100
            
            resultado["dezena"] = f"{dezena:02d}"
            resultado["centena"] = f"{centena_base:03d}"
            resultado["milhar"] = f"{milhar_base:04d}"
            
            # Sugere dias para apostar (próximos 7 dias)
            hoje = datetime.now()
            dias_sugeridos = []
            for i in range(1, 8):
                dia = hoje + timedelta(days=i)
                dias_sugeridos.append({
                    "data": dia.strftime("%d/%m/%Y"),
                    "dia_semana": dia.strftime("%A"),
                    "prioridade": "alta" if i <= 3 else "média"
                })
            resultado["dias_sugeridos"] = dias_sugeridos
            
            # Horários sugeridos (baseado em horários comuns de sorteios)
            resultado["horarios_sugeridos"] = [
                {"horario": "09:00", "prioridade": "alta"},
                {"horario": "11:00", "prioridade": "alta"},
                {"horario": "14:00", "prioridade": "média"},
                {"horario": "16:00", "prioridade": "média"},
                {"horario": "18:00", "prioridade": "alta"},
                {"horario": "20:00", "prioridade": "alta"},
            ]
            
        else:
            # Se não encontrou, retorna sugestão genérica
            resultado = {
                "sonho_original": sonho,
                "encontrado": False,
                "mensagem": "Sonho não encontrado no dicionário. Tente descrever de forma mais específica.",
                "sugestao": "Tente buscar por palavras-chave como: animal, objeto, situação ou sentimento do sonho."
            }
        
        return resultado
    
    def listar_sonhos_populares(self, limite: int = 50) -> List[Dict]:
        """Lista os sonhos mais populares"""
        sonhos_lista = []
        for chave, valor in list(self.SONHOS.items())[:limite]:
            sonhos_lista.append({
                "sonho": chave,
                "animal": valor["animal"],
                "grupo": valor["grupo"],
                "significado": valor["significado"]
            })
        return sonhos_lista
