#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versão do monitor que envia resultados para Cloudflare Workers
"""

import sys
import os

# Adicionar venv ao path
venv_path = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.14', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

try:
    import requests
    import json
    from monitor_selenium import verificar, carregar_resultados
except ImportError as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)

# URL do seu Cloudflare Worker
CLOUDFLARE_WORKER_URL = "https://seu-worker.seu-subdominio.workers.dev/api/resultados"

def enviar_para_cloudflare(dados):
    """Envia resultados para Cloudflare Worker"""
    try:
        response = requests.post(
            CLOUDFLARE_WORKER_URL,
            json=dados,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Resultados enviados para Cloudflare: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar para Cloudflare: {e}")
        return False

def main():
    """Monitor que envia para Cloudflare"""
    print("🌐 Monitor com Cloudflare")
    print(f"Worker URL: {CLOUDFLARE_WORKER_URL}")
    print("")
    
    # Fazer verificação
    novos = verificar()
    
    if novos > 0:
        # Carregar dados atualizados
        dados = carregar_resultados()
        
        # Enviar para Cloudflare
        if enviar_para_cloudflare(dados):
            print("✅ Sincronização com Cloudflare concluída!")
        else:
            print("⚠️  Dados salvos localmente, mas não foram enviados para Cloudflare")
    else:
        print("ℹ️  Nenhum resultado novo")

if __name__ == "__main__":
    main()

