# Inspeção dos Artefatos — Modelo Axion Lotofácil v1.2

**Autor:** Jacson Cruz do Nascimento  
**Projeto:** Modelo Axion Lotofácil  
**Data da inspeção:** 2026-08-19  
**Workflow:** lotofacil-v12-pr-validation  
**Run:** 32270708543  
**Artefato:** lotofacil-v12-pr-validation-artifacts  

## Resultado geral

O workflow foi executado com sucesso e gerou artefatos de reprodutibilidade contendo saídas, gráficos, checksums, base normalizada e proveniência da base CAIXA.

## Estrutura encontrada no ZIP

- checksums/CHECKSUMS.sha256
- checksums/CHECKSUMS_TEMPLATE.sha256
- checksums/README.md
- data/processed/README.md
- data/processed/lotofacil_historico_normalizado.csv
- data/raw/SOURCE_CAIXA.md
- figures/README.md
- figures/grafico_frequencia_dezenas_v12.png
- figures/grafico_score_residual_v12.png
- outputs/README.md
- outputs/diagnostico_filtros_v12.csv
- outputs/estatisticas_dezenas_v12.csv
- outputs/jogos_final_v12.csv
- outputs/metricas_conjunto_final_v12.csv
- outputs/relatorio_execucao_v12.txt
- outputs/resumo_simulacao_v12.csv
- outputs/simulacao_monte_carlo_v12.csv
- outputs/top_residual_v12.csv

## Evidências quantitativas

- Base normalizada: 3.596 concursos válidos e 16 colunas.
- Candidatos únicos gerados: 50.000.
- Espaço residual: 24.762 combinações.
- Top residual exportado: 1.000 combinações.
- Jogos finais selecionados: 25.
- Simulações Monte Carlo: 1.000.
- Checksums registrados: 15 linhas.
- Gráficos gerados: 2 PNGs, ambos com 1600 × 800 px.

## Métricas do conjunto final

| Métrica | Valor |
|---|---:|
| Número de jogos | 25 |
| Cobertura de dezenas | 25 |
| Overlap médio entre jogos | 9,6 |
| Overlap máximo entre jogos | 12 |
| Score médio | 0,807118 |
| Soma média | 195,04 |
| Entropia média das linhas | 0,990992 |

## Proveniência da base

- Fonte: Portal Loterias CAIXA.
- Endpoint: https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil
- Data/hora da execução registrada: 2026-08-19T15:33:15.
- SHA-256 da planilha bruta baixada: 3e905d86109511fbc1eb6da1dec4abdab4bae1453125c2a03a41af4ee5cdcb51.

## Decisão arquivística

A versão v1.2 adota pacote leve: preserva a base histórica normalizada, a fonte CAIXA, o hash SHA-256 da planilha bruta, outputs, figuras, relatório técnico e checksums. A planilha bruta baixada pela rotina operacional não é anexada ao pacote final.

## Conclusão

O pipeline Python executou com sucesso e produziu as evidências centrais esperadas. O pacote v1.2 está apto para consolidação como versão técnica reprodutível, observados os limites metodológicos descritos no relatório técnico.