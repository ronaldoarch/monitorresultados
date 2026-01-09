# 🎤 Funcionalidade de Gravação de Áudio e Conversão para Texto

O sistema do Livro dos Sonhos agora suporta gravação de áudio e conversão automática para texto!

## 🎯 Como Funciona

### Opção 1: Web Speech API (Recomendado - Navegador)

A funcionalidade principal usa a **Web Speech API** do navegador, que:
- ✅ Não requer backend
- ✅ Funciona diretamente no navegador
- ✅ Suporta português brasileiro (pt-BR)
- ✅ Gratuito e sem limites

#### Navegadores Suportados:
- ✅ Google Chrome
- ✅ Microsoft Edge
- ✅ Safari (iOS 14.5+)
- ⚠️ Firefox (suporte limitado)

#### Como Usar:
1. Clique no botão do microfone 🎤 ao lado do campo de texto
2. Permita o acesso ao microfone quando solicitado
3. Fale seu sonho claramente
4. O texto será transcrito automaticamente no campo

### Opção 2: Backend Speech Recognition (Opcional)

Se preferir processar no servidor, você pode usar o endpoint `/api/v1/audio/transcrever`.

#### Instalação (Opcional):
```bash
source venv_livro_sonhos/bin/activate
pip install SpeechRecognition pydub
```

#### Uso do Endpoint:
```javascript
const formData = new FormData();
formData.append('audio', arquivoAudio);

const response = await fetch('/api/v1/audio/transcrever', {
    method: 'POST',
    body: formData
});

const data = await response.json();
if (data.sucesso) {
    console.log('Texto transcrito:', data.texto);
}
```

## 🎨 Interface

A interface inclui:
- **Botão de microfone** 🎤 no campo de texto
- **Indicador visual** quando está gravando (pulso vermelho)
- **Feedback visual** do texto transcrito
- **Mensagens de erro** claras se algo der errado

## 🔒 Permissões

O navegador solicitará permissão para acessar o microfone na primeira vez. Você precisa:
1. Clicar em "Permitir" quando solicitado
2. Se negou antes, permitir manualmente nas configurações do navegador

### Como Permitir Manualmente:

**Chrome/Edge:**
1. Clique no ícone de cadeado na barra de endereços
2. Vá em "Configurações do site"
3. Permita "Microfone"

**Safari:**
1. Safari > Preferências > Sites
2. Selecione "Microfone"
3. Permita para o site

## 🐛 Solução de Problemas

### "Nenhuma fala detectada"
- Fale mais alto e claro
- Verifique se o microfone está funcionando
- Tente em um ambiente mais silencioso

### "Permissão negada"
- Permita o acesso ao microfone nas configurações do navegador
- Recarregue a página e tente novamente

### "Navegador não suportado"
- Use Chrome, Edge ou Safari
- Atualize seu navegador para a versão mais recente

### "Erro no reconhecimento"
- Verifique sua conexão com a internet (Web Speech API usa serviços online)
- Tente novamente em alguns segundos

## 📱 Compatibilidade Mobile

- ✅ **iOS Safari**: Funciona (iOS 14.5+)
- ✅ **Android Chrome**: Funciona
- ⚠️ **Outros navegadores mobile**: Pode variar

## 💡 Dicas para Melhor Reconhecimento

1. **Fale claramente** e em ritmo normal
2. **Use um ambiente silencioso** quando possível
3. **Fique próximo ao microfone** (mas não muito perto)
4. **Evite ruídos de fundo**
5. **Fale frases completas** ao invés de palavras soltas

## 🔧 Desenvolvimento

### Testar Localmente:
```bash
./iniciar_livro_sonhos.sh
```

Acesse: `http://localhost:8082/`

### Verificar Suporte:
O sistema detecta automaticamente se o navegador suporta gravação. Se não suportar, o botão será desabilitado.

## 📝 Exemplo de Código

### JavaScript (Web Speech API):
```javascript
// Já implementado no sistema
// Basta clicar no botão do microfone
```

### Backend (Opcional):
```python
# Endpoint já disponível em /api/v1/audio/transcrever
# Requer: pip install SpeechRecognition pydub
```

## ✅ Status

- ✅ Web Speech API implementada
- ✅ Interface visual completa
- ✅ Tratamento de erros
- ✅ Feedback ao usuário
- ✅ Endpoint backend opcional
- ✅ Documentação completa

A funcionalidade está **pronta para uso**! 🎉
