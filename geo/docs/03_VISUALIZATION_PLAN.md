# AXION-GEO - Plano de visualizações

**Status:** pré-especificação para Fase 1  
**Data:** 2026-09-10

O objetivo visual é detectar estrutura candidata que estatísticas isoladas podem esconder, mantendo uma trilha quantitativa que permita falsificar a impressão visual.

## Ordem proposta

### 1. Heatmap de ocupação 5x5

Mostrar frequência histórica por posição e, separadamente, desvio padronizado em relação a N0. Deve haver uma versão controlada por N1 para distinguir frequência marginal de geometria.

### 2. Perfil geométrico padronizado

Gráfico por famílias com `z` ou percentil nulo para cada métrica. Evitar misturar medidas em escalas brutas diferentes.

### 3. Radar de macrogeometria

Radar apenas com pequeno conjunto pré-registrado de eixos quase independentes, por exemplo:

- conectividade;
- dispersão;
- anisotropia;
- compacidade;
- simetria;
- concentração centro-borda.

O gráfico deve mostrar o valor observado e uma banda nula de 95%. Não usar as 47 variáveis em um radar único.

### 4. Atlas de formas

Representar concursos como miniaturas 5x5 e agrupá-los por distância no espaço GEO. Para cada cluster, exibir medóide, tamanho, dispersão interna e frequência esperada sob N0/N1.

A figura precisa informar se o cluster é apenas uma região naturalmente comum do espaço combinatório.

### 5. PCA geométrica

Projetar as métricas não redundantes em 2D com PCA. Começar por PCA por ser auditável e linear. Métodos não lineares, se utilizados, entram apenas como visualização auxiliar e nunca como prova de separação.

### 6. Trajetória temporal

Exibir em janelas fixas a evolução de macrofeatures e dos scores de distância ao nulo. A finalidade é verificar estabilidade, mudança de regime e regressão à média.

### 7. Matriz de recorrência de formas

Comparar concursos por distância geométrica e visualizar blocos de recorrência. Qualquer aparente periodicidade precisa de teste separado e correção de múltiplos testes.

## Gráficos que não entram como evidência primária

- nuvem de pontos sem baseline;
- radar sem banda nula;
- mapa de calor baseado apenas em contagens brutas;
- seleção manual de concursos parecidos;
- símbolos nomeados depois de observados;
- animações que dificultem comparação quantitativa.

## Gate antes da publicação de uma figura

Toda figura analítica deverá responder três perguntas no próprio título, legenda ou tabela associada:

1. qual é a estatística exibida;
2. qual é o comportamento esperado sob o nulo;
3. se o desvio observado sobreviveu ou não ao teste formal correspondente.
