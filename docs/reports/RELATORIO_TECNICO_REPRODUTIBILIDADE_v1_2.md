# Modelo Axion Lotofácil v1.2

## Relatório Técnico de Reprodutibilidade

**Autor:** Jacson Cruz do Nascimento  
**ORCID:** https://orcid.org/0009-0006-6535-9569  
**Local:** Brasília-DF, Brasil  
**Versão:** v1.2  
**Data:** 19/08/2026  
**Repositório:** https://github.com/Jacson-Nascimento/Jacson-Nascimento  
**PR de validação:** https://github.com/Jacson-Nascimento/Jacson-Nascimento/pull/61  
**Registro Zenodo da série v1.0:** https://doi.org/10.5281/zenodo.21522330

---

## Resumo executivo

Este relatório documenta a versão operacional v1.2 do **Modelo Axion Lotofácil**, estruturada como pipeline reprodutível para exploração combinatória, formação de espaço residual e seleção multicritério de combinações. A execução principal foi migrada para Python no GitHub Actions; a implementação em R permanece preservada como referência metodológica e histórica, sem compor a execução automatizada.

A intenção do entregável é demonstrar rastreabilidade, controle de integridade, documentação de parâmetros e geração de evidências computacionais. O modelo **não** deve ser interpretado como mecanismo de previsão de sorteios, recomendação financeira, garantia de premiação ou demonstração de vantagem preditiva contra sorteios regulares.

A execução validada processou **3,596 concursos válidos**, gerou **50,000 candidatos únicos**, formou espaço residual de **24,762 combinações**, exportou as **1.000** combinações mais bem ranqueadas, selecionou **25 jogos finais**, executou **1.000** simulações Monte Carlo, gerou gráficos, relatório de execução e **15** hashes SHA-256.

---

## 1. Intenção do entregável

O objetivo deste relatório é consolidar a versão v1.2 como evidência técnica do projeto. O documento mostra:

1. a arquitetura do pipeline;
2. a fonte e a proveniência dos dados;
3. a decisão arquivística leve;
4. os critérios de filtragem e formação do espaço residual;
5. as métricas geradas na execução validada;
6. os artefatos produzidos para reprodutibilidade;
7. os limites metodológicos que devem acompanhar qualquer interpretação dos resultados.

A contribuição do modelo está na organização analítica e auditável do processo de seleção, não na alteração da probabilidade matemática de sorteios independentes.

## 2. Fonte de dados e decisão arquivística

A fonte primária recomendada é o Portal Loterias CAIXA, seção de download de resultados da Lotofácil. A rotina operacional em Python usa o endpoint oficial de download de resultados da CAIXA para obter a planilha bruta quando ela não está presente localmente.

- Página institucional: https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
- Endpoint operacional: https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil
- Data/hora da execução no ambiente do workflow: 2026-08-19T15:33:20
- SHA-256 da planilha bruta baixada: `3e905d86109511fbc1eb6da1dec4abdab4bae1453125c2a03a41af4ee5cdcb51`

A versão v1.2 adota **pacote arquivístico leve**. O pacote final preserva a base histórica normalizada, a fonte CAIXA, o hash SHA-256 da planilha bruta, outputs, figuras, relatório de execução e checksums. A planilha bruta baixada pela rotina operacional não precisa ser anexada ao artefato final, desde que sua fonte e seu hash sejam preservados.

## 3. Arquitetura operacional

O fluxo operacional da v1.2 é:

```text
Base histórica CAIXA
        ↓
Download ou leitura local
        ↓
Registro de fonte e hash SHA-256
        ↓
Normalização e validação da base
        ↓
Métricas históricas das dezenas
        ↓
Geração de combinações candidatas
        ↓
Filtros combinatórios
        ↓
Formação do espaço residual
        ↓
Score multicritério
        ↓
Seleção final com controle de sobreposição
        ↓
Simulação Monte Carlo
        ↓
Outputs, figuras, relatório e checksums
```

## 4. Implementação computacional

A execução principal no GitHub Actions está em Python. O arquivo operacional é:

```text
lotofacil_axion/python/run_all.py
```

Os workflows usados são:

```text
.github/workflows/lotofacil-v12-reproducibility.yml
.github/workflows/lotofacil-v12-pr-validation.yml
```

A execução validada foi associada ao workflow run `32270708543` e ao artefato `9372037884`, com digest do artefato `sha256:184e62b29f351ca184bfde5a57247235ae5947dc284431c6691526ee27e4348f`.

## 5. Metodologia resumida

O espaço combinatório da Lotofácil é formado por combinações de 15 dezenas entre 25 possibilidades. A v1.2 não enumera todo o espaço combinatório; ela gera amostra operacional de candidatos, calcula métricas combinatórias e aplica filtros definidos para formar um espaço residual.

As métricas e filtros usados incluem: paridade, dezenas altas/baixas, soma total, sequências consecutivas, quantidade de números primos, borda/centro, repetição em relação ao último concurso, entropia de linha, balanceamento, antipopularidade relativa, diversidade histórica e estabilidade da soma.

O score total combina dimensões de aderência estatística, diversidade e penalização de padrões excessivamente concentrados. A seleção final controla a sobreposição entre jogos para evitar redundância excessiva no conjunto final.

## 6. Resultados da execução validada

| Indicador | Resultado |
|---|---:|
| Concursos válidos processados | 3,596 |
| Candidatos únicos gerados | 50,000 |
| Espaço residual | 24,762 |
| Top residual exportado | 1.000 |
| Jogos finais selecionados | 25 |
| Simulações Monte Carlo | 1.000 |
| Checksums registrados | 15 |
| Gráficos gerados | 2 |

## 7. Diagnóstico dos filtros

| Filtro | Antes | Depois | Eliminados |
|---|---:|---:|---:|
| pares_6_9 | 50,000 | 42,391 | 7,609 |
| altas_6_9 | 42,391 | 38,538 | 3,853 |
| soma_empirica_5_95 | 38,538 | 35,836 | 2,702 |
| max_consecutivas_ate_5 | 35,836 | 26,497 | 9,339 |
| primas_4_7 | 26,497 | 24,979 | 1,518 |
| borda_7_12 | 24,979 | 24,856 | 123 |
| repetidas_ultimo_6_12 | 24,856 | 24,762 | 94 |

## 8. Métricas do conjunto final

| Métrica | Valor |
|---|---:|
| Jogos finais | 25 |
| Cobertura de dezenas | 25 |
| Overlap médio entre jogos | 9.60 |
| Overlap máximo entre jogos | 12 |
| Score médio | 0.807118 |
| Soma média | 195.04 |
| Entropia média das linhas | 0.990992 |

## 9. Simulação Monte Carlo de referência

A simulação Monte Carlo serve como referência descritiva para comparação de métricas gerais. Ela não constitui teste de previsão. A execução v1.2 realizou 1.000 simulações uniformes de combinações de 15 dezenas.

| Métrica | Média | Desvio padrão | Mínimo | Mediana | Máximo |
|---|---:|---:|---:|---:|---:|
| soma | 195.172000 | 18.138341 | 147.000000 | 195.000000 | 252.000000 |
| pares | 7.160000 | 1.280640 | 3.000000 | 7.000000 | 11.000000 |
| altas | 7.208000 | 1.259493 | 4.000000 | 7.000000 | 11.000000 |
| primas | 5.382000 | 1.219657 | 2.000000 | 5.000000 | 9.000000 |
| borda | 9.641000 | 1.231924 | 6.000000 | 10.000000 | 13.000000 |
| max_consecutivas | 5.020000 | 1.489906 | 2.000000 | 5.000000 | 12.000000 |
| repetidas_ultimo | 8.974000 | 1.216883 | 5.000000 | 9.000000 | 13.000000 |
| entropia_linhas | 0.960629 | 0.030585 | 0.786245 | 0.971850 | 1.000000 |

## 10. Artefatos gerados

A execução validada produziu os seguintes conjuntos de evidências:

```text
data/processed/lotofacil_historico_normalizado.csv
data/raw/SOURCE_CAIXA.md
outputs/estatisticas_dezenas_v12.csv
outputs/diagnostico_filtros_v12.csv
outputs/top_residual_v12.csv
outputs/jogos_final_v12.csv
outputs/metricas_conjunto_final_v12.csv
outputs/simulacao_monte_carlo_v12.csv
outputs/resumo_simulacao_v12.csv
outputs/relatorio_execucao_v12.txt
figures/grafico_frequencia_dezenas_v12.png
figures/grafico_score_residual_v12.png
checksums/CHECKSUMS.sha256
```

## 11. Carteira final selecionada pelo pipeline

A tabela abaixo registra a saída do pipeline como evidência computacional. Ela não deve ser interpretada como recomendação de aposta.

| Jogo | Dezenas | Soma | Score |
|---:|---|---:|---:|
| 01 | 01 02 04 07 09 10 12 13 15 17 18 20 21 23 24 | 196 | 0.818955 |
| 02 | 01 03 04 06 08 10 11 13 14 17 18 20 21 24 25 | 195 | 0.813065 |
| 03 | 02 03 05 06 08 10 11 12 14 17 18 19 21 24 25 | 195 | 0.812156 |
| 04 | 01 02 04 05 07 08 11 14 15 17 18 20 22 23 25 | 192 | 0.809736 |
| 05 | 01 02 04 05 07 09 11 12 14 17 19 20 22 24 25 | 192 | 0.809736 |
| 06 | 01 02 04 05 06 10 12 13 14 17 19 20 23 24 25 | 195 | 0.809341 |
| 07 | 01 02 03 05 09 10 12 13 14 17 18 20 22 24 25 | 195 | 0.809341 |
| 08 | 01 03 05 06 08 09 11 12 14 17 18 20 23 24 25 | 196 | 0.808955 |
| 09 | 01 02 04 06 09 10 11 13 14 17 18 19 23 24 25 | 196 | 0.808955 |
| 10 | 01 03 04 06 07 10 11 13 14 17 19 20 22 24 25 | 196 | 0.806955 |
| 11 | 01 03 04 06 07 09 12 13 16 17 18 20 21 23 24 | 194 | 0.806140 |
| 12 | 02 03 04 06 07 09 10 13 15 17 18 20 21 24 25 | 194 | 0.806140 |
| 13 | 01 03 04 05 07 10 12 13 15 17 18 20 22 24 25 | 196 | 0.806140 |
| 14 | 01 03 04 05 08 10 12 13 14 17 18 20 21 23 25 | 194 | 0.806140 |
| 15 | 01 02 05 06 07 09 10 13 14 18 19 20 23 24 25 | 196 | 0.806140 |
| 16 | 02 04 05 06 08 09 10 12 15 17 18 19 21 23 25 | 194 | 0.806140 |
| 17 | 01 02 05 06 07 10 12 14 15 17 19 20 22 23 24 | 197 | 0.805753 |
| 18 | 01 03 05 06 07 10 11 12 14 17 19 20 21 24 25 | 195 | 0.805490 |
| 19 | 01 02 05 06 08 10 11 12 14 15 19 20 23 24 25 | 195 | 0.804078 |
| 20 | 01 02 05 06 08 09 11 13 15 17 18 20 21 24 25 | 195 | 0.803490 |
| 21 | 01 03 04 06 07 09 11 14 15 17 18 20 22 23 25 | 195 | 0.803490 |
| 22 | 01 04 06 07 09 10 12 13 15 16 17 19 20 23 24 | 196 | 0.803325 |
| 23 | 01 02 03 06 10 11 12 14 15 17 18 19 22 23 24 | 197 | 0.802938 |
| 24 | 01 03 05 07 08 10 11 13 14 15 17 20 22 24 25 | 195 | 0.802675 |
| 25 | 02 04 05 06 09 10 11 13 14 15 17 19 21 24 25 | 195 | 0.802675 |

## 12. Interpretação e limites

A versão v1.2 demonstra que o projeto já possui pipeline executável, evidência computacional, controle de integridade e protocolo de reprodução. O resultado central é a capacidade de documentar e reproduzir uma estratégia de filtragem e seleção multicritério.

O modelo não afirma prever sorteios. Em sorteios regulares e independentes, cada combinação válida mantém a mesma probabilidade matemática antes do sorteio. Portanto, a contribuição é de rastreabilidade, padronização, controle de redundância, diversidade do conjunto selecionado e documentação dos critérios aplicados.

## 13. Próximos passos técnicos

1. Consolidar a PR #61 como base operacional da v1.2.
2. Publicar pacote leve no Zenodo como versão v1.2.
3. Criar rotina de comparação fora da amostra.
4. Comparar carteiras geradas com carteiras aleatórias puras.
5. Implementar análise de sensibilidade dos pesos e filtros.
6. Avaliar estabilidade temporal por recortes anuais e mensais.
7. Preparar artigo metodológico após a consolidação das evidências.

## 14. Conclusão

O Modelo Axion Lotofácil v1.2 consolida a transição do projeto de uma exploração conceitual para um pacote operacional reprodutível. O entregável demonstra método, execução, evidência e integridade. A intenção é documentar um processo técnico de exploração combinatória e seleção multicritério, preservando limites metodológicos claros e evitando qualquer interpretação de garantia ou previsão de resultado.

## Referências e fontes

- CAIXA. Portal Loterias CAIXA - Lotofácil. https://loterias.caixa.gov.br/Paginas/Lotofacil.aspx
- CAIXA. Endpoint de download de resultados da Lotofácil. https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download?modalidade=Lotof%C3%A1cil
- Jacson Cruz do Nascimento. Modelo Axion Lotofácil, repositório GitHub. https://github.com/Jacson-Nascimento/Jacson-Nascimento
- Pull Request de validação v1.2. https://github.com/Jacson-Nascimento/Jacson-Nascimento/pull/61
- Registro Zenodo da série v1.0. https://doi.org/10.5281/zenodo.21522330

---

**Fonte geral das tabelas e figuras:** elaboração do autor com base nos artefatos gerados pelo workflow Python `lotofacil-v12-pr-validation`, execução de 19/08/2026.
