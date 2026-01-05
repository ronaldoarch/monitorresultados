// Cloudflare Worker para gerenciar resultados.json
// Use isso se quiser que o monitor atualize via API

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // GET - Retornar resultados
    if (request.method === 'GET' && url.pathname === '/api/resultados') {
      try {
        const data = await env.RESULTADOS.get('data', 'json');
        return new Response(JSON.stringify(data || { resultados: [] }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (e) {
        return new Response(JSON.stringify({ resultados: [], erro: e.message }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 500
        });
      }
    }
    
    // POST - Atualizar resultados (do monitor)
    if (request.method === 'POST' && url.pathname === '/api/resultados') {
      try {
        const data = await request.json();
        await env.RESULTADOS.put('data', JSON.stringify(data));
        return new Response(JSON.stringify({ sucesso: true }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      } catch (e) {
        return new Response(JSON.stringify({ sucesso: false, erro: e.message }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
          status: 500
        });
      }
    }
    
    // Servir arquivo estático (fallback)
    return new Response('API Cloudflare Worker - Use /api/resultados', {
      headers: corsHeaders
    });
  }
}

