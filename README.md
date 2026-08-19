# Modelo Axion Lotofacil

**Autor:** Jacson Cruz do Nascimento  
**ORCID:** https://orcid.org/0009-0006-6535-9569  
**Local:** Brasilia, DF, Brasil  
**Versao operacional:** v1.2  
**Registro Zenodo da serie v1.0:** https://doi.org/10.5281/zenodo.21522330  
**Licenca:** CC BY 4.0, salvo indicacao diversa nos arquivos de dados de terceiros.

Este diretorio reune os artefatos tecnicos do **Modelo Axion Lotofacil**, um projeto experimental de modelagem combinatoria, exploracao estatistica, eliminacao de padroes, formacao de espaco residual, score multicriterio e validacao por simulacao no espaco da Lotofacil.

## Escopo

O modelo nao demonstra vantagem preditiva contra sorteios regulares e nao constitui recomendacao financeira, garantia de premiacao ou instrucao de aposta. Sua contribuicao esta na estruturacao auditavel de filtros, metricas, simulacoes e criterios de selecao combinatoria.

## Fonte de dados

A fonte primaria recomendada e o Portal Loterias CAIXA:

```text
https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
```

A rotina Python baixa a base historica pelo endpoint oficial de resultados da CAIXA quando a base nao estiver presente em `data/raw/`.

## Execucao principal em Python

A execucao operacional no GitHub Actions usa Python.

No diretorio `lotofacil_axion`, executar:

```bash
python python/run_all.py
```

Dependencias:

```bash
pip install -r environment/python-requirements.txt
```

A versao R permanece preservada no repositorio como referencia metodologica e historica, mas fica desligada na execucao automatizada do GitHub Actions.

## Estrutura operacional

```text
lotofacil_axion/
├── README.md
├── REPRODUCIBILITY.md
├── CITATION.cff
├── LICENSE_NOTICE.md
├── ZENODO_RECORD.json
├── EVIDENCE_REGISTER.md
├── environment/
│   ├── README.md
│   ├── R-packages.txt
│   └── python-requirements.txt
├── python/
│   ├── README.md
│   └── run_all.py
├── scripts/
│   └── download_resultados_caixa.R
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
│   ├── raw/
│   │   └── README.md
│   └── processed/
│       └── README.md
├── outputs/
│   └── README.md
├── figures/
│   └── README.md
└── checksums/
    ├── README.md
    └── CHECKSUMS_TEMPLATE.sha256
```

## Execucao no GitHub Actions

O workflow manual `.github/workflows/lotofacil-v12-reproducibility.yml` executa o fluxo em Python. O workflow `.github/workflows/lotofacil-v12-pr-validation.yml` valida a PR quando acionado pelo GitHub.

## Saidas esperadas

A execucao cria a pasta:

```text
saida_axion_lotofacil_v12
```

E espelha evidencias em:

```text
outputs/
figures/
checksums/
data/processed/
```

Os artefatos incluem:

- estatisticas historicas das dezenas;
- diagnostico dos filtros;
- espaco residual ranqueado;
- jogos finais selecionados;
- metricas de cobertura;
- simulacao Monte Carlo de referencia;
- graficos de frequencia e score;
- relatorio de execucao;
- hashes SHA-256.

## Reprodutibilidade

O protocolo completo esta em `REPRODUCIBILITY.md`. Toda rodada operacional deve preservar:

- base bruta usada;
- parametros de execucao;
- saidas geradas;
- graficos;
- relatorio de execucao;
- hashes SHA-256.

## Citacao

Usar os metadados em `CITATION.cff`. Para a serie documental v1.0, utilizar o DOI:

```text
10.5281/zenodo.21522330
```

Novas alteracoes substantivas devem ser publicadas como nova versao no Zenodo apenas depois de uma rodada validada.
