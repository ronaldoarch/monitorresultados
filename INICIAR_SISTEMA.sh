#!/bin/bash
# Script para iniciar o sistema completo

echo "🎰 Iniciando Sistema de Apostas..."
echo ""

# Verificar qual opção usar
echo "Escolha a opção:"
echo "1) Integração com Endpoint PHP (Recomendado)"
echo "2) Sistema Python Completo"
read -p "Opção (1 ou 2): " opcao

case $opcao in
    1)
        echo ""
        echo "🚀 Iniciando integração com Endpoint PHP..."
        
        # Solicitar URL do endpoint
        read -p "URL do endpoint PHP: " endpoint_url
        
        if [ -z "$endpoint_url" ]; then
            endpoint_url="https://lotbicho.com/backend/scraper/processar-resultados-completo.php"
            echo "Usando URL padrão: $endpoint_url"
        fi
        
        # Solicitar intervalo
        read -p "Intervalo em minutos (padrão: 5): " intervalo
        intervalo=${intervalo:-5}
        
        # Solicitar porta
        read -p "Porta (padrão: 5001): " porta
        porta=${porta:-5001}
        
        # Iniciar servidor
        python3 integracao_endpoint_php.py \
            --endpoint-php "$endpoint_url" \
            --auto \
            --intervalo "$intervalo" \
            --port "$porta"
        ;;
    
    2)
        echo ""
        echo "🚀 Iniciando Sistema Python Completo..."
        
        # Verificar se precisa criar extrações
        read -p "Criar extrações? (s/n): " criar_ext
        if [ "$criar_ext" = "s" ]; then
            echo "Criando extrações de exemplo..."
            python3 script_criar_extracao.py --loteria "PT Rio de Janeiro" --horario "11:30"
            python3 script_criar_extracao.py --loteria "Look Goiás" --horario "09:20"
        fi
        
        # Solicitar intervalo
        read -p "Intervalo do monitor em segundos (padrão: 60): " intervalo
        intervalo=${intervalo:-60}
        
        # Solicitar porta
        read -p "Porta (padrão: 5001): " porta
        porta=${porta:-5001}
        
        # Iniciar servidor
        python3 app_apostas_extractions.py \
            --monitor \
            --intervalo "$intervalo" \
            --port "$porta"
        ;;
    
    *)
        echo "Opção inválida"
        exit 1
        ;;
esac

