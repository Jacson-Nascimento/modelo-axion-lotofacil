# Registro de Evidencias - Modelo Axion Lotofacil v1.2

**Autor:** Jacson Cruz do Nascimento  
**Projeto:** Modelo Axion Lotofacil  
**Versao:** v1.2  
**Data:** 2026-08-19

Este registro define as evidencias que devem ser atualizadas a cada rodada operacional do modelo.

## Decisao arquivistica v1.2

A versao v1.2 adota pacote arquivistico leve. O artefato final deve preservar:

- a base historica normalizada validada;
- o registro de fonte da CAIXA;
- o hash SHA-256 da planilha bruta efetivamente baixada;
- os outputs, graficos, relatorio de execucao e checksums.

A planilha bruta `data/raw/lotofacil_historico.xlsx` nao precisa ser anexada ao artefato final, desde que sua fonte e seu hash estejam documentados.

## Evidencias de entrada

| Evidencia | Arquivo esperado | Situacao |
|---|---|---|
| Base historica bruta | `data/raw/lotofacil_historico.xlsx` | Baixada pela rotina Python quando ausente; nao arquivada no pacote leve |
| Registro de fonte | `data/raw/SOURCE_CAIXA.md` | Gerado pela rotina Python e preservado no artefato |
| Hash da base bruta | `checksums/CHECKSUMS.sha256` | Preservado no artefato |
| Dicionario da base | `data/README.md` | Mantido neste pacote |
| Parametros de execucao | `python/run_all.py` | Mantido neste pacote |
| Pacotes do ambiente | `environment/python-requirements.txt` | Mantido neste pacote |

## Evidencias de processamento

| Evidencia | Arquivo esperado | Finalidade |
|---|---|---|
| Base normalizada | `data/processed/lotofacil_historico_normalizado.csv` | Trilha da importacao validada |
| Estatisticas das dezenas | `outputs/estatisticas_dezenas_v12.csv` | Frequencia, atraso e pesos |
| Diagnostico dos filtros | `outputs/diagnostico_filtros_v12.csv` | Trilha de eliminacao |
| Top residual | `outputs/top_residual_v12.csv` | Combinacoes ranqueadas |
| Jogos finais | `outputs/jogos_final_v12.csv` | Carteira final selecionada |
| Metricas do conjunto | `outputs/metricas_conjunto_final_v12.csv` | Cobertura e entropia do conjunto |
| Simulacao Monte Carlo | `outputs/simulacao_monte_carlo_v12.csv` | Referencia aleatoria uniforme |
| Resumo da simulacao | `outputs/resumo_simulacao_v12.csv` | Estatisticas descritivas da simulacao |

## Evidencias visuais

| Evidencia | Arquivo esperado |
|---|---|
| Frequencia das dezenas | `figures/grafico_frequencia_dezenas_v12.png` |
| Score do espaco residual | `figures/grafico_score_residual_v12.png` |

## Evidencias de integridade

| Evidencia | Arquivo esperado |
|---|---|
| Relatorio da execucao | `outputs/relatorio_execucao_v12.txt` |
| Hashes de entrada e saida | `checksums/CHECKSUMS.sha256` |
| Protocolo de reproducao | `REPRODUCIBILITY.md` |
| Metadados de citacao | `CITATION.cff` |

## Estado operacional da PR

A PR prepara o pipeline para execucao local e no GitHub Actions. As evidencias finais de saida, figuras e checksums devem ser preservadas a partir de rodada validada com a base historica baixada pela rotina operacional ou fornecida de modo documentado.

## Nota sobre implementacoes

A versao Python e a rotina operacional principal para GitHub Actions. Os scripts R permanecem preservados como referencia metodologica e historica.

## Regra de atualizacao

Toda alteracao substantiva em parametros, filtros, base historica, pesos ou criterio de score deve gerar nova rodada de saidas, novo relatorio de execucao e novos hashes.
