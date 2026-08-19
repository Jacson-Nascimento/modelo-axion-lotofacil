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

O arquivo pode estar em `data/raw/` ou em outro caminho indicado no objeto `config` do script R.

## Fonte recomendada da base historica

A fonte primaria recomendada e o Portal Loterias CAIXA:

```text
https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
```

O pacote inclui o script:

```text
scripts/download_resultados_caixa.R
```

Esse script baixa a base historica pelo endpoint:

```text
https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil
```

No GitHub Actions, o workflow `lotofacil-v12-reproducibility.yml` executa automaticamente esse download quando nenhuma base compativel estiver presente em `data/raw/`.

## Ambiente

Versao recomendada:

- R 4.3 ou superior;
- pacotes listados em `environment/R-packages.txt`;
- sistema operacional Windows, Linux ou macOS.

Os pacotes nao sao instalados automaticamente por padrao. Para ativar instalacao automatica, altere `config$instalar_pacotes` para `TRUE`.

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
Rscript run_all.R
```

Se a base ainda nao estiver em `data/raw/`, executar antes:

```bash
Rscript scripts/download_resultados_caixa.R
```

## Fluxo computacional

1. Carregar configuracoes gerais.
2. Carregar pacotes e funcoes utilitarias.
3. Importar e validar a base historica.
4. Calcular metricas historicas das dezenas.
5. Definir filtros empiricos.
6. Gerar combinacoes candidatas.
7. Calcular metricas das candidatas.
8. Aplicar filtros e formar o espaco residual.
9. Ranquear combinacoes por score multicriterio.
10. Selecionar jogos finais com controle de sobreposicao.
11. Executar simulacao Monte Carlo de referencia.
12. Exportar evidencias em CSV, PNG e TXT.

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

A pasta de saida deve conter:

```text
estatisticas_dezenas_v12.csv
diagnostico_filtros_v12.csv
top_residual_v12.csv
jogos_final_v12.csv
metricas_conjunto_final_v12.csv
simulacao_monte_carlo_v12.csv
resumo_simulacao_v12.csv
grafico_frequencia_dezenas_v12.png
grafico_score_residual_v12.png
relatorio_execucao_v12.txt
```

## Integridade

Apos a execucao, gerar hashes SHA-256 dos arquivos de entrada e saida e registrar em `checksums/CHECKSUMS.sha256`.

Exemplo em PowerShell:

```powershell
Get-FileHash .\data\raw\* -Algorithm SHA256
Get-FileHash .\saida_axion_lotofacil_v12\* -Algorithm SHA256
```

Exemplo em Linux ou macOS:

```bash
sha256sum data/raw/* saida_axion_lotofacil_v12/* > checksums/CHECKSUMS.sha256
```

## Limites de interpretacao

O modelo nao deve ser interpretado como mecanismo de previsao de sorteios. As simulacoes servem para avaliar diversidade, redundancia, aderencia estatistica e comportamento dos filtros. Qualquer alteracao de parametros deve ser registrada para preservar rastreabilidade.
