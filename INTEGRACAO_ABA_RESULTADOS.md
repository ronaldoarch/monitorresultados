# 🎯 Integração - Aba de Resultados no Site

## 📋 Guia Completo para Exibir Resultados na Aba do Seu Site

Este guia mostra como integrar a API de resultados na aba de resultados do seu site.

---

## 🔗 URL da API

```
https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados
```

---

## 💻 Exemplo 1: JavaScript Simples (Vanilla JS)

### HTML
```html
<div id="resultados-container">
    <h2>Resultados</h2>
    <div id="filtros">
        <select id="filtro-estado">
            <option value="">Todos os estados</option>
            <option value="RJ">Rio de Janeiro</option>
            <option value="SP">São Paulo</option>
            <option value="GO">Goiás</option>
            <option value="BA">Bahia</option>
            <option value="PB">Paraíba</option>
            <option value="CE">Ceará</option>
            <option value="BR">Nacional</option>
        </select>
        <select id="filtro-loteria">
            <option value="">Todas as loterias</option>
        </select>
    </div>
    <div id="resultados-lista"></div>
</div>
```

### JavaScript
```javascript
// URL da API
const API_URL = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados';

// Carregar resultados
async function carregarResultados(estado = '', loteria = '') {
    try {
        let url = API_URL;
        
        // Se filtro por estado, usar endpoint específico
        if (estado) {
            url = `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${estado}`;
            const response = await fetch(url);
            const data = await response.json();
            return data.resultados || [];
        }
        
        // Buscar todos
        const response = await fetch(url);
        const data = await response.json();
        let resultados = data.resultados || [];
        
        // Filtrar por loteria se necessário
        if (loteria) {
            resultados = resultados.filter(r => r.loteria === loteria);
        }
        
        return resultados;
    } catch (error) {
        console.error('Erro ao carregar resultados:', error);
        return [];
    }
}

// Agrupar resultados por loteria e horário
function agruparResultados(resultados) {
    const grupos = {};
    
    resultados.forEach(r => {
        const chave = `${r.loteria}_${r.horario}`;
        if (!grupos[chave]) {
            grupos[chave] = {
                loteria: r.loteria,
                horario: r.horario,
                estado: r.estado,
                resultados: []
            };
        }
        grupos[chave].resultados.push(r);
    });
    
    return Object.values(grupos);
}

// Exibir resultados
function exibirResultados(resultados) {
    const container = document.getElementById('resultados-lista');
    
    if (resultados.length === 0) {
        container.innerHTML = '<p>Nenhum resultado encontrado.</p>';
        return;
    }
    
    const grupos = agruparResultados(resultados);
    
    let html = '';
    
    grupos.forEach(grupo => {
        // Ordenar resultados por posição
        grupo.resultados.sort((a, b) => a.posicao - b.posicao);
        
        html += `
            <div class="grupo-resultado">
                <h3>${grupo.loteria} - ${grupo.horario} <span class="estado-badge">${grupo.estado}</span></h3>
                <div class="resultados-grid">
        `;
        
        grupo.resultados.forEach(r => {
            html += `
                <div class="resultado-item">
                    <span class="posicao">${r.colocacao}</span>
                    <span class="numero">${r.numero}</span>
                    <span class="animal">${r.animal}</span>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

// Atualizar lista de loterias no filtro
async function atualizarFiltroLoterias(estado = '') {
    const resultados = await carregarResultados(estado);
    const loterias = [...new Set(resultados.map(r => r.loteria))].sort();
    
    const select = document.getElementById('filtro-loteria');
    select.innerHTML = '<option value="">Todas as loterias</option>';
    
    loterias.forEach(loteria => {
        const option = document.createElement('option');
        option.value = loteria;
        option.textContent = loteria;
        select.appendChild(option);
    });
}

// Inicializar
async function inicializar() {
    const filtroEstado = document.getElementById('filtro-estado');
    const filtroLoteria = document.getElementById('filtro-loteria');
    
    // Carregar resultados iniciais
    const resultados = await carregarResultados();
    exibirResultados(resultados);
    await atualizarFiltroLoterias();
    
    // Event listeners
    filtroEstado.addEventListener('change', async () => {
        const estado = filtroEstado.value;
        await atualizarFiltroLoterias(estado);
        const resultados = await carregarResultados(estado);
        exibirResultados(resultados);
    });
    
    filtroLoteria.addEventListener('change', async () => {
        const estado = filtroEstado.value;
        const loteria = filtroLoteria.value;
        const resultados = await carregarResultados(estado, loteria);
        exibirResultados(resultados);
    });
    
    // Atualizar a cada 60 segundos
    setInterval(async () => {
        const estado = filtroEstado.value;
        const loteria = filtroLoteria.value;
        const resultados = await carregarResultados(estado, loteria);
        exibirResultados(resultados);
    }, 60000);
}

// Executar quando página carregar
document.addEventListener('DOMContentLoaded', inicializar);
```

### CSS
```css
#resultados-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

#filtros {
    display: flex;
    gap: 15px;
    margin-bottom: 30px;
}

#filtros select {
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 14px;
}

.grupo-resultado {
    background: #f9f9f9;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.grupo-resultado h3 {
    margin: 0 0 15px 0;
    color: #333;
    font-size: 18px;
}

.estado-badge {
    display: inline-block;
    background: #007bff;
    color: white;
    padding: 3px 8px;
    border-radius: 3px;
    font-size: 12px;
    margin-left: 10px;
}

.resultados-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
}

.resultado-item {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 5px;
    padding: 10px;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.resultado-item .posicao {
    font-weight: bold;
    color: #007bff;
    font-size: 14px;
}

.resultado-item .numero {
    font-size: 18px;
    font-weight: bold;
    color: #333;
}

.resultado-item .animal {
    font-size: 14px;
    color: #666;
}
```

---

## 💻 Exemplo 2: Usando jQuery (se seu site já usa)

```javascript
$(document).ready(function() {
    const API_URL = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados';
    
    function carregarResultados(estado = '') {
        let url = estado 
            ? `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${estado}`
            : API_URL;
        
        $.ajax({
            url: url,
            method: 'GET',
            dataType: 'json',
            success: function(data) {
                const resultados = estado ? data.resultados : data.resultados;
                exibirResultados(resultados);
            },
            error: function(xhr, status, error) {
                console.error('Erro:', error);
                $('#resultados-lista').html('<p>Erro ao carregar resultados.</p>');
            }
        });
    }
    
    function exibirResultados(resultados) {
        if (!resultados || resultados.length === 0) {
            $('#resultados-lista').html('<p>Nenhum resultado encontrado.</p>');
            return;
        }
        
        // Agrupar por loteria e horário
        const grupos = {};
        resultados.forEach(r => {
            const chave = `${r.loteria}_${r.horario}`;
            if (!grupos[chave]) {
                grupos[chave] = {
                    loteria: r.loteria,
                    horario: r.horario,
                    estado: r.estado,
                    resultados: []
                };
            }
            grupos[chave].resultados.push(r);
        });
        
        let html = '';
        Object.values(grupos).forEach(grupo => {
            grupo.resultados.sort((a, b) => a.posicao - b.posicao);
            
            html += `
                <div class="grupo-resultado">
                    <h3>${grupo.loteria} - ${grupo.horario} <span class="estado-badge">${grupo.estado}</span></h3>
                    <div class="resultados-grid">
            `;
            
            grupo.resultados.forEach(r => {
                html += `
                    <div class="resultado-item">
                        <span class="posicao">${r.colocacao}</span>
                        <span class="numero">${r.numero}</span>
                        <span class="animal">${r.animal}</span>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        $('#resultados-lista').html(html);
    }
    
    // Carregar inicialmente
    carregarResultados();
    
    // Atualizar a cada 60 segundos
    setInterval(() => {
        const estado = $('#filtro-estado').val() || '';
        carregarResultados(estado);
    }, 60000);
    
    // Filtro por estado
    $('#filtro-estado').on('change', function() {
        const estado = $(this).val() || '';
        carregarResultados(estado);
    });
});
```

---

## 💻 Exemplo 3: React (se usar React)

```jsx
import React, { useState, useEffect } from 'react';

const API_URL = 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados';

function Resultados() {
    const [resultados, setResultados] = useState([]);
    const [estado, setEstado] = useState('');
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        carregarResultados();
        
        // Atualizar a cada 60 segundos
        const interval = setInterval(carregarResultados, 60000);
        return () => clearInterval(interval);
    }, [estado]);
    
    async function carregarResultados() {
        setLoading(true);
        try {
            const url = estado 
                ? `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${estado}`
                : API_URL;
            
            const response = await fetch(url);
            const data = await response.json();
            setResultados(data.resultados || []);
        } catch (error) {
            console.error('Erro:', error);
        } finally {
            setLoading(false);
        }
    }
    
    function agruparResultados() {
        const grupos = {};
        resultados.forEach(r => {
            const chave = `${r.loteria}_${r.horario}`;
            if (!grupos[chave]) {
                grupos[chave] = {
                    loteria: r.loteria,
                    horario: r.horario,
                    estado: r.estado,
                    resultados: []
                };
            }
            grupos[chave].resultados.push(r);
        });
        return Object.values(grupos);
    }
    
    if (loading) {
        return <div>Carregando resultados...</div>;
    }
    
    const grupos = agruparResultados();
    
    return (
        <div className="resultados-container">
            <h2>Resultados</h2>
            
            <select 
                value={estado} 
                onChange={(e) => setEstado(e.target.value)}
                className="filtro-estado"
            >
                <option value="">Todos os estados</option>
                <option value="RJ">Rio de Janeiro</option>
                <option value="SP">São Paulo</option>
                <option value="GO">Goiás</option>
                <option value="BA">Bahia</option>
                <option value="PB">Paraíba</option>
                <option value="CE">Ceará</option>
                <option value="BR">Nacional</option>
            </select>
            
            {grupos.map((grupo, idx) => (
                <div key={idx} className="grupo-resultado">
                    <h3>
                        {grupo.loteria} - {grupo.horario}
                        <span className="estado-badge">{grupo.estado}</span>
                    </h3>
                    <div className="resultados-grid">
                        {grupo.resultados
                            .sort((a, b) => a.posicao - b.posicao)
                            .map((r, idx2) => (
                                <div key={idx2} className="resultado-item">
                                    <span className="posicao">{r.colocacao}</span>
                                    <span className="numero">{r.numero}</span>
                                    <span className="animal">{r.animal}</span>
                                </div>
                            ))}
                    </div>
                </div>
            ))}
        </div>
    );
}

export default Resultados;
```

---

## 💻 Exemplo 4: Vue.js (se usar Vue)

```vue
<template>
    <div class="resultados-container">
        <h2>Resultados</h2>
        
        <select v-model="estado" @change="carregarResultados" class="filtro-estado">
            <option value="">Todos os estados</option>
            <option value="RJ">Rio de Janeiro</option>
            <option value="SP">São Paulo</option>
            <option value="GO">Goiás</option>
            <option value="BA">Bahia</option>
            <option value="PB">Paraíba</option>
            <option value="CE">Ceará</option>
            <option value="BR">Nacional</option>
        </select>
        
        <div v-if="loading">Carregando...</div>
        
        <div v-for="grupo in grupos" :key="grupo.chave" class="grupo-resultado">
            <h3>
                {{ grupo.loteria }} - {{ grupo.horario }}
                <span class="estado-badge">{{ grupo.estado }}</span>
            </h3>
            <div class="resultados-grid">
                <div 
                    v-for="r in grupo.resultados" 
                    :key="r.numero + r.animal"
                    class="resultado-item"
                >
                    <span class="posicao">{{ r.colocacao }}</span>
                    <span class="numero">{{ r.numero }}</span>
                    <span class="animal">{{ r.animal }}</span>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            resultados: [],
            estado: '',
            loading: false
        };
    },
    computed: {
        grupos() {
            const grupos = {};
            this.resultados.forEach(r => {
                const chave = `${r.loteria}_${r.horario}`;
                if (!grupos[chave]) {
                    grupos[chave] = {
                        chave,
                        loteria: r.loteria,
                        horario: r.horario,
                        estado: r.estado,
                        resultados: []
                    };
                }
                grupos[chave].resultados.push(r);
            });
            
            return Object.values(grupos).map(g => ({
                ...g,
                resultados: g.resultados.sort((a, b) => a.posicao - b.posicao)
            }));
        }
    },
    mounted() {
        this.carregarResultados();
        setInterval(this.carregarResultados, 60000);
    },
    methods: {
        async carregarResultados() {
            this.loading = true;
            try {
                const url = this.estado
                    ? `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/estado/${this.estado}`
                    : 'https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados';
                
                const response = await fetch(url);
                const data = await response.json();
                this.resultados = data.resultados || [];
            } catch (error) {
                console.error('Erro:', error);
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

---

## 📱 Exemplo 5: Integração Simples (Código Mínimo)

Se você só quer exibir os resultados sem filtros:

```html
<div id="resultados"></div>

<script>
async function mostrarResultados() {
    const response = await fetch('https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados');
    const data = await response.json();
    const resultados = data.resultados || [];
    
    // Agrupar por loteria e horário
    const grupos = {};
    resultados.forEach(r => {
        const chave = `${r.loteria}_${r.horario}`;
        if (!grupos[chave]) grupos[chave] = [];
        grupos[chave].push(r);
    });
    
    let html = '';
    Object.entries(grupos).forEach(([chave, grupo]) => {
        const [loteria, horario] = chave.split('_');
        html += `<h3>${loteria} - ${horario}</h3>`;
        grupo.sort((a, b) => a.posicao - b.posicao).forEach(r => {
            html += `<p>${r.colocacao} - ${r.numero} ${r.animal}</p>`;
        });
    });
    
    document.getElementById('resultados').innerHTML = html;
}

// Carregar e atualizar a cada 60s
mostrarResultados();
setInterval(mostrarResultados, 60000);
</script>
```

---

## 🎨 Estilos CSS Adicionais (Opcional)

```css
/* Tema escuro */
.dark-theme .grupo-resultado {
    background: #1a1a1a;
    border-color: #333;
    color: #fff;
}

.dark-theme .resultado-item {
    background: #2a2a2a;
    border-color: #444;
}

/* Animação ao carregar */
.resultado-item {
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Responsivo */
@media (max-width: 768px) {
    .resultados-grid {
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    }
}
```

---

## ✅ Checklist de Integração

1. [ ] Adicionar código JavaScript na aba de resultados
2. [ ] Testar carregamento inicial
3. [ ] Testar atualização automática (60s)
4. [ ] Testar filtros (se implementados)
5. [ ] Ajustar estilos CSS conforme design do site
6. [ ] Testar em diferentes navegadores
7. [ ] Testar em dispositivos móveis

---

## 🔧 Solução de Problemas

### Erro CORS
Se aparecer erro de CORS, a API já está configurada com CORS. Se ainda assim houver problema, use um proxy ou contate o suporte.

### Resultados não aparecem
- Verifique o console do navegador (F12) para erros
- Teste a URL da API diretamente no navegador
- Verifique se a API está online

### Atualização não funciona
- Verifique se `setInterval` está configurado
- Verifique se não há erros no console

---

✅ **Pronto para integrar!** Escolha o exemplo que melhor se adapta ao seu site.

