# Modelo Axion Lotofacil

**Autor:** Jacson Cruz do Nascimento  
**ORCID:** https://orcid.org/0009-0006-6535-9569  
**Local:** Brasilia, DF, Brasil  
**Versao operacional:** v1.2  
**Registro Zenodo da serie v1.0:** https://doi.org/10.5281/zenodo.21522330  
**Licenca:** CC BY 4.0, salvo indicacao diversa nos arquivos de dados de terceiros.

Este diretorio reune os artefatos tecnicos do **Modelo Axion Lotofacil**, um projeto experimental de modelagem combinatoria, exploracao estatistica, eliminacao de padroes, formacao de espaco residual, score multicriterio e validacao por simulacao no espaco da Lotofacil.

## Escopo

O projeto trabalha com resultados historicos da Lotofacil para auditar propriedades combinatorias e gerar carteiras de jogos com criterios rastreaveis. O modelo nao demonstra vantagem preditiva contra sorteio justo, nao constitui recomendacao financeira e nao oferece garantia de premiacao.

A contribuicao da versao v1.2 esta em transformar a serie documental anterior em um pacote operacional reprodutivel, com:

- importacao e validacao da base historica;
- calculo de frequencias, atrasos e metricas historicas;
- geracao ponderada de combinacoes candidatas;
- filtros combinatorios;
- formacao do espaco residual;
- score multicriterio;
- selecao final com controle de redundancia;
- simulacao Monte Carlo de referencia;
- exportacao de evidencias em CSV, TXT e PNG.

## Estrutura operacional

```text
lotofacil_axion/
├── README.md
├── REPRODUCIBILITY.md
├── CITATION.cff
├── LICENSE_NOTICE.md
├── ZENODO_RECORD.json
├── EVIDENCE_REGISTER.md
├── run_all.R
├── R/
│   ├── 00_config.R
│   ├── 01_pacotes_utilitarios.R
│   ├── 02_importacao_validacao.R
│   ├── 03_metricas_historicas.R
│   ├── 04_candidatos_residual.R
│   ├── 05_selecao_validacao_relatorio.R
│   └── Framework_Axion_Lotofacil_v1_2_standalone.R
├── data/
│   ├── README.md
│   ├── raw/README.md
│   └── processed/README.md
├── outputs/README.md
├── figures/README.md
├── checksums/README.md
└── environment/
    ├── README.md
    └── R-packages.txt
```

## Fonte de dados

A base historica deve conter uma linha por concurso e quinze colunas de dezenas sorteadas. A pagina oficial das Loterias CAIXA informa area de download de resultados da Lotofacil por ordem crescente. A base local usada em cada execucao deve ser registrada em `data/raw/` ou informada no objeto `config` do arquivo `R/00_config.R`.

## Execucao local

No diretorio `lotofacil_axion`, execute:

```bash
Rscript run_all.R
```

O pipeline cria a pasta `saida_axion_lotofacil_v12` com os arquivos de evidencia.

## Saidas esperadas

- `estatisticas_dezenas_v12.csv`
- `diagnostico_filtros_v12.csv`
- `top_residual_v12.csv`
- `jogos_final_v12.csv`
- `metricas_conjunto_final_v12.csv`
- `simulacao_monte_carlo_v12.csv`
- `resumo_simulacao_v12.csv`
- `grafico_frequencia_dezenas_v12.png`
- `grafico_score_residual_v12.png`
- `relatorio_execucao_v12.txt`

## Registro e citacao

A serie documental v1.0 esta arquivada no Zenodo sob DOI `10.5281/zenodo.21522330`. A versao v1.2 deve ser tratada como pacote operacional de reprodutibilidade ate que seja publicada como nova versao no Zenodo.

## Nota metodologica

Sorteios regulares sao eventos aleatorios. O objetivo do modelo e organizar criterios tecnicos de exploracao e selecao, nao prever o resultado de concursos futuros.
