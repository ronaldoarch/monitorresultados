# 📖 Livro dos Sonhos - Sistema de Palpites para Apostas

Sistema Python que interpreta sonhos e gera palpites para apostas no jogo do bicho.

## 🚀 Como Usar

### Iniciar o Servidor

**Opção 1: Usando o script de inicialização (Recomendado)**
```bash
./iniciar_livro_sonhos.sh
```

**Opção 2: Manualmente com ambiente virtual**
```bash
# Criar ambiente virtual (apenas na primeira vez)
python3 -m venv venv_livro_sonhos
source venv_livro_sonhos/bin/activate

# Instalar dependências (apenas na primeira vez)
pip install flask flask-cors

# Iniciar servidor
python3 app_livro_sonhos.py
```

**Opção 3: Com opções personalizadas**
```bash
source venv_livro_sonhos/bin/activate
python3 app_livro_sonhos.py --port 8082 --host 0.0.0.0
```

### Acessar o Painel

Abra seu navegador e acesse:
- **Painel Web**: http://localhost:8082/
- **API de Interpretação**: http://localhost:8082/api/interpretar
- **API de Sonhos Populares**: http://localhost:8082/api/sonhos-populares

## 📋 Funcionalidades

### 1. Interpretação de Sonhos
- Digite o sonho que você teve
- O sistema busca no dicionário de sonhos
- Retorna o animal, grupo e números correspondentes

### 2. Geração de Palpites
- **Grupo**: Número do grupo do animal (1-25)
- **Dezena**: Número de dezena sugerido
- **Centena**: Número de centena sugerido
- **Milhar**: Número de milhar sugerido

### 3. Sugestões de Dias e Horários
- Lista os próximos 7 dias para apostar
- Prioriza os próximos 3 dias como "alta prioridade"
- Sugere horários comuns de sorteios (09:00, 11:00, 14:00, 16:00, 18:00, 20:00)

## 🔌 API Endpoints

### POST /api/interpretar
Interpreta um sonho e retorna palpites.

**Request:**
```json
{
  "sonho": "leão"
}
```

**Response:**
```json
{
  "encontrado": true,
  "sonho_original": "leão",
  "animal": "Leão",
  "grupo": 16,
  "numeros": [61, 62, 63, 64],
  "significado": "Poder e liderança",
  "dezena": "61",
  "centena": "060",
  "milhar": "1500",
  "dias_sugeridos": [...],
  "horarios_sugeridos": [...]
}
```

### GET /api/sonhos-populares
Lista os sonhos mais populares do dicionário.

**Query Parameters:**
- `limite` (opcional): Número máximo de sonhos (padrão: 50)

### GET /api/buscar
Busca um sonho específico.

**Query Parameters:**
- `sonho`: O sonho a buscar

## 📚 Dicionário de Sonhos

O sistema inclui um dicionário completo com:
- **25 animais** do jogo do bicho
- **Objetos comuns** (água, dinheiro, ouro, casa, etc.)
- **Situações** (casamento, morte, criança, etc.)
- **Elementos** (fogo, sol, lua, estrela, etc.)

### Exemplos de Sonhos Suportados:
- Animais: leão, cobra, cavalo, cachorro, gato, etc.
- Objetos: dinheiro, ouro, casa, carro, barco, etc.
- Situações: casamento, morte, criança, etc.
- Elementos: água, fogo, sol, lua, chuva, etc.

## 🎨 Interface Web

O painel web inclui:
- Interface moderna e responsiva
- Campo para inserir o sonho
- Exibição de resultados com:
  - Animal e grupo
  - Números sugeridos (grupo, dezena, centena, milhar)
  - Dias sugeridos para apostar
  - Horários sugeridos
- Lista de sonhos populares para seleção rápida

## 🛠️ Estrutura do Projeto

```
.
├── app_livro_sonhos.py      # Aplicação Flask principal
├── livro_sonhos.py          # Sistema de interpretação de sonhos
└── README_LIVRO_SONHOS.md   # Este arquivo
```

## 📝 Notas Importantes

- O sistema é baseado em interpretações tradicionais do livro dos sonhos
- Os palpites são sugestões baseadas no sonho informado
- Sempre aposte com responsabilidade
- Os números são gerados automaticamente baseados no grupo do animal

## 🔧 Dependências

- Flask >= 3.0.0
- flask-cors

**Instalar dependências:**

O script `iniciar_livro_sonhos.sh` instala automaticamente as dependências. Se preferir instalar manualmente:

```bash
# Criar ambiente virtual
python3 -m venv venv_livro_sonhos
source venv_livro_sonhos/bin/activate

# Instalar dependências
pip install flask flask-cors
```

## 📄 Licença

Este projeto é fornecido "como está" para fins educacionais e de entretenimento.
