#!/bin/bash
# Script para configurar Opção B (Endpoint PHP)

echo "🚀 Configurando Opção B - Integração com Endpoint PHP"
echo ""

# Solicitar URL do endpoint
read -p "URL do endpoint PHP (ou Enter para usar padrão): " endpoint_url

if [ -z "$endpoint_url" ]; then
    endpoint_url="https://lotbicho.com/backend/scraper/processar-resultados-completo.php"
    echo "Usando URL padrão: $endpoint_url"
fi

# Testar endpoint
echo ""
echo "🧪 Testando endpoint..."
response=$(curl -s -X POST "$endpoint_url" -w "\n%{http_code}" 2>&1)
http_code=$(echo "$response" | tail -1)
body=$(echo "$response" | head -n -1)

if [ "$http_code" = "200" ]; then
    echo "✅ Endpoint respondeu com sucesso!"
    echo "$body" | head -5
else
    echo "⚠️  Endpoint retornou código: $http_code"
    echo "Verifique se a URL está correta"
fi

# Configurar variável de ambiente
echo ""
echo "📝 Configurando variável de ambiente..."
export ENDPOINT_PHP="$endpoint_url"
echo "export ENDPOINT_PHP=\"$endpoint_url\"" >> ~/.bashrc
echo "export ENDPOINT_PHP=\"$endpoint_url\"" >> ~/.zshrc

echo ""
echo "✅ Configuração concluída!"
echo ""
echo "Para iniciar o servidor:"
echo "  python3 integracao_endpoint_php.py --auto --intervalo 5 --port 5001"
echo ""
echo "Ou use:"
echo "  ./INICIAR_SISTEMA.sh"

