# Registro de Evidencias - Modelo Axion Lotofacil v1.2

**Autor:** Jacson Cruz do Nascimento  
**Projeto:** Modelo Axion Lotofacil  
**Versao:** v1.2  
**Data:** 2026-08-19

Este registro define as evidencias que devem ser atualizadas a cada rodada operacional do modelo.

## Evidencias de entrada

| Evidencia | Arquivo esperado | Situacao |
|---|---|---|
| Base historica bruta | `data/raw/` | Atualizar com a base usada na rodada |
| Dicionario da base | `data/README.md` | Mantido neste pacote |
| Parametros de execucao | Script R principal | Mantido neste pacote |
| Pacotes do ambiente | `environment/R-packages.txt` | Mantido neste pacote |

## Evidencias de processamento

| Evidencia | Arquivo esperado | Finalidade |
|---|---|---|
| Estatisticas das dezenas | `estatisticas_dezenas_v12.csv` | Frequencia, atraso e pesos |
| Diagnostico dos filtros | `diagnostico_filtros_v12.csv` | Trilha de eliminacao |
| Top residual | `top_residual_v12.csv` | Combinacoes ranqueadas |
| Jogos finais | `jogos_final_v12.csv` | Carteira final selecionada |
| Metricas do conjunto | `metricas_conjunto_final_v12.csv` | Cobertura e entropia do conjunto |
| Simulacao Monte Carlo | `simulacao_monte_carlo_v12.csv` | Referencia aleatoria uniforme |
| Resumo da simulacao | `resumo_simulacao_v12.csv` | Intervalos e estatisticas da simulacao |

## Evidencias visuais

| Evidencia | Arquivo esperado |
|---|---|
| Frequencia das dezenas | `grafico_frequencia_dezenas_v12.png` |
| Score do espaco residual | `grafico_score_residual_v12.png` |

## Evidencias de integridade

| Evidencia | Arquivo esperado |
|---|---|
| Relatorio da execucao | `relatorio_execucao_v12.txt` |
| Hashes de entrada e saida | `checksums/CHECKSUMS.sha256` |
| Protocolo de reproducao | `REPRODUCIBILITY.md` |
| Metadados de citacao | `CITATION.cff` |

## Regra de atualizacao

Toda alteracao substantiva em parametros, filtros, base historica, pesos ou criterio de score deve gerar nova rodada de saidas, novo relatorio de execucao e novos hashes.
