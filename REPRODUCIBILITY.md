# Protocolo de Reprodutibilidade - Modelo Axion Lotofacil v1.2

**Autor:** Jacson Cruz do Nascimento  
**ORCID:** https://orcid.org/0009-0006-6535-9569  
**Projeto:** Modelo Axion Lotofacil  
**Versao:** v1.2  
**Local:** Brasilia, DF, Brasil

## Objetivo

Este protocolo define o procedimento minimo para reproduzir a execucao operacional do Modelo Axion Lotofacil v1.2, verificar a integridade da base de entrada, executar o pipeline e conferir as evidencias geradas.

## Entrada de dados

A entrada deve ser uma planilha historica da Lotofacil com:

- uma linha por concurso;
- coluna de identificacao do concurso, quando disponivel;
- coluna de data do sorteio, quando disponivel;
- quinze colunas numericas contendo as dezenas sorteadas;
- dezenas entre 1 e 25;
- exatamente quinze dezenas distintas por concurso.

A rotina Python baixa automaticamente a base historica oficial quando nao encontra arquivo compativel em `data/raw/`.

## Fonte recomendada da base historica

A fonte primaria recomendada e o Portal Loterias CAIXA:

```text
https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
```

A rotina principal em Python usa o endpoint:

```text
https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil
```

## Ambiente principal

A execucao operacional no GitHub Actions usa Python.

Versao recomendada:

- Python 3.11 ou superior;
- pacotes listados em `environment/python-requirements.txt`;
- sistema operacional Linux no GitHub Actions ou Windows, Linux e macOS em execucao local.

Instalacao local:

```bash
pip install -r environment/python-requirements.txt
```

## Versao R

Os scripts R permanecem preservados no repositorio como referencia metodologica e historica. A execucao automatizada do GitHub Actions fica em Python.

## Semente e parametros de controle

A configuracao padrao usa:

```text
seed = 20260427
n_candidatos = 50000
n_jogos_finais = 25
n_top_residual_export = 1000
n_sim = 1000
```

Alteracoes nesses parametros devem ser documentadas no relatorio de execucao.

## Comando de execucao local

No diretorio `lotofacil_axion`, executar:

```bash
python python/run_all.py
```

## Execucao no GitHub Actions

Workflow manual:

```text
.github/workflows/lotofacil-v12-reproducibility.yml
```

Workflow de PR:

```text
.github/workflows/lotofacil-v12-pr-validation.yml
```

Ambos usam Python como motor de execucao.

## Fluxo computacional

1. Criar diretorios de trabalho.
2. Baixar a base historica oficial quando ausente.
3. Registrar proveniencia da base em `data/raw/SOURCE_CAIXA.md`.
4. Importar e validar a planilha historica.
5. Gerar base normalizada em `data/processed/`.
6. Calcular metricas historicas das dezenas.
7. Gerar combinacoes candidatas.
8. Calcular metricas combinatorias das candidatas.
9. Aplicar filtros e formar o espaco residual.
10. Ranquear combinacoes por score multicriterio.
11. Selecionar jogos finais com controle de sobreposicao.
12. Executar simulacao Monte Carlo de referencia.
13. Exportar evidencias em CSV, PNG, TXT e SHA-256.

## Criterios de aceitacao

Uma execucao e considerada valida quando:

- a base e importada sem linhas invalidas;
- todas as dezenas estao no intervalo de 1 a 25;
- cada concurso possui quinze dezenas distintas;
- o numero de candidatos unicos e registrado;
- o espaco residual possui pelo menos uma combinacao;
- o numero de jogos finais e igual ao parametro `n_jogos_finais`, salvo restricao documentada;
- os arquivos de saida sao criados;
- o relatorio de execucao registra base, concursos, filtros, espaco residual e metricas do conjunto final;
- os checksums sao recalculados apos a geracao dos artefatos finais.

## Evidencias obrigatorias

A execucao deve gerar:

```text
outputs/estatisticas_dezenas_v12.csv
outputs/diagnostico_filtros_v12.csv
outputs/top_residual_v12.csv
outputs/jogos_final_v12.csv
outputs/metricas_conjunto_final_v12.csv
outputs/simulacao_monte_carlo_v12.csv
outputs/resumo_simulacao_v12.csv
figures/grafico_frequencia_dezenas_v12.png
figures/grafico_score_residual_v12.png
outputs/relatorio_execucao_v12.txt
checksums/CHECKSUMS.sha256
data/processed/lotofacil_historico_normalizado.csv
```

## Integridade

A rotina Python gera `checksums/CHECKSUMS.sha256` ao final da execucao. O arquivo deve ser preservado junto aos artefatos finais.

## Limites de interpretacao

O modelo nao deve ser interpretado como mecanismo de previsao de sorteios. As simulacoes servem para avaliar diversidade, redundancia, aderencia estatistica e comportamento dos filtros. Qualquer alteracao de parametros deve ser registrada para preservar rastreabilidade.
