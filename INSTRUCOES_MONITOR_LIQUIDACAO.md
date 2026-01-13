# 📘 Instruções para Monitorar Resultados e Liquidar Apostas

Referência do monitor Bicho Certo em produção: `https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/`

## Endpoints disponíveis
- `GET /api/resultados` — lista completa de resultados.
- `GET /api/resultados/por-estado` — resultados agrupados por UF.
- `GET /api/resultados/estado/<UF>` — resultados apenas de uma UF.
- `GET /api/status` — status do monitor.
- `POST /api/verificar-agora` — força coleta imediata antes de liquidar.
- Arquivos diretos: `/resultados.json` (Bicho Certo), `/resultados_deunoposte.json` (se estiver servindo o segundo monitor).

## Campos principais retornados
- `loteria`, `estado`, `horario`
- `numero`, `animal`
- `posicao` (inteiro) e `colocacao` (ex.: `"1°"`)
- `data_extração` (DD/MM/YYYY) e `timestamp` (ISO)
- `fonte`, `url_origem` e `texto_completo` (para auditoria)

## Fluxo recomendado para exibição
1) Usar `GET /api/resultados` para painel geral.
2) Para separar por UF, usar `GET /api/resultados/por-estado`.
3) Para páginas específicas de UF, usar `GET /api/resultados/estado/<UF>`.
4) Ordenar cada grupo por `posicao` (1°, 2°, 3°…) ao exibir.

## Fluxo recomendado para liquidação de apostas
1) Agenda/cron dispara logo após cada horário de concurso.
2) Chamar `POST /api/verificar-agora` (opcional, para garantir coleta fresca).
3) Chamar `GET /api/resultados` e filtrar apenas concursos ainda não liquidados.
4) Normalizar chave do concurso: `(loteria, estado, horario, data_extração)`.
5) Garantir idempotência: manter tabela de liquidações com essa chave; se já liquidado, não repetir.
6) Liquidar usando o 1º prêmio (ou todas as posições, conforme regra do produto). Usar `posicao`/`colocacao` para escolher.
7) Registrar auditoria: `numero`, `animal`, `posicao`, `timestamp`, `fonte`, `url_origem`.

### Boas práticas de idempotência
- Armazene um `hash_concurso = sha1(loteria + estado + horario + data_extração)` como chave única.
- Marque `status_liquidado` na primeira liquidação bem-sucedida.
- Rejeite ou ignore novas liquidações com o mesmo hash.

## Mapeamento de estados
O monitor preenche `estado` automaticamente a partir do nome da loteria. Novas loterias devem ser incluídas em `MAPEAMENTO_ESTADO` em `monitor_selenium.py`. Se não houver match, volta `BR` (nacional).

## Exemplos rápidos (curl)
```bash
curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados | jq '.resultados[0]'

curl https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/resultados/por-estado \
  | jq '.por_estado.RJ[0]'

curl -X POST https://okgkgswwkk8ows0csow0c4gg.agenciamidas.com/api/verificar-agora
```

## Check de saúde antes de liquidar
- `GET /api/status` deve indicar `monitor_rodando: true`.
- Falha no status → pausar liquidação e alertar.

## Integração com múltiplas fontes
- Se também usar Deu no Poste, combine ou mantenha separado; preserve `loteria` e `estado` para que as regras de liquidação diferenciem concursos.
- Ao unir fontes, sempre recalcular a chave do concurso considerando `fonte` se existirem loterias homônimas com regras distintas.

## Log e auditoria
- Salve o payload do endpoint na hora da liquidação.
- Guarde horário da coleta e ID do job/cron que liquidou.

