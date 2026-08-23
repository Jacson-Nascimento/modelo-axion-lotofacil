# Modelo Axion Lotofácil

**Autor:** Jacson Cruz do Nascimento  
**ORCID:** https://orcid.org/0009-0006-6535-9569  
**Local:** Brasília, DF, Brasil  
**Versão operacional:** v1.2  
**DOI da versão v1.2:** https://doi.org/10.5281/zenodo.21522638  
**DOI conceitual da série:** https://doi.org/10.5281/zenodo.21522329  
**DOI da série v1.0:** https://doi.org/10.5281/zenodo.21522330  
**Repositório canônico:** https://github.com/Jacson-Nascimento/modelo-axion-lotofacil  
**Licença:** CC BY 4.0, salvo indicação diversa nos arquivos de dados de terceiros.

Este repositório reúne os artefatos técnicos do **Modelo Axion Lotofácil**, um projeto experimental de modelagem combinatória, exploração estatística, eliminação de padrões, formação de espaço residual, score multicritério e validação por simulação no espaço da Lotofácil.

## Escopo

O modelo não demonstra vantagem preditiva contra sorteios regulares e não constitui recomendação financeira, garantia de premiação ou instrução de aposta. Sua contribuição está na estruturação auditável de filtros, métricas, simulações e critérios de seleção combinatória.

## Fonte de dados

A fonte primária recomendada é o Portal Loterias CAIXA:

```text
https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
```

A rotina Python baixa a base histórica pelo endpoint oficial de resultados da CAIXA quando a base não estiver presente em `data/raw/`.

## Execução principal em Python

A execução operacional no GitHub Actions usa Python.

Na raiz do repositório, executar:

```bash
python python/run_all.py
```

Dependências:

```bash
pip install -r environment/python-requirements.txt
```

A versão R permanece preservada no repositório como referência metodológica e histórica, mas fica desligada na execução automatizada do GitHub Actions.

## Estrutura operacional

```text
.
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

## Execução no GitHub Actions

O workflow manual `.github/workflows/lotofacil-v12-reproducibility.yml` executa o fluxo em Python. O workflow `.github/workflows/lotofacil-v12-pr-validation.yml` valida a PR no repositório dedicado.

## Saídas esperadas

A execução cria a pasta:

```text
saida_axion_lotofacil_v12
```

E espelha evidências em:

```text
outputs/
figures/
checksums/
data/processed/
```

Os artefatos incluem:

- estatísticas históricas das dezenas;
- diagnóstico dos filtros;
- espaço residual ranqueado;
- jogos finais selecionados;
- métricas de cobertura;
- simulação Monte Carlo de referência;
- gráficos de frequência e score;
- relatório de execução;
- hashes SHA-256.

## Reprodutibilidade

O protocolo completo está em `REPRODUCIBILITY.md`. Toda rodada operacional deve preservar:

- base bruta usada;
- parâmetros de execução;
- saídas geradas;
- gráficos;
- relatório de execução;
- hashes SHA-256.

## Citação

Usar os metadados em `CITATION.cff`. Para o pacote operacional v1.2, utilizar o DOI:

```text
10.5281/zenodo.21522638
```

O DOI conceitual da série é `10.5281/zenodo.21522329`. A versão 1.0 permanece identificada por `10.5281/zenodo.21522330`.

Novas alterações substantivas devem ser publicadas como nova versão no Zenodo apenas depois de uma rodada validada.

## Proveniência

Este repositório foi separado de `Jacson-Nascimento/Jacson-Nascimento`, onde o projeto residia em `lotofacil_axion/`. A migração de 23/08/2026 preservou o histórico e manteve a cópia de origem para rastreabilidade. O arquivo `ZENODO_RECORD.json` preserva também referências históricas ao contexto de publicação original da versão v1.2.
