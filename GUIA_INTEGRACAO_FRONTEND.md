# 🎮 Guia de Integração - Jogo do Bicho Online

## 📋 O Que Você Precisa Fazer

### 1. **Configurar Backend (API de Apostas)**

#### Opção A: Usar API Separada (Recomendado)
- Rode `app_apostas.py` na porta 5001
- Mantém separado do monitor de resultados

#### Opção B: Integrar no app_vps.py Existente
- Adicionar rotas de apostas no `app_vps.py`
- Tudo em um único servidor

### 2. **Conectar Frontend com API**

#### JavaScript/React/Vue

```javascript
// config.js - Configuração da API
const API_URL = 'http://seu-servidor:5001/api';

// api.js - Funções de API
class ApostasAPI {
  // Criar aposta
  static async criarAposta(aposta) {
    const response = await fetch(`${API_URL}/apostas`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}` // Se usar auth
      },
      body: JSON.stringify(aposta)
    });
    return response.json();
  }

  // Consultar saldo
  static async consultarSaldo(usuarioId) {
    const response = await fetch(`${API_URL}/usuarios/${usuarioId}/saldo`);
    return response.json();
  }

  // Listar apostas do usuário
  static async listarApostas(usuarioId) {
    const response = await fetch(`${API_URL}/apostas/usuario/${usuarioId}`);
    return response.json();
  }

  // Listar resultados
  static async listarResultados() {
    const response = await fetch(`${API_URL}/resultados`);
    return response.json();
  }
}
```

### 3. **Modificar Tela de Apostas**

#### Antes (sem integração):
```javascript
// Código antigo - apenas salva localmente
function fazerAposta(numero, animal, valor) {
  // Salva no localStorage ou banco local
  localStorage.setItem('aposta', JSON.stringify({numero, animal, valor}));
}
```

#### Depois (com integração):
```javascript
// Código novo - integra com API
async function fazerAposta(numero, animal, valor, loteria, horario) {
  try {
    // Pegar ID do usuário logado
    const usuarioId = getUsuarioLogado().id;
    
    // Criar aposta via API
    const resultado = await ApostasAPI.criarAposta({
      usuario_id: usuarioId,
      numero: numero,
      animal: animal,
      valor: valor,
      loteria: loteria,
      horario: horario
    });
    
    if (resultado.sucesso) {
      // Atualizar saldo na tela
      await atualizarSaldo();
      
      // Mostrar mensagem de sucesso
      mostrarMensagem('Aposta criada com sucesso!');
      
      // Atualizar lista de apostas
      await carregarApostas();
    } else {
      mostrarErro(resultado.erro);
    }
  } catch (error) {
    mostrarErro('Erro ao criar aposta: ' + error.message);
  }
}
```

### 4. **Exibir Resultados em Tempo Real**

#### Componente de Resultados (React exemplo):

```jsx
import React, { useState, useEffect } from 'react';

function ResultadosTempoReal() {
  const [resultados, setResultados] = useState([]);
  const [apostas, setApostas] = useState([]);

  useEffect(() => {
    // Carregar resultados iniciais
    carregarResultados();
    carregarApostas();

    // Atualizar a cada 30 segundos
    const interval = setInterval(() => {
      carregarResultados();
      carregarApostas();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  async function carregarResultados() {
    const data = await ApostasAPI.listarResultados();
    setResultados(data.resultados || []);
  }

  async function carregarApostas() {
    const usuarioId = getUsuarioLogado().id;
    const data = await ApostasAPI.listarApostas(usuarioId);
    setApostas(data.apostas || []);
  }

  // Verificar se aposta ganhou
  function verificarAposta(aposta, resultado) {
    if (aposta.loteria === resultado.loteria && 
        aposta.horario === resultado.horario) {
      if (aposta.numero === resultado.numero || 
          aposta.animal === resultado.animal) {
        return 'ganhou';
      }
      return 'perdeu';
    }
    return 'pendente';
  }

  return (
    <div>
      <h2>Resultados em Tempo Real</h2>
      {resultados.map(resultado => (
        <div key={resultado.id}>
          <h3>{resultado.loteria} - {resultado.horario}</h3>
          <p>Número: {resultado.numero} - {resultado.animal}</p>
          
          {/* Mostrar status das apostas relacionadas */}
          {apostas
            .filter(a => a.loteria === resultado.loteria && 
                        a.horario === resultado.horario)
            .map(aposta => (
              <div key={aposta.id}>
                Sua aposta: {aposta.numero} {aposta.animal}
                Status: {aposta.status}
                {aposta.status === 'ganhou' && (
                  <span className="ganho">
                    Ganhou R$ {(aposta.valor * 18).toFixed(2)}!
                  </span>
                )}
              </div>
            ))}
        </div>
      ))}
    </div>
  );
}
```

### 5. **Atualizar Saldo Automaticamente**

```javascript
// Componente de Saldo
let saldoAtual = 0;

async function atualizarSaldo() {
  const usuarioId = getUsuarioLogado().id;
  const data = await ApostasAPI.consultarSaldo(usuarioId);
  saldoAtual = data.saldo;
  
  // Atualizar na tela
  document.getElementById('saldo').textContent = 
    `R$ ${saldoAtual.toFixed(2)}`;
}

// Atualizar a cada 10 segundos
setInterval(atualizarSaldo, 10000);
```

### 6. **Tela de Histórico de Apostas**

```javascript
async function carregarHistoricoApostas() {
  const usuarioId = getUsuarioLogado().id;
  const data = await ApostasAPI.listarApostas(usuarioId);
  
  // Agrupar por status
  const pendentes = data.apostas.filter(a => a.status === 'pendente');
  const ganhas = data.apostas.filter(a => a.status === 'ganhou');
  const perdidas = data.apostas.filter(a => a.status === 'perdeu');
  
  // Exibir na tela
  exibirApostas('pendentes', pendentes);
  exibirApostas('ganhas', ganhas);
  exibirApostas('perdidas', perdidas);
}
```

### 7. **Notificações de Ganhos**

```javascript
// Verificar ganhos periodicamente
async function verificarGanhos() {
  const usuarioId = getUsuarioLogado().id;
  const data = await ApostasAPI.listarApostas(usuarioId);
  
  // Buscar apostas que mudaram de status
  const novasGanhas = data.apostas.filter(
    a => a.status === 'ganhou' && 
         !apostasConhecidas.includes(a.id)
  );
  
  novasGanhas.forEach(aposta => {
    // Mostrar notificação
    mostrarNotificacao(
      `🎉 Você ganhou R$ ${(aposta.valor * 18).toFixed(2)}!`,
      'success'
    );
    
    // Atualizar saldo
    atualizarSaldo();
  });
  
  apostasConhecidas = data.apostas.map(a => a.id);
}

// Verificar a cada 5 segundos
setInterval(verificarGanhos, 5000);
```

## 🔧 Passo a Passo de Implementação

### Passo 1: Preparar Backend

```bash
# No servidor, iniciar API de apostas
python3 app_apostas.py --monitor --intervalo 60 --port 5001
```

### Passo 2: Criar Usuários (Inicial)

```python
# script_criar_usuario.py
from sistema_liquidacao import SistemaLiquidacao
from models import Usuario

sistema = SistemaLiquidacao()

session = sistema.Session()
usuario = Usuario(
    nome="Usuário Teste",
    email="teste@exemplo.com",
    saldo=100.0
)
session.add(usuario)
session.commit()
print(f"Usuário criado: ID {usuario.id}")
```

### Passo 3: Modificar Frontend

1. **Adicionar arquivo `api.js`** com funções de API
2. **Modificar tela de apostas** para usar API
3. **Adicionar componente de resultados** em tempo real
4. **Atualizar exibição de saldo** para consultar API
5. **Adicionar histórico de apostas**

### Passo 4: Testar Integração

```javascript
// Teste rápido no console do navegador
const teste = async () => {
  // Criar aposta de teste
  const aposta = await ApostasAPI.criarAposta({
    usuario_id: 1,
    numero: '1234',
    animal: 'Cavalo',
    valor: 10.0,
    loteria: 'PT Rio de Janeiro',
    horario: '11:00'
  });
  console.log('Aposta criada:', aposta);
  
  // Consultar saldo
  const saldo = await ApostasAPI.consultarSaldo(1);
  console.log('Saldo:', saldo);
};
```

## 📱 Exemplo Completo - Tela de Apostas

```html
<!DOCTYPE html>
<html>
<head>
    <title>Jogo do Bicho - Apostas</title>
</head>
<body>
    <div id="app">
        <h1>🎰 Jogo do Bicho</h1>
        
        <!-- Saldo -->
        <div id="saldo">
            Saldo: R$ <span id="saldo-valor">0.00</span>
        </div>
        
        <!-- Formulário de Aposta -->
        <form id="form-aposta">
            <input type="text" id="numero" placeholder="Número (4 dígitos)" maxlength="4">
            <select id="animal">
                <option value="Avestruz">Avestruz</option>
                <option value="Águia">Águia</option>
                <!-- ... outros animais ... -->
            </select>
            <input type="number" id="valor" placeholder="Valor" step="0.01" min="1">
            <select id="loteria">
                <option value="PT Rio de Janeiro">PT Rio de Janeiro</option>
                <option value="Look Goiás">Look Goiás</option>
                <!-- ... outras loterias ... -->
            </select>
            <select id="horario">
                <option value="09:00">09:00</option>
                <option value="11:00">11:00</option>
                <!-- ... outros horários ... -->
            </select>
            <button type="submit">Apostar</button>
        </form>
        
        <!-- Resultados -->
        <div id="resultados"></div>
        
        <!-- Minhas Apostas -->
        <div id="minhas-apostas"></div>
    </div>

    <script src="api.js"></script>
    <script>
        const usuarioId = 1; // Pegar do sistema de autenticação
        
        // Atualizar saldo
        async function atualizarSaldo() {
            const data = await ApostasAPI.consultarSaldo(usuarioId);
            document.getElementById('saldo-valor').textContent = 
                data.saldo.toFixed(2);
        }
        
        // Fazer aposta
        document.getElementById('form-aposta').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const aposta = {
                usuario_id: usuarioId,
                numero: document.getElementById('numero').value,
                animal: document.getElementById('animal').value,
                valor: parseFloat(document.getElementById('valor').value),
                loteria: document.getElementById('loteria').value,
                horario: document.getElementById('horario').value
            };
            
            const resultado = await ApostasAPI.criarAposta(aposta);
            
            if (resultado.sucesso) {
                alert('Aposta criada com sucesso!');
                atualizarSaldo();
                carregarApostas();
            } else {
                alert('Erro: ' + resultado.erro);
            }
        });
        
        // Carregar apostas
        async function carregarApostas() {
            const data = await ApostasAPI.listarApostas(usuarioId);
            // Exibir na tela
            document.getElementById('minhas-apostas').innerHTML = 
                data.apostas.map(a => `
                    <div>
                        ${a.numero} ${a.animal} - R$ ${a.valor.toFixed(2)}
                        Status: ${a.status}
                    </div>
                `).join('');
        }
        
        // Carregar resultados
        async function carregarResultados() {
            const data = await ApostasAPI.listarResultados();
            // Exibir na tela
            document.getElementById('resultados').innerHTML = 
                data.resultados.map(r => `
                    <div>
                        ${r.loteria} ${r.horario}: ${r.numero} ${r.animal}
                    </div>
                `).join('');
        }
        
        // Inicializar
        atualizarSaldo();
        carregarApostas();
        carregarResultados();
        
        // Atualizar a cada 30 segundos
        setInterval(() => {
            atualizarSaldo();
            carregarApostas();
            carregarResultados();
        }, 30000);
    </script>
</body>
</html>
```

## 🔐 Segurança (Importante!)

### 1. Autenticação

```javascript
// Adicionar token JWT nas requisições
headers: {
  'Authorization': `Bearer ${getToken()}`
}
```

### 2. Validação no Frontend

```javascript
function validarAposta(numero, animal, valor) {
  if (!numero || numero.length !== 4) {
    throw new Error('Número inválido');
  }
  if (valor < 1) {
    throw new Error('Valor mínimo: R$ 1,00');
  }
  if (saldoAtual < valor) {
    throw new Error('Saldo insuficiente');
  }
}
```

### 3. Rate Limiting

```javascript
// Limitar número de apostas por minuto
let ultimaAposta = 0;
const LIMITE_APOSTAS = 10; // por minuto

function podeApostar() {
  const agora = Date.now();
  if (agora - ultimaAposta < 60000 / LIMITE_APOSTAS) {
    return false;
  }
  ultimaAposta = agora;
  return true;
}
```

## ✅ Checklist de Implementação

- [ ] Backend rodando (`app_apostas.py`)
- [ ] Monitor ativo
- [ ] API testada (Postman/curl)
- [ ] Frontend conectado com API
- [ ] Tela de apostas modificada
- [ ] Saldo atualizando automaticamente
- [ ] Resultados em tempo real
- [ ] Histórico de apostas
- [ ] Notificações de ganhos
- [ ] Autenticação implementada
- [ ] Validações no frontend
- [ ] Testes completos

## 🚀 Próximos Passos

1. **Testar localmente** primeiro
2. **Criar usuários de teste**
3. **Fazer apostas de teste**
4. **Verificar liquidação automática**
5. **Integrar com seu sistema existente**
6. **Adicionar autenticação real**
7. **Implementar WebSocket** (opcional, para tempo real)

Precisa de ajuda com alguma parte específica da integração?

