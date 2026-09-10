# AXION-GEO

Braço experimental do Modelo Axion Lotofácil dedicado à análise espacial e morfológica dos concursos na grade 5x5.

## Objetivo

Investigar propriedades geométricas observáveis dos sorteios sem assumir capacidade preditiva. Todo padrão visual deve ser comparado com modelo nulo e submetido a controle de multiplicidade, estabilidade temporal e validação fora da amostra antes de qualquer uso operacional.

## Fase 0

A Fase 0 congelou 47 atributos geométricos e comparou suas médias contra o modelo nulo uniforme 15/25. Nenhuma feature foi promovida como evidência estatística após correção Benjamini-Hochberg.

## Fase 1 visual

A Fase 1 gera automaticamente, via GitHub Actions, a camada visual exploratória a partir da matriz binária congelada da Fase 0.

Artefatos previstos em `geo/outputs/visuals/`:

- `01_heatmap_observado_total.png`
- `02_heatmap_esperado_n0_total.png`
- `03_heatmap_residuo_padronizado_total.png`
- `04_small_multiples_observado_janelas.png`
- `05_small_multiples_residuo_janelas.png`
- `06_barplot_macrogeometria_zscores.png`
- `07_dashboard_fase1_resumo.png`
- `visuals_summary.csv`
- `visuals_metadata.json`
- `visuals_manifest.md`
- `README.md`

## Entrada congelada

A matriz binária da Fase 0 é preservada em `geo/data/binary_matrix.csv.gz`. O arquivo representa concursos 1 a 3435, com 25 colunas binárias `d01` a `d25`, além de `contest` e `date`.

## Execução local

```bash
python geo/src/run_visual_phase1.py \
  --input geo/data/binary_matrix.csv.gz \
  --phase0-summary geo/outputs/null_summary_B20000.csv \
  --output-dir geo/outputs/visuals
```

## Execução no GitHub

O workflow `.github/workflows/axion-geo-visual.yml` roda automaticamente em mudanças da camada GEO e também permite execução manual. Ele valida a base, executa os testes, produz os sete gráficos, publica os resultados no Job Summary e disponibiliza todos os artefatos para download.

## Regra de interpretação

Os gráficos são diagnósticos exploratórios. Concentração visual, simetria, cluster ou resíduo extremo não constituem evidência de vantagem preditiva. A hipótese operacional prioritária permanece a aleatoriedade.

Autor: Jacson Cruz do Nascimento
