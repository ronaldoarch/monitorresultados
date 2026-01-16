#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor com Selenium para páginas que carregam via JavaScript
"""

import sys
import os

# Adicionar venv ao path se necessário
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.14', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

# Também adicionar user site-packages
import site
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site):
    sys.path.insert(0, user_site)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    from bs4 import BeautifulSoup
    import json
    from datetime import datetime
    import time
    import hashlib
    import re
    try:
        from zoneinfo import ZoneInfo
    except ImportError:
        # Fallback para Python < 3.9
        from pytz import timezone
        ZoneInfo = lambda tz: timezone(tz)
    import logging
except ImportError as e:
    print(f"❌ Erro ao importar bibliotecas: {e}")
    print("Execute: pip install selenium beautifulsoup4")
    sys.exit(1)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# URLs específicas para monitorar
URLS_ESPECIFICAS = {
    "https://bichocerto.com/resultados/rj/para-todos/": "PT Rio de Janeiro",
    "https://bichocerto.com/resultados/lk/look/": "Look Goiás",
    "https://bichocerto.com/resultados/fd/loteria-federal/": "Loteria Federal",
    "https://bichocerto.com/resultados/ln/loteria-nacional/": "Loteria Nacional",
    "https://bichocerto.com/resultados/sp/pt-band/": "PT-SP/Bandeirantes",
    "https://bichocerto.com/resultados/lce/lotece/": "Lotece",
    "https://bichocerto.com/resultados/pb/pt-lotep/": "PT Paraiba/Lotep",
    "https://bichocerto.com/resultados/ba/para-todos/": "PT Bahia",
    "https://bichocerto.com/resultados/mba/maluquinha-bahia/": "Maluca Bahia"
}

# URL principal (HTML estático)
URL_PRINCIPAL = "https://bichocerto.com/resultados/"

# Mapeamento de loterias para estados
MAPEAMENTO_ESTADO = {
    "PT Rio de Janeiro": "RJ",
    "PT-SP/Bandeirantes": "SP",
    "PT Bahia": "BA",
    "PT Paraiba/Lotep": "PB",
    "PT Paraíba": "PB",
    "Lotep": "PB",
    "Look Goiás": "GO",
    "Lotece": "CE",
    "Maluca Bahia": "BA",
    "Loteria Nacional": "BR",  # Nacional
    "Loteria Federal": "BR",   # Nacional
    "Maluquinha RJ": "RJ",
    "PT Paraiba": "PB",
    "PT Goiás": "GO",
    "PT Ceará": "CE",
    "PT Minas Gerais": "MG",
    "PT Paraná": "PR",
    "PT Santa Catarina": "SC",
    "PT Rio Grande do Sul": "RS"
}

def identificar_estado(loteria):
    """Identifica o estado baseado no nome da loteria"""
    # Buscar correspondência exata
    if loteria in MAPEAMENTO_ESTADO:
        return MAPEAMENTO_ESTADO[loteria]
    
    # Buscar por palavras-chave
    loteria_upper = loteria.upper()
    if "RIO DE JANEIRO" in loteria_upper or "RJ" in loteria_upper:
        return "RJ"
    elif "SÃO PAULO" in loteria_upper or "SP" in loteria_upper or "BANDEIRANTES" in loteria_upper:
        return "SP"
    elif "BAHIA" in loteria_upper or "BA" in loteria_upper:
        return "BA"
    elif "PARAIBA" in loteria_upper or "PARAÍBA" in loteria_upper or "PB" in loteria_upper or "LOTEP" in loteria_upper:
        return "PB"
    elif "GOIÁS" in loteria_upper or "GOIAS" in loteria_upper or "GO" in loteria_upper or "LOOK" in loteria_upper:
        return "GO"
    elif "CEARÁ" in loteria_upper or "CEARA" in loteria_upper or "CE" in loteria_upper or "LOTECE" in loteria_upper:
        return "CE"
    elif "MINAS" in loteria_upper or "MG" in loteria_upper:
        return "MG"
    elif "PARANÁ" in loteria_upper or "PARANA" in loteria_upper or "PR" in loteria_upper:
        return "PR"
    elif "SANTA CATARINA" in loteria_upper or "SC" in loteria_upper:
        return "SC"
    elif "RIO GRANDE DO SUL" in loteria_upper or "RS" in loteria_upper:
        return "RS"
    elif "NACIONAL" in loteria_upper or "FEDERAL" in loteria_upper:
        return "BR"
    
    return "BR"  # Default: Brasil (nacional)

def criar_driver():
    """Cria e configura o driver do Selenium"""
    options = Options()
    options.add_argument('--headless')  # Executar sem abrir janela
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        return driver
    except WebDriverException as e:
        logger.error(f"Erro ao criar driver: {e}")
        logger.info("💡 Certifique-se de que o ChromeDriver está instalado:")
        logger.info("   brew install chromedriver (macOS)")
        logger.info("   ou baixe de: https://chromedriver.chromium.org/")
        return None

def extrair_resultados_selenium(driver, url, loteria_nome):
    """Extrai resultados usando Selenium (para páginas com JavaScript)"""
    resultados = []
    
    try:
        logger.info(f"Carregando {url}...")
        driver.get(url)
        
        # Aguardar conteúdo carregar (até 15 segundos)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            # Aguardar mais tempo para JavaScript carregar resultados
            time.sleep(5)
            
            # Aguardar que o elemento "Aguardando Numeros..." mude (indica que resultados carregaram)
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: "Aguardando Numeros" not in d.page_source or 
                              len(d.find_elements(By.CSS_SELECTOR, "h4, [class*='card'], [id*='horario']")) > 0
                )
                # Aguardar mais para garantir que conteúdo foi renderizado
                time.sleep(5)
            except TimeoutException:
                logger.warning(f"Timeout aguardando resultados em {url}")
                time.sleep(3)  # Aguardar um pouco mesmo com timeout
        except TimeoutException:
            logger.warning(f"Timeout ao carregar {url}")
            return resultados
        
        # Obter HTML após JavaScript executar
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        
        # Método 1: Extrair de tabelas (estrutura principal das páginas específicas)
        # Procurar por divs com id="div_display_XX" que contêm tabelas com resultados
        divs_display = soup.find_all('div', id=re.compile(r'div_display_\d+'))
        
        for div_display in divs_display:
            # Buscar título com horário
            titulo = div_display.find('h5', class_='card-title')
            horario = None
            if titulo:
                texto_titulo = titulo.get_text(strip=True)
                horario_match = re.search(r'(\d{1,2}[:h]\d{0,2})', texto_titulo)
                if horario_match:
                    horario = horario_match.group(1)
            
            # Buscar tabela dentro do div
            tabela = div_display.find('table')
            if tabela:
                linhas = tabela.find_all('tr')
                posicao = 0
                # Obter contexto do título para ajudar na identificação
                texto_contexto = titulo.get_text(strip=True) if titulo else ""
                for linha in linhas:
                    # Procurar células com número e animal
                    tds = linha.find_all('td')
                    if len(tds) >= 3:
                        # TD 1 ou primeira célula: pode conter posição/colocação
                        # TD 2: número (dentro de <a> ou <h5>)
                        # TD 3: número do animal (dentro de <h5>)
                        # TD 4: nome do animal (dentro de <h5>)
                        numero_elem = tds[2].find('a') or tds[2].find('h5')
                        animal_elem = tds[4].find('h5') if len(tds) > 4 else None
                        
                        if numero_elem and animal_elem:
                            numero = numero_elem.get_text(strip=True)
                            animal = animal_elem.get_text(strip=True)
                            
                            # Tentar extrair posição da primeira célula ou usar contador
                            posicao_texto = tds[0].get_text(strip=True) if len(tds) > 0 else ""
                            # Procurar número de posição (1, 2, 3, etc.) ou usar contador
                            posicao_match = re.search(r'^(\d+)', posicao_texto)
                            if posicao_match:
                                posicao = int(posicao_match.group(1))
                            else:
                                posicao += 1
                            
                            # Validar se é um resultado válido (número de 3-4 dígitos e animal conhecido)
                            if re.match(r'^\d{3,4}$', numero) and len(animal) > 2:
                                # Separar PT Paraíba e Lotep baseado no horário
                                loteria_final = separar_pt_paraiba_lotep(loteria_nome, horario, texto_contexto)
                                estado = identificar_estado(loteria_final)
                                resultados.append({
                                    'numero': numero,
                                    'animal': animal,
                                    'loteria': loteria_final,
                                    'estado': estado,
                                    'horario': horario,
                                    'posicao': posicao,
                                    'colocacao': f"{posicao}°",
                                    'texto_completo': f"{numero} {animal}",
                                    'timestamp': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
                                    'data_extração': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y'),
                                    'url_origem': url
                                })
        
        # Método 2: Extrair de h4 tags (página principal)
        h4_tags = soup.find_all('h4')
        posicao_h4 = 0
        for h4 in h4_tags:
            texto = h4.get_text(strip=True)
            match = re.search(r'^(\d{4})\s+([A-Za-záàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+)$', texto)
            
            if match:
                numero = match.group(1)
                animal = match.group(2).strip()
                
                contexto = h4.find_parent()
                texto_contexto = contexto.get_text(separator=' ', strip=True) if contexto else ""
                
                horario_match = re.search(r'(\d{1,2}[:h]\d{0,2})', texto_contexto.lower())
                horario = horario_match.group(1) if horario_match else None
                
                posicao_h4 += 1
                # Separar PT Paraíba e Lotep baseado no horário
                loteria_final = separar_pt_paraiba_lotep(loteria_nome, horario, texto_contexto)
                estado = identificar_estado(loteria_final)
                resultados.append({
                    'numero': numero,
                    'animal': animal,
                    'loteria': loteria_final,
                    'estado': estado,
                    'horario': horario,
                    'posicao': posicao_h4,
                    'colocacao': f"{posicao_h4}°",
                    'texto_completo': texto,
                    'timestamp': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
                    'data_extração': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y'),
                    'url_origem': url
                })
        
        # Remover duplicatas
        resultados_unicos = []
        vistos = set()
        for r in resultados:
            chave = (r['numero'], r['animal'], r.get('horario'))
            if chave not in vistos:
                vistos.add(chave)
                resultados_unicos.append(r)
        
        resultados = resultados_unicos
        
        # Se não encontrou, procurar em outras tags (fallback)
        if not resultados:
            elementos = soup.find_all(['div', 'span', 'p', 'td', 'h1', 'h2', 'h3', 'h5', 'h6'])
            posicao_fallback = 0
            for elem in elementos:
                texto = elem.get_text(separator=' ', strip=True)
                match = re.search(r'(\d{4})\s+([A-Za-záàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+)', texto)
                
                if match:
                    numero = match.group(1)
                    animal = match.group(2).strip()
                    
                    animais_validos = ['cavalo', 'burro', 'gato', 'macaco', 'elefante', 'cachorro', 
                                      'avestruz', 'veado', 'porco', 'peru', 'jacaré', 'camelo', 'vaca',
                                      'carneiro', 'tigre', 'leão', 'coelho', 'galo', 'pavão', 'pato']
                    
                    if animal.lower() in animais_validos:
                        horario_match = re.search(r'(\d{1,2}[:h]\d{0,2})', texto.lower())
                        horario = horario_match.group(1) if horario_match else None
                        
                        posicao_fallback += 1
                        # Separar PT Paraíba e Lotep baseado no horário
                        loteria_final = separar_pt_paraiba_lotep(loteria_nome, horario, texto)
                        estado = identificar_estado(loteria_final)
                        resultados.append({
                            'numero': numero,
                            'animal': animal,
                            'loteria': loteria_final,
                            'estado': estado,
                            'horario': horario,
                            'posicao': posicao_fallback,
                            'colocacao': f"{posicao_fallback}°",
                            'texto_completo': texto[:100],
                            'timestamp': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
                            'data_extração': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y'),
                            'url_origem': url
                        })
                        break  # Encontrou um, pode parar
        
    except Exception as e:
        logger.error(f"Erro ao extrair de {url}: {e}")
    
    return resultados

def extrair_resultados_principal():
    """Extrai resultados da página principal (HTML estático)"""
    import requests
    
    resultados = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        response = requests.get(URL_PRINCIPAL, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Agrupar por loteria e horário para calcular posições
        resultados_por_grupo = {}
        
        h4_tags = soup.find_all('h4')
        for h4 in h4_tags:
            texto = h4.get_text(strip=True)
            match = re.search(r'^(\d{4})\s+([A-Za-záàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+)$', texto)
            
            if match:
                numero = match.group(1)
                animal = match.group(2).strip()
                
                contexto = h4.find_parent()
                texto_contexto = contexto.get_text(separator=' ', strip=True) if contexto else ""
                
                # Identificar loteria pelo contexto
                loteria = identificar_loteria_por_contexto(texto_contexto)
                
                horario_match = re.search(r'(\d{1,2}[:h]\d{0,2})', texto_contexto.lower())
                horario = horario_match.group(1) if horario_match else None
                
                # Chave para agrupar (loteria + horário)
                chave_grupo = f"{loteria}_{horario}"
                if chave_grupo not in resultados_por_grupo:
                    resultados_por_grupo[chave_grupo] = []
                
                estado = identificar_estado(loteria)
                resultados_por_grupo[chave_grupo].append({
                    'numero': numero,
                    'animal': animal,
                    'loteria': loteria,
                    'estado': estado,
                    'horario': horario,
                    'texto_completo': texto,
                    'timestamp': datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat(),
                    'data_extração': datetime.now(ZoneInfo('America/Sao_Paulo')).strftime('%d/%m/%Y'),
                    'url_origem': URL_PRINCIPAL
                })
        
        # Adicionar posições e estados baseadas na ordem dentro de cada grupo
        for chave, grupo_resultados in resultados_por_grupo.items():
            for idx, resultado in enumerate(grupo_resultados, start=1):
                resultado['posicao'] = idx
                resultado['colocacao'] = f"{idx}°"
                # Garantir que estado existe
                if 'estado' not in resultado:
                    resultado['estado'] = identificar_estado(resultado.get('loteria', ''))
                resultados.append(resultado)
    except Exception as e:
        logger.error(f"Erro ao extrair da página principal: {e}")
    
    return resultados

def separar_pt_paraiba_lotep(loteria_nome, horario, contexto=''):
    """
    Separa PT Paraíba e Lotep baseado no horário e contexto.
    Horários Lotep: 09:45, 10:45, 12:45, 15:45, 18:45
    Horários PT Paraíba: 09:00, 20:00 (e outros)
    """
    if loteria_nome != "PT Paraiba/Lotep":
        return loteria_nome
    
    # Normalizar horário
    horario_str = str(horario or '').replace('h', ':').replace('H', ':')
    contexto_lower = str(contexto).lower()
    
    # Horários específicos do Lotep
    horarios_lotep = ['09:45', '10:45', '12:45', '15:45', '18:45', '9:45', '10:45', '12:45', '15:45', '18:45']
    
    # Verificar se o contexto menciona "lotep" explicitamente
    if 'lotep' in contexto_lower:
        return "Lotep"
    
    # Verificar se o contexto menciona "pt paraíba" ou "pt paraiba" explicitamente
    if 'pt paraíba' in contexto_lower or 'pt paraiba' in contexto_lower:
        return "PT Paraíba"
    
    # Verificar horário
    for h_lotep in horarios_lotep:
        if h_lotep in horario_str or horario_str.startswith(h_lotep.split(':')[0]):
            # Verificar se é realmente Lotep (horários terminam em :45)
            if ':45' in horario_str or horario_str.endswith('45'):
                return "Lotep"
    
    # Se não conseguir identificar pelo horário, verificar padrões comuns
    # PT Paraíba geralmente tem horários redondos (09:00, 20:00)
    if horario_str:
        try:
            partes = horario_str.split(':')
            if len(partes) >= 2:
                minutos = partes[1].strip()
                if minutos == '00' or minutos == '0':
                    return "PT Paraíba"
                elif minutos == '45':
                    return "Lotep"
        except:
            pass
    
    # Default: manter como está (será separado depois se necessário)
    return "PT Paraíba"  # Default para PT Paraíba

def identificar_loteria_por_contexto(texto):
    """Identifica loteria pelo contexto"""
    texto_lower = texto.lower()
    mapeamento = {
        'PT Rio de Janeiro': ['pt rio', 'pt-rj', 'ppt-rj'],
        'PT-SP/Bandeirantes': ['pt-sp', 'bandeirantes'],
        'Look Goiás': ['look-go', 'look goiás'],
        'Loteria Federal': ['federal'],
        'Loteria Nacional': ['nacional'],
        'Boa Sorte Goiás': ['boa sorte'],
        'Lotece': ['lotece'],
        'PT Paraiba/Lotep': ['pt paraíba', 'pt paraiba', 'lotep'],
        'PT Bahia': ['pt bahia'],
        'Maluca Bahia': ['maluca ba', 'maluca bahia'],
        'Maluquinha RJ': ['maluquinha rj', 'maluquinha'],
        'Loteria Popular': ['popular'],
        'LBR Loterias': ['lbr'],
        'Abaese': ['abaese'],
        'Caminho da Sorte': ['caminho da sorte'],
        'Monte Carlos': ['monte carlos'],
        'Aval': ['aval'],
        'Campina Grande': ['campina grande']
    }
    
    for loteria, variantes in mapeamento.items():
        if any(v in texto_lower for v in variantes):
            return loteria
    
    return "Desconhecida"

def carregar_resultados(arquivo='resultados.json'):
    """Carrega resultados salvos e adiciona posições se não existirem"""
    if os.path.exists(arquivo):
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                # Adicionar posições e estados se não existirem
                if 'resultados' in dados:
                    # Sempre deduplicar primeiro
                    dados['resultados'] = deduplicar_resultados_por_chave(dados['resultados'])
                    # Verificar se algum resultado não tem posição ou estado
                    precisa_atualizacao = any(
                        'posicao' not in r or 'estado' not in r 
                        for r in dados['resultados']
                    )
                    if precisa_atualizacao:
                        dados['resultados'] = adicionar_posicoes(dados['resultados'])
                        # Salvar com posições e estados
                        salvar_resultados(dados, arquivo)
                return dados
        except:
            return {'resultados': [], 'ultima_verificacao': None}
    return {'resultados': [], 'ultima_verificacao': None}

def salvar_resultados(dados, arquivo='resultados.json'):
    """Salva resultados"""
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Erro ao salvar: {e}")

def gerar_id(resultado):
    """Gera ID único para resultado"""
    chave = f"{resultado['loteria']}_{resultado['numero']}_{resultado['animal']}"
    return hashlib.md5(chave.encode()).hexdigest()

def adicionar_posicoes(resultados):
    """Adiciona posições/colocações e estados aos resultados baseado na ordem dentro de cada grupo (loteria + horário)"""
    # Agrupar por loteria normalizada e horário normalizado
    grupos = {}
    for resultado in resultados:
        loteria_norm = normalizar_loteria(resultado.get('loteria', ''))
        horario_norm = normalizar_horario(resultado.get('horario', ''))
        chave = f"{loteria_norm}_{horario_norm}"
        if chave not in grupos:
            grupos[chave] = []
        grupos[chave].append(resultado)
    
    # Adicionar posições e estados dentro de cada grupo
    resultados_com_posicao = []
    for chave, grupo in grupos.items():
        # Ordenar por timestamp ou manter ordem original
        for idx, resultado in enumerate(grupo, start=1):
            resultado['posicao'] = idx
            resultado['colocacao'] = f"{idx}°"
            # Adicionar estado se não existir
            if 'estado' not in resultado:
                resultado['estado'] = identificar_estado(resultado.get('loteria', ''))
            resultados_com_posicao.append(resultado)
    
    return resultados_com_posicao

def normalizar_horario(horario):
    """Normaliza formato de horário para comparação"""
    if not horario:
        return None
    # Remover espaços e converter para minúsculas
    horario = str(horario).strip().lower()
    # Remover 'h' e ':' para normalizar "09:30", "9:30", "09h30", "9h30" -> "0930"
    horario = horario.replace('h', '').replace(':', '').replace(' ', '')
    # Garantir formato HHMM (adicionar zero à esquerda se necessário)
    if len(horario) == 3:
        horario = '0' + horario
    return horario if len(horario) == 4 else None

def normalizar_loteria(loteria):
    """Normaliza nome da loteria para comparação"""
    if not loteria:
        return ''
    loteria = str(loteria).strip().upper()
    # Normalizar variações comuns - fazer antes de outras transformações
    # Substituir variações de PT Rio de Janeiro
    if 'RIO DE JANEIRO' in loteria or 'RIO' in loteria:
        if 'PT' in loteria or 'PPT' in loteria or 'PTM' in loteria or 'PTV' in loteria:
            return 'PT-RJ'
    # Outras normalizações
    loteria = loteria.replace('PT-RIO', 'PT-RJ')
    loteria = loteria.replace('PPT-RJ', 'PT-RJ')  # PPT-RJ é variação de PT-RJ
    loteria = loteria.replace('PTM-RJ', 'PT-RJ')
    loteria = loteria.replace('PTV-RJ', 'PT-RJ')
    return loteria

def deduplicar_resultados_por_chave(resultados):
    """Remove resultados duplicados baseado em (loteria normalizada, horario normalizado, numero)"""
    total_antes = len(resultados)
    unicos = {}
    duplicados_removidos = 0
    
    for r in resultados:
        loteria_norm = normalizar_loteria(r.get('loteria', ''))
        horario_norm = normalizar_horario(r.get('horario', ''))
        numero = str(r.get('numero', '')).strip()
        
        # Criar chave única
        chave = (loteria_norm, horario_norm, numero)
        
        # Se já existe, manter o primeiro (ou o que tem mais informações)
        if chave not in unicos:
            unicos[chave] = r
        else:
            duplicados_removidos += 1
            # Se o novo tem mais campos preenchidos, substituir
            existente = unicos[chave]
            campos_existente = sum(1 for v in existente.values() if v)
            campos_novo = sum(1 for v in r.values() if v)
            if campos_novo > campos_existente:
                unicos[chave] = r
    
    resultado_final = list(unicos.values())
    if duplicados_removidos > 0:
        logger.info(f"🔍 Deduplicação: {total_antes} → {len(resultado_final)} resultados ({duplicados_removidos} duplicados removidos)")
    
    return resultado_final

def verificar():
    """Faz verificação em todas as URLs"""
    logger.info(f"Verificando {len(URLS_ESPECIFICAS)} URLs específicas + página principal...")
    
    dados_anteriores = carregar_resultados()
    # Deduplicar base anterior para evitar acúmulo entre execuções
    if 'resultados' in dados_anteriores:
        dados_anteriores['resultados'] = deduplicar_resultados_por_chave(dados_anteriores['resultados'])
        dados_anteriores['resultados'] = adicionar_posicoes(dados_anteriores['resultados'])
        salvar_resultados(dados_anteriores)
    ids_anteriores = {gerar_id(r) for r in dados_anteriores.get('resultados', [])}
    
    todos_resultados = []
    
    # 1. Extrair da página principal (rápido)
    logger.info("Verificando página principal...")
    resultados_principal = extrair_resultados_principal()
    logger.info(f"  → {len(resultados_principal)} resultados da página principal")
    todos_resultados.extend(resultados_principal)
    
    # 2. Extrair das URLs específicas (com Selenium)
    driver = criar_driver()
    if driver:
        try:
            for url, loteria_nome in URLS_ESPECIFICAS.items():
                logger.info(f"Verificando: {url}")
                resultados = extrair_resultados_selenium(driver, url, loteria_nome)
                logger.info(f"  → {len(resultados)} resultados")
                todos_resultados.extend(resultados)
        finally:
            driver.quit()
    else:
        logger.warning("⚠️  Selenium não disponível. Apenas página principal será verificada.")
        logger.info("💡 Para verificar URLs específicas, instale ChromeDriver:")
        logger.info("   brew install chromedriver")
    
    # Remover duplicados entre fontes (mesma loteria, horário e número)
    todos_resultados = deduplicar_resultados_por_chave(todos_resultados)
    
    # Adicionar posições aos resultados
    todos_resultados = adicionar_posicoes(todos_resultados)
    
    # Detectar novos resultados
    novos = [r for r in todos_resultados if gerar_id(r) not in ids_anteriores]
    
    if novos:
        logger.info(f"✓ {len(novos)} novos resultados encontrados!")
        dados_anteriores['resultados'].extend(novos)
        # Deduplicar antes de adicionar posições
        dados_anteriores['resultados'] = deduplicar_resultados_por_chave(dados_anteriores['resultados'])
        # Re-adicionar posições a todos os resultados (incluindo antigos)
        dados_anteriores['resultados'] = adicionar_posicoes(dados_anteriores['resultados'])
        dados_anteriores['ultima_verificacao'] = datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()
        dados_anteriores['total_resultados'] = len(dados_anteriores['resultados'])
        salvar_resultados(dados_anteriores)
        # Sincronizar com Cloudflare
        sincronizar_cloudflare()
        return len(novos)
    
    # Atualizar posições mesmo se não houver novos resultados
    # Deduplicar antes de adicionar posições
    dados_anteriores['resultados'] = deduplicar_resultados_por_chave(dados_anteriores['resultados'])
    dados_anteriores['resultados'] = adicionar_posicoes(dados_anteriores['resultados'])
    dados_anteriores['ultima_verificacao'] = datetime.now(ZoneInfo('America/Sao_Paulo')).isoformat()
    salvar_resultados(dados_anteriores)
    return 0

def sincronizar_cloudflare():
    """Sincroniza resultados.json com Cloudflare via Git"""
    try:
        import subprocess
        from datetime import datetime
        
        # Verificar se está em repositório Git
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            # Está em repositório Git
            logger.info("📤 Sincronizando com Cloudflare via Git...")
            
            # Copiar para deploy/
            deploy_dir = os.path.join(os.path.dirname(__file__), 'deploy')
            if os.path.exists(deploy_dir):
                import shutil
                shutil.copy('resultados.json', os.path.join(deploy_dir, 'resultados.json'))
            
            # Adicionar e commitar
            subprocess.run(['git', 'add', 'resultados.json'], check=False, cwd=os.path.dirname(__file__))
            if os.path.exists(deploy_dir):
                subprocess.run(['git', 'add', 'deploy/resultados.json'], check=False, cwd=os.path.dirname(__file__))
            
            subprocess.run([
                'git', 'commit', '-m',
                f'Atualizar resultados - {datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M:%S")}'
            ], check=False, cwd=os.path.dirname(__file__))
            
            # Push
            push_result = subprocess.run(
                ['git', 'push'],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(__file__)
            )
            
            if push_result.returncode == 0:
                logger.info("✅ Sincronizado com Cloudflare!")
                return True
            else:
                logger.warning(f"⚠️  Git push falhou (pode ser normal se não houver mudanças)")
                return False
        else:
            logger.info("ℹ️  Não está em repositório Git - pulando sincronização")
            return False
            
    except FileNotFoundError:
        logger.info("ℹ️  Git não encontrado - pulando sincronização")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Erro ao sincronizar: {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--intervalo', type=int, default=60)
    parser.add_argument('--uma-vez', action='store_true')
    args = parser.parse_args()
    
    if args.uma_vez:
        verificar()
    else:
        logger.info(f"Monitor iniciado (verifica a cada {args.intervalo}s)")
        try:
            while True:
                verificar()
                time.sleep(args.intervalo)
        except KeyboardInterrupt:
            logger.info("\nMonitor encerrado")

if __name__ == "__main__":
    main()

