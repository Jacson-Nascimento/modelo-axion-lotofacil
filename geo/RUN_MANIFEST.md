# AXION-GEO - Run Manifest

Autor: Jacson Cruz do Nascimento  
Branch experimental: `feature/axion-geo-phase0`

## Fase 0

- Base congelada: concursos 1 a 3435.
- Representação: matriz binária 25D / grade 5x5.
- Catálogo: 47 atributos geométricos.
- Nulo: uniforme 15/25 sem reposição.
- Monte Carlo: B = 20.000.
- Seed: 20260910.
- Correção: Benjamini-Hochberg.
- Resultado: nenhuma feature promovida após controle de multiplicidade.

## Fase 1 visual

- Entrada: `geo/data/binary_matrix.csv.gz`.
- Script: `geo/src/run_visual_phase1.py`.
- Workflow: `.github/workflows/axion-geo-visual.yml`.
- Janelas: total, 1000, 500 e 250 concursos.
- Saídas: sete PNGs, resumo por célula, metadados, manifesto, checksums e README de resultados.
- Publicação: GitHub Actions Job Summary, artefato de execução e commit automático em `geo/outputs/visuals/`.
- Status: exploratório, sem uso preditivo.

Próximo gate: N1 com preservação das frequências marginais históricas por dezena.
