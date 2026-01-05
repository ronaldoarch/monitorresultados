#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar usuários iniciais no sistema
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sistema_liquidacao import SistemaLiquidacao
from models import Usuario

def criar_usuario(nome, email, saldo_inicial=0.0):
    """Cria um novo usuário"""
    sistema = SistemaLiquidacao()
    session = sistema.Session()
    
    try:
        # Verificar se usuário já existe
        usuario_existente = session.query(Usuario).filter_by(email=email).first()
        if usuario_existente:
            print(f"⚠️  Usuário {email} já existe (ID: {usuario_existente.id})")
            return usuario_existente.id
        
        # Criar novo usuário
        usuario = Usuario(
            nome=nome,
            email=email,
            saldo=saldo_inicial
        )
        session.add(usuario)
        session.commit()
        
        print(f"✅ Usuário criado:")
        print(f"   ID: {usuario.id}")
        print(f"   Nome: {usuario.nome}")
        print(f"   Email: {usuario.email}")
        print(f"   Saldo: R$ {usuario.saldo:.2f}")
        
        return usuario.id
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao criar usuário: {e}")
        return None
    finally:
        session.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Criar usuário no sistema')
    parser.add_argument('--nome', required=True, help='Nome do usuário')
    parser.add_argument('--email', required=True, help='Email do usuário')
    parser.add_argument('--saldo', type=float, default=0.0, help='Saldo inicial')
    
    args = parser.parse_args()
    
    criar_usuario(args.nome, args.email, args.saldo)

