#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Resultados - Deu no Poste
Monitora resultados do site deunoposte.com.br
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import re
from typing import List, Dict, Optional

class MonitorDeuNoPoste:
    """Monitor para extrair resultados do site deunoposte.com.br"""
    
    BASE_URL = "https://deunoposte.com.br"
    
    # Mapeamento de loterias e seus horários
    # URLs baseadas na estrutura real do site
    LOTERIAS = {
        "Deu no Poste": {
            "base_url": "/deu-no-poste",
            "horarios": ["9h", "11h", "14h", "16h", "18h", "19h", "21h"]
        },
        "Caminho da Sorte": {
            "base_url": "/caminho-da-sorte",
            "horarios": ["9h40", "11h", "12h40", "14h", "15h40", "17h", "18h30", "20h", "21h"]
        },
        "Look Loterias": {
            "base_url": "/look-loterias",
            "horarios": ["7h", "9h", "11h", "14h", "16h", "18h", "21h", "23h"]
        },
        "Loteria Nacional": {
            "base_url": "/loteria-nacional",
            "horarios": ["2h", "8h", "10h", "12h", "15h", "17h", "20h", "23h"]
        },
        "Loteria dos Sonhos": {
            "base_url": "/loteria-dos-sonhos",
            "horarios": ["11h", "14h", "15h", "19h"]
        },
        "Paratodos Bahia": {
            "base_url": "/paratodos-bahia",
            "horarios": ["10h", "12h", "15h", "19h", "21h"]
        },
        "LBR Loterias": {
            "base_url": "/lbr-loterias",
            "horarios": ["8h", "10h", "13h", "15h", "17h", "19h", "20h", "22h", "23h"]
        },
        "Abaese Sergipe": {
            "base_url": "/abaese",
            "horarios": ["13h", "14h", "16h", "19h"]
        },
        "Aval Pernambuco": {
            "base_url": "/aval-pernambuco",
            "horarios": ["9h", "11h", "12h", "14h", "15h", "17h", "19h"]
        },
        "Monte Carlos": {
            "base_url": "/monte-carlos",
            "horarios": ["10h", "11h", "12h", "14h", "15h", "17h", "18h", "20h"]
        },
        "Lotep Paraíba": {
            "base_url": "/lotep",
            "horarios": ["9h", "10h", "12h", "15h", "18h", "20h"]
        },
        "Loteria Popular": {
            "base_url": "/loteria-popular",
            "horarios": ["9h", "11h", "12h", "14h", "15h", "17h", "18h"]
        },
        "Boa Sorte Goiás": {
            "base_url": "/boa-sorte-goias",
            "horarios": ["9h", "11h", "14h", "16h", "18h", "21h"]
        },
        "Jogo do Bicho São Paulo": {
            "base_url": "/jogo-do-bicho-sao-paulo",
            "horarios": ["8h", "10h", "12h", "13h", "15h", "17h", "19h", "20h"]
        }
    }
    
    # Mapeamento de animais para grupos
    ANIMAIS_GRUPOS = {
        "Avestruz": 1, "Águia": 2, "Burro": 3, "Borboleta": 4,
        "Cachorro": 5, "Cabra": 6, "Carneiro": 7, "Camelo": 8,
        "Cobra": 9, "Coelho": 10, "Cavalo": 11, "Elefante": 12,
        "Galo": 13, "Gato": 14, "Jacaré": 15, "Leão": 16,
        "Macaco": 17, "Porco": 18, "Pavão": 19, "Peru": 20,
        "Touro": 21, "Tigre": 22, "Urso": 23, "Veado": 24,
        "Vaca": 25
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.resultados = []
    
    def extrair_numero_grupo(self, texto: str) -> Optional[int]:
        """Extrai o número do grupo do texto do bicho"""
        # Procura por padrão (número) no texto
        match = re.search(r'\((\d+)\)', texto)
        if match:
            return int(match.group(1))
        return None
    
    def extrair_nome_animal(self, texto: str) -> str:
        """Extrai o nome do animal do texto"""
        # Remove espaços extras e o número do grupo
        texto = re.sub(r'\s*\(\d+\)\s*', '', texto).strip()
        return texto
    
    def horario_ja_passou(self, horario: str, data: str = None) -> bool:
        """Verifica se o horário já passou"""
        try:
            # Se não tem data, usa a data atual
            if not data:
                data_atual = datetime.now()
            else:
                # Converte string de data para datetime
                data_atual = datetime.strptime(data, '%Y-%m-%d')
            
            # Extrai hora e minuto do horário (formato: "14h", "15h40", "9h30")
            horario_match = re.match(r'(\d{1,2})h(\d{2})?', horario)
            if not horario_match:
                # Se não conseguir parsear, assume que já passou (para não filtrar)
                return True
            
            hora = int(horario_match.group(1))
            minuto = int(horario_match.group(2)) if horario_match.group(2) else 0
            
            # Cria datetime do horário do resultado
            horario_resultado = data_atual.replace(hour=hora, minute=minuto, second=0, microsecond=0)
            
            # Se a data do resultado é hoje, compara com horário atual
            if data_atual.date() == datetime.now().date():
                return datetime.now() >= horario_resultado
            # Se a data do resultado é no passado, já passou
            elif data_atual.date() < datetime.now().date():
                return True
            # Se a data do resultado é no futuro, ainda não passou
            else:
                return False
                
        except Exception as e:
            print(f"    ⚠️  Erro ao validar horário {horario}: {e}")
            # Em caso de erro, assume que já passou (para não filtrar resultados válidos)
            return True
    
    def extrair_data_pagina(self, soup: BeautifulSoup) -> Optional[str]:
        """Tenta extrair a data da página HTML"""
        try:
            # Procura por padrões de data no texto da página
            texto = soup.get_text()
            
            # Procura por padrão DD/MM/YYYY ou DD-MM-YYYY
            match = re.search(r'(\d{2})[/-](\d{2})[/-](\d{4})', texto)
            if match:
                dia, mes, ano = match.groups()
                return f"{ano}-{mes}-{dia}"
            
            # Procura por "Hoje" ou data em formato brasileiro
            hoje_match = re.search(r'Hoje[,\s]+(\d{2})[/-](\d{2})[/-](\d{4})', texto, re.IGNORECASE)
            if hoje_match:
                dia, mes, ano = hoje_match.groups()
                return f"{ano}-{mes}-{dia}"
            
            # Procura em headings ou títulos
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                texto_heading = heading.get_text()
                match = re.search(r'(\d{2})[/-](\d{2})[/-](\d{4})', texto_heading)
                if match:
                    dia, mes, ano = match.groups()
                    return f"{ano}-{mes}-{dia}"
            
        except Exception as e:
            print(f"    ⚠️  Erro ao extrair data: {e}")
        
        # Se não encontrou, retorna a data atual
        return datetime.now().strftime('%Y-%m-%d')
    
    def parse_resultado_tabela(self, soup: BeautifulSoup, loteria: str, horario: str) -> List[Dict]:
        """Extrai resultados de uma tabela HTML"""
        resultados = []
        
        # Tenta extrair a data da página
        data_resultado = self.extrair_data_pagina(soup)
        
        # Procura pela tabela de resultados
        tabela = soup.find('table', class_='resultado-tabela')
        if not tabela:
            # Tenta encontrar qualquer tabela
            tabela = soup.find('table')
        
        if not tabela:
            return resultados
        
        # Extrai as linhas da tabela
        linhas = tabela.find('tbody')
        if not linhas:
            linhas = tabela
        
        rows = linhas.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                try:
                    premio = cells[0].get_text(strip=True)
                    milhar = cells[1].get_text(strip=True)
                    bicho_texto = cells[2].get_text(strip=True)
                    
                    # Valida se é um milhar válido (4 dígitos)
                    if not re.match(r'^\d{4}$', milhar):
                        continue
                    
                    # Extrai nome do animal e grupo
                    animal = self.extrair_nome_animal(bicho_texto)
                    grupo = self.extrair_numero_grupo(bicho_texto)
                    
                    # Se não encontrou grupo no texto, tenta pelo nome do animal
                    if not grupo and animal in self.ANIMAIS_GRUPOS:
                        grupo = self.ANIMAIS_GRUPOS[animal]
                    
                    resultado = {
                        "loteria": loteria,
                        "horario": horario,
                        "numero": milhar,
                        "animal": animal,
                        "grupo": grupo,
                        "premio": premio,
                        "data": data_resultado,
                        "timestamp": datetime.now().isoformat(),
                        "fonte": "deunoposte.com.br"
                    }
                    
                    # Filtra apenas resultados de horários que já passaram
                    if self.horario_ja_passou(horario, data_resultado):
                        resultados.append(resultado)
                    else:
                        # Log apenas em modo debug (comentado para não poluir logs)
                        # print(f"    ⏭️  Pulando {horario} - ainda não passou")
                        pass
                    
                except Exception as e:
                    print(f"Erro ao processar linha da tabela: {e}")
                    continue
        
        return resultados
    
    def buscar_resultados_loteria(self, loteria: str, config: Dict) -> List[Dict]:
        """Busca resultados de uma loteria específica"""
        todos_resultados = []
        
        print(f"\n🔍 Monitorando: {loteria}")
        
        # Página principal da loteria
        url_principal = f"{self.BASE_URL}{config['base_url']}/"
        resultados_principal = self.buscar_resultados_url(url_principal, loteria, "Principal")
        todos_resultados.extend(resultados_principal)
        
        # Páginas por horário (apenas horários que já passaram)
        data_atual = datetime.now().strftime('%Y-%m-%d')
        for horario in config['horarios']:
            # Verifica se o horário já passou antes de buscar
            if not self.horario_ja_passou(horario, data_atual):
                print(f"  ⏭️  Pulando {horario} - ainda não passou")
                continue
            
            # Formata a URL do horário (formato: /base-url-horario/)
            url_horario = f"{self.BASE_URL}{config['base_url']}-{horario}/"
            
            print(f"  📄 Verificando {horario}...")
            resultados_horario = self.buscar_resultados_url(url_horario, loteria, horario)
            todos_resultados.extend(resultados_horario)
            
            # Pequeno delay para não sobrecarregar o servidor
            time.sleep(0.5)
        
        return todos_resultados
    
    def buscar_resultados_url(self, url: str, loteria: str, horario: str) -> List[Dict]:
        """Busca resultados de uma URL específica"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            resultados = self.parse_resultado_tabela(soup, loteria, horario)
            
            if resultados:
                print(f"    ✅ Encontrados {len(resultados)} resultados")
            else:
                print(f"    ⚠️  Nenhum resultado encontrado")
            
            return resultados
            
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Erro ao acessar {url}: {e}")
            return []
        except Exception as e:
            print(f"    ❌ Erro ao processar {url}: {e}")
            return []
    
    def monitorar_todos(self) -> List[Dict]:
        """Monitora todas as loterias"""
        print("🚀 Iniciando monitoramento do Deu no Poste...")
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        todos_resultados = []
        
        for loteria, config in self.LOTERIAS.items():
            resultados = self.buscar_resultados_loteria(loteria, config)
            todos_resultados.extend(resultados)
            time.sleep(1)  # Delay entre loterias
        
        print(f"\n✅ Monitoramento concluído!")
        print(f"📊 Total de resultados coletados: {len(todos_resultados)}")
        
        return todos_resultados
    
    def salvar_resultados(self, resultados: List[Dict], arquivo: str = "resultados_deunoposte.json"):
        """Salva resultados em arquivo JSON com agrupamento por data"""
        # Agrupa resultados por data
        resultados_por_data = {}
        for resultado in resultados:
            data = resultado.get('data', datetime.now().strftime('%Y-%m-%d'))
            if data not in resultados_por_data:
                resultados_por_data[data] = []
            resultados_por_data[data].append(resultado)
        
        # Ordena as datas
        datas_ordenadas = sorted(resultados_por_data.keys(), reverse=True)
        
        # Estrutura final com separação por data
        dados = {
            "ultima_verificacao": datetime.now().isoformat(),
            "total_resultados": len(resultados),
            "fonte": "deunoposte.com.br",
            "resultados_por_data": {
                data: {
                    "data": data,
                    "total": len(resultados_por_data[data]),
                    "resultados": resultados_por_data[data]
                }
                for data in datas_ordenadas
            },
            # Mantém lista plana para compatibilidade
            "resultados": resultados
        }
        
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Resultados salvos em: {arquivo}")
        print(f"📅 Resultados agrupados por {len(datas_ordenadas)} data(s): {', '.join(datas_ordenadas)}")


def main():
    """Função principal"""
    monitor = MonitorDeuNoPoste()
    resultados = monitor.monitorar_todos()
    monitor.salvar_resultados(resultados)
    
    # Também salva em formato compatível com o dashboard existente
    monitor.salvar_resultados(resultados, "resultados.json")


if __name__ == "__main__":
    main()
