// Função para atualizar resultados
async function atualizarResultados() {
    try {
        const response = await fetch('/api/resultados');
        const dados = await response.json();
        
        // Atualizar estatísticas
        document.getElementById('total-resultados').textContent = dados.total_resultados || dados.resultados.length;
        
        if (dados.ultima_verificacao) {
            const data = new Date(dados.ultima_verificacao);
            document.getElementById('ultima-verificacao').textContent = 
                data.toLocaleString('pt-BR', { 
                    day: '2-digit', 
                    month: '2-digit', 
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
        }
        
        // Atualizar grid de resultados
        atualizarGridResultados(dados.resultados);
        
        // Atualizar filtro de loterias
        atualizarFiltroLoterias(dados.resultados);
        
        // Mostrar notificação
        mostrarNotificacao('✅ Resultados atualizados!', 'success');
        
    } catch (error) {
        console.error('Erro ao atualizar:', error);
        mostrarNotificacao('❌ Erro ao atualizar resultados', 'error');
    }
}

        function atualizarGridResultados(resultados) {
            const container = document.getElementById('resultados-container');
            
            if (resultados.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <p>📭 Nenhum resultado encontrado ainda.</p>
                        <p>Execute o monitor para começar a coletar resultados.</p>
                    </div>
                `;
                return;
            }
            
            // Agrupar por loteria e horário
            const agrupados = {};
            resultados.forEach(r => {
                const chave = `${r.loteria}_${r.horario || 'sem-horario'}`;
                if (!agrupados[chave]) {
                    agrupados[chave] = {
                        loteria: r.loteria,
                        horario: r.horario || 'N/A',
                        resultados: []
                    };
                }
                agrupados[chave].resultados.push(r);
            });
            
            // Ordenar grupos por loteria e horário
            const gruposOrdenados = Object.values(agrupados).sort((a, b) => {
                if (a.loteria !== b.loteria) {
                    return a.loteria.localeCompare(b.loteria);
                }
                return (b.horario || '').localeCompare(a.horario || '');
            });
            
            // Gerar HTML agrupado
            container.innerHTML = gruposOrdenados.map(grupo => {
                // Ordenar resultados do grupo por timestamp
                grupo.resultados.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
                
                const resultadosHTML = grupo.resultados.map(resultado => {
                    const data = new Date(resultado.timestamp);
                    const dataFormatada = data.toLocaleString('pt-BR', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    
                    return `
                        <div class="resultado-card" data-loteria="${resultado.loteria}">
                            <div class="card-body">
                                <div class="numero-resultado">${resultado.numero}</div>
                                <div class="animal-resultado">${resultado.animal}</div>
                            </div>
                            <div class="card-footer">
                                <small>${dataFormatada}</small>
                            </div>
                        </div>
                    `;
                }).join('');
                
                return `
                    <div class="tabela-grupo" data-loteria="${grupo.loteria}">
                        <div class="grupo-header">
                            <h3 class="grupo-titulo">${grupo.loteria}</h3>
                            <span class="grupo-horario">🕐 ${grupo.horario}</span>
                            <span class="grupo-count">${grupo.resultados.length} resultado(s)</span>
                        </div>
                        <div class="resultados-grid">
                            ${resultadosHTML}
                        </div>
                    </div>
                `;
            }).join('');
        }

function atualizarFiltroLoterias(resultados) {
    const select = document.getElementById('filtro-loteria');
    const loterias = [...new Set(resultados.map(r => r.loteria))].sort();
    
    // Manter a opção "Todas as Loterias"
    const todasOption = select.querySelector('option[value=""]');
    select.innerHTML = '';
    select.appendChild(todasOption);
    
    loterias.forEach(loteria => {
        const option = document.createElement('option');
        option.value = loteria;
        option.textContent = loteria;
        select.appendChild(option);
    });
}

        function filtrarPorLoteria() {
            const select = document.getElementById('filtro-loteria');
            const loteriaSelecionada = select.value;
            const grupos = document.querySelectorAll('.tabela-grupo');
            
            grupos.forEach(grupo => {
                if (!loteriaSelecionada || grupo.dataset.loteria === loteriaSelecionada) {
                    grupo.style.display = 'block';
                    grupo.style.animation = 'fadeIn 0.5s ease-in';
                } else {
                    grupo.style.display = 'none';
                }
            });
        }

async function mostrarEstatisticas() {
    try {
        const response = await fetch('/api/estatisticas');
        const stats = await response.json();
        
        const content = document.getElementById('estatisticas-content');
        
        let html = `
            <div class="stat-item">
                <h3>Total de Resultados</h3>
                <p class="stat-number">${stats.total}</p>
            </div>
            
            <div class="stat-item" style="margin-top: 30px;">
                <h3>Resultados por Loteria</h3>
                <ul style="list-style: none; padding: 0;">
        `;
        
        const loteriasOrdenadas = Object.entries(stats.por_loteria)
            .sort((a, b) => b[1] - a[1]);
        
        loteriasOrdenadas.forEach(([loteria, count]) => {
            html += `
                <li style="padding: 10px; margin: 5px 0; background: var(--border-color); border-radius: 6px;">
                    <strong>${loteria}</strong>: ${count} resultado(s)
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
            
            <div class="stat-item" style="margin-top: 30px;">
                <h3>Top 10 Animais Mais Frequentes</h3>
                <ul style="list-style: none; padding: 0;">
        `;
        
        Object.entries(stats.animais_mais_frequentes).forEach(([animal, count]) => {
            html += `
                <li style="padding: 10px; margin: 5px 0; background: var(--border-color); border-radius: 6px;">
                    <strong>${animal}</strong>: ${count} vez(es)
                </li>
            `;
        });
        
        html += `
                </ul>
            </div>
        `;
        
        content.innerHTML = html;
        document.getElementById('modal-estatisticas').style.display = 'block';
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        mostrarNotificacao('❌ Erro ao carregar estatísticas', 'error');
    }
}

function fecharModal() {
    document.getElementById('modal-estatisticas').style.display = 'none';
}

function mostrarNotificacao(mensagem, tipo) {
    // Criar elemento de notificação
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${tipo === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = mensagem;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('modal-estatisticas');
    if (event.target == modal) {
        fecharModal();
    }
}

// Atualizar automaticamente a cada 30 segundos
setInterval(atualizarResultados, 30000);

// Inicializar filtro de loterias ao carregar
document.addEventListener('DOMContentLoaded', function() {
    const resultados = {{ dados.resultados|tojson }};
    atualizarFiltroLoterias(resultados);
});

