# AXION-GEO - Catálogo de métricas da Fase 0

**Versão congelada:** 0.1.0  
**Data:** 2026-09-10

## Convenção espacial

O volante é mapeado em ordem por linhas:

```text
01 02 03 04 05
06 07 08 09 10
11 12 13 14 15
16 17 18 19 20
21 22 23 24 25
```

Para momentos espaciais, coluna e linha são centradas em `-2, -1, 0, 1, 2`. Cada concurso contém exatamente 15 células ocupadas.

## Catálogo congelado, 47 atributos

### A. Ocupação por linha e coluna, 10

`row_1` a `row_5`: quantidade de dezenas sorteadas em cada linha.  
`col_1` a `col_5`: quantidade de dezenas sorteadas em cada coluna.

Essas métricas são marginais e servem também para identificar quando um aparente efeito de forma pode ser explicado apenas por deslocamento de massa no volante.

### B. Adjacência, 6

`adj_h`: pares ocupados adjacentes horizontalmente.  
`adj_v`: pares ocupados adjacentes verticalmente.  
`adj_diag_dr`: pares ocupados na diagonal descendente para a direita.  
`adj_diag_dl`: pares ocupados na diagonal descendente para a esquerda.  
`adj_orth`: `adj_h + adj_v`.  
`adj_diag`: `adj_diag_dr + adj_diag_dl`.

### C. Conectividade e componentes, 5

`comp4_count`: número de componentes conexos com vizinhança ortogonal.  
`comp4_largest`: tamanho do maior componente ortogonal.  
`isolated4`: células sem vizinho ortogonal ocupado.  
`comp8_count`: número de componentes com vizinhança ortogonal e diagonal.  
`comp8_largest`: tamanho do maior componente com vizinhança de 8 direções.

### D. Centroide e momentos, 8

`centroid_x`: média das coordenadas horizontais das 15 células.  
`centroid_y`: média das coordenadas verticais.  
`centroid_radius`: distância euclidiana do centroide ao centro do volante.  
`var_x`: variância horizontal.  
`var_y`: variância vertical.  
`cov_xy`: covariância espacial entre os eixos.  
`anisotropy`: diferença normalizada entre os autovalores principal e secundário da matriz de covariância.  
`radius_gyration`: raiz da soma dos autovalores, equivalente à dispersão radial RMS em torno do centroide.

### E. Caixa, perímetro e compacidade, 5

`bbox_width`: largura da menor caixa alinhada aos eixos contendo as 15 células.  
`bbox_height`: altura da caixa.  
`bbox_area`: área da caixa.  
`perimeter4`: perímetro ortogonal da forma binária, definido por `4*15 - 2*adj_orth`.  
`compactness`: `4*pi*15/perimeter4^2`.

### F. Anéis concêntricos, 3

`outer_ring`: ocupação das 16 posições da borda externa.  
`inner_ring`: ocupação das 8 posições internas que circundam o centro.  
`center`: indicador de ocupação da posição 13.

As três métricas formam uma partição exata das 15 dezenas, portanto `outer_ring + inner_ring + center = 15`.

### G. Corridas, 5

`h_runs`: número total de blocos horizontais contíguos de 1s.  
`v_runs`: número total de blocos verticais contíguos.  
`longest_h`: maior bloco horizontal.  
`longest_v`: maior bloco vertical.  
`longest_diag`: maior bloco diagonal contínuo em qualquer uma das duas orientações.

### H. Simetrias contínuas, 5

Cada score é a proporção das 15 células ocupadas que continua ocupada após a transformação, intervalo `[0,1]`.

`sym_lr`: reflexão esquerda-direita.  
`sym_ud`: reflexão cima-baixo.  
`sym_rot180`: rotação de 180 graus.  
`sym_diag_main`: reflexão na diagonal principal.  
`sym_diag_anti`: reflexão na diagonal secundária.

## Dependências determinísticas conhecidas

Alguns atributos são deliberadamente redundantes para legibilidade e diagnóstico. Exemplos:

- `perimeter4` é função exata de `adj_orth`;
- `outer_ring + inner_ring + center = 15`;
- os cinco `row_*` somam 15;
- os cinco `col_*` somam 15;
- `h_runs` e `v_runs` possuem relações diretas com adjacências nas respectivas direções.

Por isso, os 47 atributos não devem ser interpretados como 47 dimensões independentes. A Fase 0 aplicou uma correção global conservadora aos 47 testes e preserva esse resultado como executado. A Fase 1 deverá pré-registrar famílias inferenciais não redundantes antes de novos testes.
