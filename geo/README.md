# AXION-GEO

## Geometria espacial da Lotofácil

**Autor:** Jacson Cruz do Nascimento  
**Status:** experimental, Fase 0  
**Versão:** 0.1.0  
**Data de congelamento da especificação:** 2026-09-10

AXION-GEO é um braço experimental do Modelo Axion dedicado à morfologia espacial dos sorteios da Lotofácil no volante 5x5. Cada concurso é representado como uma matriz binária 5x5, com as dezenas 01 a 25 em ordem por linhas.

O objetivo é medir propriedades geométricas que podem ficar ocultas em estatísticas agregadas, como adjacência, componentes conectados, centroide, dispersão, forma, corridas e simetrias. A existência de um padrão visual não é tratada como evidência preditiva. Toda hipótese deve ser confrontada com modelos nulos explícitos e, antes de qualquer uso operacional, com validação fora da amostra.

## Relação com os demais braços do Axion

AXION-GEO não substitui o Axion principal nem o estudo anterior de quadrantes. O estudo de quadrantes resume cada combinação em poucos eixos agregados. O GEO preserva a estrutura completa do volante e mede a morfologia da ocupação das 15 células.

A Fase 0 reutiliza a matriz binária produzida pelo projeto Axion até o concurso 3435. Concursos posteriores não foram utilizados para ajustar o catálogo GEO de atributos.

## Fase 0

A Fase 0 congela:

- mapeamento 5x5;
- catálogo de 47 atributos espaciais;
- validações de integridade;
- modelo nulo N0, 15 dezenas escolhidas uniformemente entre 25, sem reposição;
- seed `20260910`;
- triagem com `B = 20.000` combinações nulas;
- correção Benjamini-Hochberg sobre os 47 testes de média;
- política de não integração preditiva nesta etapa.

Resultado: nenhum atributo atingiu `q < 0,05`. Os menores valores ajustados foram aproximadamente `q = 0,0601` para `centroid_x` e `col_5`. Esses dois resultados são fortemente relacionados e apontam primeiro para uma assimetria marginal horizontal, não para evidência independente de uma forma geométrica recorrente.

## Estrutura

```text
geo/
  README.md
  config/
    phase0.json
  docs/
    00_PROJECT_CHARTER.md
    01_METRICS_CATALOG.md
    02_VALIDATION_PROTOCOL.md
    03_VISUALIZATION_PLAN.md
    04_DECISION_LOG.md
    05_PHASE0_REPORT.md
  src/
    geometry.py
    run_phase0.py
  tests/
    test_geometry.py
  outputs/
    README.md
    null_summary_B20000.csv
    phase0_metadata_B20000.json
    CHECKSUMS.sha256
```

O arquivo completo `geo_feature_matrix.csv` é um artefato derivado e pode ser regenerado a partir da matriz binária de entrada.

## Execução

```bash
PYTHONPATH=geo/src python geo/src/run_phase0.py \
  --input /caminho/para/binary_matrix.csv \
  --output-dir geo/outputs \
  --null-draws 20000 \
  --seed 20260910
```

Testes:

```bash
PYTHONPATH=geo/src python -m pytest -q geo/tests/test_geometry.py
```

## Regra de interpretação

O AXION-GEO parte da hipótese de aleatoriedade. Um padrão só pode avançar para teste prospectivo se for definido antes do teste, superar o modelo nulo apropriado, resistir ao controle de multiplicidade, mostrar estabilidade e sobreviver fora da amostra. Visualizações são instrumentos de diagnóstico, não provas.
