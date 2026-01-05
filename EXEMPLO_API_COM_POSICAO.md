# 📊 Exemplo: API com Posição dos Bichos

## ✅ O Que Foi Adicionado

Agora a API retorna a **posição/colocação** de cada animal nos resultados:

```json
{
  "numero": "9498",
  "animal": "Vaca",
  "loteria": "Look Goiás",
  "horario": "11:20",
  "posicao": 1,
  "colocacao": "1°",
  "data_extracao": "05/01/2026",
  "timestamp": "2026-01-05T17:00:23.142170"
}
```

## 🔍 Campos Adicionados

- **`posicao`**: Número da posição (1, 2, 3, ...)
- **`colocacao`**: Texto formatado ("1°", "2°", "3°", ...)

A posição é calculada **dentro de cada grupo** (loteria + horário).

---

## 📡 Exemplo de Uso da API

### Buscar Resultados com Posição

```bash
curl http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados
```

### Resposta Exemplo

```json
{
  "resultados": [
    {
      "numero": "9498",
      "animal": "Vaca",
      "loteria": "Look Goiás",
      "horario": "11:20",
      "posicao": 1,
      "colocacao": "1°",
      "data_extracao": "05/01/2026",
      "timestamp": "2026-01-05T17:00:23.142170"
    },
    {
      "numero": "4845",
      "animal": "Elefante",
      "loteria": "Look Goiás",
      "horario": "11:20",
      "posicao": 2,
      "colocacao": "2°",
      "data_extracao": "05/01/2026",
      "timestamp": "2026-01-05T17:00:23.142255"
    }
  ]
}
```

---

## 💻 Exemplo em PHP

```php
<?php
function buscarResultadosComPosicao() {
    $url = 'http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados';
    
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    
    $response = curl_exec($ch);
    curl_close($ch);
    
    $data = json_decode($response, true);
    return $data['resultados'] ?? [];
}

// Buscar resultados
$resultados = buscarResultadosComPosicao();

// Filtrar por loteria e horário
$look_1120 = array_filter($resultados, function($r) {
    return $r['loteria'] === 'Look Goiás' && $r['horario'] === '11:20';
});

// Ordenar por posição
usort($look_1120, function($a, $b) {
    return $a['posicao'] <=> $b['posicao'];
});

// Exibir
foreach ($look_1120 as $r) {
    echo "{$r['colocacao']} - {$r['numero']} {$r['animal']}\n";
}
?>
```

---

## 🎮 Exemplo em JavaScript (Frontend)

```javascript
async function buscarResultadosComPosicao() {
    const response = await fetch('http://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados');
    const data = await response.json();
    
    return data.resultados;
}

// Filtrar e exibir
async function exibirResultadosLook1120() {
    const resultados = await buscarResultadosComPosicao();
    
    // Filtrar LOOK 11:20
    const look1120 = resultados.filter(r => 
        r.loteria === 'Look Goiás' && r.horario === '11:20'
    );
    
    // Ordenar por posição
    look1120.sort((a, b) => a.posicao - b.posicao);
    
    // Exibir
    look1120.forEach(r => {
        console.log(`${r.colocacao} - ${r.numero} ${r.animal}`);
    });
    
    return look1120;
}
```

---

## 🔍 Verificar Posição de um Animal Específico

```php
<?php
function verificarPosicaoAnimal($loteria, $horario, $animal) {
    $resultados = buscarResultadosComPosicao();
    
    foreach ($resultados as $r) {
        if ($r['loteria'] === $loteria 
            && $r['horario'] === $horario 
            && $r['animal'] === $animal) {
            return [
                'posicao' => $r['posicao'],
                'colocacao' => $r['colocacao'],
                'numero' => $r['numero']
            ];
        }
    }
    
    return null;
}

// Exemplo: Verificar posição de Avestruz em LOOK 11:20
$posicao = verificarPosicaoAnimal('Look Goiás', '11:20', 'Avestruz');
if ($posicao) {
    echo "Avestruz está na {$posicao['colocacao']} posição (número {$posicao['numero']})";
} else {
    echo "Avestruz não encontrado em LOOK 11:20";
}
?>
```

---

## 💰 Liquidar Aposta com Posição

```php
<?php
function liquidarApostaComPosicao($aposta) {
    $resultados = buscarResultadosComPosicao();
    
    // Buscar resultado correspondente
    $resultado = null;
    foreach ($resultados as $r) {
        if ($r['loteria'] === $aposta['loteria'] 
            && $r['horario'] === $aposta['horario']) {
            $resultado = $r;
            break;
        }
    }
    
    if (!$resultado) {
        return ['status' => 'pendente', 'mensagem' => 'Resultado não disponível'];
    }
    
    // Verificar se ganhou baseado na posição
    $ganhou = false;
    
    if ($aposta['tipo'] === 'animal_colocacao') {
        // Aposta em animal + colocação específica
        $ganhou = ($resultado['animal'] === $aposta['palpite'] 
                   && $resultado['posicao'] === $aposta['colocacao_esperada']);
    } elseif ($aposta['tipo'] === 'animal') {
        // Aposta apenas em animal (qualquer posição)
        $ganhou = ($resultado['animal'] === $aposta['palpite']);
    }
    
    return [
        'status' => $ganhou ? 'ganhou' : 'perdeu',
        'posicao_resultado' => $resultado['posicao'],
        'colocacao_resultado' => $resultado['colocacao'],
        'animal_resultado' => $resultado['animal'],
        'numero_resultado' => $resultado['numero']
    ];
}

// Exemplo: Liquidar aposta #338 (Avestruz 1° em LOOK 11:20)
$aposta = [
    'id' => 338,
    'loteria' => 'Look Goiás',
    'horario' => '11:20',
    'palpite' => 'Avestruz',
    'tipo' => 'animal_colocacao',
    'colocacao_esperada' => 1
];

$liquidacao = liquidarApostaComPosicao($aposta);
print_r($liquidacao);
?>
```

---

## 📋 Resumo

Agora a API retorna:

✅ **`posicao`**: Número da posição (1, 2, 3...)  
✅ **`colocacao`**: Texto formatado ("1°", "2°", "3°"...)

A posição é calculada **dentro de cada grupo** (loteria + horário), então:
- LOOK 11:20 tem posições 1, 2, 3, ...
- LOOK 09:20 tem suas próprias posições 1, 2, 3, ...
- PT Rio 11:30 tem suas próprias posições 1, 2, 3, ...

---

## 🚀 Próximos Passos

1. **Fazer redeploy no Coolify** para aplicar as mudanças
2. **Testar a API** e verificar se `posicao` e `colocacao` aparecem
3. **Integrar no seu sistema** usando os exemplos acima

Pronto! Agora a API retorna a posição dos bichos! 🎯

