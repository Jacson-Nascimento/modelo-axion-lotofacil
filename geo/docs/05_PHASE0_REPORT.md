# AXION-GEO - Relatório da Fase 0

**Execução:** 2026-09-10  
**Versão:** 0.1.0  
**Autor:** Jacson Cruz do Nascimento  
**Status:** triagem, sem uso preditivo

## 1. Entrada

Arquivo: `binary_matrix.csv`  
Concursos: 1 a 3435  
Quantidade: 3435  
Período: 2003-09-29 a 2025-07-05  
SHA-256 da matriz binária usada: `1b914b6ce9c566c12352d92ba739177ab741a587eaf1be4f64e5de1597768166`

Validações:

- 25 colunas binárias presentes;
- todos os concursos com exatamente 15 células ocupadas;
- nenhuma duplicidade de identificador de concurso detectada.

## 2. Feature matrix

Foram calculados 47 atributos geométricos por concurso, conforme `01_METRICS_CATALOG.md`.

O arquivo derivado completo é `geo_feature_matrix.csv`. O pipeline grava também summary, metadados e checksums.

## 3. Testes unitários

Comando:

```bash
PYTHONPATH=geo/src python -m pytest -q geo/tests/test_geometry.py
```

Resultado da execução: `5 passed`.

Foram testados:

- mapeamento row-major 01 a 25;
- conservação das somas por linha e coluna;
- identidade do perímetro;
- limites dos scores de simetria;
- rejeição de grade com quantidade inválida de dezenas.

## 4. Modelo nulo N0

Modelo: seleção uniforme sem reposição de 15 entre 25.  
Combinações simuladas: `B = 20.000`.  
Seed: `20260910`.  
Correção: Benjamini-Hochberg nos 47 testes de média.

## 5. Resultado de triagem

| Feature | Média observada | Média N0 | z triagem | p | q BH |
|---|---:|---:|---:|---:|---:|
| centroid_x | 0,01454 | 0,00123 | 3,0559 | 0,00224 | 0,06008 |
| col_5 | 3,06346 | 3,00825 | 3,0166 | 0,00256 | 0,06008 |
| cov_xy | 0,01165 | -0,00286 | 2,2956 | 0,02170 | 0,29325 |
| row_3 | 3,02737 | 2,98970 | 2,0323 | 0,04212 | 0,29325 |
| row_2 | 2,97787 | 3,01500 | -2,0103 | 0,04440 | 0,29325 |
| sym_diag_main | 0,66428 | 0,66808 | -1,9881 | 0,04680 | 0,29325 |
| inner_ring | 4,75750 | 4,80005 | -1,9799 | 0,04771 | 0,29325 |
| center | 0,60932 | 0,59195 | 1,9131 | 0,05574 | 0,29325 |
| adj_diag_dl | 5,56157 | 5,60785 | -1,9098 | 0,05615 | 0,29325 |
| adj_orth | 13,94294 | 14,00195 | -1,7817 | 0,07480 | 0,31958 |

Nenhuma feature alcançou `q < 0,05`.

## 6. Interpretação

O resultado mais próximo do limiar está em `centroid_x` e `col_5`. Não há fundamento para tratá-los como duas descobertas independentes. As duas variáveis capturam, por construções diferentes, uma pequena concentração horizontal no lado direito do volante.

Isso pode nascer de frequências marginais de dezenas específicas, sem qualquer organização de forma entre as 15 posições. Portanto, a Fase 0 não identificou até aqui evidência de um padrão morfológico distinto do nulo uniforme depois do controle de multiplicidade.

A conclusão correta desta etapa é negativa, porém informativa: não existe base para acrescentar filtro geométrico ao Axion.

## 7. Limitações

- O teste atual compara médias, podendo perder diferenças em caudas, multimodalidade ou dependência conjunta.
- Os 47 atributos incluem redundâncias determinísticas.
- O z de triagem não modela eventual dependência temporal entre concursos.
- N0 não controla heterogeneidade marginal histórica entre dezenas.
- O conjunto pós-3435 não deve ser usado para redesenhar a Fase 0.

## 8. Fase 1 proposta

Antes de produzir um atlas visual com interpretação inferencial:

1. congelar famílias de features não redundantes;
2. implementar N1 com margens fixas por dezena;
3. comparar N0 versus N1;
4. produzir heatmap, perfil padronizado, radar de macrogeometria e atlas de formas com bandas nulas;
5. definir qualquer motivo geométrico formalmente antes de testá-lo;
6. somente depois avaliar estabilidade temporal e fora da amostra.
