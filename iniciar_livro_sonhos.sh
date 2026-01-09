#!/bin/bash
# Script para iniciar o servidor do Livro dos Sonhos

cd "$(dirname "$0")"

# Ativar ambiente virtual
if [ ! -d "venv_livro_sonhos" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv_livro_sonhos
    echo "📥 Instalando dependências..."
    source venv_livro_sonhos/bin/activate
    pip install flask flask-cors
else
    source venv_livro_sonhos/bin/activate
fi

echo "🚀 Iniciando servidor do Livro dos Sonhos..."
echo "📖 Acesse: http://localhost:8082/"
echo ""

python3 app_livro_sonhos.py
