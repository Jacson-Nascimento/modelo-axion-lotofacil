# Registro de evidencias - Modelo Axion Lotofacil v1.2

**Autor:** Jacson Cruz do Nascimento  
**Projeto:** Modelo Axion Lotofacil  
**Versao operacional:** 1.2  
**Data-base documental:** 27 de abril de 2026

Este registro define as evidencias minimas para classificar uma execucao do Modelo Axion Lotofacil v1.2 como auditavel e reprodutivel.

## 1. Evidencias de entrada

| Evidencia | Arquivo esperado | Situacao |
|---|---|---|
| Base historica bruta | `data/raw/lotofacil_historico.xlsx` | pendente de inclusao |
| Descricao da base | `data/raw/README.md` | criado |
| Lista de pacotes | `environment/R-packages.txt` | criado |
| Configuracao do modelo | `R/00_config.R` | criado |

## 2. Evidencias de processamento

| Evidencia | Arquivo esperado | Situacao |
|---|---|---|
| Ponto unico de execucao | `run_all.R` | criado |
| Importacao e validacao | `R/02_importacao_validacao.R` | criado |
| Metricas historicas | `R/03_metricas_historicas.R` | criado |
| Geracao de candidatos e residual | `R/04_candidatos_residual.R` | criado |
| Selecao, simulacao e relatorio | `R/05_selecao_validacao_relatorio.R` | criado |
| Script standalone de referencia | `R/Framework_Axion_Lotofacil_v1_2_standalone.R` | criado |
| Workflow manual | `.github/workflows/lotofacil-v12-reproducibility.yml` | criado |

## 3. Evidencias de saida

| Evidencia | Arquivo esperado | Situacao |
|---|---|---|
| Estatisticas das dezenas | `outputs/estatisticas_dezenas_v12.csv` | pendente de execucao |
| Diagnostico dos filtros | `outputs/diagnostico_filtros_v12.csv` | pendente de execucao |
| Espaco residual ranqueado | `outputs/top_residual_v12.csv` | pendente de execucao |
| Jogos finais | `outputs/jogos_final_v12.csv` | pendente de execucao |
| Metricas do conjunto final | `outputs/metricas_conjunto_final_v12.csv` | pendente de execucao |
| Simulacao Monte Carlo | `outputs/simulacao_monte_carlo_v12.csv` | pendente de execucao |
| Resumo da simulacao | `outputs/resumo_simulacao_v12.csv` | pendente de execucao |
| Relatorio de execucao | `outputs/relatorio_execucao_v12.txt` | pendente de execucao |
| Graficos | `figures/*.png` | pendente de execucao |
| Checksums | `checksums/CHECKSUMS.sha256` | pendente apos execucao |

## 4. Criterio de aceite

A versao operacional pode ser considerada pronta para release e deposito atualizado no Zenodo somente quando:

1. a base historica oficial estiver identificada;
2. `Rscript run_all.R` executar sem erro;
3. todos os arquivos de saida forem gerados;
4. os resultados principais forem descritos no relatorio de execucao;
5. os checksums forem calculados;
6. o README e o protocolo de reprodutibilidade forem revisados contra as evidencias finais.

## 5. Observacao metodologica

O projeto registra um metodo de exploracao estatistica e combinatoria. Ele nao constitui recomendacao financeira, garantia de premiacao ou demonstracao de vantagem preditiva contra sorteios regulares.
