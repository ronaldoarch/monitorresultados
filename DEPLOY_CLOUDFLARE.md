# 🚀 Como Fazer Deploy no Cloudflare

## Opções Disponíveis

### Opção 1: Cloudflare Pages (Recomendado para Dashboard)

**Vantagens:**
- ✅ Grátis
- ✅ HTTPS automático
- ✅ CDN global
- ✅ Deploy automático via Git

**Limitações:**
- ⚠️ Apenas arquivos estáticos (HTML, CSS, JS)
- ⚠️ O monitor Python precisa rodar em outro lugar

**Como fazer:**

1. **Preparar arquivos para deploy:**
```bash
# Criar pasta para deploy
mkdir cloudflare-deploy
cp dashboard_mini.html cloudflare-deploy/index.html
cp resultados.json cloudflare-deploy/
```

2. **Fazer deploy:**
   - Acesse: https://dash.cloudflare.com
   - Vá em "Pages" > "Create a project"
   - Conecte seu repositório Git OU faça upload direto
   - Configure:
     - Build command: (deixe vazio)
     - Output directory: `/`

3. **Atualizar resultados:**
   - O `resultados.json` pode ser atualizado via API do Cloudflare
   - Ou usar Cloudflare Workers para fazer proxy

### Opção 2: Cloudflare Workers (Para API)

**Para criar uma API que atualiza o JSON:**

```javascript
// worker.js
export default {
  async fetch(request, env) {
    if (request.method === 'GET') {
      // Retornar resultados.json
      const results = await env.RESULTADOS.get('data');
      return new Response(results, {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    if (request.method === 'POST') {
      // Atualizar resultados (do monitor)
      const data = await request.json();
      await env.RESULTADOS.put('data', JSON.stringify(data));
      return new Response('OK');
    }
  }
}
```

### Opção 3: Cloudflare Tunnel (Expor Servidor Local)

**Para expor seu servidor local na internet:**

1. Instalar cloudflared:
```bash
brew install cloudflare/cloudflare/cloudflared
```

2. Criar tunnel:
```bash
cloudflared tunnel create monitor-resultados
```

3. Configurar e rodar:
```bash
cloudflared tunnel run monitor-resultados
```

## 🎯 Solução Completa Recomendada

### Arquitetura:

1. **Dashboard:** Cloudflare Pages (grátis, estático)
2. **Monitor:** Servidor VPS barato (DigitalOcean, Linode, etc.) ou sempre rodando local
3. **Sincronização:** Monitor atualiza JSON via Cloudflare Workers KV ou API

### Passo a Passo Simplificado:

1. **Deploy do Dashboard:**
```bash
# Criar repositório Git
git init
git add dashboard_mini.html
git commit -m "Dashboard"
git remote add origin SEU_REPO
git push

# No Cloudflare Pages, conectar o repositório
```

2. **Configurar Monitor para atualizar Cloudflare:**
   - Modificar monitor para fazer POST para Cloudflare Workers
   - Ou usar Cloudflare KV para armazenar resultados

## 📝 Arquivos Necessários para Deploy

Criei um script que prepara tudo:

```bash
./preparar_deploy.sh
```

Isso criará uma pasta `deploy/` pronta para upload no Cloudflare Pages.

